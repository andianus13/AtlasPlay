"""Seeding data awal: akun, developer, platform, 30 game, 100 ulasan, wishlist, dan request.

Seeding bersifat inkremental dan idempoten, jadi aman dipanggil setiap aplikasi start:
- game ditambahkan hanya bila jumlahnya di database masih di bawah 30 (judul yang sudah ada dilewati),
- ulasan ditambahkan hanya bila jumlahnya di bawah 100 dan pasangan (pengguna, game) belum ada,
- akun lama berdomain @atlasplay.local otomatis diubah menjadi @gmail.com.
Poster dan banner dibuat dengan Pillow (karya orisinal berbasis tipografi) sehingga website
langsung terisi tanpa koneksi internet dan tanpa memakai gambar bermerek dagang.

Catatan: spesifikasi pada data seed dirangkum dari informasi publik dan bersifat contoh.
Verifikasi ke situs resmi game bila data dipakai untuk keperluan selain demo tugas.
"""
import random
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import (
    BANNER_DIR,
    BANNER_SIZE,
    COVER_DIR,
    COVER_SIZE,
    IMAGE_QUALITY,
    ROLE_ADMIN,
    ROLE_USER,
)
from app.models import (
    Comment,
    Developer,
    Game,
    GameRequest,
    Platform,
    SavedGame,
    User,
    utcnow,
)
from app.security import hash_password
from app.seed_extra import EXTRA_COMMENTS, EXTRA_DEVELOPERS, EXTRA_GAMES, EXTRA_USERS
from app.services import recalculate_average_rating

TARGET_GAMES = 30
TARGET_COMMENTS = 100

# --------------------------------------------------------------------------- #
# DATA
# --------------------------------------------------------------------------- #
USERS = [
    # username, email, password, role
    ("admin", "admin@gmail.com", "admin123", ROLE_ADMIN),
    ("user", "user@gmail.com", "user123", ROLE_USER),
    ("rina", "rina@gmail.com", "user123", ROLE_USER),
    ("bayu", "bayu@gmail.com", "user123", ROLE_USER),
]
# 17 pengguna tambahan: total 20 pengguna biasa dengan password user123
USERS += [(name, email, "user123", ROLE_USER) for name, email in EXTRA_USERS]

DEVELOPERS = [
    dict(name="FromSoftware", country="Jepang", website_url="https://www.fromsoftware.jp/",
         description="Studio asal Tokyo yang dikenal lewat game aksi-RPG dengan tingkat tantangan tinggi dan dunia yang bercerita lewat lingkungan."),
    dict(name="CD PROJEKT RED", country="Polandia", website_url="https://www.cdprojektred.com/",
         description="Studio pengembang game RPG naratif dunia terbuka yang juga mengelola platform GOG."),
    dict(name="Larian Studios", country="Belgia", website_url="https://larian.com/",
         description="Studio RPG berbasis giliran dengan fokus pada kebebasan pemain dan pilihan yang berdampak pada cerita."),
    dict(name="Team Cherry", country="Australia", website_url="https://www.teamcherry.com.au/",
         description="Studio independen dari Adelaide yang membuat game petualangan 2D bergaya gambar tangan."),
    dict(name="ConcernedApe", country="Amerika Serikat", website_url="https://www.stardewvalley.net/",
         description="Nama pengembang solo Eric Barone, pembuat game simulasi pertanian yang dikerjakan seorang diri."),
    dict(name="Supergiant Games", country="Amerika Serikat", website_url="https://www.supergiantgames.com/",
         description="Studio independen asal San Francisco yang dikenal lewat game aksi dengan arahan seni dan musik yang kuat."),
    dict(name="Playground Games", country="Inggris", website_url="https://playground-games.com/",
         description="Studio balap asal Leamington Spa yang mengembangkan seri Forza Horizon."),
]

PLATFORMS = [
    dict(name="PC Windows", slug="pc-windows", short_name="PC", badge_color="#14B8A6"),
    dict(name="PlayStation 5", slug="playstation-5", short_name="PS5", badge_color="#7DD3FC"),
    dict(name="PlayStation 4", slug="playstation-4", short_name="PS4", badge_color="#60A5FA"),
    dict(name="Nintendo Switch", slug="nintendo-switch", short_name="Switch", badge_color="#F87171"),
    dict(name="Xbox Series X", slug="xbox-series-x", short_name="Xbox", badge_color="#4ADE80"),
]

PC, PS5, PS4, NSW, XBX = "pc-windows", "playstation-5", "playstation-4", "nintendo-switch", "xbox-series-x"

GAMES = [
    dict(
        title="Elden Ring", developer="FromSoftware", platforms=[PC, PS4, PS5, XBX],
        release_date=date(2022, 2, 25), featured=True, accent="#D9A441",
        official="https://eldenring.bn-ent.net/",
        summary="Action RPG dunia terbuka dari FromSoftware: jelajahi The Lands Between ke arah mana pun dan hadapi bos yang tidak mengampuni.",
        description=(
            "Elden Ring membawa formula pertarungan FromSoftware ke dunia terbuka yang luas. "
            "Pemain bebas memilih rute, menemukan gua, benteng, dan bos opsional tanpa penanda misi yang menuntun langkah.\n\n"
            "Build karakter sangat fleksibel: dari ksatria berperisai tebal sampai penyihir jarak jauh, ditambah pemanggilan roh "
            "untuk membantu di pertempuran sulit. Di PC, kestabilan frame rate sangat dipengaruhi CPU, jadi spesifikasi prosesor patut diperhatikan."),
        min_os="Windows 10", min_cpu="Intel Core i5-8400 / AMD Ryzen 3 3300X", min_ram="12 GB",
        min_gpu="NVIDIA GeForce GTX 1060 3 GB / AMD Radeon RX 580 4 GB", storage="60 GB",
        rec_os="Windows 10/11", rec_cpu="Intel Core i7-8700K / AMD Ryzen 5 3600X", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce GTX 1070 8 GB / AMD Radeon RX Vega 56 8 GB",
    ),
    dict(
        title="Cyberpunk 2077", developer="CD PROJEKT RED", platforms=[PC, PS4, PS5, XBX],
        release_date=date(2020, 12, 10), featured=True, accent="#E8D44D",
        official="https://www.cyberpunk.net/",
        summary="RPG aksi orang pertama di Night City: kota futuristik penuh korporasi, implan siber, dan pilihan yang membentuk cerita.",
        description=(
            "Kamu berperan sebagai V, tentara bayaran yang mengejar implan langka di Night City. "
            "Misi utama dan sampingan sama-sama punya cabang cerita, dan gaya bermain bisa diarahkan ke peretasan, tembak-menembak, atau pertarungan jarak dekat.\n\n"
            "Game ini termasuk berat untuk laptop. Pengaturan ray tracing dan DLSS/FSR sangat menentukan kenyamanan, "
            "sehingga ulasan performa dari perangkat sejenis sangat membantu sebelum membeli."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i7-6700 / AMD Ryzen 5 1600", min_ram="12 GB",
        min_gpu="NVIDIA GeForce GTX 1060 6 GB / AMD Radeon RX 580 8 GB", storage="70 GB (SSD)",
        rec_os="Windows 10/11 64-bit", rec_cpu="Intel Core i7-12700 / AMD Ryzen 7 7800X3D", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce RTX 2060 SUPER / AMD Radeon RX 5700 XT",
    ),
    dict(
        title="Baldur's Gate 3", developer="Larian Studios", platforms=[PC, PS5, XBX],
        release_date=date(2023, 8, 3), featured=True, accent="#C2570C",
        official="https://baldursgate3.game/",
        summary="RPG berbasis giliran dengan cerita bercabang, pertarungan taktis, dan mode kooperatif hingga empat pemain.",
        description=(
            "Berlatar di dunia Dungeons & Dragons, game ini menempatkan pemain pada petualangan yang dimulai dari infeksi misterius. "
            "Hampir setiap percakapan, pertarungan, dan interaksi dengan lingkungan bisa diselesaikan dengan lebih dari satu cara.\n\n"
            "Area kota di Act 3 paling berat bagi CPU dan RAM. Penyimpanan SSD sangat disarankan karena ukuran instalasinya besar."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-4690 / AMD FX 4350", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 970 / AMD Radeon RX 480 (4 GB+)", storage="150 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-8700K / AMD Ryzen 5 3600", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce RTX 2060 SUPER / AMD Radeon RX 5700 XT (8 GB+)",
    ),
    dict(
        title="The Witcher 3: Wild Hunt", developer="CD PROJEKT RED", platforms=[PC, PS4, PS5, NSW, XBX],
        release_date=date(2015, 5, 19), featured=False, accent="#B4B8C0",
        official="https://www.thewitcher.com/en/witcher3",
        summary="RPG dunia terbuka tentang pemburu monster Geralt yang mencari anak angkatnya di tengah perang dan kutukan.",
        description=(
            "Geralt dari Rivia menerima kontrak membunuh monster sambil menelusuri jejak Ciri. "
            "Kekuatan game ini ada pada misi sampingan yang bercerita utuh dan konsekuensi pilihan yang baru terasa jauh kemudian.\n\n"
            "Versi PC cukup ramah untuk laptop kelas menengah pada pengaturan standar, sehingga sering dipakai sebagai patokan kemampuan perangkat."),
        min_os="Windows 7 / 8 / 8.1 64-bit", min_cpu="Intel Core i5-2500K 3.3 GHz / AMD Phenom II X4 940", min_ram="6 GB",
        min_gpu="NVIDIA GeForce GTX 660 / AMD Radeon HD 7870", storage="35 GB",
        rec_os="Windows 7 / 8 / 8.1 64-bit", rec_cpu="Intel Core i7-3770 3.4 GHz / AMD FX-8350 4 GHz", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 770 / AMD Radeon R9 290",
    ),
    dict(
        title="Hollow Knight", developer="Team Cherry", platforms=[PC, PS4, NSW, XBX],
        release_date=date(2017, 2, 24), featured=False, accent="#7DD3FC",
        official="https://www.hollowknight.com/",
        summary="Metroidvania 2D bergaya gambar tangan: turun ke kerajaan serangga Hallownest yang luas dan sunyi.",
        description=(
            "Kamu menjelajahi gua, kota bawah tanah, dan taman berbahaya sambil menemukan jalan pintas yang membuka peta pelan-pelan. "
            "Pertarungan bos tegas dan adil, dengan sistem pesona yang memungkinkan banyak variasi gaya bermain.\n\n"
            "Kebutuhan sumber dayanya sangat ringan, jadi cocok untuk laptop tanpa GPU dedicated."),
        min_os="Windows 7", min_cpu="Intel Core 2 Duo E5200", min_ram="4 GB",
        min_gpu="NVIDIA GeForce 9800GTX+ (1 GB VRAM)", storage="9 GB",
        rec_os="Windows 10", rec_cpu="Intel Core i5", rec_ram="8 GB", rec_gpu="NVIDIA GeForce GTX 560",
    ),
    dict(
        title="Stardew Valley", developer="ConcernedApe", platforms=[PC, PS4, NSW, XBX],
        release_date=date(2016, 2, 26), featured=False, accent="#84CC16",
        official="https://www.stardewvalley.net/",
        summary="Simulasi pertanian santai: warisi ladang tua, tanam, berternak, menambang, dan akrab dengan warga desa.",
        description=(
            "Setiap hari di Pelican Town terbatas oleh energi dan waktu, sehingga pemain terus memilih: menyiram tanaman, memancing, "
            "turun ke tambang, atau mengobrol dengan penduduk. Ritme musim memberi tujuan jangka panjang tanpa tekanan.\n\n"
            "Game ini berjalan lancar di hampir semua laptop. Mode multipemain memungkinkan bertani bersama teman."),
        min_os="Windows Vista atau lebih baru", min_cpu="2 GHz", min_ram="2 GB",
        min_gpu="Mendukung Shader Model 3.0+ (256 MB VRAM)", storage="500 MB",
        rec_os=None, rec_cpu=None, rec_ram=None, rec_gpu=None,
    ),
    dict(
        title="Hades", developer="Supergiant Games", platforms=[PC, PS4, PS5, NSW, XBX],
        release_date=date(2020, 9, 17), featured=True, accent="#EF4444",
        official="https://www.supergiantgames.com/games/hades/",
        summary="Roguelike aksi tentang Zagreus yang mencoba kabur dari dunia bawah, dengan cerita yang bergerak setiap kali kamu mati.",
        description=(
            "Tiap percobaan kabur berlangsung singkat dan padat: pilih senjata, ambil berkah dari para dewa, lalu hadapi penjaga di tiap wilayah. "
            "Kegagalan bukan akhir karena dialog dan hubungan antar karakter terus berkembang.\n\n"
            "Pertarungannya cepat dan membutuhkan respons tepat, namun kebutuhan perangkatnya rendah sehingga nyaman dimainkan di laptop tipis."),
        min_os="Windows 7 SP1", min_cpu="Dual Core 2.4 GHz", min_ram="4 GB",
        min_gpu="1 GB VRAM, DirectX 10+", storage="15 GB",
        rec_os=None, rec_cpu=None, rec_ram=None, rec_gpu=None,
    ),
    dict(
        title="Forza Horizon 5", developer="Playground Games", platforms=[PC, XBX],
        release_date=date(2021, 11, 9), featured=False, accent="#F97316",
        official="https://forza.net/horizon",
        summary="Balap dunia terbuka di Meksiko dengan ratusan mobil, cuaca dinamis, dan festival yang terus berganti.",
        description=(
            "Pemain menjelajahi gurun, hutan, dan pesisir Meksiko lewat balapan, kejuaraan, dan tantangan acak. "
            "Cuaca dan musim berganti mingguan sehingga rute yang sama terasa berbeda.\n\n"
            "Mode grafis tinggi menuntut GPU kuat dan RAM cukup. Laptop kelas menengah tetap bisa menikmatinya dengan preset menengah."),
        min_os="Windows 10 versi 15063.0 atau lebih baru", min_cpu="Intel Core i5-4460 / AMD Ryzen 3 1200", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 970 / AMD Radeon RX 470", storage="110 GB",
        rec_os="Windows 10 versi 15063.0 atau lebih baru", rec_cpu="Intel Core i5-8400 / AMD Ryzen 5 1500X", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce GTX 1070 / AMD Radeon RX 590",
    ),
]

DEVELOPERS = DEVELOPERS + EXTRA_DEVELOPERS
GAMES = GAMES + EXTRA_GAMES  # 8 game awal + 22 game tambahan = 30

# (judul game, username, rating, perangkat, isi komentar)
COMMENTS = [
    ("Elden Ring", "user", 5, "Laptop RTX 3050 / RAM 16GB",
     "Jalan stabil di preset medium 1080p. Di area terbuka sesekali turun ke 45 FPS, tetap nyaman dimainkan."),
    ("Elden Ring", "rina", 4, "Ryzen 5 5600H / GTX 1650 / RAM 8GB",
     "Bisa jalan di low, tapi RAM 8GB terasa mepet. Disarankan menutup aplikasi lain dulu."),
    ("Cyberpunk 2077", "bayu", 4, "Laptop RTX 3060 / RAM 16GB",
     "Ray tracing mati, DLSS Quality, dapat sekitar 60 FPS. Suhu GPU cukup tinggi."),
    ("Cyberpunk 2077", "user", 3, "Core i5-10300H / GTX 1650 / RAM 8GB",
     "Hanya nyaman di low 900p. Loading lama kalau instalasi tidak di SSD."),
    ("Baldur's Gate 3", "rina", 5, "Laptop RTX 4050 / RAM 16GB",
     "Act 1 sangat mulus. Di Act 3 kota ramai, FPS turun tapi masih bisa dimainkan karena giliran."),
    ("Baldur's Gate 3", "bayu", 5, "Ryzen 7 5800H / RTX 3060 / RAM 32GB",
     "Ukuran instalasi besar sekali, siapkan ruang SSD. Performa sangat baik setelah update terbaru."),
    ("The Witcher 3: Wild Hunt", "user", 5, "Laptop GTX 1650 / RAM 8GB",
     "Preset high 1080p masih 50-60 FPS. Pilihan bagus untuk laptop kelas menengah."),
    ("Hollow Knight", "rina", 5, "Intel UHD Graphics / RAM 8GB",
     "Tanpa GPU dedicated pun lancar 60 FPS. Cocok untuk laptop kantor."),
    ("Stardew Valley", "bayu", 5, "Laptop lama Core i3 / RAM 4GB",
     "Ringan sekali. Mode multipemain jalan baik asal koneksi stabil."),
    ("Hades", "user", 5, "Laptop GTX 1650 / RAM 8GB",
     "Konsisten 60 FPS, kipas laptop hampir tidak berisik."),
    ("Hades", "rina", 4, "Intel Iris Xe / RAM 16GB",
     "Jalan lancar di 1080p tanpa GPU dedicated, hanya sesekali tersendat saat efek ramai."),
    ("Forza Horizon 5", "bayu", 4, "Laptop RTX 3050 Ti / RAM 16GB",
     "Preset medium 1080p stabil. Perlu SSD supaya texture tidak muncul terlambat."),
]

COMMENTS = COMMENTS + EXTRA_COMMENTS  # total 100 ulasan, masing-masing akun pengguna mendapat 5

# (username, judul game)
SAVED = [
    ("user", "Elden Ring"), ("user", "Hades"), ("user", "Stardew Valley"),
    ("rina", "Baldur's Gate 3"), ("rina", "Cyberpunk 2077"), ("bayu", "Forza Horizon 5"),
]

# (username, judul, platform, link, catatan, status)
REQUESTS = [
    ("user", "Hollow Knight: Silksong", "PC, Nintendo Switch", "https://www.hollowknight.com/",
     "Mohon ditambahkan beserta spesifikasi PC-nya.", "Pending"),
    ("rina", "Hades II", "PC", "https://www.supergiantgames.com/games/hades-ii/",
     "Lanjutan Hades, banyak yang menanyakan spesifikasinya.", "Approved"),
    ("bayu", "Game Percobaan", "PC", None, "Hanya untuk mencoba fitur pengajuan.", "Rejected"),
]

# --------------------------------------------------------------------------- #
# GENERATOR GAMBAR (Pillow)
# --------------------------------------------------------------------------- #
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "DejaVuSans-Bold.ttf",
    "arialbd.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_art(size: tuple[int, int], title: str, accent_hex: str, key: str, banner: bool) -> Image.Image:
    w, h = size
    rng = random.Random(key)
    ar, ag, ab = _hex_to_rgb(accent_hex)

    # 1) gradien dasar: obsidian di atas, bernuansa aksen di bawah
    base = Image.new("RGB", size)
    line = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        line.line(
            [(0, y), (w, y)],
            fill=(int(11 + (ar * 0.30 - 11) * t), int(15 + (ag * 0.30 - 15) * t), int(23 + (ab * 0.30 - 23) * t)),
        )
    canvas = base.convert("RGBA")

    # 2) bentuk geometris translusen
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for _ in range(3):
        x0 = rng.randint(-w // 4, w)
        band = rng.randint(w // 8, w // 3)
        od.polygon([(x0, 0), (x0 + band, 0), (x0 + band - w // 2, h), (x0 - w // 2, h)],
                   fill=(ar, ag, ab, rng.randint(14, 34)))
    radius = int(min(w, h) * (0.55 if not banner else 0.8))
    cx = rng.randint(int(w * 0.45), int(w * 0.8)) if not banner else int(w * 0.78)
    cy = int(h * 0.34) if not banner else int(h * 0.45)
    for i, alpha in enumerate((150, 90, 50)):
        r = int(radius * (1 - i * 0.22))
        od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(ar, ag, ab, alpha), width=3 if i else 5)
    canvas = Image.alpha_composite(canvas, overlay)

    # 3) vignette gelap agar judul terbaca
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    if banner:
        for x in range(w):
            alpha = int(200 * max(0.0, 1 - x / (w * 0.65)))
            sd.line([(x, 0), (x, h)], fill=(5, 8, 14, alpha))
    else:
        for y in range(int(h * 0.45), h):
            alpha = int(215 * (y - h * 0.45) / (h * 0.55))
            sd.line([(0, y), (w, y)], fill=(5, 8, 14, alpha))
    canvas = Image.alpha_composite(canvas, shade)

    # 4) judul (hanya pada cover; banner tampil bersih karena judul ditulis oleh halaman)
    if banner:
        return canvas.convert("RGB")
    draw = ImageDraw.Draw(canvas)
    margin = 80 if banner else 42
    max_w = int(w * 0.52) if banner else w - margin * 2
    max_lines = 3
    for font_size in range(110 if banner else 72, 28, -4):
        font = _font(font_size)
        lines = _wrap(draw, title, font, max_w)
        if len(lines) <= max_lines and all(draw.textlength(s, font=font) <= max_w for s in lines):
            break
    line_h = int(font_size * 1.18)
    block_h = line_h * len(lines)
    top = (h - block_h) // 2 if banner else h - margin - block_h
    bar_y = top - 26
    draw.rectangle([margin, bar_y, margin + 64, bar_y + 6], fill=(ar, ag, ab, 255))
    for i, text in enumerate(lines):
        draw.text((margin, top + i * line_h), text, font=font, fill=(241, 245, 249, 255))
    return canvas.convert("RGB")


def _ensure_image(path: Path, size: tuple[int, int], title: str, accent: str, key: str, banner: bool) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    _draw_art(size, title, accent, key, banner).save(path, "WEBP", quality=IMAGE_QUALITY)


# --------------------------------------------------------------------------- #
# SEEDER (inkremental, tanpa duplikat)
# --------------------------------------------------------------------------- #
OLD_EMAIL_DOMAIN = "@atlasplay.local"
NEW_EMAIL_DOMAIN = "@gmail.com"


def _seed_users(db: Session) -> None:
    """Tambah akun yang belum ada dan migrasikan email lama @atlasplay.local ke @gmail.com."""
    existing = {u.username: u for u in db.scalars(select(User))}
    taken = {u.email.lower() for u in existing.values()}

    for user in existing.values():
        if user.email.lower().endswith(OLD_EMAIL_DOMAIN):
            fresh = user.email[: -len(OLD_EMAIL_DOMAIN)] + NEW_EMAIL_DOMAIN
            if fresh.lower() not in taken:
                taken.discard(user.email.lower())
                user.email = fresh
                taken.add(fresh.lower())

    for username, email, password, role in USERS:
        if username in existing or email.lower() in taken:
            continue
        db.add(User(username=username, email=email, password_hash=hash_password(password), role=role))
        taken.add(email.lower())
    db.commit()


def _seed_catalog(db: Session) -> int:
    """Lengkapi developer, platform, dan game sampai TARGET_GAMES. Mengembalikan jumlah game baru."""
    developers = {d.name: d for d in db.scalars(select(Developer))}
    for item in DEVELOPERS:
        if item["name"] not in developers:
            developers[item["name"]] = Developer(**item)
            db.add(developers[item["name"]])
    platforms = {p.slug: p for p in db.scalars(select(Platform))}
    for item in PLATFORMS:
        if item["slug"] not in platforms:
            platforms[item["slug"]] = Platform(**item)
            db.add(platforms[item["slug"]])
    db.flush()

    total = db.scalar(select(func.count(Game.id))) or 0
    if total >= TARGET_GAMES:
        db.commit()
        return 0
    titles = {t.lower() for t in db.scalars(select(Game.title))}

    # import lokal agar tidak ada ketergantungan melingkar
    from app.services import unique_game_slug

    now = utcnow()
    added = 0
    for index, item in enumerate(GAMES):
        if total + added >= TARGET_GAMES:
            break
        if item["title"].lower() in titles:
            continue
        slug = unique_game_slug(db, item["title"])
        cover_path = COVER_DIR / f"seed-{slug}.webp"
        banner_path = BANNER_DIR / f"seed-{slug}.webp"
        _ensure_image(cover_path, COVER_SIZE, item["title"], item["accent"], slug + "-cover", banner=False)
        _ensure_image(banner_path, BANNER_SIZE, item["title"], item["accent"], slug + "-banner", banner=True)

        db.add(Game(
            title=item["title"],
            slug=slug,
            cover_image=f"/static/uploads/covers/{cover_path.name}",
            banner_image=f"/static/uploads/banners/{banner_path.name}",
            short_summary=item["summary"],
            full_description=item["description"],
            official_website_url=item["official"],
            release_date=item["release_date"],
            developer=developers[item["developer"]],
            platforms=[platforms[s] for s in item["platforms"]],
            min_os=item["min_os"], min_cpu=item["min_cpu"], min_ram=item["min_ram"], min_gpu=item["min_gpu"],
            storage_req=item["storage"],
            rec_os=item["rec_os"], rec_cpu=item["rec_cpu"], rec_ram=item["rec_ram"], rec_gpu=item["rec_gpu"],
            is_featured=item["featured"],
            created_at=now - timedelta(days=3 + (TARGET_GAMES - 1 - index) * 3),
            updated_at=now - timedelta(days=(index * 3) % 14),
        ))
        titles.add(item["title"].lower())
        added += 1
    db.commit()
    return added


def _seed_activity(db: Session, first_run: bool) -> None:
    """Ulasan (maks. TARGET_COMMENTS, tanpa pasangan pengguna-game ganda), lalu hitung ulang rating.

    Wishlist dan pengajuan contoh hanya dibuat pada database yang benar-benar baru."""
    users = {u.username: u for u in db.scalars(select(User))}
    games = {g.title: g for g in db.scalars(select(Game))}
    now = utcnow()

    pairs = set(db.execute(select(Comment.user_id, Comment.game_id)).all())
    total = db.scalar(select(func.count(Comment.id))) or 0
    for i, (title, username, rating, device, content) in enumerate(COMMENTS):
        if total >= TARGET_COMMENTS:
            break
        user, game = users.get(username), games.get(title)
        if not user or not game or (user.id, game.id) in pairs:
            continue
        db.add(Comment(
            user_id=user.id, game_id=game.id, rating=rating, device_tested=device, content=content,
            created_at=now - timedelta(days=1 + (i * 7) % 80, hours=(i * 5) % 24),
        ))
        pairs.add((user.id, game.id))
        total += 1

    if first_run:
        for i, (username, title) in enumerate(SAVED):
            db.add(SavedGame(user_id=users[username].id, game_id=games[title].id, saved_at=now - timedelta(days=6 - i)))
        for i, (username, title, platform, link, notes, status) in enumerate(REQUESTS):
            db.add(GameRequest(
                user_id=users[username].id, game_title=title, platform_info=platform, official_link=link,
                notes=notes, status=status, submitted_at=now - timedelta(days=9 - i * 3),
            ))
    db.flush()
    for game in games.values():
        recalculate_average_rating(db, game.id)
    db.commit()


_SEED_LOCK_ID = 727274  # nomor bebas untuk advisory lock PostgreSQL


def seed_database(db: Session) -> None:
    """Idempotent. Advisory lock mencegah seeding ganda bila beberapa worker start bersamaan."""
    # Kunci dipegang koneksi khusus agar tidak ikut lepas saat session seeding commit.
    with db.get_bind().connect() as lock_conn:
        lock_conn.execute(text("SELECT pg_advisory_lock(:id)"), {"id": _SEED_LOCK_ID})
        try:
            first_run = not db.scalar(select(func.count(Game.id)))
            _seed_users(db)
            _seed_catalog(db)
            _seed_activity(db, first_run)
        finally:
            lock_conn.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": _SEED_LOCK_ID})
