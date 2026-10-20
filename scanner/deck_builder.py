"""
Stakeholder deck builder — public API.

One form input produces persona-tailored briefs (Executive, CMO, CFO, GC/CCO,
Privacy/CISO, CTO) as PDFs and/or a PowerPoint deck.

    content  -> scanner/deck_content.py   (what each brief says)
    PDF      -> scanner/deck_pdf.py
    PPTX     -> scanner/deck_pptx.py
    facts    -> scanner/regulatory.py, scanner/data/state_laws.json
"""

import io
import re
import zipfile

from scanner.deck_content import (
    PERSONAS, PERSONA_ORDER, ORG_PROFILES, build_brief, build_briefs, calc_roi, prepare, summarize_scan,
)
from scanner.deck_pdf import render_combined_pdf, render_pdf
from scanner.deck_pptx import render_pptx
from scanner.state_privacy import ALL_STATES

# Backward-compatible names used by older pages
_calc_roi = calc_roi
STATE_LAWS = {abbr: (rec.get("law", "None"), rec.get("summary", "")) for abbr, rec in ALL_STATES.items()}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "prospect").lower()).strip("_") or "prospect"


def generate_brief(persona_key: str, data: dict) -> bytes:
    d = prepare(data)
    return render_pdf(build_brief(persona_key, d), d)


def generate_pdfs(data: dict, personas: list[str] | None = None) -> dict:
    d = prepare(data)
    return {b.key: render_pdf(b, d) for b in build_briefs(d, personas)}


def generate_combined_pdf(data: dict, personas: list[str] | None = None) -> bytes:
    d = prepare(data)
    return render_combined_pdf(build_briefs(d, personas), d)


def generate_pptx(data: dict, personas: list[str] | None = None) -> bytes:
    d = prepare(data)
    return render_pptx(build_briefs(d, personas), d)


def generate_all_zip(data: dict, personas: list[str] | None = None, include_pptx: bool = True) -> bytes:
    d = prepare(data)
    briefs = build_briefs(d, personas)
    slug = slugify(d.get("company"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for b in briefs:
            zf.writestr(f"freshpaint_{b.key}_brief_{slug}.pdf", render_pdf(b, d))
        if include_pptx:
            zf.writestr(f"freshpaint_stakeholder_deck_{slug}.pptx", render_pptx(briefs, d))
    return buf.getvalue()
