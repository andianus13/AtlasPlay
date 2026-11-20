"""Dashboard admin: statistik, CRUD file master, moderasi file transaksi, dan laporan (HTML + PDF)."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload
from starlette.datastructures import UploadFile

from app.config import REQUEST_STATUSES, ROLE_ADMIN, ROLE_USER
from app.database import get_db
from app.images import ImageError, delete_local_image, is_http_url, save_upload
from app.models import (
    Comment,
    Developer,
    Game,
    GameRequest,
    Platform,
    SavedGame,
    User,
    utcnow,
)
from app.reports import (
    REPORT_SHORT,
    REPORT_TITLES,
    activity_report,
    build_activity_pdf,
    build_master_pdf,
    build_popular_pdf,
    master_report,
    popular_report,
)
from app.security import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    hash_password,
    require_admin,
    verify_csrf,
)
from app.services import (
    like_pattern,
    paginate,
    parse_int,
    platform_counts,
    recalculate_average_rating,
    unique_game_slug,
)
from app.templating import flash, render
from app.utils import is_local_upload, is_valid_email, is_valid_username, safe_next_url, slugify

def _load_pending_count(request: Request, db: Session = Depends(get_db)) -> None:
    """Jumlah pengajuan Pending untuk lencana di sidebar admin (dipakai semua halaman admin)."""
    request.state.pending_count = (
        db.scalar(select(func.count(GameRequest.id)).where(GameRequest.status == "Pending")) or 0
    )


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin), Depends(verify_csrf), Depends(_load_pending_count)],
)

PER_PAGE = 12
_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")

# (field, label, panjang maksimal, wajib, harus URL)
GAME_TEXT_RULES = [
    ("title", "Judul", 160, True, False),
    ("short_summary", "Ringkasan singkat", 300, False, False),
    ("official_website_url", "Website resmi", 255, False, True),
    ("min_os", "OS minimum", 120, False, False),
    ("min_cpu", "CPU minimum", 160, False, False),
    ("min_ram", "RAM minimum", 60, False, False),
    ("min_gpu", "GPU minimum", 160, False, False),
    ("storage_req", "Penyimpanan", 60, False, False),
    ("rec_os", "OS rekomendasi", 120, False, False),
    ("rec_cpu", "CPU rekomendasi", 160, False, False),
    ("rec_ram", "RAM rekomendasi", 60, False, False),
    ("rec_gpu", "GPU rekomendasi", 160, False, False),
]


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def _text(form, key: str) -> str:
    return str(form.get(key) or "").strip()


def _get_or_404(db: Session, model, object_id: int):
    from fastapi import HTTPException

    instance = db.get(model, object_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="Data yang dicari tidak ditemukan.")
    return instance


def _admin_ctx(section: str, **extra) -> dict:
    return {"admin_section": section, **extra}


# --------------------------------------------------------------------------- #
# DASHBOARD
# --------------------------------------------------------------------------- #
@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db)):
    def count(model, *where) -> int:
        stmt = select(func.count(model.id))
        for clause in where:
            stmt = stmt.where(clause)
        return db.scalar(stmt) or 0

    stats = [
        {"key": "games", "label": "Total game", "value": count(Game), "href": "/admin/games"},
        {"key": "developers", "label": "Total developer", "value": count(Developer), "href": "/admin/developers"},
        {"key": "users", "label": "Total pengguna", "value": count(User), "href": "/admin/users"},
        {"key": "saved", "label": "Game disimpan", "value": count(SavedGame), "href": "/admin/saved"},
        {"key": "comments", "label": "Total komentar", "value": count(Comment), "href": "/admin/comments"},
        {
            "key": "pending",
            "label": "Request pending",
            "value": count(GameRequest, GameRequest.status == "Pending"),
            "href": "/admin/requests?status=Pending",
        },
    ]
    platforms = platform_counts(db)
    pending = list(
        db.scalars(
            select(GameRequest)
            .options(joinedload(GameRequest.user))
            .where(GameRequest.status == "Pending")
            .order_by(GameRequest.submitted_at.desc())
            .limit(5)
        ).all()
    )
    latest_comments = list(
        db.scalars(
            select(Comment)
            .options(joinedload(Comment.user), joinedload(Comment.game))
            .order_by(Comment.created_at.desc())
            .limit(5)
        ).all()
    )
    most_saved = popular_report(db, 5)["most_saved"]
    return render(
        request,
        "admin/dashboard.html",
        _admin_ctx(
            "dashboard",
            stats=stats,
            platforms=platforms,
            platform_max=max([c for _, c in platforms], default=1) or 1,
            pending=pending,
            latest_comments=latest_comments,
            most_saved=most_saved,
        ),
    )


# --------------------------------------------------------------------------- #
# CRUD GAMES
# --------------------------------------------------------------------------- #
def _game_form_ctx(db: Session, game: Optional[Game], form: dict, errors: dict) -> dict:
    return _admin_ctx(
        "games",
        game=game,
        form=form,
        errors=errors,
        developers=list(db.scalars(select(Developer).order_by(func.lower(Developer.name))).all()),
        platforms=list(db.scalars(select(Platform).order_by(Platform.id)).all()),
    )


def _game_to_form(game: Game) -> dict:
    data = {field: getattr(game, field) or "" for field, *_ in GAME_TEXT_RULES}
    data["full_description"] = game.full_description or ""
    data["release_date"] = game.release_date.isoformat() if game.release_date else ""
    data["developer_id"] = game.developer_id or ""
    data["is_featured"] = game.is_featured
    data["platform_ids"] = [p.id for p in game.platforms]
    data["cover_url"] = game.cover_image if game.cover_image and not is_local_upload(game.cover_image) else ""
    data["banner_url"] = game.banner_image if game.banner_image and not is_local_upload(game.banner_image) else ""
    return data


@router.get("/games")
def games_list(request: Request, q: str = "", page: str = "1", db: Session = Depends(get_db)):
    q = q.strip()[:80]
    stmt = select(Game).options(selectinload(Game.platforms), selectinload(Game.developer))
    if q:
        stmt = stmt.where(Game.title.ilike(like_pattern(q), escape="\\"))
    stmt = stmt.order_by(Game.updated_at.desc(), Game.id.desc())
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE)
    return render(
        request, "admin/games_list.html", _admin_ctx("games", result=result, q=q, params={"q": q})
    )


@router.get("/games/new")
def game_new(request: Request, db: Session = Depends(get_db)):
    return render(request, "admin/game_form.html", _game_form_ctx(db, None, {"platform_ids": []}, {}))


@router.get("/games/{game_id}/edit")
def game_edit(game_id: int, request: Request, db: Session = Depends(get_db)):
    game = _get_or_404(db, Game, game_id)
    return render(request, "admin/game_form.html", _game_form_ctx(db, game, _game_to_form(game), {}))


async def _save_game(request: Request, db: Session, game: Optional[Game]):
    form = await request.form()
    values: dict = {field: _text(form, field) for field, *_ in GAME_TEXT_RULES}
    values["full_description"] = _text(form, "full_description")
    values["release_date"] = _text(form, "release_date")
    values["developer_id"] = _text(form, "developer_id")
    values["is_featured"] = form.get("is_featured") == "on"
    values["cover_url"] = _text(form, "cover_url")
    values["banner_url"] = _text(form, "banner_url")
    errors: dict[str, str] = {}

    for field, label, limit, required, is_url in GAME_TEXT_RULES:
        value = values[field]
        if required and not value:
            errors[field] = f"{label} wajib diisi."
        elif len(value) > limit:
            errors[field] = f"{label} maksimal {limit} karakter."
        elif is_url and value and not is_http_url(value):
            errors[field] = f"{label} harus diawali http:// atau https://."
    if len(values["full_description"]) > 20000:
        errors["full_description"] = "Deskripsi maksimal 20.000 karakter."

    release: Optional[date] = None
    if values["release_date"]:
        try:
            release = date.fromisoformat(values["release_date"])
        except ValueError:
            errors["release_date"] = "Format tanggal tidak valid."

    developer_id = parse_int(values["developer_id"])
    if values["developer_id"] and (developer_id is None or db.get(Developer, developer_id) is None):
        errors["developer_id"] = "Developer tidak ditemukan."

    wanted_ids = {parse_int(v) for v in form.getlist("platform_ids")}
    wanted_ids.discard(None)
    platforms = list(db.scalars(select(Platform).where(Platform.id.in_(wanted_ids))).all()) if wanted_ids else []
    values["platform_ids"] = [p.id for p in platforms]
    if not platforms:
        errors["platform_ids"] = "Pilih minimal satu platform."

    # ---- gambar: unggah > URL > hapus > biarkan -------------------------- #
    new_files: list[str] = []
    final: dict[str, Optional[str]] = {
        "cover": game.cover_image if game else None,
        "banner": game.banner_image if game else None,
    }
    for kind in ("cover", "banner"):
        upload = form.get(f"{kind}_file")
        url = values[f"{kind}_url"]
        clear = form.get(f"clear_{kind}") == "on"
        if isinstance(upload, UploadFile) and upload.filename:
            try:
                path = await save_upload(upload, kind)
                new_files.append(path)
                final[kind] = path
            except ImageError as exc:
                errors[f"{kind}_file"] = str(exc)
        elif url:
            if len(url) > 400 or not is_http_url(url):
                errors[f"{kind}_url"] = "URL gambar harus diawali http:// atau https:// (maksimal 400 karakter)."
            else:
                final[kind] = url
        elif clear:
            final[kind] = None

    if errors:
        for path in new_files:  # jangan tinggalkan file yatim bila form gagal
            delete_local_image(path)
        return render(
            request, "admin/game_form.html", _game_form_ctx(db, game, values, errors), status_code=400
        )

    creating = game is None
    if creating:
        game = Game(slug=unique_game_slug(db, values["title"]))
        db.add(game)
    old_images = [] if creating else [game.cover_image, game.banner_image]

    for field, *_ in GAME_TEXT_RULES:
        setattr(game, field, values[field] or None)
    game.title = values["title"]
    game.full_description = values["full_description"] or None
    game.release_date = release
    game.developer_id = developer_id
    game.is_featured = values["is_featured"]
    game.platforms = platforms
    game.cover_image = final["cover"]
    game.banner_image = final["banner"]
    game.updated_at = utcnow()
    db.commit()

    for old in old_images:  # hapus file lama yang sudah tidak dipakai
        if old and old not in (game.cover_image, game.banner_image):
            delete_local_image(old)

    flash(request, f"Game “{game.title}” {'ditambahkan' if creating else 'diperbarui'}.", "success")
    return _redirect("/admin/games")


@router.post("/games/new")
async def game_create(request: Request, db: Session = Depends(get_db)):
    return await _save_game(request, db, None)


@router.post("/games/{game_id}/edit")
async def game_update(game_id: int, request: Request, db: Session = Depends(get_db)):
    return await _save_game(request, db, _get_or_404(db, Game, game_id))


@router.post("/games/{game_id}/delete")
def game_delete(game_id: int, request: Request, db: Session = Depends(get_db)):
    game = _get_or_404(db, Game, game_id)
    title, images = game.title, [game.cover_image, game.banner_image]
    db.delete(game)
    db.commit()
    for path in images:
        delete_local_image(path)
    flash(request, f"Game “{title}” dihapus beserta ulasan dan datanya.", "success")
    return _redirect("/admin/games")


# --------------------------------------------------------------------------- #
# CRUD DEVELOPERS
# --------------------------------------------------------------------------- #
@router.get("/developers")
def developers_list(request: Request, q: str = "", page: str = "1", db: Session = Depends(get_db)):
    q = q.strip()[:80]
    game_count = (
        select(func.count(Game.id)).where(Game.developer_id == Developer.id).correlate(Developer).scalar_subquery()
    )
    stmt = select(Developer, game_count.label("game_count")).order_by(func.lower(Developer.name))
    if q:
        stmt = stmt.where(Developer.name.ilike(like_pattern(q), escape="\\"))
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE, rows=True)
    return render(
        request, "admin/developers_list.html", _admin_ctx("developers", result=result, q=q, params={"q": q})
    )


@router.get("/developers/new")
def developer_new(request: Request):
    return render(request, "admin/developer_form.html", _admin_ctx("developers", developer=None, form={}, errors={}))


@router.get("/developers/{developer_id}/edit")
def developer_edit(developer_id: int, request: Request, db: Session = Depends(get_db)):
    developer = _get_or_404(db, Developer, developer_id)
    form = {
        "name": developer.name,
        "country": developer.country or "",
        "website_url": developer.website_url or "",
        "description": developer.description or "",
    }
    return render(
        request, "admin/developer_form.html", _admin_ctx("developers", developer=developer, form=form, errors={})
    )


async def _save_developer(request: Request, db: Session, developer: Optional[Developer]):
    raw = await request.form()
    form = {key: _text(raw, key) for key in ("name", "country", "website_url", "description")}
    errors: dict[str, str] = {}
    if not form["name"]:
        errors["name"] = "Nama developer wajib diisi."
    elif len(form["name"]) > 120:
        errors["name"] = "Nama maksimal 120 karakter."
    else:
        clash = select(Developer.id).where(func.lower(Developer.name) == form["name"].lower())
        if developer is not None:
            clash = clash.where(Developer.id != developer.id)
        if db.scalar(clash):
            errors["name"] = "Developer dengan nama ini sudah ada."
    if len(form["country"]) > 80:
        errors["country"] = "Negara maksimal 80 karakter."
    if form["website_url"] and (len(form["website_url"]) > 255 or not is_http_url(form["website_url"])):
        errors["website_url"] = "Website harus diawali http:// atau https://."
    if len(form["description"]) > 5000:
        errors["description"] = "Deskripsi maksimal 5000 karakter."

    if errors:
        return render(
            request,
            "admin/developer_form.html",
            _admin_ctx("developers", developer=developer, form=form, errors=errors),
            status_code=400,
        )
    creating = developer is None
    if creating:
        developer = Developer(name=form["name"])
        db.add(developer)
    developer.name = form["name"]
    developer.country = form["country"] or None
    developer.website_url = form["website_url"] or None
    developer.description = form["description"] or None
    db.commit()
    flash(request, f"Developer “{developer.name}” {'ditambahkan' if creating else 'diperbarui'}.", "success")
    return _redirect("/admin/developers")


@router.post("/developers/new")
async def developer_create(request: Request, db: Session = Depends(get_db)):
    return await _save_developer(request, db, None)


@router.post("/developers/{developer_id}/edit")
async def developer_update(developer_id: int, request: Request, db: Session = Depends(get_db)):
    return await _save_developer(request, db, _get_or_404(db, Developer, developer_id))


@router.post("/developers/{developer_id}/delete")
def developer_delete(developer_id: int, request: Request, db: Session = Depends(get_db)):
    developer = _get_or_404(db, Developer, developer_id)
    name = developer.name
    db.delete(developer)  # game terkait otomatis menjadi "tanpa developer" (ON DELETE SET NULL)
    db.commit()
    flash(request, f"Developer “{name}” dihapus. Game miliknya tetap ada tanpa developer.", "success")
    return _redirect("/admin/developers")


# --------------------------------------------------------------------------- #
# CRUD PLATFORMS
# --------------------------------------------------------------------------- #
@router.get("/platforms")
def platforms_list(request: Request, db: Session = Depends(get_db)):
    return render(request, "admin/platforms_list.html", _admin_ctx("platforms", rows=platform_counts(db)))


@router.get("/platforms/new")
def platform_new(request: Request):
    return render(
        request,
        "admin/platform_form.html",
        _admin_ctx("platforms", platform=None, form={"badge_color": "#14B8A6"}, errors={}),
    )


@router.get("/platforms/{platform_id}/edit")
def platform_edit(platform_id: int, request: Request, db: Session = Depends(get_db)):
    platform = _get_or_404(db, Platform, platform_id)
    form = {"name": platform.name, "short_name": platform.short_name, "badge_color": platform.badge_color}
    return render(
        request, "admin/platform_form.html", _admin_ctx("platforms", platform=platform, form=form, errors={})
    )


async def _save_platform(request: Request, db: Session, platform: Optional[Platform]):
    raw = await request.form()
    form = {key: _text(raw, key) for key in ("name", "short_name", "badge_color")}
    errors: dict[str, str] = {}
    if not form["name"]:
        errors["name"] = "Nama platform wajib diisi."
    elif len(form["name"]) > 60:
        errors["name"] = "Nama maksimal 60 karakter."
    else:
        clash = select(Platform.id).where(func.lower(Platform.name) == form["name"].lower())
        if platform is not None:
            clash = clash.where(Platform.id != platform.id)
        if db.scalar(clash):
            errors["name"] = "Platform dengan nama ini sudah ada."
    if not form["short_name"]:
        form["short_name"] = form["name"][:12]
    if len(form["short_name"]) > 12:
        errors["short_name"] = "Nama singkat maksimal 12 karakter."
    if not _HEX_COLOR.match(form["badge_color"]):
        errors["badge_color"] = "Gunakan kode warna heksadesimal, contoh #14B8A6."

    if errors:
        return render(
            request,
            "admin/platform_form.html",
            _admin_ctx("platforms", platform=platform, form=form, errors=errors),
            status_code=400,
        )
    creating = platform is None
    # Slug dihitung SEBELUM objek baru dimasukkan ke session, supaya autoflush tidak
    # menyimpan baris dengan slug kosong (kolom slug NOT NULL).
    base_slug = slugify(form["name"])
    candidate, counter = base_slug, 2
    own_id = 0 if creating else platform.id
    while db.scalar(select(Platform.id).where(Platform.slug == candidate, Platform.id != own_id)):
        candidate = f"{base_slug}-{counter}"
        counter += 1
    if creating:
        platform = Platform()
    platform.name = form["name"]
    platform.short_name = form["short_name"]
    platform.badge_color = form["badge_color"].upper()
    platform.slug = candidate
    if creating:
        db.add(platform)
    db.commit()
    flash(request, f"Platform “{platform.name}” {'ditambahkan' if creating else 'diperbarui'}.", "success")
    return _redirect("/admin/platforms")


@router.post("/platforms/new")
async def platform_create(request: Request, db: Session = Depends(get_db)):
    return await _save_platform(request, db, None)


@router.post("/platforms/{platform_id}/edit")
async def platform_update(platform_id: int, request: Request, db: Session = Depends(get_db)):
    return await _save_platform(request, db, _get_or_404(db, Platform, platform_id))


@router.post("/platforms/{platform_id}/delete")
def platform_delete(platform_id: int, request: Request, db: Session = Depends(get_db)):
    platform = _get_or_404(db, Platform, platform_id)
    name = platform.name
    db.delete(platform)  # baris game_platforms ikut terhapus (ON DELETE CASCADE)
    db.commit()
    flash(request, f"Platform “{name}” dihapus dari semua game.", "success")
    return _redirect("/admin/platforms")


# --------------------------------------------------------------------------- #
# CRUD USERS
# --------------------------------------------------------------------------- #
def _admin_count(db: Session) -> int:
    return db.scalar(select(func.count(User.id)).where(User.role == ROLE_ADMIN)) or 0


@router.get("/users")
def users_list(request: Request, q: str = "", role: str = "", page: str = "1", db: Session = Depends(get_db)):
    q = q.strip()[:80]
    role = role if role in (ROLE_ADMIN, ROLE_USER) else ""
    stmt = select(User).order_by(User.created_at.desc(), User.id.desc())
    if q:
        pattern = like_pattern(q)
        stmt = stmt.where(or_(User.username.ilike(pattern, escape="\\"), User.email.ilike(pattern, escape="\\")))
    if role:
        stmt = stmt.where(User.role == role)
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE)
    return render(
        request,
        "admin/users_list.html",
        _admin_ctx("users", result=result, q=q, role=role, params={"q": q, "role": role}),
    )


@router.get("/users/new")
def user_new(request: Request):
    return render(
        request, "admin/user_form.html", _admin_ctx("users", target=None, form={"role": ROLE_USER}, errors={})
    )


@router.get("/users/{user_id}/edit")
def user_edit(user_id: int, request: Request, db: Session = Depends(get_db)):
    target = _get_or_404(db, User, user_id)
    form = {"username": target.username, "email": target.email, "role": target.role}
    return render(request, "admin/user_form.html", _admin_ctx("users", target=target, form=form, errors={}))


async def _save_user(request: Request, db: Session, target: Optional[User]):
    raw = await request.form()
    form = {key: _text(raw, key) for key in ("username", "email", "role")}
    form["email"] = form["email"].lower()
    password = str(raw.get("password") or "")
    errors: dict[str, str] = {}

    if not is_valid_username(form["username"]):
        errors["username"] = "Username 3-30 karakter: huruf, angka, atau garis bawah."
    else:
        clash = select(User.id).where(func.lower(User.username) == form["username"].lower())
        if target is not None:
            clash = clash.where(User.id != target.id)
        if db.scalar(clash):
            errors["username"] = "Username ini sudah dipakai."
    if not is_valid_email(form["email"]):
        errors["email"] = "Format email tidak valid."
    else:
        clash = select(User.id).where(func.lower(User.email) == form["email"])
        if target is not None:
            clash = clash.where(User.id != target.id)
        if db.scalar(clash):
            errors["email"] = "Email ini sudah terdaftar."
    if form["role"] not in (ROLE_ADMIN, ROLE_USER):
        errors["role"] = "Role tidak valid."
    if target is None and not password:
        errors["password"] = "Password wajib diisi untuk akun baru."
    elif password and not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        errors["password"] = f"Password {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} karakter."
    if (
        target is not None
        and target.role == ROLE_ADMIN
        and form["role"] == ROLE_USER
        and _admin_count(db) <= 1
    ):
        errors["role"] = "Tidak bisa menurunkan admin terakhir. Jadikan pengguna lain admin terlebih dahulu."

    if errors:
        return render(
            request, "admin/user_form.html", _admin_ctx("users", target=target, form=form, errors=errors), status_code=400
        )
    creating = target is None
    if creating:
        target = User(username=form["username"], email=form["email"], password_hash="", role=form["role"])
        db.add(target)
    target.username = form["username"]
    target.email = form["email"]
    target.role = form["role"]
    if password:
        target.password_hash = hash_password(password)
    db.commit()
    flash(request, f"Akun “{target.username}” {'dibuat' if creating else 'diperbarui'}.", "success")
    return _redirect("/admin/users")


@router.post("/users/new")
async def user_create(request: Request, db: Session = Depends(get_db)):
    return await _save_user(request, db, None)


@router.post("/users/{user_id}/edit")
async def user_update(user_id: int, request: Request, db: Session = Depends(get_db)):
    return await _save_user(request, db, _get_or_404(db, User, user_id))


@router.post("/users/{user_id}/delete")
def user_delete(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    me: User = Depends(require_admin),
):
    target = _get_or_404(db, User, user_id)
    if target.id == me.id:
        flash(request, "Kamu tidak bisa menghapus akunmu sendiri.", "error")
        return _redirect("/admin/users")
    if target.role == ROLE_ADMIN and _admin_count(db) <= 1:
        flash(request, "Tidak bisa menghapus admin terakhir.", "error")
        return _redirect("/admin/users")

    username = target.username
    affected = set(db.scalars(select(Comment.game_id).where(Comment.user_id == target.id)).all())
    db.delete(target)  # komentar, wishlist, dan pengajuan milik user ikut terhapus
    db.flush()
    for game_id in affected:  # rating rata-rata game yang pernah diulas user ini harus dihitung ulang
        recalculate_average_rating(db, game_id)
    db.commit()
    flash(request, f"Akun “{username}” dihapus beserta ulasan dan datanya.", "success")
    return _redirect("/admin/users")


# --------------------------------------------------------------------------- #
# TRANSAKSI: pengajuan game
# --------------------------------------------------------------------------- #
@router.get("/requests")
def requests_list(request: Request, status: str = "", page: str = "1", db: Session = Depends(get_db)):
    status = status if status in REQUEST_STATUSES else ""
    stmt = select(GameRequest).options(joinedload(GameRequest.user)).order_by(
        GameRequest.submitted_at.desc(), GameRequest.id.desc()
    )
    if status:
        stmt = stmt.where(GameRequest.status == status)
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE)
    counts = dict(db.execute(select(GameRequest.status, func.count(GameRequest.id)).group_by(GameRequest.status)).all())
    return render(
        request,
        "admin/requests.html",
        _admin_ctx(
            "requests",
            result=result,
            status=status,
            counts={name: counts.get(name, 0) for name in REQUEST_STATUSES},
            statuses=REQUEST_STATUSES,
            params={"status": status},
        ),
    )


@router.post("/requests/{request_id}/status")
async def request_set_status(request_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    status = _text(form, "status")
    item = _get_or_404(db, GameRequest, request_id)
    if status not in REQUEST_STATUSES:
        flash(request, "Status tidak valid.", "error")
    else:
        item.status = status
        db.commit()
        label = {"Pending": "dikembalikan ke menunggu", "Approved": "disetujui", "Rejected": "ditolak"}[status]
        flash(request, f"Pengajuan “{item.game_title}” {label}.", "success")
    return _redirect(safe_next_url(_text(form, "next"), "/admin/requests"))


@router.post("/requests/{request_id}/delete")
async def request_delete(request_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    item = _get_or_404(db, GameRequest, request_id)
    title = item.game_title
    db.delete(item)
    db.commit()
    flash(request, f"Pengajuan “{title}” dihapus.", "success")
    return _redirect(safe_next_url(_text(form, "next"), "/admin/requests"))


# --------------------------------------------------------------------------- #
# TRANSAKSI: moderasi komentar dan log simpan
# --------------------------------------------------------------------------- #
@router.get("/comments")
def comments_list(
    request: Request, q: str = "", rating: str = "", page: str = "1", db: Session = Depends(get_db)
):
    q = q.strip()[:80]
    stars = parse_int(rating)
    stars = stars if stars in (1, 2, 3, 4, 5) else None
    stmt = (
        select(Comment)
        .join(Comment.user)
        .join(Comment.game)
        .options(joinedload(Comment.user), joinedload(Comment.game))
        .order_by(Comment.created_at.desc(), Comment.id.desc())
    )
    if q:
        pattern = like_pattern(q)
        stmt = stmt.where(
            or_(
                Game.title.ilike(pattern, escape="\\"),
                User.username.ilike(pattern, escape="\\"),
                Comment.content.ilike(pattern, escape="\\"),
            )
        )
    if stars:
        stmt = stmt.where(Comment.rating == stars)
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE)
    return render(
        request,
        "admin/comments.html",
        _admin_ctx("comments", result=result, q=q, rating=stars, params={"q": q, "rating": stars}),
    )


@router.post("/comments/{comment_id}/delete")
async def comment_delete(comment_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    comment = _get_or_404(db, Comment, comment_id)
    game_id = comment.game_id
    db.delete(comment)
    db.flush()
    recalculate_average_rating(db, game_id)
    db.commit()
    flash(request, "Komentar dihapus dan rating game dihitung ulang.", "success")
    return _redirect(safe_next_url(_text(form, "next"), "/admin/comments"))


@router.get("/saved")
def saved_log(request: Request, q: str = "", page: str = "1", db: Session = Depends(get_db)):
    q = q.strip()[:80]
    stmt = (
        select(SavedGame)
        .join(SavedGame.user)
        .join(SavedGame.game)
        .options(joinedload(SavedGame.user), joinedload(SavedGame.game))
        .order_by(SavedGame.saved_at.desc(), SavedGame.id.desc())
    )
    if q:
        pattern = like_pattern(q)
        stmt = stmt.where(or_(Game.title.ilike(pattern, escape="\\"), User.username.ilike(pattern, escape="\\")))
    result = paginate(db, stmt, parse_int(page, 1) or 1, PER_PAGE)
    return render(request, "admin/saved.html", _admin_ctx("saved", result=result, q=q, params={"q": q}))


# --------------------------------------------------------------------------- #
# LAPORAN (tampilan HTML + unduh PDF + cetak)
# --------------------------------------------------------------------------- #
def _parse_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value.strip()) if value and value.strip() else None
    except ValueError:
        return None


def _build_report(
    db: Session, report: str, platform: str, developer: str, limit: str, status: str, date_from: str, date_to: str
) -> dict:
    number = parse_int(report, 1)
    number = number if number in (1, 2, 3) else 1
    params: dict = {"report": number}
    descriptions: list[str] = []

    if number == 1:
        platform_id, developer_id = parse_int(platform), parse_int(developer)
        platform_obj = db.get(Platform, platform_id) if platform_id else None
        developer_obj = db.get(Developer, developer_id) if developer_id else None
        data = master_report(db, platform_obj.id if platform_obj else None, developer_obj.id if developer_obj else None)
        params["platform"] = platform_obj.id if platform_obj else ""
        params["developer"] = developer_obj.id if developer_obj else ""
        descriptions = [
            f"Platform: {platform_obj.name if platform_obj else 'semua'}",
            f"Developer: {developer_obj.name if developer_obj else 'semua'}",
        ]
    elif number == 2:
        top = parse_int(limit, 10)
        top = top if top in (5, 10, 20) else 10
        data = popular_report(db, top)
        params["limit"] = top
        descriptions = [f"Menampilkan {top} teratas"]
    else:
        status = status if status in REQUEST_STATUSES else ""
        start, end = _parse_date(date_from), _parse_date(date_to)
        data = activity_report(db, status, start, end)
        params.update(status=status, date_from=start.isoformat() if start else "", date_to=end.isoformat() if end else "")
        descriptions = [
            f"Status pengajuan: {status or 'semua'}",
            f"Periode: {start.isoformat() if start else 'awal'} s/d {end.isoformat() if end else 'sekarang'}",
        ]
    return {"number": number, "data": data, "params": params, "filters_text": "Filter - " + "; ".join(descriptions)}


_REPORT_ARGS = dict(report="1", platform="", developer="", limit="10", status="", date_from="", date_to="")


@router.get("/reports")
def reports_page(
    request: Request,
    report: str = "1",
    platform: str = "",
    developer: str = "",
    limit: str = "10",
    status: str = "",
    date_from: str = "",
    date_to: str = "",
    db: Session = Depends(get_db),
):
    built = _build_report(db, report, platform, developer, limit, status, date_from, date_to)
    return render(
        request,
        "admin/reports.html",
        _admin_ctx(
            "reports",
            number=built["number"],
            data=built["data"],
            params=built["params"],
            report_titles=REPORT_TITLES,
            report_short=REPORT_SHORT,
            platforms=list(db.scalars(select(Platform).order_by(Platform.id)).all()),
            developers=list(db.scalars(select(Developer).order_by(func.lower(Developer.name))).all()),
            statuses=REQUEST_STATUSES,
            generated_at=utcnow(),
        ),
    )


@router.get("/reports/pdf")
def reports_pdf(
    request: Request,
    report: str = "1",
    platform: str = "",
    developer: str = "",
    limit: str = "10",
    status: str = "",
    date_from: str = "",
    date_to: str = "",
    db: Session = Depends(get_db),
    me: User = Depends(require_admin),
):
    built = _build_report(db, report, platform, developer, limit, status, date_from, date_to)
    builder = {1: build_master_pdf, 2: build_popular_pdf, 3: build_activity_pdf}[built["number"]]
    pdf_bytes = builder(built["data"], me.username, built["filters_text"])
    filename = f"atlasplay-laporan-{built['number']}-{datetime.now():%Y%m%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
