"""
PDF renderer for stakeholder briefs (fpdf2). Renders the content model from
scanner/deck_content.py; contains no copy of its own.
"""

from __future__ import annotations

from fpdf import FPDF
from fpdf.fonts import FontFace

from scanner.deck_content import Brief, TONES

_DARK  = (11, 22, 40)
_LIGHT = (245, 247, 252)
_DIM   = (110, 125, 148)
_TEXT  = (30, 40, 58)
_RULE  = (220, 225, 235)

PAGE_W, PAGE_H = 210, 297
MARGIN = 16
CONTENT_W = PAGE_W - 2 * MARGIN
HEADER_H = 46
FOOTER_H = 14

_REPLACEMENTS = {
    "—": "--", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"',
    "•": "*", "·": ".", "→": "->", "®": "(R)", "…": "...", "≥": ">=",
    "≤": "<=", " ": " ",
}


def safe(text) -> str:
    text = str(text)
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _tint(rgb, amount=0.10):
    return tuple(int(c * amount + 250 * (1 - amount)) for c in rgb)


class BriefPDF(FPDF):
    def __init__(self, brief: Brief, data: dict):
        super().__init__(format="A4")
        self.brief = brief
        self.p = brief.persona
        self.data = data
        self.accent = self.p["accent"]
        self.set_margins(MARGIN, HEADER_H + 8, MARGIN)
        self.set_auto_page_break(auto=True, margin=FOOTER_H + 6)
        self.set_title(safe(f"Freshpaint brief for the {self.p['short']} - {data.get('company', '')}"))
        self.set_author("Freshpaint")
        self._brief_first_page = True

    def start_brief(self, brief: Brief):
        # Applied in header(), after add_page() has drawn the previous page's footer.
        self._pending_brief = brief
        self.add_page()

    def normalize_text(self, text):
        return super().normalize_text(safe(text))

    # ── Page furniture ───────────────────────────────────────────────────
    def header(self):
        pending = getattr(self, "_pending_brief", None)
        if pending is not None:
            self.brief, self.p, self.accent = pending, pending.persona, pending.persona["accent"]
            self._brief_first_page = True
            self._brief_start = self.page_no()
            self._pending_brief = None
        first = self._brief_first_page
        self._brief_first_page = False
        h = HEADER_H if first else 16
        self.set_fill_color(*_DARK)
        self.rect(0, 0, PAGE_W, h, "F")
        self.set_fill_color(*self.accent)
        self.rect(0, 0, 4, h, "F")

        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*self.accent)
        self.set_xy(MARGIN, 6)
        self.cell(0, 4, "FRESHPAINT  |  PRIVACY-COMPLIANT HEALTHCARE ANALYTICS")
        company = safe(self.data.get("company", "Your Organization"))
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*_DIM)
        self.set_xy(0, 6)
        self.cell(PAGE_W - MARGIN, 4, f"Prepared for {company}  |  For the {self.p['short']}", align="R")

        if first:
            l1, l2 = self.p["headline"]
            self.set_font("Helvetica", "B", 19)
            self.set_text_color(245, 248, 255)
            self.set_xy(MARGIN, 16)
            self.cell(0, 9, safe(l1))
            self.set_font("Helvetica", "", 17)
            self.set_text_color(*self.accent)
            self.set_xy(MARGIN, 25)
            self.cell(0, 9, safe(l2))
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*_DIM)
            self.set_xy(MARGIN, 37)
            self.cell(0, 4, safe(f"{self.p['title']}  -  {self.p['focus']}"))
            self.set_y(HEADER_H + 6)
        else:
            self.set_y(16 + 6)

    def footer(self):
        y = PAGE_H - FOOTER_H
        self.set_fill_color(*_DARK)
        self.rect(0, y, PAGE_W, FOOTER_H, "F")
        self.set_fill_color(*self.accent)
        self.rect(0, y, 4, FOOTER_H, "F")
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*self.accent)
        self.set_xy(MARGIN, y + 3)
        self.cell(80, 4, safe(self.data.get("rep_name", "Your Freshpaint Account Executive")))
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*_DIM)
        self.set_xy(MARGIN, y + 7)
        self.cell(80, 4, safe(self.data.get("rep_email", "sales@freshpaint.io")))
        self.set_font("Helvetica", "", 6.5)
        self.set_xy(0, y + 3)
        self.cell(PAGE_W - MARGIN, 4,
                  f"freshpaint.io  |  {self.data.get('date_str', '')}  |  Confidential  |  Page {self.page_no() - getattr(self, '_brief_start', 1) + 1}",
                  align="R")
        self.set_xy(0, y + 7)
        self.cell(PAGE_W - MARGIN, 4, "Directional benchmarks and regulatory summary. Not legal advice.", align="R")

    # ── Helpers ──────────────────────────────────────────────────────────
    def space_left(self) -> float:
        return self.page_break_trigger - self.get_y()

    def ensure(self, h: float):
        if self.space_left() < h:
            self.add_page()

    def section_head(self, title: str):
        self.ensure(30)
        self.ln(2)
        y = self.get_y()
        self.set_fill_color(*self.accent)
        self.rect(MARGIN, y + 0.5, 2.5, 5, "F")
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*_TEXT)
        self.set_xy(MARGIN + 5, y)
        self.cell(0, 6, safe(title.upper()), new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def b_text(self, s: str):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*_TEXT)
        self.set_x(MARGIN)
        self.multi_cell(CONTENT_W, 4.8, safe(s), new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def b_bullets(self, items):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*_TEXT)
        for it in items:
            self.ensure(10)
            y = self.get_y()
            self.set_fill_color(*self.accent)
            self.rect(MARGIN + 1.5, y + 1.8, 1.4, 1.4, "F")
            self.set_xy(MARGIN + 5, y)
            self.multi_cell(CONTENT_W - 5, 4.8, safe(it), new_x="LMARGIN", new_y="NEXT")
            self.ln(0.8)
        self.ln(1)

    def b_kv(self, pairs):
        key_w = 38
        for k, v in pairs:
            self.ensure(10)
            y = self.get_y()
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(*self.accent)
            self.set_xy(MARGIN, y)
            self.multi_cell(key_w - 2, 4.8, safe(k))
            y_key = self.get_y()
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(*_TEXT)
            self.set_xy(MARGIN + key_w, y)
            self.multi_cell(CONTENT_W - key_w, 4.8, safe(v), new_x="LMARGIN", new_y="NEXT")
            self.set_y(max(self.get_y(), y_key) + 1)
        self.ln(1)

    def b_stats(self, items):
        n = len(items)
        gap = 3
        w = (CONTENT_W - gap * (n - 1)) / n
        h = 21
        self.ensure(h + 4)
        y = self.get_y()
        for i, (val, label, tone) in enumerate(items):
            color = TONES.get(tone) or self.accent
            x = MARGIN + i * (w + gap)
            self.set_fill_color(*_LIGHT)
            self.rect(x, y, w, h, "F")
            self.set_fill_color(*color)
            self.rect(x, y, w, 1.6, "F")
            size = 15
            self.set_font("Helvetica", "B", size)
            while self.get_string_width(safe(val)) > w - 4 and size > 8:
                size -= 0.5
                self.set_font("Helvetica", "B", size)
            self.set_text_color(*color)
            self.set_xy(x, y + 4)
            self.cell(w, 8, safe(val), align="C")
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*_DIM)
            self.set_xy(x + 2, y + 12)
            self.multi_cell(w - 4, 3.4, safe(label), align="C", max_line_height=3.4)
        self.set_y(y + h + 3)

    def b_table(self, spec):
        cols, widths, rows = spec["cols"], spec["widths"], spec["rows"]
        col_widths = [CONTENT_W * w / sum(widths) for w in widths]
        self.ensure(20)
        self.set_font("Helvetica", "", 7.8)
        self.set_text_color(*_TEXT)
        self.set_draw_color(*_RULE)
        fill = _tint(self.accent, 0.07)
        self.set_fill_color(*fill)
        head = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=_DARK, size_pt=7.5)
        with self.table(col_widths=col_widths, width=CONTENT_W, align="LEFT",
                        line_height=4.2, padding=(1.3, 1.6), borders_layout="HORIZONTAL_LINES",
                        headings_style=head, cell_fill_color=fill,
                        cell_fill_mode="ROWS", repeat_headings=1, text_align="LEFT") as t:
            r = t.row()
            for c in cols:
                r.cell(safe(c))
            for row in rows:
                r = t.row()
                for c in row:
                    r.cell(safe(c))
        self.ln(3)

    def b_callout(self, s: str):
        self.set_font("Helvetica", "", 9)
        lines = self.multi_cell(CONTENT_W - 10, 4.8, safe(s), dry_run=True, output="LINES")
        h = len(lines) * 4.8 + 7
        self.ensure(h + 2)
        y = self.get_y()
        self.set_fill_color(*_tint(self.accent, 0.12))
        self.rect(MARGIN, y, CONTENT_W, h, "F")
        self.set_fill_color(*self.accent)
        self.rect(MARGIN, y, 2.5, h, "F")
        self.set_text_color(*_TEXT)
        self.set_xy(MARGIN + 6, y + 3.5)
        self.multi_cell(CONTENT_W - 10, 4.8, safe(s), new_x="LMARGIN", new_y="NEXT")
        self.set_y(y + h + 3)

    def b_flow(self, steps):
        box_h, arrow = 8, 4
        total = len(steps) * box_h + (len(steps) - 1) * arrow
        self.ensure(total + 4)
        y = self.get_y() + 1
        for i, s in enumerate(steps):
            last = i == len(steps) - 1
            self.set_fill_color(*(self.accent if i in (1, 2) else _LIGHT))
            self.rect(MARGIN + 10, y, CONTENT_W - 20, box_h, "F")
            self.set_font("Helvetica", "B" if i in (1, 2) else "", 8)
            self.set_text_color(*((255, 255, 255) if i in (1, 2) else _TEXT))
            self.set_xy(MARGIN + 10, y)
            self.cell(CONTENT_W - 20, box_h, safe(s), align="C")
            y += box_h
            if not last:
                self.set_draw_color(*_DIM)
                cx = PAGE_W / 2
                self.line(cx, y + 0.5, cx, y + arrow - 0.5)
                self.line(cx - 1.2, y + arrow - 1.8, cx, y + arrow - 0.5)
                self.line(cx + 1.2, y + arrow - 1.8, cx, y + arrow - 0.5)
                y += arrow
        self.set_y(y + 4)


def _render_into(pdf: BriefPDF, brief: Brief):
    pdf.start_brief(brief)
    for sec in brief.sections:
        pdf.section_head(sec.title)
        for kind, payload in sec.blocks:
            getattr(pdf, "b_" + kind)(payload)


def render_pdf(brief: Brief, data: dict) -> bytes:
    pdf = BriefPDF(brief, data)
    _render_into(pdf, brief)
    return bytes(pdf.output())


def render_combined_pdf(briefs: list[Brief], data: dict) -> bytes:
    """All selected briefs in one PDF; each starts on a new page with its own header."""
    pdf = BriefPDF(briefs[0], data)
    pdf.set_title(safe(f"Freshpaint stakeholder briefing - {data.get('company', '')}"))
    for b in briefs:
        _render_into(pdf, b)
    return bytes(pdf.output())
