"""
PDF report generator using fpdf2.
Produces a branded, structured report from a ScanResult dict.
"""

from fpdf import FPDF
from scanner.registry import RISK_COLORS, RISK_LABELS

_RISK_RGB = {
    "critical": (255, 45, 85),
    "high":     (255, 140, 0),
    "medium":   (255, 214, 10),
    "low":      (0, 230, 118),
    "clean":    (0, 255, 178),
}

_DARK_BG   = (5, 10, 20)
_PANEL_BG  = (12, 22, 42)
_TEXT_MAIN = (232, 237, 245)
_TEXT_DIM  = (120, 140, 170)
_ACCENT    = (0, 255, 178)


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class PHIReport(FPDF):
    def __init__(self, scan_result: dict):
        super().__init__()
        self.result = scan_result
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=16)

    def normalize_text(self, text: str) -> str:
        """Override to gracefully handle characters outside Latin-1."""
        return _safe(text)

    def header(self):
        # Dark header bar
        self.set_fill_color(*_DARK_BG)
        self.rect(0, 0, 210, 22, "F")

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*_ACCENT)
        self.set_y(7)
        self.set_x(16)
        self.cell(0, 8, "PHI RISK SCANNER  ·  Powered by Freshpaint", ln=False)

        # Right side: page number
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*_TEXT_DIM)
        self.set_x(-40)
        self.cell(30, 8, f"Page {self.page_no()}", align="R")
        self.ln(14)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*_TEXT_DIM)
        self.cell(
            0, 8,
            "This report is a screening tool, not legal advice. "
            "Consult qualified legal counsel for HIPAA compliance decisions.  "
            "© Freshpaint Inc.  ·  freshpaint.io",
            align="C",
        )

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _s(self, text: str) -> str:
        return _safe(text)

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*_ACCENT)
        self.set_fill_color(*_PANEL_BG)
        self.cell(0, 7, f"  {title.upper()}", ln=True, fill=True)
        self.ln(2)

    def kv_row(self, key: str, value: str, value_color=None):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*_TEXT_DIM)
        self.cell(42, 6, key, ln=False)

        self.set_font("Helvetica", "", 8)
        if value_color:
            self.set_text_color(*value_color)
        else:
            self.set_text_color(*_TEXT_MAIN)
        self.multi_cell(0, 6, value)

    def risk_badge(self, risk: str, x=None, y=None, w=36, h=10):
        rgb = _RISK_RGB.get(risk, (128, 128, 128))
        if x is not None:
            self.set_xy(x, y)
        cx = self.get_x()
        cy = self.get_y()
        self.set_fill_color(*rgb)
        self.rect(cx, cy, w, h, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(5, 10, 20)
        self.set_xy(cx, cy + 1.5)
        self.cell(w, 7, RISK_LABELS.get(risk, risk.upper()), align="C")

    def tracker_card(self, f: dict):
        risk = f["risk_level"]
        rgb = _RISK_RGB.get(risk, (128, 128, 128))

        # Card background
        y_start = self.get_y()
        self.set_fill_color(*_PANEL_BG)
        card_h = 10 + len(f["phi_capture"]) * 5 + 14
        # Left color stripe
        self.set_fill_color(*rgb)
        self.rect(self.l_margin, y_start, 3, card_h, "F")

        self.set_x(self.l_margin + 5)

        # Tracker name + risk badge on same line
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*_TEXT_MAIN)
        self.cell(100, 7, f["name"], ln=False)

        badge_x = self.l_margin + 108
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*rgb)
        self.set_x(badge_x)
        self.cell(30, 7, f"■ {RISK_LABELS.get(risk, risk.upper())}", ln=True)

        # Company
        self.set_x(self.l_margin + 5)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*_TEXT_DIM)
        self.cell(0, 5, f["company"], ln=True)

        # BAA line
        self.set_x(self.l_margin + 5)
        self.set_font("Helvetica", "B", 8)
        baa_color = (0, 230, 118) if f["baa_available"] else (255, 45, 85)
        self.set_text_color(*baa_color)
        baa_text = "BAA AVAILABLE" if f["baa_available"] else "NO BAA AVAILABLE"
        self.cell(42, 5, baa_text, ln=False)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*_TEXT_DIM)
        note = f["baa_notes"][:90] + ("…" if len(f["baa_notes"]) > 90 else "")
        self.multi_cell(0, 5, note)

        # PHI captured
        self.set_x(self.l_margin + 5)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*_TEXT_DIM)
        self.cell(0, 5, "PHI CAPTURED:", ln=True)
        for item in f["phi_capture"][:5]:
            self.set_x(self.l_margin + 10)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*_TEXT_MAIN)
            self.cell(0, 4.5, f"· {item}", ln=True)

        # Detection snippet
        self.set_x(self.l_margin + 5)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*_TEXT_DIM)
        via = f.get("detected_via", "").replace("_", " ").upper()
        snippet = f.get("detected_snippet", "")[:80]
        self.multi_cell(0, 4.5, f"Detected via {via}: {snippet}")
        self.ln(3)


def _safe(text: str) -> str:
    """Strip/replace characters outside Latin-1 for fpdf Helvetica compatibility."""
    return (
        text
        .replace("\u2014", "--")   # em dash
        .replace("\u2013", "-")    # en dash
        .replace("\u2019", "'")    # right single quote
        .replace("\u2018", "'")    # left single quote
        .replace("\u201C", '"')    # left double quote
        .replace("\u201D", '"')    # right double quote
        .replace("\u2022", "*")    # bullet
        .replace("\u00B7", ".")    # middle dot
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


def generate_pdf(scan_result: dict) -> bytes:
    pdf = PHIReport(scan_result)
    pdf.add_page()

    # Sanitize all strings for Latin-1 (fpdf Helvetica encoding)
    import copy

    def _sanitize(obj):
        if isinstance(obj, str):
            return _safe(obj)
        if isinstance(obj, list):
            return [_sanitize(i) for i in obj]
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        return obj

    scan_result = _sanitize(copy.deepcopy(scan_result))

    findings = scan_result.get("findings", [])
    overall = scan_result.get("overall_risk", "clean")
    url = scan_result.get("canonical_url", scan_result.get("url", ""))
    ts = scan_result.get("scan_timestamp", "")

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        lvl = f.get("risk_level", "low")
        counts[lvl] = counts.get(lvl, 0) + 1

    # ── Hero block ───────────────────────────────────────────────────────────
    pdf.set_fill_color(*_DARK_BG)
    pdf.rect(0, pdf.get_y() - 2, 210, 46, "F")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*_TEXT_MAIN)
    pdf.cell(0, 10, "PHI Risk Report", ln=True, align="C")
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_TEXT_DIM)
    pdf.cell(0, 6, url, ln=True, align="C")
    pdf.cell(0, 5, f"Scanned: {ts}", ln=True, align="C")
    pdf.ln(3)

    # Overall risk badge centered
    badge_w = 60
    badge_x = (210 - badge_w) / 2
    pdf.set_fill_color(*_RISK_RGB.get(overall, (128, 128, 128)))
    pdf.rect(badge_x, pdf.get_y(), badge_w, 12, "F")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(5, 10, 20)
    pdf.set_x(badge_x)
    pdf.cell(badge_w, 12, f"OVERALL RISK: {RISK_LABELS.get(overall, overall.upper())}", align="C", ln=True)
    pdf.ln(6)

    # ── Summary stats ────────────────────────────────────────────────────────
    pdf.section_title("Executive Summary")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_TEXT_MAIN)
    total = len(findings)
    summary = (
        f"This scan identified {total} third-party tracking technolog{'y' if total == 1 else 'ies'} "
        f"on {url}. "
    )
    if counts["critical"] > 0:
        summary += (
            f"{counts['critical']} tracker(s) are rated CRITICAL and require immediate removal — "
            "they have no available HIPAA Business Associate Agreement and are explicitly named "
            "in HHS OCR guidance or FTC enforcement actions. "
        )
    if counts["high"] > 0:
        summary += (
            f"{counts['high']} tracker(s) are rated HIGH risk and should be reviewed promptly. "
        )
    if total == 0:
        summary = (
            f"No known third-party trackers were detected on {url} via static HTML analysis. "
            "Note: this scan does not execute JavaScript and may not detect dynamically injected trackers "
            "or tags deployed via Google Tag Manager containers."
        )
    pdf.multi_cell(0, 6, summary)
    pdf.ln(3)

    # Stats row
    stat_labels = [
        (str(counts["critical"]), "CRITICAL", _RISK_RGB["critical"]),
        (str(counts["high"]),     "HIGH",     _RISK_RGB["high"]),
        (str(counts["medium"]),   "MEDIUM",   _RISK_RGB["medium"]),
        (str(total),              "TOTAL",    _ACCENT),
    ]
    col_w = (210 - 32) / 4
    x_start = 16
    for val, label, color in stat_labels:
        pdf.set_fill_color(*_PANEL_BG)
        pdf.rect(x_start, pdf.get_y(), col_w - 2, 18, "F")
        pdf.set_fill_color(*color)
        pdf.rect(x_start, pdf.get_y(), col_w - 2, 3, "F")

        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*color)
        pdf.set_xy(x_start, pdf.get_y() + 4)
        pdf.cell(col_w - 2, 8, val, align="C")
        pdf.ln(0)
        pdf.set_xy(x_start, pdf.get_y() + 8)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*_TEXT_DIM)
        pdf.cell(col_w - 2, 5, label, align="C")
        x_start += col_w
    pdf.ln(24)

    # ── Tracker findings ─────────────────────────────────────────────────────
    if findings:
        pdf.section_title("Tracker Findings")
        for f in findings:
            pdf.tracker_card(f)

    # ── Regulatory context ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("Regulatory Context")

    regs = [
        ("HIPAA Privacy Rule", "45 CFR §164.514(b)",
         "PHI shared with third-party trackers without a BAA constitutes an impermissible disclosure."),
        ("HHS OCR Bulletin", "December 2022",
         "Explicitly names Meta Pixel, Google Analytics, and similar tools as potential HIPAA violations on healthcare websites."),
        ("HHS / FTC Joint Letter", "July 2023",
         "130 healthcare organizations warned about tracking pixel risks. Meta and Google named."),
        ("HIPAA Breach Notification", "45 CFR §164.400–414",
         "Impermissible PHI disclosure to a tracker may trigger mandatory patient and HHS notification."),
        ("CCPA / CPRA", "California Civil Code §1798.100+",
         "Applies to California patients. Health data is a 'sensitive personal information' category with heightened protection."),
        ("TX THIPA", "Texas Health & Safety Code §181",
         "Texas Health Privacy Act covers health information collected by non-HIPAA entities as well."),
        ("VA VCDPA", "Virginia Code §59.1-578",
         "Sensitive data category includes health data. Applies to organizations that process data of 100K+ Virginians."),
    ]
    for name, citation, description in regs:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*_TEXT_MAIN)
        pdf.cell(0, 6, f"{name}  ({citation})", ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_TEXT_DIM)
        pdf.multi_cell(0, 5, description)
        pdf.ln(2)

    # ── Recommendations ──────────────────────────────────────────────────────
    pdf.ln(2)
    pdf.section_title("Recommendations")

    recs = []
    for f in findings:
        if f["risk_level"] == "critical":
            recs.append(
                f"REMOVE IMMEDIATELY: {f['name']} ({f['company']}) — "
                f"No BAA is available and this tracker is explicitly named in regulatory enforcement actions."
            )
        elif f["risk_level"] == "high" and not f["baa_available"]:
            recs.append(
                f"REMOVE OR REPLACE: {f['name']} — No BAA available. "
                f"Replace with a Freshpaint-routed equivalent that sanitizes PHI before sending data."
            )
        elif f["risk_level"] == "high" and f["baa_available"]:
            recs.append(
                f"REVIEW AND RECONFIGURE: {f['name']} — BAA is available but must be explicitly signed "
                f"and the tool configured to suppress PHI. Current default implementation is non-compliant."
            )
        elif f["risk_level"] == "medium":
            recs.append(
                f"AUDIT: {f['name']} — BAA may be available. Verify agreement status and review "
                f"data governance configuration to ensure PHI is not passed in event properties."
            )

    if not recs:
        recs.append(
            "No critical or high-risk trackers detected via static analysis. "
            "Conduct a dynamic scan (using Freshpaint's Web Tracker Monitor) to detect "
            "JavaScript-injected trackers and Google Tag Manager container contents."
        )

    for i, rec in enumerate(recs, 1):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_ACCENT)
        pdf.cell(8, 6, f"{i}.", ln=False)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*_TEXT_MAIN)
        pdf.multi_cell(0, 6, rec)
        pdf.ln(1)

    # ── CTA ──────────────────────────────────────────────────────────────────
    pdf.ln(4)
    cta_y = pdf.get_y()
    pdf.set_fill_color(*_PANEL_BG)
    pdf.rect(16, cta_y, 178, 28, "F")
    pdf.set_fill_color(*_ACCENT)
    pdf.rect(16, cta_y, 4, 28, "F")

    pdf.set_xy(24, cta_y + 4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_ACCENT)
    pdf.cell(0, 7, "Replace all non-compliant trackers with Freshpaint.", ln=True)
    pdf.set_x(24)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_TEXT_MAIN)
    pdf.multi_cell(
        160, 6,
        "Freshpaint intercepts and sanitizes tracking events before they reach non-compliant "
        "tools, letting your marketing team keep full analytics visibility without PHI exposure. "
        "Includes a signed BAA."
    )
    pdf.set_xy(24, pdf.get_y() + 1)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_ACCENT)
    pdf.cell(0, 5, "freshpaint.io  ·  Talk to an expert today")

    return bytes(pdf.output())
