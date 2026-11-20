"""Fungsi bantu umum: slug, validasi redirect, format tanggal Indonesia."""
import re
import unicodedata
from datetime import date, datetime
from typing import Optional, Union

_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def slugify(text: str) -> str:
    """'Baldur's Gate 3' -> 'baldurs-gate-3'. Aman untuk karakter non-ASCII."""
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"['’`]", "", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return ascii_text or "game"


def safe_next_url(url: Optional[str], default: str = "/") -> str:
    """Hanya izinkan redirect ke path internal (cegah open redirect)."""
    if not url or not url.startswith("/") or url.startswith("//") or "\\" in url:
        return default
    return url


def is_valid_email(value: str) -> bool:
    return bool(_EMAIL_RE.match(value or "")) and len(value) <= 120


def is_valid_username(value: str) -> bool:
    return bool(_USERNAME_RE.match(value or ""))


def is_local_upload(path: Optional[str]) -> bool:
    """True bila gambar berasal dari upload lokal (bukan URL eksternal)."""
    return bool(path) and path.startswith("/static/uploads/")


def format_date(value: Union[date, datetime, None]) -> str:
    """Filter Jinja: 16 Nov 2026."""
    if not value:
        return "-"
    return f"{value.day} {_BULAN[value.month - 1]} {value.year}"


def format_datetime(value: Optional[datetime]) -> str:
    """Filter Jinja: 16 Nov 2026, 01:33."""
    if not value:
        return "-"
    return f"{value.day} {_BULAN[value.month - 1]} {value.year}, {value:%H:%M}"
