"""Password hashing (bcrypt), session login, dan dependency otorisasi."""
import secrets
from typing import Optional
from urllib.parse import quote, urlparse

import bcrypt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

_BCRYPT_MAX_BYTES = 72  # batas bawaan algoritma bcrypt
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 64


def hash_password(password: str) -> str:
    raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        raw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        return bcrypt.checkpw(raw, password_hash.encode("utf-8"))
    except ValueError:
        return False


# Hash tiruan agar waktu respons login tetap mirip saat username tidak ditemukan.
DUMMY_HASH = hash_password("dummy-password-for-timing")


# --------------------------------------------------------------------------- #
# Session
# --------------------------------------------------------------------------- #
def login_user(request: Request, user: User) -> None:
    """Mulai session baru (session lama dibuang agar tidak ada session fixation)."""
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["csrf"] = secrets.token_urlsafe(32)


def logout_user(request: Request) -> None:
    request.session.clear()


# --------------------------------------------------------------------------- #
# Dependency
# --------------------------------------------------------------------------- #
class LoginRequired(Exception):
    """Dilempar ketika halaman butuh login; ditangani di main.py menjadi redirect ke /login."""

    def __init__(self, next_url: str = "/") -> None:
        self.next_url = next_url


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """User yang sedang login, atau None. Hasilnya disimpan di request.state untuk template."""
    user: Optional[User] = None
    user_id = request.session.get("user_id")
    if user_id:
        user = db.get(User, user_id)
        if user is None:  # akun sudah dihapus admin
            request.session.pop("user_id", None)
    request.state.current_user = user
    return user


def require_user(request: Request, user: Optional[User] = Depends(get_current_user)) -> User:
    if user is None:
        if request.method == "GET":
            target = request.url.path
            if request.url.query:
                target += f"?{request.url.query}"
        else:
            # Aksi POST tidak bisa dibuka lewat GET: setelah login kembali ke halaman asal (Referer).
            referer = urlparse(request.headers.get("referer", ""))
            same_host = referer.netloc in ("", request.url.netloc)
            target = (referer.path + (f"?{referer.query}" if referer.query else "")) if same_host and referer.path else "/"
        raise LoginRequired(next_url=target)
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Halaman ini khusus admin.")
    return user


def login_redirect_url(next_url: str) -> str:
    return f"/login?next={quote(next_url, safe='')}"


# --------------------------------------------------------------------------- #
# CSRF: token acak per session, dikirim lewat input tersembunyi atau header X-CSRF-Token.
# --------------------------------------------------------------------------- #
def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def _is_same_origin(request: Request) -> bool:
    host = request.headers.get("host") or request.url.netloc
    origin = request.headers.get("origin")
    if origin:
        return urlparse(origin).netloc == host
    referer = request.headers.get("referer")
    if referer:
        return urlparse(referer).netloc == host
    return False


async def verify_csrf(request: Request) -> None:
    """Dependency untuk seluruh request yang mengubah data (POST/PUT/PATCH/DELETE)."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    submitted = request.headers.get("x-csrf-token")
    if not submitted:
        form = await request.form()
        submitted = form.get("csrf_token")
    expected = request.session.get("csrf")
    if expected and submitted and secrets.compare_digest(str(submitted), str(expected)):
        return
    if submitted and _is_same_origin(request):
        request.session["csrf"] = secrets.token_urlsafe(32)
        return
    raise HTTPException(
        status_code=403,
        detail="Token formulir tidak valid atau sudah kedaluwarsa. Muat ulang halaman lalu coba lagi.",
    )
