"""Engine, session, dan inisialisasi database PostgreSQL."""
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


# DATABASE_URL dibaca dari .env lewat app.config. Driver bawaan untuk "postgresql://" adalah psycopg2.
# pool_pre_ping membuang koneksi mati (mis. server di-restart) sebelum dipakai.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dependency FastAPI: satu session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_database_exists() -> None:
    """Membuat database (mis. game_catalog_db) bila server PostgreSQL ada tetapi database belum dibuat.

    Memakai koneksi ke database bawaan "postgres" dan membutuhkan hak CREATE DATABASE.
    Bila server tidak bisa dijangkau atau password salah, error aslinya dilempar apa adanya.
    """
    try:
        with engine.connect():
            return
    except OperationalError as exc:
        if "does not exist" not in str(exc.orig):
            raise

    url = make_url(DATABASE_URL)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.scalar(text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database})
            if not exists:
                quoted = '"' + url.database.replace('"', '""') + '"'
                conn.execute(text(f"CREATE DATABASE {quoted}"))
    finally:
        admin_engine.dispose()


def init_db() -> None:
    """Membuat database (bila belum ada) dan seluruh tabel (bila belum ada)."""
    from app import models  # noqa: F401  (memastikan semua model terdaftar di metadata)

    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
