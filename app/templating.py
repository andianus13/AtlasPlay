"""Instance Jinja2, filter, dan helper render + flash message (dipakai untuk toast)."""
import re
from typing import Any, Optional
from urllib.parse import urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape

from app.config import APP_NAME, APP_TAGLINE, TEMPLATES_DIR


def _asset_version() -> int:
    """Penanda versi berkas statis (waktu ubah terbaru) agar browser tidak memakai CSS/JS lama dari cache."""
    root = TEMPLATES_DIR.parent / "static"
    stamps = [f.stat().st_mtime for ext in ("css", "js") for f in (root / ext).glob(f"*.{ext}")]
    return int(max(stamps)) if stamps else 0


ASSET_V = _asset_version()
from app.security import csrf_token
from app.utils import format_date, format_datetime

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

_STATUS_LABEL = {"Pending": "Menunggu", "Approved": "Disetujui", "Rejected": "Ditolak"}
_STATUS_SLUG = {"Pending": "pending", "Approved": "approved", "Rejected": "rejected"}
_GPU_PREFIXES = ("NVIDIA GeForce ", "NVIDIA ", "AMD Radeon ", "AMD ", "Intel ")


def paragraphs(text: Optional[str]) -> Markup:
    """Ubah teks biasa menjadi paragraf HTML yang aman (baris kosong = paragraf baru)."""
    if not text:
        return Markup("")
    parts = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return Markup("".join(f"<p>{escape(p).replace(chr(10), Markup('<br>'))}</p>" for p in parts))


def rating_text(value: Optional[float]) -> str:
    return f"{value:.1f}" if value else "-"


def first_option(value: Optional[str]) -> str:
    """'GTX 1060 / RX 580' -> 'GTX 1060' (opsi pertama saja)."""
    return (value or "").split(" / ")[0].strip()


def compact_hw(value: Optional[str]) -> str:
    """Ringkas nama perangkat keras untuk tempat sempit: 'NVIDIA GeForce GTX 1060 3 GB / ...' -> 'GTX 1060 3 GB'."""
    text = first_option(value)
    for prefix in _GPU_PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix):]
    return text


def initial(name: Optional[str]) -> str:
    return (name or "?").strip()[:1].upper() or "?"


def number_id(value: Any) -> str:
    """12345 -> '12.345' (pemisah ribuan gaya Indonesia)."""
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def build_qs(params: dict, **overrides: Any) -> str:
    """Bangun query string dari dict; nilai kosong dibuang. build_qs(p, page=2) -> '?q=a&page=2'."""
    merged = {**params, **overrides}
    clean = {k: v for k, v in merged.items() if v is not None and v != ""}
    if str(clean.get("page")) == "1":
        clean.pop("page")
    return f"?{urlencode(clean)}" if clean else ""


templates.env.filters.update(
    tanggal=format_date,
    tanggal_waktu=format_datetime,
    paragraphs=paragraphs,
    rating_text=rating_text,
    first_option=first_option,
    compact_hw=compact_hw,
    initial=initial,
    number_id=number_id,
    status_label=lambda s: _STATUS_LABEL.get(s, s),
    status_slug=lambda s: _STATUS_SLUG.get(s, "pending"),
)
def pending_requests_count() -> int:
    """Jumlah pengajuan game yang menunggu; dipakai lencana di sidebar admin."""
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models import GameRequest

    with SessionLocal() as db:
        return db.scalar(select(func.count(GameRequest.id)).where(GameRequest.status == "Pending")) or 0


templates.env.globals.update(
    app_name=APP_NAME, app_tagline=APP_TAGLINE, asset_v=ASSET_V, qs=build_qs, pending_requests_count=pending_requests_count
)


# --------------------------------------------------------------------------- #
# Flash message: disimpan di session, dibaca sekali lalu dihapus.
# category: "success" | "error" | "info"
# --------------------------------------------------------------------------- #
def flash(request: Request, message: str, category: str = "info") -> None:
    queue = list(request.session.get("_flashes", []))
    queue.append({"message": message, "category": category})
    request.session["_flashes"] = queue


def pop_flashes(request: Request) -> list[dict]:
    return request.session.pop("_flashes", [])


def render(
    request: Request,
    name: str,
    context: Optional[dict[str, Any]] = None,
    status_code: int = 200,
):
    """Render template dengan konteks umum: current_user, flashes, csrf_token, current_path."""
    base_context = {
        "current_user": getattr(request.state, "current_user", None),
        "flashes": pop_flashes(request),
        "csrf_token": csrf_token(request),
        "current_path": request.url.path,
        "pending_count": getattr(request.state, "pending_count", 0),
    }
    base_context.update(context or {})
    return templates.TemplateResponse(request, name, base_context, status_code=status_code)


def render_fragment(request: Request, name: str, context: Optional[dict[str, Any]] = None):
    """Render potongan HTML untuk fetch() tanpa menghabiskan flash message milik halaman utama."""
    base_context = {
        "current_user": getattr(request.state, "current_user", None),
        "csrf_token": csrf_token(request),
        "current_path": request.url.path,
    }
    base_context.update(context or {})
    return templates.TemplateResponse(request, name, base_context)
