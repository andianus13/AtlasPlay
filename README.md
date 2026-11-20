# AtlasPlay

Direktori spesifikasi game multi-platform dengan situs publik dan dashboard admin CRUD.
Stack: FastAPI, Jinja2, SQLAlchemy, PostgreSQL, Pillow, fpdf2.

## Menjalankan

1. Pastikan PostgreSQL berjalan. Buka `.env`, sesuaikan `DATABASE_URL` (user, password, host) dan ganti `ATLASPLAY_SECRET_KEY`.
2. Buat virtualenv lalu pasang dependensi:
   ```
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Jalankan dari folder ini:
   ```
   uvicorn app.main:app --reload
   ```
4. Buka http://127.0.0.1:8000

Saat pertama dijalankan, database `game_catalog_db` dibuat otomatis, lalu tabel dan data awal
(termasuk gambar poster/banner buatan Pillow) terisi sendiri.

## Akun bawaan

| Peran | Username | Password |
|-------|----------|----------|
| Admin | `admin`  | `admin123` |
| User  | `user`   | `user123`  |

Ada juga akun contoh `rina` dan `bayu`. Lihat `app/seed.py`. Ganti password sebelum deploy.

## Catatan

- Halaman memuat Tailwind (CDN), GSAP, dan Google Fonts, jadi butuh internet.
- Data spesifikasi game adalah contoh. Verifikasi ke situs resmi sebelum dipakai sungguhan.
- Unggahan gambar otomatis dipotong dari tengah: cover 600x800, banner 1400x550 (WebP).
- Laporan PDF: Admin > Laporan > Download Laporan PDF.

## Perubahan v5

- Thumbnail vertikal di banner hero dihapus. Navigasi kini berupa titik pagination minimalis di pojok kanan bawah banner (titik aktif memanjang dan terisi selama 5 detik) plus panah tipis yang muncul saat banner di-hover. Auto-slide 5 detik tetap berjalan; klik titik/panah langsung pindah dan timer diulang.
- Latar halaman kini berupa poster game yang di-blur (fixed, `blur 65px`, `scale 1.1`, opacity 45%, overlay gradien gelap) dengan crossfade 0,7 detik: Beranda mengikuti slide aktif dan poster yang di-hover, Katalog mengikuti kartu yang di-hover, Detail Game memakai banner game yang dibuka.
- Seeding diperluas menjadi 30 game nyata (PC, PS5, PS4, Switch, Xbox Series X) dan 100 ulasan dari 20 akun pengguna (masing-masing 5 ulasan). Rata-rata rating dihitung ulang otomatis.
- Seeding inkremental: bila jumlah game di database < 30 (mis. baru 8 game lama), sisanya ditambahkan otomatis saat server start tanpa duplikat. Ulasan hanya ditambahkan bila total < 100 dan pasangan (pengguna, game) belum ada.
- Semua email akun memakai `@gmail.com`. Akun lama berakhiran `@atlasplay.local` otomatis diubah saat server start.
- Akun: `admin` / `admin123`; 20 pengguna (`user`, `rina`, `bayu`, `dimas`, `sari`, `aldo`, `mita`, `fajar`, `nadia`, `galih`, `putri`, `rizky`, `anisa`, `hendra`, `wulan`, `yoga`, `citra`, `bagas`, `laras`, `eko`) dengan password `user123`. Akun yang sudah ada di database tidak diubah passwordnya.

## Perubahan final (v6)

- Hero banner bersih: tombol panah dan titik pagination dihapus. Slide berganti otomatis tiap 5 detik dengan crossfade dan slow zoom.
- Latar poster blur kini menutup seluruh layar (`fixed`, `100vw x 100vh`, `blur 70px`, `scale 1.25`, opacity 55%) dengan overlay merata `rgba(10,13,18,.72)`, tanpa gradasi hitam di bawah, sehingga tetap terlihat saat scroll.
- Objek 3D orisinal berupa gamepad wireless pro controller (bodi extrude + bevel obsidian/slate satin, dua analog stick cekung dengan cincin emerald `#10b981`, D-pad, empat tombol aksi, bumper L1/R1 dan trigger L2/R2 beraksen cyan `#38bdf8`) dengan Three.js; animasi perakitan (exploded assembly), ayunan melayang, dan respons kursor/scroll.
  - `/welcome`: layar pembuka penuh dengan tombol Login, Register, dan tautan "Masuk sebagai Tamu / Jelajahi Katalog" (`/enter`). Pengunjung belum login yang membuka `/` pertama kali diarahkan ke sini.
  - `/login` dan `/register`: kanvas 3D di belakang form kaca.
  - Beranda: kanvas 3D opacity 18% di atas poster blur.
- Three.js dimuat dari CDN dengan cadangan lokal `static/vendor/three.module.min.js`; tanpa WebGL halaman tetap normal.

## Revisi akhir (v7)

- Latar seragam di semua halaman (Welcome, Login, Register, Beranda, Katalog, Koleksiku, Detail, Admin): `#070b10` dengan pendaran emerald-slate lembut, debu bintang melayang, dan gamepad 3D di tengah. Latar poster blur dihapus.
- Welcome/Login/Register: gamepad tampil penuh di tengah. Halaman lain: gamepad di tengah belakang dengan opacity 18% dan kartu konten berlapis kaca gelap tipis (`rgba(7,11,16,.6)` + blur 2px).
- Animasi: intro zoom-in kamera + komponen melayang masuk dari berbagai arah lalu merakit sambil berputar; setelah itu melayang naik-turun, berayun, miring mengikuti kursor, dan sesekali berputar 360 derajat. Klik: putaran cepat + denyut cahaya emissive.
- Alur masuk: `/` (belum login, belum memilih tamu) -> `/welcome` -> Login / Register / Masuk sebagai Tamu -> Beranda.
- Teks hero slide sebelumnya langsung disembunyikan sebelum slide baru tampil (tidak bertumpuk).

## Perbaikan 3D Controller (Welcome, Login, Register)

- Welcome: controller berada di area atas layar (ukuran dan posisinya dihitung dari tinggi layar) sehingga tidak menabrak logo, judul, dan tombol di bawah.
- Login/Register: kanvas 3D tampil kembali di tengah layar dengan opacity 45%, di atas latar kosmik dan di bawah form kaca. Penyebab hilangnya: gradien latar sebelumnya dipasang di `<body>` sehingga menutupi kanvas; kini dipasang di `<html>`.
- Welcome memakai animasi siklus: utuh (0-2,5 dtk) -> kilatan emerald + shatter radial (2,5-3,0) -> slow-motion ~0,07x (3,0-5,2) -> tersedot kembali menyatu (5,2-6,5) -> berputar santai lalu mengulang. Klik pada Welcome memicu siklus segera. Cangkang dibagi tiga (grip kiri, tengah, grip kanan) ditambah pelat, stick, D-pad, tombol, bumper/trigger, inti chip, 46 serpihan, dan partikel cahaya emerald/cyan.
- Login/Register: animasi merakit saat halaman dibuka lalu melayang halus.
- Animasi 3D tidak dimatikan oleh `prefers-reduced-motion`.
- Dashboard (Beranda dst.) dibuat tetap bersih: kanvas latar hanya bayangan tipis (opacity 8%).

## Revisi visual terakhir (v8)

- Latar poster blur penuh layar kembali di Beranda, Katalog, dan Detail Game (`fixed inset-0`, z -20, `blur 75px`, `scale 1.25`, opacity 50%, crossfade 0,7 dtk, overlay `#070b10` 70%). Mengikuti slide hero aktif, poster yang di-hover, dan game yang dibuka. Tidak dipasang di Welcome, Login, dan Register.
- Controller 3D samar (opacity 14%, desaturasi) di tengah belakang pada halaman dashboard, di atas latar blur.
- Logo brand (diperbarui): gamepad dua warna dengan pembelah lengkung S, sisi kiri emerald dengan D-pad plus, sisi kanan cyan ke biru tua dengan stick dan tombol, tepi perak, bumper cyan dengan teks "Atlas" putih + "Play" emerald di sebelah kanan. Favicon ikut diganti.
- Ikon platform (Windows, PlayStation, Nintendo Switch, Xbox) diganti ikon vektor bergaya logo brand dengan warna masing-masing dalam badge kaca gelap. Ini gambar vektor sederhana buatan sendiri, bukan berkas aset resmi; ganti dengan SVG resmi dari pedoman brand tiap perusahaan bila diperlukan untuk publikasi.

- Logo (v9): ikon minimalis fill solid tanpa stroke, satu gradasi emerald (`#34d399` ke `#059669`), siluet gamepad beratap puncak "A" dengan negative space (satu irisan diagonal, satu silang, satu titik). Teks `Atlas` putih + `Play` emerald (`#34d399`), font-semibold.

- Logo (v10): dua lapisan solid tanpa garis tepi: folder arsip berwarna cyan `#38bdf8` di belakang dan gamepad emerald `#10b981` di depan, dipisah celah transparan (SVG mask); D-pad dan 4 tombol wajik berupa negative space. Teks `Atlas` putih + `Play` `#34d399`.
- Logo (v11): folder cyan-biru (dua lapisan, gradasi #38bdf8 > #0284c7 > #072a44) di belakang dan gamepad emerald (#34d399 > #10b981 > #065f46) di depan, menghadap depan tanpa stroke; celah transparan via mask, D-pad dan 4 tombol wajik sebagai lubang transparan, drop shadow halus dari gamepad ke folder. Teks Atlas putih + Play mint dengan glow tipis. Dipasang di navbar, Welcome (besar), Login/Register (di atas form), dan favicon.
- Logo (v12): memakai aset gambar langsung dari desain yang dikirim: ikon folder + gamepad di-crop, latar gelap (termasuk lubang D-pad/tombol) dijadikan transparan dengan Pillow, disimpan di `static/img/atlasplay-logo.png` (RGBA) dan `static/favicon.png` (64x64). Teks "AtlasPlay" dibuat dengan HTML/CSS. Semua `<link rel="icon">` mengarah ke `/static/favicon.png`.
