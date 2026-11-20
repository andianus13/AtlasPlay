"""Data laporan admin dan pembuat PDF (fpdf2).

Tiga laporan:
  1. Rekap data master game per platform dan developer
  2. Transaksi game terpopuler (paling banyak disimpan dan rating tertinggi)
  3. Aktivitas pengajuan game dan ulasan pengguna
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from fpdf import FPDF
from fpdf.fonts import FontFace
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import APP_NAME
from app.models import Comment, Game, GameRequest, SavedGame, utcnow
from app.utils import format_date, format_datetime

REPORT_TITLES = {
    1: "Rekap Data Master Game per Platform dan Developer",
    2: "Laporan Transaksi Game Terpopuler",
    3: "Laporan Aktivitas Pengajuan Game dan Ulasan Pengguna",
}
REPORT_SHORT = {1: "Master Game", 2: "Game Terpopuler", 3: "Pengajuan dan Ulasan"}


# --------------------------------------------------------------------------- #
# DATA
# --------------------------------------------------------------------------- #
def master_report(db: Session, platform_id: Optional[int] = None, developer_id: Optional[int] = None) -> dict:
    stmt = (
        select(Game)
        .options(selectinload(Game.platforms), selectinload(Game.developer))
        .order_by(func.lower(Game.title))
    )
    if platform_id:
        stmt = stmt.where(Game.platforms.any(id=platform_id))
    if developer_id:
        stmt = stmt.where(Game.developer_id == developer_id)
    games = list(db.scalars(stmt).all())

    by_platform: dict[str, int] = {}
    by_developer: dict[str, int] = {}
    for game in games:
        for platform in game.platforms:
            by_platform[platform.name] = by_platform.get(platform.name, 0) + 1
        name = game.developer.name if game.developer else "Tanpa developer"
        by_developer[name] = by_developer.get(name, 0) + 1

    def ranked(data: dict[str, int]) -> list[tuple[str, int]]:
        return sorted(data.items(), key=lambda item: (-item[1], item[0].lower()))

    return {"games": games, "by_platform": ranked(by_platform), "by_developer": ranked(by_developer)}


def popular_report(db: Session, limit: int = 10) -> dict:
    saves = (
        select(func.count(SavedGame.id)).where(SavedGame.game_id == Game.id).correlate(Game).scalar_subquery()
    )
    reviews = select(func.count(Comment.id)).where(Comment.game_id == Game.id).correlate(Game).scalar_subquery()
    base = select(Game, saves.label("saves"), reviews.label("reviews")).options(selectinload(Game.developer))

    most_saved = db.execute(base.order_by(saves.desc(), Game.average_rating.desc(), Game.title).limit(limit)).all()
    top_rated = db.execute(
        base.where(reviews > 0).order_by(Game.average_rating.desc(), reviews.desc(), Game.title).limit(limit)
    ).all()
    return {"most_saved": most_saved, "top_rated": top_rated, "limit": limit}


def _day_start(value: Optional[date]) -> Optional[datetime]:
    return datetime.combine(value, datetime.min.time()) if value else None


def activity_report(
    db: Session,
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> dict:
    start = _day_start(date_from)
    end = _day_start(date_to + timedelta(days=1)) if date_to else None

    req_stmt = select(GameRequest).options(joinedload(GameRequest.user)).order_by(GameRequest.submitted_at.desc())
    com_stmt = (
        select(Comment)
        .options(joinedload(Comment.user), joinedload(Comment.game))
        .order_by(Comment.created_at.desc())
    )
    if start:
        req_stmt = req_stmt.where(GameRequest.submitted_at >= start)
        com_stmt = com_stmt.where(Comment.created_at >= start)
    if end:
        req_stmt = req_stmt.where(GameRequest.submitted_at < end)
        com_stmt = com_stmt.where(Comment.created_at < end)

    all_requests = list(db.scalars(req_stmt).all())
    status_counts = {name: 0 for name in ("Pending", "Approved", "Rejected")}
    for item in all_requests:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1

    requests = [r for r in all_requests if not status or r.status == status]
    comments = list(db.scalars(com_stmt).all())
    average = round(sum(c.rating for c in comments) / len(comments), 2) if comments else 0.0
    return {
        "requests": requests,
        "comments": comments,
        "status_counts": status_counts,
        "average_rating": average,
    }


# --------------------------------------------------------------------------- #
# PDF
# --------------------------------------------------------------------------- #
_ASCII_MAP = str.maketrans(
    {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "...",
     "→": "->", "★": "*", " ": " "}
)


def _t(value: object) -> str:
    """Font bawaan PDF hanya mendukung Latin-1; karakter lain diganti agar tidak error."""
    text = str(value if value is not None else "-").translate(_ASCII_MAP)
    return text.encode("latin-1", "replace").decode("latin-1")


def _clip(value: Optional[str], limit: int) -> str:
    text = (value or "-").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


class ReportPDF(FPDF):
    def __init__(self, title: str, printed_by: str, filters: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = _t(title)
        self.printed_by = _t(printed_by)
        self.filters_text = _t(filters)
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=20)
        self.alias_nb_pages()
        self.set_title(self.report_title)
        self.set_author(APP_NAME)
        self.add_page()
        self._title_block()

    def header(self) -> None:
        self.set_fill_color(11, 15, 23)
        self.rect(0, 0, 210, 20, "F")
        self.set_fill_color(16, 185, 129)
        self.rect(0, 20, 210, 1.2, "F")
        self.set_xy(15, 6)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(241, 245, 249)
        self.cell(60, 8, APP_NAME)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, "Laporan Resmi Direktori Spesifikasi Game", align="R")
        self.set_y(28)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_draw_color(210, 214, 220)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_font("Helvetica", "", 8)
        self.set_text_color(110, 118, 130)
        self.cell(
            0, 8,
            f"Dicetak oleh {self.printed_by} pada {_t(format_datetime(utcnow()))} UTC",
            align="L",
        )
        self.set_x(15)
        self.cell(0, 8, f"Halaman {self.page_no()} dari {{nb}}", align="R")

    def _title_block(self) -> None:
        self.set_text_color(15, 23, 42)
        self.set_font("Helvetica", "B", 15)
        self.multi_cell(0, 7.5, self.report_title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(90, 100, 115)
        self.multi_cell(0, 5, self.filters_text, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def heading(self, text: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(4, 120, 87)
        self.cell(0, 7, _t(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(15, 23, 42)

    def note(self, text: str) -> None:
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(110, 118, 130)
        self.multi_cell(0, 5, _t(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(15, 23, 42)

    def data_table(self, headers: list[str], rows: list[list], widths: tuple, aligns: tuple) -> None:
        if not rows:
            self.note("Tidak ada data untuk ditampilkan.")
            return
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(15, 23, 42)
        with self.table(
            col_widths=widths,
            text_align=aligns,
            line_height=5.2,
            headings_style=FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=(16, 120, 90)),
            cell_fill_color=(243, 246, 249),
            cell_fill_mode="ROWS",
            borders_layout="HORIZONTAL_LINES",
            padding=(1.4, 1.8),
        ) as table:
            table.row([_t(h) for h in headers])
            for row in rows:
                table.row([_t(cell) for cell in row])
        self.ln(2)

    def summary_line(self, pairs: list[tuple[str, object]]) -> None:
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(15, 23, 42)
        text = "   |   ".join(f"{label}: {value}" for label, value in pairs)
        self.multi_cell(0, 6, _t(text), new_x="LMARGIN", new_y="NEXT")


def _finish(pdf: ReportPDF) -> bytes:
    return bytes(pdf.output())


def build_master_pdf(data: dict, printed_by: str, filters: str) -> bytes:
    pdf = ReportPDF(REPORT_TITLES[1], printed_by, filters)
    pdf.summary_line([("Total game", len(data["games"])), ("Platform terwakili", len(data["by_platform"])),
                      ("Developer terwakili", len(data["by_developer"]))])
    pdf.heading("Jumlah game per platform")
    pdf.data_table(["Platform", "Jumlah game"], [[n, c] for n, c in data["by_platform"]], (130, 50), ("L", "R"))
    pdf.heading("Jumlah game per developer")
    pdf.data_table(["Developer", "Jumlah game"], [[n, c] for n, c in data["by_developer"]], (130, 50), ("L", "R"))
    pdf.heading("Daftar game")
    rows = [
        [
            i,
            g.title,
            g.developer.name if g.developer else "-",
            ", ".join(p.short_name for p in g.platforms) or "-",
            format_date(g.release_date),
            f"{g.average_rating:.1f}" if g.average_rating else "-",
        ]
        for i, g in enumerate(data["games"], start=1)
    ]
    pdf.data_table(
        ["No", "Judul", "Developer", "Platform", "Rilis", "Rating"], rows,
        (10, 52, 38, 38, 26, 16), ("C", "L", "L", "L", "L", "C"),
    )
    return _finish(pdf)


def build_popular_pdf(data: dict, printed_by: str, filters: str) -> bytes:
    pdf = ReportPDF(REPORT_TITLES[2], printed_by, filters)
    pdf.heading(f"Paling banyak disimpan (top {data['limit']})")
    rows = [
        [i, g.title, g.developer.name if g.developer else "-", saves, reviews,
         f"{g.average_rating:.1f}" if g.average_rating else "-"]
        for i, (g, saves, reviews) in enumerate(data["most_saved"], start=1)
    ]
    pdf.data_table(["No", "Judul", "Developer", "Disimpan", "Ulasan", "Rating"], rows,
                   (10, 58, 44, 24, 22, 22), ("C", "L", "L", "C", "C", "C"))
    pdf.heading(f"Rating tertinggi (top {data['limit']})")
    rows = [
        [i, g.title, g.developer.name if g.developer else "-", f"{g.average_rating:.2f}", reviews, saves]
        for i, (g, saves, reviews) in enumerate(data["top_rated"], start=1)
    ]
    pdf.data_table(["No", "Judul", "Developer", "Rating", "Ulasan", "Disimpan"], rows,
                   (10, 58, 44, 22, 22, 24), ("C", "L", "L", "C", "C", "C"))
    pdf.note("Rating dihitung dari rata-rata ulasan pengguna. Game tanpa ulasan tidak masuk daftar rating tertinggi.")
    return _finish(pdf)


def build_activity_pdf(data: dict, printed_by: str, filters: str) -> bytes:
    pdf = ReportPDF(REPORT_TITLES[3], printed_by, filters)
    counts = data["status_counts"]
    pdf.summary_line([("Menunggu", counts.get("Pending", 0)), ("Disetujui", counts.get("Approved", 0)),
                      ("Ditolak", counts.get("Rejected", 0)), ("Ulasan", len(data["comments"])),
                      ("Rata-rata rating", data["average_rating"] or "-")])
    status_id = {"Pending": "Menunggu", "Approved": "Disetujui", "Rejected": "Ditolak"}
    pdf.heading("Pengajuan game baru")
    rows = [
        [format_date(r.submitted_at), r.user.username, r.game_title, _clip(r.platform_info, 40),
         status_id.get(r.status, r.status)]
        for r in data["requests"]
    ]
    pdf.data_table(["Tanggal", "Pengaju", "Judul game", "Platform", "Status"], rows,
                   (26, 30, 62, 38, 24), ("L", "L", "L", "L", "C"))
    pdf.heading("Ulasan pengguna")
    rows = [
        [format_date(c.created_at), c.user.username, c.game.title, c.rating, _clip(c.device_tested, 34),
         _clip(c.content, 70)]
        for c in data["comments"]
    ]
    pdf.data_table(["Tanggal", "Pengguna", "Game", "Rating", "Perangkat", "Ringkasan ulasan"], rows,
                   (22, 22, 32, 14, 36, 54), ("L", "L", "L", "C", "L", "L"))
    return _finish(pdf)
