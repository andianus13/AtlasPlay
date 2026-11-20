"""Login, register, logout (session-based)."""
from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import ROLE_USER
from app.database import get_db
from app.models import User
from app.security import (
    DUMMY_HASH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    get_current_user,
    hash_password,
    login_user,
    logout_user,
    verify_csrf,
    verify_password,
)
from app.templating import flash, render
from app.utils import is_valid_email, is_valid_username, safe_next_url

router = APIRouter(dependencies=[Depends(verify_csrf)], tags=["auth"])


@router.get("/login")
def login_page(
    request: Request,
    next_url: str = Query("/", alias="next"),
    user: Optional[User] = Depends(get_current_user),
):
    target = safe_next_url(next_url)
    if user:
        return RedirectResponse(target, status_code=303)
    return render(request, "auth/login.html", {"next": target, "form": {}, "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    identifier: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/", alias="next"),
    db: Session = Depends(get_db),
):
    target = safe_next_url(next_url)
    ident = identifier.strip()
    user = db.scalar(
        select(User).where(
            or_(func.lower(User.username) == ident.lower(), func.lower(User.email) == ident.lower())
        )
    )
    valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
    if user is None or not valid:
        return render(
            request,
            "auth/login.html",
            {"next": target, "form": {"identifier": ident}, "error": "Username/email atau password salah."},
            status_code=400,
        )

    login_user(request, user)
    flash(request, f"Selamat datang kembali, {user.username}.", "success")
    if user.is_admin and target == "/":
        target = "/admin"
    return RedirectResponse(target, status_code=303)


@router.get("/register")
def register_page(request: Request, user: Optional[User] = Depends(get_current_user)):
    if user:
        return RedirectResponse("/", status_code=303)
    return render(request, "auth/register.html", {"form": {}, "errors": {}})


@router.post("/register")
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()
    email = email.strip().lower()
    errors: dict[str, str] = {}

    if not is_valid_username(username):
        errors["username"] = "Username 3-30 karakter: huruf, angka, atau garis bawah."
    elif db.scalar(select(User.id).where(func.lower(User.username) == username.lower())):
        errors["username"] = "Username ini sudah dipakai."

    if not is_valid_email(email):
        errors["email"] = "Format email tidak valid."
    elif db.scalar(select(User.id).where(func.lower(User.email) == email)):
        errors["email"] = "Email ini sudah terdaftar."

    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        errors["password"] = f"Password {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} karakter."
    elif password != password_confirm:
        errors["password_confirm"] = "Konfirmasi password tidak sama."

    if errors:
        return render(
            request,
            "auth/register.html",
            {"form": {"username": username, "email": email}, "errors": errors},
            status_code=400,
        )

    user = User(username=username, email=email, password_hash=hash_password(password), role=ROLE_USER)
    db.add(user)
    db.commit()

    login_user(request, user)
    flash(request, "Akun berhasil dibuat. Selamat datang di AtlasPlay.", "success")
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    logout_user(request)
    flash(request, "Kamu sudah keluar.", "info")
    return RedirectResponse("/", status_code=303)
