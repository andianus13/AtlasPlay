"""Konfigurasi terpusat AtlasPlay. Nilai rahasia dibaca dari file .env di root proyek."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variable yang sudah ada di sistem tidak ditimpa oleh isi .env (override=False).
load_dotenv(BASE_DIR / ".env")
IS_VERCEL = bool(os.getenv("VERCEL"))

APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"
UPLOAD_DIR = Path("/tmp/uploads") if IS_VERCEL else (STATIC_DIR / "uploads")
COVER_DIR = UPLOAD_DIR / "covers"
BANNER_DIR = UPLOAD_DIR / "banners"

APP_NAME = "AtlasPlay"
APP_TAGLINE = "Perpustakaan game lintas platform"

# PostgreSQL, contoh: postgresql://postgres:password@localhost:5432/game_catalog_db
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL belum diatur. Salin .env.example menjadi .env lalu isi koneksi PostgreSQL kamu."
    )
# SQLAlchemy 2.1 memilih driver psycopg (v3) untuk "postgresql://", sedangkan proyek ini memakai
# psycopg2-binary. Skema dinormalkan agar .env cukup berisi URL PostgreSQL standar.
# Skema lama "postgres://" (Heroku/Render) juga ikut diterima.
for _scheme in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(_scheme):
        DATABASE_URL = "postgresql+psycopg2://" + DATABASE_URL[len(_scheme):]
        break

# Ganti dengan string acak panjang di .env. Nilai default hanya untuk pengembangan lokal.
SECRET_KEY = (
    os.getenv("ATLASPLAY_SECRET_KEY")
    or os.getenv("SECRET_KEY")
    or "dev-only-secret-ganti-sebelum-deploy"
)
SESSION_COOKIE = "atlasplay_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14  # 14 hari

# Ukuran gambar wajib (lebar, tinggi) -> rasio 3:4 dan 21:9
COVER_SIZE = (600, 800)
BANNER_SIZE = (1400, 550)
IMAGE_QUALITY = 85
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

# Konstanta domain
ROLE_ADMIN = "admin"
ROLE_USER = "user"
REQUEST_STATUSES = ("Pending", "Approved", "Rejected")
