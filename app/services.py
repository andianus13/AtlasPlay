"""Logika bisnis dan query yang dipakai bersama oleh banyak route."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Comment,
    Developer,
    Game,
    Platform,
    SavedGame,
    User,
    game_platforms,
    utcnow,
)
from app.utils import slugify


# --------------------------------------------------------------------------- #
# Pagination
# --------------------------------------------------------------------------- #
@dataclass
class Page:
    items: list = field(default_factory=list)
    page: int = 1
    per_page: int = 12
    total: int = 0

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.per_page))

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def first_index(self) -> int:
        return (self.page - 1) * self.per_page + 1 if self.total else 0

    @property
    def last_index(self) -> int:
        return min(self.page * self.per_page, self.total)

    def window(self, radius: int = 2) -> list[Optional[int]]:
        """Nomor halaman yang ditampilkan; None = titik-titik pemisah."""
        shown = sorted({1, self.pages, *range(max(1, self.page - radius), min(self.pages, self.page + radius) + 1)})
        result: list[Optional[int]] = []
        previous = 0
        for number in shown:
            if number - previous > 1:
                result.append(None)
            result.append(number)
            previous = number
        return result


def paginate(db: Session, stmt: Select, page: int, per_page: int, rows: bool = False) -> Page:
    """Jalankan stmt dengan limit/offset. rows=True untuk select multi-kolom (hasil berupa Row)."""
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    pages = max(1, math.ceil(total / per_page))
    page = min(max(1, page), pages)
    paged = stmt.limit(per_page).offset((page - 1) * per_page)
    items = list(db.execute(paged).all()) if rows else list(db.scalars(paged).all())
    return Page(items=items, page=page, per_page=per_page, total=total)


def parse_int(value: object, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------------------- #
# Katalog game
# --------------------------------------------------------------------------- #
def game_load_options() -> tuple:
    """Eager loading relasi yang dipakai kartu poster (menghindari N+1)."""
    return (selectinload(Game.platforms), selectinload(Game.developer))


SORT_OPTIONS = [
    ("terbaru", "Terbaru diperbarui"),
    ("rating", "Rating tertinggi"),
    ("rilis", "Rilis terbaru"),
    ("judul", "Judul A-Z"),
]
_SORT_ORDER = {
    "terbaru": lambda: (Game.updated_at.desc(), Game.id.desc()),
    "rating": lambda: (Game.average_rating.desc(), Game.id),
    "rilis": lambda: (Game.release_date.desc().nulls_last(), Game.id),
    "judul": lambda: (func.lower(Game.title).asc(), Game.id),
}


def like_pattern(text: str) -> str:
    """Pola ILIKE aman: karakter % _ dan \\ dari pengguna di-escape."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def games_query(
    q: str = "", platform: str = "", developer_id: Optional[int] = None, sort: str = "terbaru"
) -> Select:
    stmt = select(Game).options(*game_load_options())
    if q:
        pattern = like_pattern(q)
        stmt = stmt.where(
            or_(
                Game.title.ilike(pattern, escape="\\"),
                Game.short_summary.ilike(pattern, escape="\\"),
                Game.developer.has(Developer.name.ilike(pattern, escape="\\")),
            )
        )
    if platform:
        slugs = [p for p in platform.split(",") if p]
        stmt = stmt.where(Game.platforms.any(Platform.slug.in_(slugs)))
    if developer_id:
        stmt = stmt.where(Game.developer_id == developer_id)
    return stmt.order_by(*_SORT_ORDER.get(sort, _SORT_ORDER["terbaru"])())


def trending_games(db: Session, limit: int = 6) -> list[Game]:
    """Skor 'minggu ini' = 2 x simpan + 1 x komentar dalam 7 hari terakhir; seri diurutkan rating."""
    since = utcnow() - timedelta(days=7)
    saves = (
        select(func.count(SavedGame.id))
        .where(SavedGame.game_id == Game.id, SavedGame.saved_at >= since)
        .correlate(Game)
        .scalar_subquery()
    )
    comments = (
        select(func.count(Comment.id))
        .where(Comment.game_id == Game.id, Comment.created_at >= since)
        .correlate(Game)
        .scalar_subquery()
    )
    stmt = (
        select(Game)
        .options(*game_load_options())
        .order_by((saves * 2 + comments).desc(), Game.average_rating.desc(), Game.id)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def platform_counts(db: Session) -> list[tuple[Platform, int]]:
    stmt = (
        select(Platform, func.count(game_platforms.c.game_id))
        .outerjoin(game_platforms, game_platforms.c.platform_id == Platform.id)
        .group_by(Platform.id)
        .order_by(Platform.id)
    )
    return [(platform, count) for platform, count in db.execute(stmt).all()]


def saved_game_ids(db: Session, user: Optional[User]) -> set[int]:
    if user is None:
        return set()
    return set(db.scalars(select(SavedGame.game_id).where(SavedGame.user_id == user.id)).all())


def rating_distribution(db: Session, game_id: int) -> dict[int, int]:
    rows = db.execute(
        select(Comment.rating, func.count(Comment.id)).where(Comment.game_id == game_id).group_by(Comment.rating)
    ).all()
    result = {star: 0 for star in (5, 4, 3, 2, 1)}
    for rating, count in rows:
        result[int(rating)] = int(count)
    return result


# --------------------------------------------------------------------------- #
# Aturan bisnis rating & slug
# --------------------------------------------------------------------------- #
def recalculate_average_rating(db: Session, game_id: int) -> float:
    """Hitung ulang games.average_rating dari seluruh komentar game tersebut.

    Dipanggil setiap kali komentar ditambah atau dihapus (oleh user maupun moderasi admin).
    """
    avg = db.scalar(select(func.avg(Comment.rating)).where(Comment.game_id == game_id))
    value = round(float(avg), 2) if avg is not None else 0.0
    game = db.get(Game, game_id)
    if game is not None:
        game.average_rating = value
        db.flush()
    return value


def unique_game_slug(db: Session, title: str, exclude_id: Optional[int] = None) -> str:
    """Slug unik dari judul. Bila bentrok ditambah akhiran -2, -3, dst."""
    base = slugify(title)
    candidate, counter = base, 2
    while True:
        query = select(Game.id).where(Game.slug == candidate)
        if exclude_id is not None:
            query = query.where(Game.id != exclude_id)
        if db.scalar(query) is None:
            return candidate
        candidate = f"{base}-{counter}"
        counter += 1


# Kelompok platform untuk kartu di beranda: satu keluarga bisa berisi beberapa platform (PS4 + PS5).
_FAMILIES = (
    ("pc", "PC Windows", ("pc", "windows", "steam")),
    ("ps", "PlayStation", ("playstation", "ps4", "ps5")),
    ("switch", "Nintendo Switch", ("switch", "nintendo")),
    ("xbox", "Xbox", ("xbox",)),
)


def platform_families(db: Session) -> list[dict]:
    """Kembalikan kelompok platform berisi nama, daftar slug, ikon (objek Platform), dan jumlah game unik."""
    platforms = list(db.scalars(select(Platform).order_by(Platform.id)).all())
    groups: dict[str, dict] = {}
    for p in platforms:
        text = f"{p.slug} {p.short_name} {p.name}".lower()
        key, name = None, p.name
        for fk, fname, needles in (_FAMILIES[1], _FAMILIES[2], _FAMILIES[3], _FAMILIES[0]):
            if any(n in text for n in needles):
                key, name = fk, fname
                break
        key = key or f"x-{p.id}"
        group = groups.setdefault(key, {"key": key, "name": name, "slugs": [], "ids": [], "icon": p, "color": p.badge_color})
        group["slugs"].append(p.slug)
        group["ids"].append(p.id)
    order = [f[0] for f in _FAMILIES]
    ordered = [groups[k] for k in order if k in groups] + [g for k, g in groups.items() if k not in order]
    for g in ordered:
        g["count"] = db.scalar(
            select(func.count(func.distinct(game_platforms.c.game_id))).where(game_platforms.c.platform_id.in_(g["ids"]))
        ) or 0
        g["filter"] = ",".join(g["slugs"])
    return ordered
