"""Model SQLAlchemy: 5 file master + 3 file transaksi."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import ROLE_ADMIN
from app.database import Base

PLACEHOLDER_COVER = "/static/img/placeholder-cover.svg"
PLACEHOLDER_BANNER = "/static/img/placeholder-banner.svg"


def utcnow() -> datetime:
    """Waktu UTC tanpa tzinfo (SQLite menyimpan datetime naif)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# --------------------------------------------------------------------------- #
# FILE MASTER
# --------------------------------------------------------------------------- #
class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'user')", name="ck_users_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10), default="user", server_default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    saved_games: Mapped[List["SavedGame"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    game_requests: Mapped[List["GameRequest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Developer(Base):
    __tablename__ = "developers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    country: Mapped[Optional[str]] = mapped_column(String(80))
    website_url: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    games: Mapped[List["Game"]] = relationship(back_populates="developer", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<Developer {self.name}>"


# Tabel relasi many-to-many game <-> platform
game_platforms = Table(
    "game_platforms",
    Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
    Column("platform_id", Integer, ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True),
)


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    # Tambahan di luar spesifikasi: slug untuk URL filter (?platform=pc-windows)
    # dan short_name untuk badge ringkas pada kartu poster (PC, PS5, Switch).
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(12))
    badge_color: Mapped[str] = mapped_column(String(9), default="#14B8A6", server_default="#14B8A6")

    games: Mapped[List["Game"]] = relationship(
        secondary=game_platforms, back_populates="platforms", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Platform {self.name}>"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)

    # Berisi URL penuh (http/https) atau path lokal seperti /static/uploads/covers/xxx.webp
    cover_image: Mapped[Optional[str]] = mapped_column(String(400))
    banner_image: Mapped[Optional[str]] = mapped_column(String(400))

    short_summary: Mapped[Optional[str]] = mapped_column(String(300))
    full_description: Mapped[Optional[str]] = mapped_column(Text)
    official_website_url: Mapped[Optional[str]] = mapped_column(String(255))
    release_date: Mapped[Optional[date]] = mapped_column(Date)
    developer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("developers.id", ondelete="SET NULL"), index=True
    )

    # Spesifikasi minimum
    min_os: Mapped[Optional[str]] = mapped_column(String(120))
    min_cpu: Mapped[Optional[str]] = mapped_column(String(160))
    min_ram: Mapped[Optional[str]] = mapped_column(String(60))
    min_gpu: Mapped[Optional[str]] = mapped_column(String(160))
    storage_req: Mapped[Optional[str]] = mapped_column(String(60))
    # Spesifikasi rekomendasi
    rec_os: Mapped[Optional[str]] = mapped_column(String(120))
    rec_cpu: Mapped[Optional[str]] = mapped_column(String(160))
    rec_ram: Mapped[Optional[str]] = mapped_column(String(60))
    rec_gpu: Mapped[Optional[str]] = mapped_column(String(160))

    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), index=True)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    # Tambahan di luar spesifikasi: dipakai section "Baru Diperbarui" di beranda.
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, index=True)

    developer: Mapped[Optional[Developer]] = relationship(back_populates="games")
    platforms: Mapped[List[Platform]] = relationship(
        secondary=game_platforms, back_populates="games", order_by="Platform.id"
    )
    saved_by: Mapped[List["SavedGame"]] = relationship(
        back_populates="game", cascade="all, delete-orphan", passive_deletes=True
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Comment.created_at.desc()",
    )

    # ---- helper untuk template -------------------------------------------- #
    @property
    def cover_src(self) -> str:
        return self.cover_image or PLACEHOLDER_COVER

    @property
    def banner_src(self) -> str:
        return self.banner_image or PLACEHOLDER_BANNER

    @property
    def spec_rows(self) -> list[tuple[str, str, str]]:
        """Baris tabel spesifikasi: (label, minimum, rekomendasi)."""
        dash = "-"
        return [
            ("OS", self.min_os or dash, self.rec_os or dash),
            ("CPU", self.min_cpu or dash, self.rec_cpu or dash),
            ("RAM", self.min_ram or dash, self.rec_ram or dash),
            ("GPU", self.min_gpu or dash, self.rec_gpu or dash),
        ]

    @property
    def has_pc_specs(self) -> bool:
        return any([self.min_os, self.min_cpu, self.min_ram, self.min_gpu, self.storage_req])

    def __repr__(self) -> str:
        return f"<Game {self.title}>"


# --------------------------------------------------------------------------- #
# FILE TRANSAKSI
# --------------------------------------------------------------------------- #
class SavedGame(Base):
    """Wishlist / game tersimpan."""

    __tablename__ = "saved_games"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_saved_user_game"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user: Mapped[User] = relationship(back_populates="saved_games")
    game: Mapped[Game] = relationship(back_populates="saved_by")


class Comment(Base):
    """Ulasan dan rating performa."""

    __tablename__ = "comments"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="ck_comments_rating"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    device_tested: Mapped[Optional[str]] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="comments")
    game: Mapped[Game] = relationship(back_populates="comments")


class GameRequest(Base):
    """Pengajuan game baru oleh user."""

    __tablename__ = "game_requests"
    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'Approved', 'Rejected')", name="ck_requests_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    game_title: Mapped[str] = mapped_column(String(160))
    platform_info: Mapped[Optional[str]] = mapped_column(String(160))
    official_link: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default="Pending", server_default="Pending", index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    user: Mapped[User] = relationship(back_populates="game_requests")
