"""Route publik: beranda, katalog, detail game, koleksi tersimpan, komentar, dan pengajuan game."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.images import is_http_url
from app.models import Comment, Developer, Game, GameRequest, Platform, SavedGame, User
from app.security import get_current_user, require_user
from app.services import (
    platform_families,
    SORT_OPTIONS,
    game_load_options,
    games_query,
    like_pattern,
    paginate,
    parse_int,
    platform_counts,
    rating_distribution,
    recalculate_average_rating,
    saved_game_ids,
    trending_games,
)
from app.templating import flash, render, render_fragment
from app.utils import safe_next_url

router = APIRouter(tags=["public"])

CATALOG_PER_PAGE = 12
SAVED_PER_PAGE = 12
COMMENT_SORTS = {"terbaru": "Terbaru", "tertinggi": "Rating tertinggi", "terendah": "Rating terendah"}


def _wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "")


def _get_game_or_404(db: Session, slug: str, *, full: bool = False) -> Game:
    stmt = select(Game).where(Game.slug == slug)
    stmt = stmt.options(*game_load_options())
    game = db.scalar(stmt)
    if game is None:
        raise HTTPException(status_code=404, detail="Game tidak ditemukan.")
    return game


# --------------------------------------------------------------------------- #
# Beranda
# --------------------------------------------------------------------------- #
SEEN_COOKIE = "ap_seen"


@router.get("/welcome")
def welcome(request: Request, user: Optional[User] = Depends(get_current_user)):
    """Layar pembuka dengan objek 3D. Pengguna yang sudah login langsung diarahkan ke beranda."""
    if user:
        return RedirectResponse("/", status_code=303)
    return render(request, "welcome.html", {})


@router.get("/enter")
def enter_as_guest():
    """Masuk sebagai tamu: tandai sesi browser ini sudah melihat welcome, lalu buka beranda."""
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(SEEN_COOKIE, "1", httponly=True, samesite="lax")   # cookie sesi, hilang saat browser ditutup
    return resp


@router.get("/")
def home(request: Request, db: Session = Depends(get_db), user: Optional[User] = Depends(get_current_user)):
    if not user and not request.cookies.get(SEEN_COOKIE):
        return RedirectResponse("/welcome", status_code=303)
    base = select(Game).options(*game_load_options())
    featured = list(
        db.scalars(
            base.where(Game.is_featured.is_(True)).order_by(Game.average_rating.desc(), Game.id).limit(5)
        ).all()
    )
    if not featured:
        featured = list(db.scalars(base.order_by(Game.average_rating.desc(), Game.id).limit(5)).all())

    stats = {
        "games": db.scalar(select(func.count(Game.id))) or 0,
        "reviews": db.scalar(select(func.count(Comment.id))) or 0,
        "platforms": db.scalar(select(func.count(Platform.id))) or 0,
    }
    return render(
        request,
        "home.html",
        {
            "featured": featured,
            "trending": trending_games(db, 6),
            "updated": list(db.scalars(games_query(sort="terbaru").limit(8)).all()),
            "platforms": platform_counts(db),
            "families": platform_families(db),
            "stats": stats,
            "saved_ids": saved_game_ids(db, user),
        },
    )


# --------------------------------------------------------------------------- #
# Pencarian cepat untuk dropdown di hero (JSON)
# --------------------------------------------------------------------------- #
@router.get("/api/search")
def api_search(q: str = "", db: Session = Depends(get_db)):
    q = q.strip()[:80]
    if len(q) < 2:
        return {"results": []}
    games = db.scalars(games_query(q=q, sort="rating").limit(6)).all()
    return {
        "results": [
            {
                "title": g.title,
                "url": f"/game/{g.slug}",
                "cover": g.cover_src,
                "developer": g.developer.name if g.developer else "",
                "platforms": [p.short_name for p in g.platforms],
                "rating": round(g.average_rating, 1) if g.average_rating else None,
            }
            for g in games
        ]
    }


# --------------------------------------------------------------------------- #
# Katalog semua game (filter, cari, urut, halaman)
# --------------------------------------------------------------------------- #
@router.get("/games")
def games_page(
    request: Request,
    q: str = "",
    platform: str = "",
    developer: str = "",
    sort: str = "terbaru",
    page: str = "1",
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    q = q.strip()[:80]
    sort = sort if sort in dict(SORT_OPTIONS) else "terbaru"
    developer_id = parse_int(developer)
    platform = platform.strip()[:60]

    result = paginate(db, games_query(q, platform, developer_id, sort), parse_int(page, 1) or 1, CATALOG_PER_PAGE)
    current_developer = db.get(Developer, developer_id) if developer_id else None
    current_platform = db.scalar(select(Platform).where(Platform.slug == platform)) if platform else None
    platform_label = current_platform.name if current_platform else ""
    if platform and not current_platform and "," in platform:
        names = db.scalars(select(Platform.name).where(Platform.slug.in_(platform.split(","))).order_by(Platform.id)).all()
        platform_label = " / ".join(names)

    context = {
        "result": result,
        "q": q,
        "sort": sort,
        "sort_options": SORT_OPTIONS,
        "platform_slug": platform,
        "current_platform": current_platform,
        "platform_label": platform_label,
        "current_developer": current_developer,
        "platforms": platform_counts(db),
        "saved_ids": saved_game_ids(db, user),
        "params": {
            "q": q,
            "platform": platform,
            "developer": developer_id,
            "sort": sort if sort != "terbaru" else "",
        },
    }
    if request.headers.get("x-partial"):
        return render_fragment(request, "partials/_results.html", context)
    return render(request, "games.html", context)


# --------------------------------------------------------------------------- #
# Detail game
# --------------------------------------------------------------------------- #
@router.get("/game/{slug}")
def game_detail(
    slug: str,
    request: Request,
    urut: str = "terbaru",
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    game = _get_game_or_404(db, slug)
    urut = urut if urut in COMMENT_SORTS else "terbaru"

    order = {
        "terbaru": (Comment.created_at.desc(),),
        "tertinggi": (Comment.rating.desc(), Comment.created_at.desc()),
        "terendah": (Comment.rating.asc(), Comment.created_at.desc()),
    }[urut]
    comments = list(
        db.scalars(
            select(Comment).options(joinedload(Comment.user)).where(Comment.game_id == game.id).order_by(*order)
        ).all()
    )
    saved_count = db.scalar(select(func.count(SavedGame.id)).where(SavedGame.game_id == game.id)) or 0
    more_from_developer = []
    if game.developer_id:
        more_from_developer = list(
            db.scalars(
                select(Game)
                .options(*game_load_options())
                .where(Game.developer_id == game.developer_id, Game.id != game.id)
                .order_by(Game.average_rating.desc(), Game.id)
                .limit(4)
            ).all()
        )
    saved_ids = saved_game_ids(db, user)
    return render(
        request,
        "game_detail.html",
        {
            "game": game,
            "comments": comments,
            "comment_sorts": COMMENT_SORTS,
            "urut": urut,
            "distribution": rating_distribution(db, game.id),
            "saved_count": saved_count,
            "is_saved": game.id in saved_ids,
            "saved_ids": saved_ids,
            "more_from_developer": more_from_developer,
        },
    )


@router.post("/game/{slug}/save")
def toggle_save(
    slug: str,
    request: Request,
    next_url: str = Form("", alias="next"),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    game = _get_game_or_404(db, slug)
    existing = db.scalar(select(SavedGame).where(SavedGame.user_id == user.id, SavedGame.game_id == game.id))
    if existing:
        db.delete(existing)
        db.commit()
        saved, message = False, f"{game.title} dihapus dari koleksi."
    else:
        db.add(SavedGame(user_id=user.id, game_id=game.id))
        try:
            db.commit()
        except IntegrityError:  # klik ganda: baris sudah ada, anggap tersimpan
            db.rollback()
        saved, message = True, f"{game.title} disimpan ke koleksi."

    count = db.scalar(select(func.count(SavedGame.id)).where(SavedGame.game_id == game.id)) or 0
    if _wants_json(request):
        return JSONResponse({"saved": saved, "message": message, "count": count})
    flash(request, message, "success")
    return RedirectResponse(safe_next_url(next_url, f"/game/{game.slug}"), status_code=303)


# --------------------------------------------------------------------------- #
# Komentar dan rating performa
# --------------------------------------------------------------------------- #
@router.post("/game/{slug}/comment")
def add_comment(
    slug: str,
    request: Request,
    rating: str = Form(""),
    device_tested: str = Form(""),
    content: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    game = _get_game_or_404(db, slug)
    stars = parse_int(rating)
    device = device_tested.strip()
    text = content.strip()
    back = RedirectResponse(f"/game/{game.slug}#ulasan", status_code=303)

    if stars is None or not 1 <= stars <= 5:
        flash(request, "Pilih rating bintang 1 sampai 5 terlebih dahulu.", "error")
        return back
    if len(device) > 160:
        flash(request, "Nama perangkat maksimal 160 karakter.", "error")
        return back
    if not 10 <= len(text) <= 2000:
        flash(request, "Ulasan 10 sampai 2000 karakter.", "error")
        return back

    db.add(Comment(user_id=user.id, game_id=game.id, rating=stars, device_tested=device or None, content=text))
    db.flush()
    recalculate_average_rating(db, game.id)
    db.commit()
    flash(request, "Ulasan terkirim. Terima kasih sudah berbagi performa perangkatmu.", "success")
    return back


@router.post("/comment/{comment_id}/delete")
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Ulasan tidak ditemukan.")
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Kamu hanya bisa menghapus ulasanmu sendiri.")
    game = db.get(Game, comment.game_id)
    db.delete(comment)
    db.flush()
    recalculate_average_rating(db, comment.game_id)
    db.commit()
    flash(request, "Ulasan dihapus.", "success")
    return RedirectResponse(f"/game/{game.slug}#ulasan" if game else "/", status_code=303)


# --------------------------------------------------------------------------- #
# Koleksi tersimpan
# --------------------------------------------------------------------------- #
@router.get("/my-saved")
def my_saved(
    request: Request,
    page: str = "1",
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    stmt = (
        select(Game)
        .join(SavedGame, SavedGame.game_id == Game.id)
        .options(*game_load_options())
        .where(SavedGame.user_id == user.id)
        .order_by(SavedGame.saved_at.desc(), SavedGame.id.desc())
    )
    result = paginate(db, stmt, parse_int(page, 1) or 1, SAVED_PER_PAGE)
    return render(
        request,
        "saved.html",
        {"result": result, "saved_ids": {g.id for g in result.items}, "params": {}},
    )


# --------------------------------------------------------------------------- #
# Ajukan game baru
# --------------------------------------------------------------------------- #
def _my_requests(db: Session, user: User) -> list[GameRequest]:
    return list(
        db.scalars(
            select(GameRequest).where(GameRequest.user_id == user.id).order_by(GameRequest.submitted_at.desc())
        ).all()
    )


@router.get("/request-game")
def request_game_page(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    return render(request, "request_game.html", {"form": {}, "errors": {}, "my_requests": _my_requests(db, user)})


@router.post("/request-game")
def request_game_submit(
    request: Request,
    game_title: str = Form(""),
    platform_info: str = Form(""),
    official_link: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    form = {
        "game_title": game_title.strip(),
        "platform_info": platform_info.strip(),
        "official_link": official_link.strip(),
        "notes": notes.strip(),
    }
    errors: dict[str, str] = {}
    if not 2 <= len(form["game_title"]) <= 160:
        errors["game_title"] = "Judul game 2 sampai 160 karakter."
    if len(form["platform_info"]) > 160:
        errors["platform_info"] = "Info platform maksimal 160 karakter."
    if form["official_link"] and (len(form["official_link"]) > 255 or not is_http_url(form["official_link"])):
        errors["official_link"] = "Isi dengan alamat lengkap yang diawali http:// atau https://."
    if len(form["notes"]) > 2000:
        errors["notes"] = "Catatan maksimal 2000 karakter."

    if not errors:
        duplicate = db.scalar(
            select(GameRequest.id).where(
                GameRequest.user_id == user.id,
                func.lower(GameRequest.game_title) == form["game_title"].lower(),
                GameRequest.status == "Pending",
            )
        )
        if duplicate:
            errors["game_title"] = "Pengajuan untuk game ini masih menunggu ditinjau admin."

    if errors:
        return render(
            request,
            "request_game.html",
            {"form": form, "errors": errors, "my_requests": _my_requests(db, user)},
            status_code=400,
        )

    db.add(
        GameRequest(
            user_id=user.id,
            game_title=form["game_title"],
            platform_info=form["platform_info"] or None,
            official_link=form["official_link"] or None,
            notes=form["notes"] or None,
        )
    )
    db.commit()
    flash(request, "Pengajuan terkirim. Admin akan meninjaunya.", "success")
    return RedirectResponse("/request-game", status_code=303)
