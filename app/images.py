"""Pemrosesan gambar upload: validasi, center-crop + resize (Pillow ImageOps.fit), simpan WebP 85%.

Cover  : selalu 600x800 px  (rasio 3:4)
Banner : selalu 1400x550 px (rasio 21:9)
Gambar dengan rasio lain dipotong dari tengah, tidak pernah diregangkan.
"""
import io
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from PIL import Image, ImageOps, UnidentifiedImageError
from starlette.datastructures import UploadFile

from app.config import (
    BANNER_DIR,
    BANNER_SIZE,
    COVER_DIR,
    COVER_SIZE,
    IMAGE_QUALITY,
    MAX_UPLOAD_BYTES,
    UPLOAD_DIR,
)
from app.utils import is_local_upload

MAX_PIXELS = 40_000_000  # lindungi server dari "decompression bomb"
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
# Batas minimum = setengah ukuran target, agar hasil upscale tidak pecah.
MIN_SIZE = {"cover": (COVER_SIZE[0] // 2, COVER_SIZE[1] // 2), "banner": (BANNER_SIZE[0] // 2, BANNER_SIZE[1] // 2)}
TARGET_SIZE = {"cover": COVER_SIZE, "banner": BANNER_SIZE}
FOLDER = {"cover": COVER_DIR, "banner": BANNER_DIR}
URL_PREFIX = {"cover": "/static/uploads/covers", "banner": "/static/uploads/banners"}


class ImageError(ValueError):
    """Pesan error ramah pengguna untuk gambar yang tidak bisa diproses."""


def _flatten(image: Image.Image) -> Image.Image:
    """Ratakan transparansi ke latar gelap agar tidak muncul kotak hitam/putih aneh."""
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, (19, 26, 38))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def process_image(data: bytes, kind: str) -> bytes:
    """Validasi lalu center-crop + resize ke ukuran target. Mengembalikan bytes WebP."""
    size, minimum = TARGET_SIZE[kind], MIN_SIZE[kind]
    try:
        image = Image.open(io.BytesIO(data))
        if image.format not in ALLOWED_FORMATS:
            raise ImageError("Format tidak didukung. Gunakan JPG, PNG, WebP, atau GIF.")
        if image.width * image.height > MAX_PIXELS:
            raise ImageError("Resolusi gambar terlalu besar (maksimal sekitar 40 megapiksel).")
        image.load()
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ImageError("File bukan gambar yang valid atau rusak.") from None

    image = ImageOps.exif_transpose(image)
    if image.width < minimum[0] or image.height < minimum[1]:
        raise ImageError(
            f"Gambar terlalu kecil ({image.width}x{image.height} px). Minimal {minimum[0]}x{minimum[1]} px "
            f"agar tidak pecah setelah diubah ke {size[0]}x{size[1]} px."
        )

    fitted = ImageOps.fit(_flatten(image), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    buffer = io.BytesIO()
    fitted.save(buffer, "WEBP", quality=IMAGE_QUALITY, method=6)
    return buffer.getvalue()


def has_upload(upload: object) -> bool:
    """True bila field file benar-benar berisi file (browser mengirim bagian kosong bila tidak dipilih)."""
    return isinstance(upload, UploadFile) and bool(upload.filename)


async def prepare_upload(upload: UploadFile, kind: str) -> bytes:
    """Baca upload lalu validasi + crop + resize. Belum menulis apa pun ke disk."""
    data = await upload.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise ImageError("File kosong.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageError(f"Ukuran file maksimal {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
    return process_image(data, kind)


def store_processed(processed: bytes, kind: str) -> str:
    """Tulis bytes WebP hasil prepare_upload ke static/uploads dan kembalikan path publiknya."""
    folder: Path = FOLDER[kind]
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}.webp"
    (folder / name).write_bytes(processed)
    return f"{URL_PREFIX[kind]}/{name}"


async def save_upload(upload: UploadFile, kind: str) -> str:
    """Proses dan simpan sekaligus."""
    return store_processed(await prepare_upload(upload, kind), kind)


def delete_local_image(path: Optional[str]) -> None:
    """Hapus file upload lokal. URL eksternal dan path di luar static/uploads diabaikan."""
    if not is_local_upload(path):
        return
    target = (UPLOAD_DIR.parent.parent / path.lstrip("/")).resolve()
    try:
        target.relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        return
    target.unlink(missing_ok=True)


def is_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
