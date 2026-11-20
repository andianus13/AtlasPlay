"""Data seed tambahan: 22 game, 17 akun, 16 developer, dan 88 ulasan.

Digabung dengan data di seed.py sehingga total menjadi 30 game dan 100 ulasan.
Spesifikasi dirangkum dari informasi publik dan bersifat contoh; cocokkan dengan situs resmi.
"""
from datetime import date

PC, PS5, PS4, NSW, XBX = "pc-windows", "playstation-5", "playstation-4", "nintendo-switch", "xbox-series-x"

EXTRA_USERS = [
    ("dimas", "dimas@gmail.com"),
    ("sari", "sari@gmail.com"),
    ("aldo", "aldo@gmail.com"),
    ("mita", "mita@gmail.com"),
    ("fajar", "fajar@gmail.com"),
    ("nadia", "nadia@gmail.com"),
    ("galih", "galih@gmail.com"),
    ("putri", "putri@gmail.com"),
    ("rizky", "rizky@gmail.com"),
    ("anisa", "anisa@gmail.com"),
    ("hendra", "hendra@gmail.com"),
    ("wulan", "wulan@gmail.com"),
    ("yoga", "yoga@gmail.com"),
    ("citra", "citra@gmail.com"),
    ("bagas", "bagas@gmail.com"),
    ("laras", "laras@gmail.com"),
    ("eko", "eko@gmail.com"),
]

EXTRA_DEVELOPERS = [
    dict(name="Rockstar Games", country="Amerika Serikat", website_url="https://www.rockstargames.com/",
         description="Penerbit dan pengembang seri dunia terbuka Grand Theft Auto dan Red Dead dengan skala produksi sinematik."),
    dict(name="Santa Monica Studio", country="Amerika Serikat", website_url="https://sms.playstation.com/",
         description="Studio first-party PlayStation di balik seri God of War, dikenal lewat aksi sinematik dan narasi karakter."),
    dict(name="Insomniac Games", country="Amerika Serikat", website_url="https://insomniac.games/",
         description="Studio first-party PlayStation yang membuat Ratchet & Clank dan Marvel's Spider-Man."),
    dict(name="Nintendo EPD", country="Jepang", website_url="https://www.nintendo.com/",
         description="Divisi pengembangan internal Nintendo untuk seri Mario, Zelda, dan Animal Crossing."),
    dict(name="Maddy Makes Games", country="Kanada", website_url="https://www.celestegame.com/",
         description="Studio indie kecil pembuat Celeste, platformer presisi dengan cerita yang personal."),
    dict(name="ZA/UM", country="Britania Raya", website_url="https://zaumstudio.com/",
         description="Studio RPG naratif yang dikenal lewat Disco Elysium dengan sistem dialog dan pikiran karakter."),
    dict(name="Capcom", country="Jepang", website_url="https://www.capcom.com/",
         description="Penerbit game Jepang di balik Resident Evil, Monster Hunter, dan Street Fighter."),
    dict(name="Atlus", country="Jepang", website_url="https://atlus.com/",
         description="Pengembang JRPG seri Persona dan Shin Megami Tensei dengan gaya visual dan musik khas."),
    dict(name="Avalanche Software", country="Amerika Serikat", website_url="https://www.avalanchesoftware.com/",
         description="Studio pengembang RPG aksi dunia terbuka berlatar semesta Wizarding World."),
    dict(name="Tango Gameworks", country="Jepang", website_url="https://www.tangogameworks.com/",
         description="Studio asal Tokyo pembuat The Evil Within dan Hi-Fi Rush yang berirama."),
    dict(name="BlueTwelve Studio", country="Prancis", website_url="https://www.bluetwelvestudio.com/",
         description="Studio indie pembuat Stray, petualangan dari sudut pandang seekor kucing."),
    dict(name="Hazelight Studios", country="Swedia", website_url="https://www.hazelight.se/",
         description="Studio yang berfokus pada game kooperatif dua pemain seperti A Way Out dan It Takes Two."),
    dict(name="Mintrocket", country="Korea Selatan", website_url="https://www.mintrocket.com/",
         description="Studio di bawah Nexon yang membuat Dave the Diver, perpaduan menyelam dan mengelola restoran."),
    dict(name="Motion Twin", country="Prancis", website_url="https://motion-twin.com/",
         description="Kolektif pengembang yang membuat Dead Cells, roguelite aksi dengan pergerakan cepat."),
    dict(name="343 Industries", country="Amerika Serikat", website_url="https://www.halowaypoint.com/",
         description="Studio Xbox Game Studios yang mengelola kelanjutan waralaba Halo."),
    dict(name="Studio MDHR", country="Kanada", website_url="https://www.cupheadgame.com/",
         description="Studio independen pembuat Cuphead dengan animasi gambar tangan ala kartun 1930-an."),
    dict(name="Mojang Studios", country="Swedia", website_url="https://www.minecraft.net/",
         description="Studio pembuat Minecraft, game sandbox membangun dan bertahan hidup."),
]

EXTRA_GAMES = [
    dict(
        title="Red Dead Redemption 2", developer="Rockstar Games", platforms=[PC, PS4, XBX],
        release_date=date(2018, 10, 26), featured=False, accent="#B4532A",
        official="https://www.rockstargames.com/reddeadredemption2",
        summary="Petualangan koboi dunia terbuka bersama geng Van der Linde di akhir era Wild West.",
        description=(
            "Kamu berperan sebagai Arthur Morgan, anggota geng buronan yang terus berpindah tempat sambil dikejar penegak hukum. "
            "Ritme permainan sengaja pelan: berburu, memasak, mengurus kuda, dan mengobrol di kamp ikut membangun suasana.\n\n"
            "Di PC, game ini sangat bergantung pada GPU dan VRAM. Pilihan API Vulkan atau DirectX 12 bisa berbeda hasilnya tergantung perangkat."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-2500K / AMD FX-6300", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 770 2 GB / AMD Radeon R9 280 3 GB", storage="150 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-4770K / AMD Ryzen 5 1500X", rec_ram="12 GB",
        rec_gpu="NVIDIA GeForce GTX 1060 6 GB / AMD Radeon RX 480 4 GB",
    ),
    dict(
        title="God of War", developer="Santa Monica Studio", platforms=[PC, PS4, PS5],
        release_date=date(2018, 4, 20), featured=False, accent="#9CA3AF",
        official="https://www.playstation.com/games/god-of-war/",
        summary="Kratos dan putranya Atreus menempuh perjalanan menembus mitologi Nordik dengan kamera satu tarikan tanpa putus.",
        description=(
            "Setelah meninggalkan tanah Yunani, Kratos hidup tenang di dunia Nordik sampai sebuah perjalanan membawanya bersama Atreus. "
            "Pertarungan kapak Leviathan terasa berbobot, dipadukan dengan eksplorasi, teka-teki, dan hubungan ayah-anak yang jadi pusat cerita.\n\n"
            "Versi PC mendukung DLSS dan FSR sehingga cukup bersahabat untuk laptop kelas menengah."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-2500K / AMD Ryzen 3 1200", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 960 4 GB / AMD Radeon R9 290X", storage="70 GB (SSD disarankan)",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-7700K / AMD Ryzen 5 2400G", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 1060 6 GB / AMD Radeon RX 570 4 GB",
    ),
    dict(
        title="Marvel's Spider-Man Remastered", developer="Insomniac Games", platforms=[PC, PS5],
        release_date=date(2022, 8, 12), featured=False, accent="#DC2626",
        official="https://www.playstation.com/games/marvels-spider-man-remastered/",
        summary="Peter Parker mengayun di antara gedung Manhattan sambil menghadapi musuh-musuh lamanya dalam aksi dunia terbuka yang mulus.",
        description=(
            "Peter Parker sudah delapan tahun jadi Spider-Man ketika kota diguncang ancaman baru. "
            "Gerakan berayun jadi daya tarik utama, ditemani pertarungan akrobatik, gadget, dan cerita yang menjaga sisi manusiawi Peter.\n\n"
            "Versi PC menawarkan ray tracing dan dukungan layar ultrawide. Menyimpan game di SSD sangat membantu agar kota termuat tanpa tersendat."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i3-4160 / AMD Ryzen 3 1200", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 950 / AMD Radeon RX 580", storage="75 GB (SSD)",
        rec_os="Windows 10/11 64-bit", rec_cpu="Intel Core i5-11600K / AMD Ryzen 5 3600", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce GTX 1060 6 GB / AMD Radeon RX 580 8 GB",
    ),
    dict(
        title="The Legend of Zelda: Tears of the Kingdom", developer="Nintendo EPD", platforms=[NSW],
        release_date=date(2023, 5, 12), featured=False, accent="#38BDF8",
        official="https://www.zelda.com/tears-of-the-kingdom/",
        summary="Link menjelajahi Hyrule dan langit di atasnya, dengan kemampuan merakit kendaraan dan senjata dari benda apa pun.",
        description=(
            "Lanjutan Breath of the Wild ini memperluas dunia ke langit dan gua bawah tanah. "
            "Kemampuan Ultrahand memungkinkan pemain menyusun alat dan kendaraan sendiri, sehingga banyak teka-teki punya lebih dari satu jawaban.\n\n"
            "Game ini hanya tersedia di Nintendo Switch, jadi tidak ada data spesifikasi PC."),
        min_os=None, min_cpu=None, min_ram=None, min_gpu=None, storage=None,
        rec_os=None, rec_cpu=None, rec_ram=None, rec_gpu=None,
    ),
    dict(
        title="Super Mario Odyssey", developer="Nintendo EPD", platforms=[NSW],
        release_date=date(2017, 10, 27), featured=False, accent="#F59E0B",
        official="https://www.nintendo.com/us/store/products/super-mario-odyssey-switch/",
        summary="Mario berkeliling berbagai kerajaan dengan topi hidup Cappy untuk mengejar Bowser yang hendak menikahi Putri Peach.",
        description=(
            "Setiap kerajaan adalah sandbox kecil yang penuh Power Moon untuk dikumpulkan. "
            "Cappy memberi kemampuan menguasai musuh dan benda sehingga cara bergerak berubah-ubah sepanjang permainan.\n\n"
            "Mode dua pemain membuat orang kedua mengendalikan Cappy, cocok dimainkan bersama anak atau pasangan."),
        min_os=None, min_cpu=None, min_ram=None, min_gpu=None, storage=None,
        rec_os=None, rec_cpu=None, rec_ram=None, rec_gpu=None,
    ),
    dict(
        title="Animal Crossing: New Horizons", developer="Nintendo EPD", platforms=[NSW],
        release_date=date(2020, 3, 20), featured=False, accent="#4ADE80",
        official="https://animal-crossing.com/new-horizons/",
        summary="Bangun kehidupan santai di pulau terpencil: kumpulkan bahan, dekorasi rumah, dan berteman dengan para penghuni pulau.",
        description=(
            "Permainan berjalan mengikuti jam dan kalender asli, jadi musim, event, dan pergantian pagi-malam ikut berubah. "
            "Tidak ada tujuan yang memburu: pemain bebas menata pulau, memancing, atau sekadar mengobrol.\n\n"
            "Pulau teman bisa dikunjungi lewat internet, dan hal ini jadi salah satu bagian paling menyenangkan."),
        min_os=None, min_cpu=None, min_ram=None, min_gpu=None, storage=None,
        rec_os=None, rec_cpu=None, rec_ram=None, rec_gpu=None,
    ),
    dict(
        title="Celeste", developer="Maddy Makes Games", platforms=[PC, PS4, NSW, XBX],
        release_date=date(2018, 1, 25), featured=False, accent="#F472B6",
        official="https://www.celestegame.com/",
        summary="Platformer presisi tentang Madeline yang mendaki Gunung Celeste sambil berdamai dengan kecemasannya.",
        description=(
            "Madeline punya lompatan, dash satu arah, dan kemampuan memanjat. Dari tiga gerakan itu lahir ratusan tantangan yang adil sekaligus menantang.\n\n"
            "Mode bantuan memungkinkan pemain mengatur kecepatan game atau membuat diri kebal, sehingga cerita bisa dinikmati tanpa tekanan. "
            "Sangat ringan di PC sehingga cocok untuk laptop lama."),
        min_os="Windows 7 64-bit", min_cpu="Intel Core i3 M380 / setara", min_ram="2 GB",
        min_gpu="Intel HD Graphics 4000 / setara", storage="1.2 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5 / setara", rec_ram="4 GB",
        rec_gpu="Intel HD Graphics 5000 / setara",
    ),
    dict(
        title="Disco Elysium", developer="ZA/UM", platforms=[PC, PS4, PS5, NSW, XBX],
        release_date=date(2019, 10, 15), featured=False, accent="#D97706",
        official="https://discoelysium.com/",
        summary="RPG detektif tanpa pertarungan klasik: kamu menyelidiki pembunuhan sambil bergulat dengan pikiran sendiri.",
        description=(
            "Kamu bangun tanpa ingatan di sebuah kamar hotel dan harus menyelesaikan kasus pembunuhan. "
            "Alih-alih pertarungan, keterampilan dalam kepalamu berdebat dan memberi pandangan berbeda atas setiap situasi.\n\n"
            "Versi Final Cut menambahkan pengisi suara untuk hampir seluruh dialog. Kebutuhan perangkat sangat ringan."),
        min_os="Windows 7 64-bit", min_cpu="Intel Core 2 Duo 2.4 GHz / setara", min_ram="4 GB",
        min_gpu="Intel HD Graphics 4000 / NVIDIA GeForce 600 series", storage="30 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5 2.5 GHz / setara", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 660 / setara",
    ),
    dict(
        title="Resident Evil 4", developer="Capcom", platforms=[PC, PS5, PS4, XBX],
        release_date=date(2023, 3, 24), featured=False, accent="#7F1D1D",
        official="https://www.residentevil.com/re4/",
        summary="Remake horor aksi: Leon S. Kennedy menyelamatkan putri presiden dari desa yang dihuni warga yang berubah menjadi ancaman.",
        description=(
            "Leon dikirim ke pedesaan Eropa untuk mencari Ashley Graham, putri presiden Amerika Serikat. "
            "Remake ini mempertahankan ketegangan versi asli dengan grafis modern, kontrol baru, dan pertarungan pisau yang bisa menangkis serangan.\n\n"
            "Pengaturan ray tracing cukup berat, jadi untuk laptop kelas menengah disarankan memilih mode prioritas FPS."),
        min_os="Windows 10 64-bit", min_cpu="AMD Ryzen 5 1500 / Intel Core i7 4770", min_ram="8 GB",
        min_gpu="AMD Radeon RX 560 / NVIDIA GeForce GTX 1050 Ti", storage="60 GB (SSD)",
        rec_os="Windows 10/11 64-bit", rec_cpu="AMD Ryzen 5 3600 / Intel Core i7 8700", rec_ram="16 GB",
        rec_gpu="AMD Radeon RX 5700 / NVIDIA GeForce GTX 1070",
    ),
    dict(
        title="Monster Hunter: World", developer="Capcom", platforms=[PC, PS4, XBX],
        release_date=date(2018, 1, 26), featured=False, accent="#65A30D",
        official="https://www.monsterhunter.com/world/",
        summary="Berburu monster raksasa di ekosistem yang hidup, lalu menempa senjata dan armor dari bahan hasil buruan.",
        description=(
            "Pemburu dikirim ke Dunia Baru untuk meneliti Elder Dragon. Setiap perburuan melibatkan pelacakan, persiapan, dan pertarungan panjang yang menuntut pola yang dipelajari.\n\n"
            "Tersedia 14 jenis senjata dengan gaya bermain berbeda. Game ini terkenal paling nikmat dimainkan bersama teman dalam satu sesi."),
        min_os="Windows 7 / 8.1 / 10 64-bit", min_cpu="Intel Core i5-4460 / AMD FX-6300", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 760 / AMD Radeon R7 260x", storage="48 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-3770 / Intel Core i3-9100F", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 1060 3 GB / AMD Radeon RX 570X 4 GB",
    ),
    dict(
        title="Persona 5 Royal", developer="Atlus", platforms=[PC, PS4, PS5, NSW, XBX],
        release_date=date(2019, 10, 31), featured=False, accent="#E11D48",
        official="https://atlus.com/",
        summary="Murid SMA yang menjadi Phantom Thief: bagi waktu antara sekolah, pertemanan, dan mencuri hati orang jahat di dunia lain.",
        description=(
            "Kamu pindah ke Tokyo lalu menemukan Metaverse, tempat keinginan menyimpang orang dewasa berwujud istana. "
            "Hari-hari dibagi antara kegiatan sekolah, kerja paruh waktu, dan menjelajah istana.\n\n"
            "Versi Royal menambahkan karakter, area, dan akhir cerita baru. Sangat ringan di PC walau durasinya bisa lebih dari 100 jam."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-2400 / AMD FX-6300", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 650 Ti / AMD Radeon R7 260X", storage="40 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5-6600 / AMD Ryzen 5 1500X", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 1050 / AMD Radeon RX 460",
    ),
    dict(
        title="Sekiro: Shadows Die Twice", developer="FromSoftware", platforms=[PC, PS4, XBX],
        release_date=date(2019, 3, 22), featured=False, accent="#B91C1C",
        official="https://www.sekirothegame.com/",
        summary="Shinobi yang kehilangan lengan membalas dendam di Jepang era Sengoku, dengan pertarungan pedang berbasis ritme dan parry.",
        description=(
            "Berbeda dari game FromSoftware lain, Sekiro tidak punya build karakter. Fokusnya ada pada postur musuh: tangkis dengan tepat sampai pertahanan lawan pecah.\n\n"
            "Tombol lompat dan grappling hook memberi eksplorasi vertikal yang jarang ada di game sejenis. Tuntutan perangkat relatif rendah untuk game sebesar ini."),
        min_os="Windows 7 / 8 / 10 64-bit", min_cpu="Intel Core i3-2100 / AMD FX-6300", min_ram="4 GB",
        min_gpu="NVIDIA GeForce GTX 760 / AMD Radeon HD 7950", storage="25 GB",
        rec_os="Windows 7 / 8 / 10 64-bit", rec_cpu="Intel Core i5-2500K / AMD Ryzen 3 1300X", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 970 / AMD Radeon RX 570",
    ),
    dict(
        title="Hogwarts Legacy", developer="Avalanche Software", platforms=[PC, PS5, PS4, NSW, XBX],
        release_date=date(2023, 2, 10), featured=False, accent="#CA8A04",
        official="https://www.hogwartslegacy.com/",
        summary="RPG aksi dunia terbuka di Hogwarts abad ke-19, tempat kamu jadi murid baru dengan kemampuan sihir langka.",
        description=(
            "Kamu masuk Hogwarts di tahun kelima dengan kemampuan langka yang menarik perhatian banyak pihak. "
            "Eksplorasi kastil, kelas sihir, ramuan, dan hewan ajaib menjadi inti permainan, ditambah duel sihir yang cepat.\n\n"
            "Kawasan kastil dan Hogsmeade menekan CPU dan VRAM, jadi pemilik laptop kelas menengah sebaiknya memakai DLSS atau FSR."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-6600 / AMD Ryzen 5 1400", min_ram="16 GB",
        min_gpu="NVIDIA GeForce GTX 960 4 GB / AMD Radeon RX 470 4 GB", storage="85 GB (SSD)",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-8700 / AMD Ryzen 5 3600", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce 1080 Ti / AMD Radeon RX 5700 XT",
    ),
    dict(
        title="Hi-Fi Rush", developer="Tango Gameworks", platforms=[PC, PS5, XBX],
        release_date=date(2023, 1, 25), featured=False, accent="#22D3EE",
        official="https://hifirush.com/",
        summary="Aksi hack-and-slash yang bergerak mengikuti irama musik: tiap serangan, lompatan, dan animasi dunia berdenyut mengikuti beat.",
        description=(
            "Chai, calon rockstar, tanpa sengaja terhubung dengan pemutar musik yang membuat seluruh dunia bergerak mengikuti irama. "
            "Menyerang tepat di ketukan memberi damage lebih besar dan combo yang lebih meriah.\n\n"
            "Gaya visual cel-shaded membuatnya tampak seperti kartun interaktif dan relatif ringan untuk laptop kelas menengah."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i7-4770K / AMD Ryzen 5 1600", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 1050 Ti / AMD Radeon RX 570", storage="40 GB",
        rec_os="Windows 10/11 64-bit", rec_cpu="Intel Core i7-8700K / AMD Ryzen 5 3600", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce GTX 1660 Ti / AMD Radeon RX 5600 XT",
    ),
    dict(
        title="Stray", developer="BlueTwelve Studio", platforms=[PC, PS5, PS4, XBX, NSW],
        release_date=date(2022, 7, 19), featured=False, accent="#F97316",
        official="https://www.stray-game.com/",
        summary="Seekor kucing oranye tersesat di kota siber yang dihuni robot, dan mencari jalan pulang bersama drone kecil.",
        description=(
            "Kamu bermain sebagai kucing yang bisa melompat, memanjat, dan bersembunyi. Dunianya dibangun dari lorong sempit dan gang neon yang dihuni robot yang meniru kebiasaan manusia.\n\n"
            "Game ini berdurasi singkat sekitar lima sampai enam jam, cocok diselesaikan dalam satu akhir pekan."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-2500K / AMD FX-6300", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 1050 / AMD Radeon R7 360", storage="10 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i7-4770K / AMD Ryzen 5 1500X", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce GTX 1060 / AMD Radeon RX 570",
    ),
    dict(
        title="It Takes Two", developer="Hazelight Studios", platforms=[PC, PS5, PS4, XBX],
        release_date=date(2021, 3, 26), featured=False, accent="#FACC15",
        official="https://www.ea.com/games/it-takes-two",
        summary="Petualangan kooperatif dua pemain tentang pasangan yang berubah menjadi boneka dan harus bekerja sama memperbaiki hubungan mereka.",
        description=(
            "Cody dan May bersiap bercerai ketika mereka berubah menjadi boneka kecil. "
            "Tiap bab punya mekanik berbeda, dari memanipulasi waktu sampai bertarung dengan peralatan rumah, dan semuanya wajib dikerjakan bersama.\n\n"
            "Game ini hanya bisa dimainkan berdua. Tersedia Friend's Pass sehingga hanya satu pemain yang perlu membeli."),
        min_os="Windows 7 64-bit", min_cpu="Intel Core i3-2100T / AMD FX 6100", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 660 / AMD Radeon R7 260", storage="50 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5-3570K / AMD FX 8350", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 980 / AMD Radeon R9 290",
    ),
    dict(
        title="Dave the Diver", developer="Mintrocket", platforms=[PC, NSW, PS4, PS5],
        release_date=date(2023, 6, 28), featured=False, accent="#0EA5E9",
        official="https://www.davethediver.com/",
        summary="Menyelam di Blue Hole pada siang hari untuk berburu ikan, lalu mengelola restoran sushi saat malam.",
        description=(
            "Dave menangkap ikan dan bahan masakan di lubang biru yang berubah tiap kali dimasuki. "
            "Hasil tangkapan dijual dan dimasak di restoran, dan semakin lama fitur baru terus bertambah: pertanian, budidaya ikan, minigame, hingga cerita sampingan.\n\n"
            "Pixel art 2D membuatnya sangat ringan dan cocok untuk laptop tanpa GPU khusus."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i3 / AMD A8 setara", min_ram="4 GB",
        min_gpu="NVIDIA GeForce GTX 560 / Intel HD 4000", storage="8 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5 / AMD Ryzen 3 setara", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 750 Ti / Intel Iris Xe",
    ),
    dict(
        title="Dead Cells", developer="Motion Twin", platforms=[PC, PS4, NSW, XBX],
        release_date=date(2018, 8, 7), featured=False, accent="#A855F7",
        official="https://dead-cells.com/",
        summary="Roguelite aksi bergaya Metroidvania: tiap mati kamu mulai dari awal dengan peta yang berubah.",
        description=(
            "Kamu mengendalikan sosok tanpa kepala yang menyusuri kastil luas. Senjata, mutasi, dan rute berubah setiap percobaan, sementara kemajuan permanen membuka opsi baru.\n\n"
            "Pengembang rutin merilis pembaruan gratis dan DLC. Kebutuhan perangkatnya sangat rendah sehingga pas untuk laptop lama."),
        min_os="Windows 7 64-bit", min_cpu="Intel Core 2 Duo 2.4 GHz / setara", min_ram="2 GB",
        min_gpu="NVIDIA GeForce 9800 GTX / Intel HD 4000", storage="2 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i3 / setara", rec_ram="4 GB",
        rec_gpu="NVIDIA GeForce GTX 460 / setara",
    ),
    dict(
        title="Halo Infinite", developer="343 Industries", platforms=[PC, XBX],
        release_date=date(2021, 12, 8), featured=False, accent="#84CC16",
        official="https://www.halowaypoint.com/halo-infinite",
        summary="Master Chief kembali dengan kampanye dunia semi-terbuka di Zeta Halo dan multiplayer gratis bergaya arena.",
        description=(
            "Setelah kekalahan telak, Master Chief terdampar dan harus merebut kembali sebuah cincin Halo. "
            "Kampanyenya menggabungkan eksplorasi dunia terbuka dengan pertempuran yang bebas memilih pendekatan, dibantu grappling hook.\n\n"
            "Mode multiplayer gratis dengan pembaruan musiman. Laptop berspesifikasi rendah mungkin perlu menurunkan resolusi dan kualitas tekstur."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i5-4440 / AMD Ryzen 5 1600", min_ram="8 GB",
        min_gpu="NVIDIA GeForce GTX 1050 Ti / AMD Radeon RX 570", storage="50 GB",
        rec_os="Windows 10/11 64-bit", rec_cpu="Intel Core i7-9700K / AMD Ryzen 7 3700X", rec_ram="16 GB",
        rec_gpu="NVIDIA GeForce RTX 2070 / AMD Radeon RX 5700 XT",
    ),
    dict(
        title="Cuphead", developer="Studio MDHR", platforms=[PC, PS4, NSW, XBX],
        release_date=date(2017, 9, 29), featured=False, accent="#EAB308",
        official="https://cupheadgame.com/",
        summary="Run and gun dengan gaya kartun 1930-an yang digambar tangan, penuh pertarungan bos yang cepat dan menantang.",
        description=(
            "Dua bersaudara, Cuphead dan Mugman, berutang pada iblis dan harus mengumpulkan jiwa para penghutang. "
            "Hampir seluruh permainan berisi pertarungan bos dengan pola serangan berfase banyak.\n\n"
            "Animasi digambar tangan dan musik jazz big band bikin penampilannya sangat khas. Ringan untuk laptop tanpa GPU khusus."),
        min_os="Windows 7 64-bit", min_cpu="Intel Core i3-2100 / AMD Phenom II X4", min_ram="3 GB",
        min_gpu="NVIDIA GeForce GTX 750 / Intel HD 4000", storage="4 GB",
        rec_os="Windows 10 64-bit", rec_cpu="Intel Core i5-3570K / AMD FX-6300", rec_ram="4 GB",
        rec_gpu="NVIDIA GeForce GTX 960 / setara",
    ),
    dict(
        title="Minecraft", developer="Mojang Studios", platforms=[PC, PS5, PS4, NSW, XBX],
        release_date=date(2011, 11, 18), featured=False, accent="#16A34A",
        official="https://www.minecraft.net/",
        summary="Dunia blok tanpa batas: bertahan hidup, membangun apa saja, dan menjelajahi dimensi bersama teman.",
        description=(
            "Pemain mengumpulkan sumber daya, membuat peralatan, lalu membangun apa saja dari gubuk sampai kota. Mode kreatif membuka semua blok, sedangkan mode bertahan hidup menuntut kewaspadaan terhadap monster malam hari.\n\n"
            "Komunitas modifikasi dan server sangat besar, terutama untuk versi Java di PC."),
        min_os="Windows 10 64-bit", min_cpu="Intel Core i3-3210 / AMD A8-7600", min_ram="4 GB",
        min_gpu="Intel UHD Graphics 620 / AMD Radeon R5", storage="4 GB",
        rec_os="Windows 10/11 64-bit", rec_cpu="Intel Core i5-4690 / AMD A10-7800", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce 700 series / AMD Radeon Rx 200 series",
    ),
    dict(
        title="Grand Theft Auto V", developer="Rockstar Games", platforms=[PC, PS5, PS4, XBX],
        release_date=date(2013, 9, 17), featured=False, accent="#10B981",
        official="https://www.rockstargames.com/gta-v",
        summary="Tiga tokoh utama dengan jalan hidup berbeda terlibat perampokan dan kejahatan di kota Los Santos yang luas.",
        description=(
            "Michael, Franklin, dan Trevor bergantian jadi karakter utama, masing-masing dengan kemampuan khusus. "
            "Selain cerita, ada mode online yang terus diperbarui dan komunitas modifikasi yang sangat aktif di PC.\n\n"
            "Meski sudah lama dirilis, game ini masih menuntut spesifikasi sedang untuk berjalan stabil dengan grafis tinggi."),
        min_os="Windows 8.1 64-bit", min_cpu="Intel Core 2 Quad Q6600 / AMD Phenom 9850", min_ram="4 GB",
        min_gpu="NVIDIA GeForce 9800 GT 1 GB / AMD Radeon HD 4870 1 GB", storage="72 GB",
        rec_os="Windows 8.1 64-bit", rec_cpu="Intel Core i5-3470 / AMD FX-8350", rec_ram="8 GB",
        rec_gpu="NVIDIA GeForce GTX 660 2 GB / AMD Radeon HD 7870 2 GB",
    ),
]

# (judul, username, rating, perangkat, isi)
EXTRA_COMMENTS = [
    # ---- Red Dead Redemption 2
    ("Red Dead Redemption 2", "anisa", 5, "Laptop RTX 3060 / RAM 16GB",
     "Baru tamat chapter 3 dan masih kagum sama detail kecilnya, sampai kuda aja bisa kedinginan. Preset campuran medium-high stabil di kisaran 50 FPS, cuma rumput di kejauhan agak bergelombang."),
    ("Red Dead Redemption 2", "sari", 5, "PS4 Pro",
     "Pelan banget ritmenya dan justru itu nilai jualnya buatku. Berburu, ngobrol di kamp, dengerin Arthur nyanyi. Loading awalnya lama tapi worth it."),
    ("Red Dead Redemption 2", "bagas", 4, "Ryzen 5 3600 / GTX 1660 Super / RAM 16GB",
     "Grafisnya gila tapi GTX 1660 Super harus rela di bawah medium biar 45 FPS stabil. Kontrolnya kaku dulu, butuh beberapa jam sampai terbiasa."),
    ("Red Dead Redemption 2", "dimas", 4, "Xbox Series X",
     "Ceritanya kuat. Yang bikin sebel cuma misi yang harus diulang dari awal padahal tinggal sedikit lagi selesai."),
    # ---- God of War
    ("God of War", "sari", 5, "PS5",
     "Satu kamera tanpa potongan dari awal sampai akhir itu keputusan desain yang berani. Kratos jadi lebih manusiawi, dan hubungan sama Atreus yang bikin aku terus lanjut."),
    ("God of War", "rina", 5, "Laptop RTX 3050 4GB / RAM 16GB",
     "Nggak nyangka laptop segini bisa dapet 60 FPS di preset original pakai DLSS. Lemparan kapaknya terasa nendang. Skill tree-nya awalnya bikin pusing."),
    ("God of War", "fajar", 4, "GTX 1650 / i5-10300H / RAM 8GB",
     "1080p low dapat sekitar 40 FPS dan masih enak. Cuma RAM 8GB bikin pindah area sering nahan beberapa detik."),
    ("God of War", "anisa", 4, "PS4 Slim",
     "Grafisnya masih bagus walau di PS4 biasa, tapi kipasnya kencang banget. Puzzle di Alfheim agak berulang, bosnya seru."),
    # ---- Spider-Man Remastered
    ("Marvel's Spider-Man Remastered", "rizky", 5, "RTX 3060 / Ryzen 5 5600H / RAM 16GB",
     "Ayunan di antara gedung itu candu, kadang aku keliling kota doang tanpa ngerjain misi. Ray tracing nyala plus DLSS balanced masih dapat 70-an FPS."),
    ("Marvel's Spider-Man Remastered", "anisa", 4, "PS5",
     "Ceritanya hangat, Peter dan MJ ditulis dengan relatable. Aktivitas sampingannya mirip-mirip jadi kuselesaikan seperlunya saja."),
    ("Marvel's Spider-Man Remastered", "fajar", 4, "Laptop GTX 1650 / RAM 8GB",
     "Di low 900p kisaran 35-45 FPS dan terasa agak patah pas ngebut di tengah kota. Wajib install di SSD, kalau HDD texture-nya telat muncul."),
    ("Marvel's Spider-Man Remastered", "aldo", 5, "Ryzen 7 5800H / RTX 3070 / RAM 16GB",
     "Parry dan dodge-nya responsif, pertarungannya makin memuaskan setelah gadget terbuka. 1440p mulus banget."),
    # ---- Zelda Tears of the Kingdom
    ("The Legend of Zelda: Tears of the Kingdom", "rizky", 5, "Switch OLED, handheld",
     "Puluhan jam dan aku masih nemu cara baru bikin kendaraan paling absurd. Ultrahand itu mainan sekaligus mekanik inti. Langit dan gua bawah tanah bikin dunianya terasa berlipat."),
    ("The Legend of Zelda: Tears of the Kingdom", "anisa", 5, "Switch (docked)",
     "FPS memang sempat turun di area ramai, tapi aku nggak peduli karena eksplorasinya seluas ini. Jadwal tidur berantakan seminggu."),
    ("The Legend of Zelda: Tears of the Kingdom", "sari", 4, "Switch Lite",
     "Senjata gampang rusak masih bikin kesal walau ada fitur menggabungkan. Ceritanya terasa lebih dewasa dari Breath of the Wild."),
    ("The Legend of Zelda: Tears of the Kingdom", "laras", 5, "Switch OLED",
     "Musik di momen tertentu bikin merinding. Mulai dari yang tampak biasa saja, ujungnya malah bikin mataku berkaca-kaca."),
    # ---- Super Mario Odyssey
    ("Super Mario Odyssey", "nadia", 5, "Switch OLED",
     "Gerakan Mario enak banget sampai sekadar lompat-lompat di taman pun bikin senyum. Cappy bikin tiap kerajaan terasa segar."),
    ("Super Mario Odyssey", "citra", 5, "Switch (docked)",
     "Moon-nya banyak tapi nggak terasa kayak kerjaan rumah, hampir tiap sudut ada kejutan kecil. Seru main bareng adik yang pegang Cappy."),
    ("Super Mario Odyssey", "sari", 4, "Switch Lite",
     "Kontrol gerak yang wajib dipakai di beberapa lompatan agak nyebelin di mode handheld. Selebihnya riang dan padat."),
    ("Super Mario Odyssey", "eko", 4, "Switch OLED",
     "Ceritanya nyaris nggak ada, tapi memang bukan itu tujuannya. Kurangnya cuma kelar terlalu cepat, kurang dari 15 jam kalau kejar jalur utama."),
    # ---- Animal Crossing
    ("Animal Crossing: New Horizons", "nadia", 5, "Switch Lite",
     "Tiap pagi buka buat cek toko dan bunga di pulau sudah jadi ritual. Dekor interior makan waktuku berjam-jam tanpa terasa."),
    ("Animal Crossing: New Horizons", "bagas", 4, "Switch (docked)",
     "Awalnya santai, lama-lama sadar aku sibuk ngejar bell buat lunasi pinjaman rumah. Penyimpanan barang sempit sampai upgrade ketiga."),
    ("Animal Crossing: New Horizons", "laras", 4, "Switch OLED",
     "Paling enak dimainkan ramai-ramai, main ke pulau teman itu seru. Event musimannya manis walau sering tinggal nunggu hari berganti."),
    ("Animal Crossing: New Horizons", "galih", 5, "Switch Lite",
     "Cocok banget buat penutup hari yang capek. Nggak ada yang ngejar, nggak ada yang marahin."),
    # ---- Celeste
    ("Celeste", "nadia", 5, "Laptop Intel UHD 620 / RAM 4GB",
     "Jalan mulus di laptop kantor tua. Soal sulitnya lumayan, tapi mode bantuan bikin game ini terasa ramah, bukan menghakimi."),
    ("Celeste", "putri", 5, "Switch OLED",
     "Cerita Madeline dan rasa cemasnya kena banget, apalagi sambil denger musiknya. Aku sempat berhenti sebentar di chapter 7 karena terlalu pas."),
    ("Celeste", "eko", 4, "Ryzen 3 3200G / RAM 8GB",
     "Ratusan kali mati di satu layar, tapi respawn-nya cepat jadi sempat nggak marah. B-side itu level lain."),
    ("Celeste", "fajar", 5, "PS4",
     "Tiap selesai satu chapter ada rasa lega yang susah dijelaskan. Pendek tapi nggak ada yang berlebihan."),
    # ---- Disco Elysium
    ("Disco Elysium", "nadia", 5, "Laptop i5-8250U / RAM 8GB",
     "Teks terbaik yang pernah kubaca di game. Skill-skill di kepalamu berdebat satu sama lain dan sering lebih lucu daripada dialog NPC-nya."),
    ("Disco Elysium", "eko", 4, "PS5",
     "Butuh kesabaran karena banyak banget yang dibaca. Tapi begitu tamat, kamu ingat betul detektif seperti apa yang kamu bentuk sendiri."),
    ("Disco Elysium", "yoga", 3, "Switch OLED",
     "Gaya ceritanya kuat tapi buatku terlalu padat teks di layar kecil. Loading antar area di Switch juga lumayan sering."),
    ("Disco Elysium", "citra", 5, "GTX 1050 Ti / RAM 8GB",
     "Voice acting di Final Cut bikin ceritanya hidup. Pilihan yang kelihatan sepele bisa mengubah arah hari itu drastis."),
    # ---- Resident Evil 4
    ("Resident Evil 4", "wulan", 5, "RTX 3060 Laptop / RAM 16GB",
     "Remake yang tahu mana yang harus dipertahankan. Desa di awal tetap tegang, parry pisau bikin pertarungan lebih dinamis."),
    ("Resident Evil 4", "anisa", 4, "PS5",
     "Ashley sekarang nggak menyebalkan, bagus. Beberapa bagian tengah terasa lebih panjang dari yang perlu."),
    ("Resident Evil 4", "dimas", 5, "GTX 1660 Ti / RAM 16GB",
     "Prioritas FPS di medium dapat sekitar 70, ray tracing kumatikan. Suara musuh di desa bikin aku cek belakang berkali-kali."),
    ("Resident Evil 4", "sari", 4, "Xbox Series X",
     "Jumpscare-nya nggak berlebihan dan senjatanya terasa punya bobot. Cuma level kesulitan tertinggi lumayan menyiksa buat yang baru kenal seri ini."),
    # ---- Monster Hunter: World
    ("Monster Hunter: World", "laras", 5, "Laptop GTX 1650 Ti / RAM 8GB",
     "Awalnya bingung sama banyaknya menu, dua jam kemudian baru paham ritmenya. Berburu Rathalos bareng teman itu seru sampai lupa waktu."),
    ("Monster Hunter: World", "citra", 4, "PS4",
     "Ngegrind material buat armor memang melelahkan, tapi tiap selesai bikin set baru rasanya sepadan."),
    ("Monster Hunter: World", "galih", 4, "Ryzen 5 4600H / GTX 1650 / RAM 16GB",
     "Optimasi PC-nya nggak sehalus yang kukira. Di hub kota FPS turun, tapi pas berburu stabil di 50-an."),
    ("Monster Hunter: World", "hendra", 5, "Xbox One X",
     "Mekanik senjatanya dalam. Aku pindah dari Great Sword ke Insect Glaive dan rasanya seperti main game yang berbeda."),
    # ---- Persona 5 Royal
    ("Persona 5 Royal", "yoga", 5, "PS5",
     "Gaya visualnya ngena banget, sampai menunya aja kayak poster. Ratusan jam buat sekolah dan palace, dan nggak bosan sama sekali."),
    ("Persona 5 Royal", "wulan", 5, "Laptop GTX 1050 / RAM 8GB",
     "Ringan di laptop jadul, tidak ada lag. Pakai gamepad jauh lebih nyaman."),
    ("Persona 5 Royal", "citra", 4, "Switch OLED",
     "Sempat ragu main di Switch, ternyata kualitas visualnya masih oke walau resolusinya lebih rendah. Durasi 100 jam jadi tantangan buat pegawai kayak aku."),
    ("Persona 5 Royal", "hendra", 5, "Xbox Series X",
     "Karakter pendukungnya ditulis dengan baik, tiap confidant punya cerita yang hangat. Palace terakhir menaikkan taruhan dengan keren."),
    # ---- Sekiro
    ("Sekiro: Shadows Die Twice", "eko", 5, "Ryzen 5 5500 / GTX 1660 / RAM 16GB",
     "Bertarungnya soal ritme, bukan soal level. Begitu paham parry rasanya kayak menari. Genichiro bikin aku mati dua puluh kali."),
    ("Sekiro: Shadows Die Twice", "fajar", 4, "PS4 Pro",
     "Sulit tapi adil. Ada tombol lompat dan grappling hook jadi eksplorasi lebih cepat dari game Souls lain."),
    ("Sekiro: Shadows Die Twice", "galih", 5, "Laptop RTX 2060 / RAM 16GB",
     "Stabil di 60 FPS terkunci. Tanpa menu kustomisasi build, fokusnya ke satu gaya main, dan itu malah menyenangkan."),
    ("Sekiro: Shadows Die Twice", "putri", 3, "GTX 1050 Ti / RAM 8GB",
     "Aku nyerah di Guardian Ape setelah beberapa hari. Bagus dan tajam, tapi buatku terlalu menuntut."),
    # ---- Hogwarts Legacy
    ("Hogwarts Legacy", "aldo", 4, "Laptop RTX 3050 Ti / RAM 16GB",
     "Kastilnya terasa hidup, tapi Hogsmeade bikin FPS anjlok. Dengan DLSS dan setting medium akhirnya enak."),
    ("Hogwarts Legacy", "fajar", 5, "PS5",
     "Masuk asrama dan keliling kastil sendirian itu mimpi masa kecil yang jadi nyata. Sistem sihirnya memuaskan."),
    ("Hogwarts Legacy", "hendra", 4, "Xbox Series X",
     "Misi sampingannya agak monoton (cari kotak, buka). Tapi suasana dunianya menutup kekurangan itu."),
    ("Hogwarts Legacy", "galih", 3, "Switch OLED",
     "Penurunan grafis di Switch lumayan terasa, tekstur buram dan FPS naik-turun. Mungkin lebih pas dimainkan di platform lain."),
    # ---- Hi-Fi Rush
    ("Hi-Fi Rush", "mita", 5, "Laptop GTX 1650 / RAM 8GB",
     "Semua gerakan mengikuti beat dan itu bikin berantem terasa kayak main game ritme. Ringan juga di laptop menengah."),
    ("Hi-Fi Rush", "yoga", 5, "Xbox Series X",
     "Humor dan musiknya segar. Aku sampai main ulang demi ngejar peringkat S."),
    ("Hi-Fi Rush", "wulan", 4, "PS5",
     "Visualnya seperti kartun interaktif. Platforming-nya agak kaku, tapi nggak sampai mengganggu."),
    ("Hi-Fi Rush", "rizky", 4, "RTX 3060 / RAM 16GB",
     "Stabil 144 FPS. Ceritanya sederhana tapi karakternya lucu-lucu."),
    # ---- Stray
    ("Stray", "bagas", 5, "PS5",
     "Jadi kucing dan tidak ada yang menyuruhmu menembak. Gesek-gesek badan ke robot sampai mereka jadi sahabat itu terapi."),
    ("Stray", "putri", 4, "Laptop GTX 1650 / RAM 8GB",
     "Latar kota siber yang lembap cantik banget. Adegan kejar-kejaran sama Zurk menegangkan tapi singkat."),
    ("Stray", "mita", 5, "Xbox Series X",
     "Animasi kucingnya juara. Aku sempat berhenti sepuluh menit cuma buat tidur di atas kardus."),
    ("Stray", "rizky", 4, "Switch OLED",
     "Versi Switch ada penurunan resolusi, tapi inti pengalamannya sama. Gamenya pendek, sekitar lima jam."),
    # ---- It Takes Two
    ("It Takes Two", "rizky", 5, "Laptop RTX 3050 / RAM 16GB (co-op via Friend's Pass)",
     "Main sama pacar lewat Friend's Pass. Tiap level mekaniknya ganti total jadi nggak ada yang bosan. Kami berdebat dan ketawa terus."),
    ("It Takes Two", "eko", 5, "PS5",
     "Bukti bahwa co-op bisa jadi pusat desain, bukan tambahan. Cara dua pemain saling bergantung terasa bermakna."),
    ("It Takes Two", "mita", 4, "Xbox Series X",
     "Ceritanya agak klise dan Dr. Hakim menjengkelkan, tapi gameplay-nya menyelamatkan. Wajib dimainkan berdua."),
    ("It Takes Two", "citra", 4, "GTX 1060 / RAM 8GB",
     "Split screen jalan 60 FPS di low. Beberapa puzzle sempat bikin kami berantem beneran."),
    # ---- Dave the Diver
    ("Dave the Diver", "hendra", 5, "Switch OLED",
     "Siang menyelam, malam jadi pemilik restoran sushi. Dua loop yang saling menyuap itu bikin susah berhenti."),
    ("Dave the Diver", "dimas", 5, "Laptop Intel Iris Xe / RAM 8GB",
     "Pixel art-nya manis dan jalan lancar di laptop tanpa GPU. Humor di tengah cerita sering mengejutkan."),
    ("Dave the Diver", "aldo", 4, "PS5",
     "Setelah 15 jam fitur baru terus berdatangan sampai agak kewalahan. Harus sabar ngatur menu."),
    ("Dave the Diver", "yoga", 4, "RTX 3050 / RAM 16GB",
     "Performa nggak ada masalah. Cuma loop malamnya bisa terasa berulang kalau main berjam-jam."),
    # ---- Dead Cells
    ("Dead Cells", "nadia", 5, "Switch Lite",
     "Satu run cuma setengah jam, pas buat di perjalanan. Tiap mati aku belajar sesuatu, bukan kecewa."),
    ("Dead Cells", "aldo", 4, "Laptop Core i3 / RAM 4GB",
     "Ringan, 60 FPS tanpa masalah. Awalnya acak-acakan itu frustrasi, tapi lama-lama kelihatan betapa gilanya kombinasi build-nya."),
    ("Dead Cells", "dimas", 5, "PS4",
     "Combat-nya cepat dan responsif. Update gratis dari developer selama bertahun-tahun bikin nilainya makin tinggi."),
    ("Dead Cells", "yoga", 4, "Xbox Series X",
     "Lama-lama terasa grind buat membuka semua item. Desain level yang bercabang menyelamatkannya."),
    # ---- Halo Infinite
    ("Halo Infinite", "aldo", 4, "RTX 3060 / Ryzen 5 3600 / RAM 16GB",
     "Kampanye semi-terbuka yang terasa Halo klasik. Grappling hook mengubah cara bergerak total. Multiplayer gratis dan tetap ramai."),
    ("Halo Infinite", "laras", 4, "Xbox Series X",
     "Musik ikoniknya muncul di momen yang tepat. Sayang ceritanya pendek dan misi sampingan kurang bervariasi."),
    ("Halo Infinite", "mita", 3, "GTX 1650 / RAM 8GB",
     "Harus turun ke low supaya 45 FPS, dan tekstur sering buram saat loading. Laptop gaming murah jangan berharap banyak."),
    ("Halo Infinite", "bagas", 5, "RTX 3070 / RAM 32GB",
     "Gunplay-nya memuaskan banget. Mode arena bareng squad ada rasa nostalgianya."),
    # ---- Cuphead
    ("Cuphead", "mita", 5, "Switch OLED",
     "Gaya kartun 1930-an digambar tangan dan tiap bos terasa seperti kartun yang hidup. Mati terus tapi nggak bisa berhenti."),
    ("Cuphead", "putri", 4, "Laptop Intel UHD / RAM 4GB",
     "Jalan di laptop jadul tanpa kendala. Sulitnya bukan main, mode Simple bantu sedikit."),
    ("Cuphead", "galih", 5, "PS4",
     "Musik jazz big band-nya kelas dunia. Co-op sama adik jadi ajang saling salah-salahan, tapi seru."),
    ("Cuphead", "bagas", 4, "Xbox Series X",
     "Pendek kalau sudah jago, tapi sampai ke sana bisa makan puluhan jam. Bagian run and gun awal kurang beragam."),
    # ---- Minecraft
    ("Minecraft", "hendra", 5, "Laptop Core i5 / RAM 8GB",
     "Dari 2012 sampai sekarang masih main bareng teman SMA. Server survival dengan rumah bersama jadi tempat nongkrong online kami."),
    ("Minecraft", "laras", 4, "Switch",
     "Dunia lebih kecil di Switch dan jarak pandang terbatas. Tetap oke buat main santai sama anak."),
    ("Minecraft", "wulan", 5, "Laptop Intel Iris Xe / RAM 16GB (Java + shader ringan)",
     "Pakai mod performa dan shader ringan masih lancar. Kreativitas tanpa batasnya yang bikin ketagihan."),
    ("Minecraft", "dimas", 4, "PS5",
     "Terlalu banyak yang bisa dilakukan sampai pemula bingung mulai dari mana. Tutorial resminya kurang membantu, YouTube lebih berguna."),
    # ---- Grand Theft Auto V
    ("Grand Theft Auto V", "user", 5, "Laptop GTX 1650 / RAM 8GB",
     "Walau sudah tua, masih jalan di 60 FPS pengaturan menengah. Trio karakter utamanya, terutama Trevor, masih jadi yang terbaik."),
    ("Grand Theft Auto V", "putri", 4, "PS4",
     "Mode cerita memuaskan, mode online tidak ramah pemain baru. Mod dari komunitas PC memperpanjang umurnya."),
    ("Grand Theft Auto V", "wulan", 4, "Xbox Series X",
     "Peningkatan grafis versi baru terasa, apalagi ray tracing di bulan. Loading mode online tetap lama."),
    ("Grand Theft Auto V", "bayu", 5, "RTX 3050 / RAM 16GB",
     "Perampokan terkoordinasi itu momen terbaiknya. Jalan-jalan di pantai sambil dengar radio saja sudah menyenangkan."),
]
