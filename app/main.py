"""Titik masuk aplikasi.  Jalankan:  uvicorn app.main:app --reload"""
import shutil
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import (
    APP_NAME,
    BANNER_DIR,
    COVER_DIR,
    IS_VERCEL,
    SECRET_KEY,
    SESSION_COOKIE,
    SESSION_MAX_AGE,
    STATIC_DIR,
    UPLOAD_DIR,
)
from app.database import SessionLocal, init_db
from app.routers import admin, auth, public
from app.security import LoginRequired, get_current_user, login_redirect_url, verify_csrf
from app.seed import seed_database
from app.templating import render

_ERROR_TITLES = {
    400: "Permintaan tidak valid",
    403: "Akses ditolak",
    404: "Halaman tidak ditemukan",
    405: "Metode tidak diizinkan",
    422: "Data tidak lengkap",
}
_ERROR_HINTS = {
    404: "Alamat yang kamu buka tidak ada atau sudah dipindahkan.",
    405: "Halaman ini tidak bisa dibuka dengan cara tersebut.",
    422: "Ada isian yang kosong atau formatnya tidak sesuai. Kembali ke halaman sebelumnya lalu periksa isiannya.",
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    BANNER_DIR.mkdir(parents=True, exist_ok=True)
    if IS_VERCEL and (STATIC_DIR / "uploads").exists():
        shutil.copytree(STATIC_DIR / "uploads", UPLOAD_DIR, dirs_exist_ok=True)
    init_db()
    with SessionLocal() as db:
        seed_database(db)
    yield


# get_current_user dipasang global agar nama pengguna selalu tersedia di navbar.
app = FastAPI(title=APP_NAME, lifespan=lifespan, dependencies=[Depends(get_current_user)])

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE,
    max_age=SESSION_MAX_AGE,
    same_site="lax",
    https_only=False,  # ubah ke True bila di-deploy lewat HTTPS
)

if IS_VERCEL:
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    BANNER_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_DIR), check_dir=False), name="uploads")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), check_dir=False), name="static")

# Semua POST/PUT/DELETE wajib membawa token CSRF yang cocok dengan session.
app.include_router(auth.router, dependencies=[Depends(verify_csrf)])
app.include_router(public.router, dependencies=[Depends(verify_csrf)])
app.include_router(admin.router)  # CSRF sudah dipasang di router admin


# --------------------------------------------------------------------------- #
# Penanganan error
# --------------------------------------------------------------------------- #
def _wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "")


@app.exception_handler(LoginRequired)
async def _login_required_handler(request: Request, exc: LoginRequired):
    if _wants_json(request):
        return JSONResponse({"detail": "Silakan login terlebih dahulu.", "login": login_redirect_url(exc.next_url)}, 401)
    return RedirectResponse(login_redirect_url(exc.next_url), status_code=303)


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
    if _wants_json(request) or request.url.path.startswith("/static/"):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    generic = exc.detail in (None, "", "Not Found", "Forbidden", "Method Not Allowed")
    message = _ERROR_HINTS.get(exc.status_code) if generic else exc.detail
    return render(
        request,
        "error.html",
        {
            "code": exc.status_code,
            "title": _ERROR_TITLES.get(exc.status_code, "Terjadi kesalahan"),
            "message": message or "Sesuatu tidak berjalan semestinya.",
        },
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, _exc: RequestValidationError):
    if _wants_json(request):
        return JSONResponse({"detail": "Data tidak valid."}, status_code=422)
    return render(
        request,
        "error.html",
        {"code": 422, "title": _ERROR_TITLES[422], "message": _ERROR_HINTS[422]},
        status_code=422,
    )


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok", "app": APP_NAME}
