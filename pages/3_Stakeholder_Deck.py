"""
Stakeholder Deck Builder — persona-tailored briefs (PDF) and a presentation deck
(PowerPoint) for every member of a healthcare buying committee, from one form.
"""

import streamlit as st
from scanner.deck_builder import (
    PERSONAS, PERSONA_ORDER, calc_roi, generate_combined_pdf, generate_pdfs, generate_pptx,
    generate_all_zip, slugify, summarize_scan,
)
from scanner.state_privacy import ALL_STATES, LAST_REVIEWED, score_state

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #05080F !important;
    color: #E8EDF5 !important;
}
.stApp { background: #05080F; }
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,255,178,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,178,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none; z-index: 0;
}
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
.block-container { padding-top: 0 !important; max-width: 1100px !important; }

/* ── Hero ── */
.deck-hero {
    background: linear-gradient(135deg, #05080F 0%, #0B1628 50%, #05080F 100%);
    border-bottom: 1px solid rgba(0,255,178,0.15);
    padding: 2.8rem 2rem 2.2rem;
    margin: 0 -4rem 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.deck-hero::before {
    content: '';
    position: absolute; top: -60px; left: 50%; transform: translateX(-50%);
    width: 500px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,255,178,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.fp-wordmark {
    font-family: 'Syne', sans-serif; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.35em; text-transform: uppercase;
    color: rgba(0,255,178,0.6); margin-bottom: 0.6rem;
}
.deck-hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.1rem); font-weight: 800;
    line-height: 1.1; margin: 0 0 0.6rem; color: #E8EDF5; letter-spacing: -0.02em;
}
.deck-hero h1 span { color: #00FFB2; }
.deck-hero p {
    font-size: 0.83rem; color: rgba(232,237,245,0.5);
    max-width: 580px; margin: 0 auto; line-height: 1.7;
}

/* ── Form panel ── */
.form-section {
    font-family: 'Syne', sans-serif; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.3em; text-transform: uppercase;
    color: rgba(0,255,178,0.6);
    border-bottom: 1px solid rgba(0,255,178,0.1);
    padding-bottom: 0.5rem; margin: 1.5rem 0 1rem;
}

/* ── Input overrides ── */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: rgba(232,237,245,0.45) !important;
}
.stTextInput input, .stNumberInput input {
    background: rgba(5,8,15,0.9) !important;
    border: 1px solid rgba(0,255,178,0.2) !important;
    border-radius: 3px !important;
    color: #E8EDF5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(5,8,15,0.9) !important;
    border: 1px solid rgba(0,255,178,0.2) !important;
    border-radius: 3px !important;
}

/* ── Generate button ── */
.stButton > button {
    background: #00FFB2 !important;
    color: #05080F !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #00E5A0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,255,178,0.25) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: transparent !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 0.7rem 1.2rem !important;
    transition: all 0.15s !important;
    width: 100%;
}

/* ── Persona cards (preview) ── */
.persona-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin: 1.5rem 0;
}
.persona-card {
    background: rgba(12,22,42,0.8);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px;
    padding: 1.1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.persona-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: 4px 0 0 4px;
}
.pc-cmo::before  { background: #00C896; }
.pc-cfo::before  { background: #E8630A; }
.pc-gc::before   { background: #D42B4A; }
.pc-cto::before  { background: #1A8BFF; }

.pc-badge {
    display: inline-block;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 0.15rem 0.5rem;
    border-radius: 2px; margin-bottom: 0.4rem;
}
.pc-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem; font-weight: 700;
    color: #E8EDF5; margin-bottom: 0.3rem;
}
.pc-focus {
    font-size: 0.68rem; color: rgba(232,237,245,0.4);
    margin-bottom: 0.5rem; letter-spacing: 0.03em;
}
.pc-bullets {
    font-size: 0.7rem; color: rgba(232,237,245,0.55);
    line-height: 1.7;
}

/* ── Download panel ── */
.download-panel {
    background: rgba(12,22,42,0.8);
    border: 1px solid rgba(0,255,178,0.2);
    border-radius: 4px;
    padding: 1.8rem;
    margin-top: 1.5rem;
}
.dp-title {
    font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 800;
    color: #E8EDF5; margin-bottom: 0.3rem;
}
.dp-sub {
    font-size: 0.72rem; color: rgba(232,237,245,0.4);
    margin-bottom: 1.2rem; line-height: 1.6;
}

/* ── ROI preview strip ── */
.roi-strip {
    display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap;
}
.roi-chip {
    flex: 1; min-width: 100px;
    background: rgba(12,22,42,0.7);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px; padding: 0.7rem; text-align: center;
}
.roi-chip-num {
    font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 800;
    color: #00FFB2; line-height: 1; margin-bottom: 0.2rem;
}
.roi-chip-label {
    font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(232,237,245,0.3);
}
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="deck-hero">
  <div class="fp-wordmark">Freshpaint · Sales Enablement</div>
  <h1>Stakeholder <span>Deck Builder</span></h1>
  <p>
    Fill in one form. Get a tailored brief for every member of the buying committee —
    as PDFs to send and a PowerPoint deck to present. Add the prospect's website and
    the briefs cite the actual trackers we find on it.
  </p>
</div>
""", unsafe_allow_html=True)


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


# ── Stakeholders ──────────────────────────────────────────────────────────────
st.markdown('<div class="form-section">Stakeholders</div>', unsafe_allow_html=True)

cards_html = '<div class="persona-grid" style="grid-template-columns:repeat(3,1fr)">'
for key in PERSONA_ORDER:
    p = PERSONAS[key]
    c = _hex(p["accent"])
    cards_html += f"""
    <div class="persona-card" style="border-left:3px solid {c}">
      <div class="pc-badge" style="background:{c}22;color:{c};border:1px solid {c}44">{p['short']}</div>
      <div class="pc-title">{p['title']}</div>
      <div class="pc-focus">{p['focus']}</div>
      <div class="pc-bullets">{p['blurb']}</div>
    </div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

persona_labels = {k: f"{PERSONAS[k]['short']} — {PERSONAS[k]['title']}" for k in PERSONA_ORDER}
personas = st.multiselect(
    "Briefs to generate",
    options=PERSONA_ORDER,
    default=PERSONA_ORDER,
    format_func=lambda k: persona_labels[k],
)

# ── Prospect ──────────────────────────────────────────────────────────────────
st.markdown('<div class="form-section">Prospect Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    company = st.text_input("Prospect company name", placeholder="Baptist Health")
    org_type = st.selectbox("Organization type", [
        "Hospital / Health System", "Digital Health / DTC",
        "Telehealth", "Specialty Practice / Group", "Payer / Insurance",
    ])
    site_url = st.text_input(
        "Prospect website (optional)", placeholder="baptisthealth.com",
        help="We run the PHI risk scan and cite the trackers found in the Executive, CMO, Privacy and CTO briefs.",
    )
with col2:
    monthly_spend = st.number_input(
        "Monthly ad spend ($)", min_value=5_000, max_value=5_000_000,
        value=75_000, step=5_000,
    )
    freshpaint_cost = st.number_input(
        "Freshpaint annual quote ($)", min_value=15_000, max_value=300_000,
        value=40_000, step=5_000,
    )

st.markdown('<div class="form-section">Geography & Exposure</div>', unsafe_allow_html=True)

state_opts = sorted(ALL_STATES, key=lambda a: ALL_STATES[a]["name"])
states = st.multiselect(
    "States where the org serves or markets to patients",
    options=state_opts,
    default=["TX", "CA", "FL"],
    format_func=lambda a: f"{a} — {ALL_STATES[a]['name']}  ({score_state(a)['tier_label']})",
    help=f"Feeds the Executive, GC and Privacy briefs. State law data reviewed {LAST_REVIEWED}.",
)

st.markdown('<div class="form-section">Sales Rep & Output</div>', unsafe_allow_html=True)

col3, col4, col5 = st.columns([1, 1, 1])
with col3:
    rep_name = st.text_input("Your name", placeholder="Alex Smith")
with col4:
    rep_email = st.text_input("Your email", placeholder="alex@freshpaint.io")
with col5:
    out_format = st.radio("Output", ["PDF + PowerPoint", "PDF only", "PowerPoint only"], horizontal=False)

# ── Live ROI preview ──────────────────────────────────────────────────────────
m = calc_roi(monthly_spend, org_type, freshpaint_cost)
chips = [
    (f"${m['total']:,.0f}", "Annual dark cost"),
    (f"{m['roi']:.1f}x", "Freshpaint ROI"),
    (f"{m['payback']:.1f} mo", "Payback period"),
    (f"${m['total'] - freshpaint_cost:,.0f}", "Net savings"),
]
chips_html = '<div class="roi-strip">' + "".join(
    f'<div class="roi-chip"><div class="roi-chip-num">{n}</div><div class="roi-chip-label">{l}</div></div>'
    for n, l in chips) + "</div>"
st.markdown(
    '<div style="font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;'
    'color:rgba(0,255,178,0.5);margin-top:0.5rem">ROI Preview (used in Executive, CMO & CFO briefs)</div>',
    unsafe_allow_html=True,
)
st.markdown(chips_html, unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
generate = st.button("Generate Briefs →")

if generate:
    if not company.strip():
        st.warning("Enter a company name to personalize the briefs.")
    elif not personas:
        st.warning("Pick at least one stakeholder brief.")
    else:
        data = {
            "company":         company.strip(),
            "org_type":        org_type,
            "monthly_spend":   monthly_spend,
            "freshpaint_cost": freshpaint_cost,
            "states":          states,
            "rep_name":        rep_name.strip() or "Your Freshpaint AE",
            "rep_email":       rep_email.strip() or "sales@freshpaint.io",
        }
        scan = None
        if site_url.strip():
            with st.spinner(f"Scanning {site_url.strip()} for trackers…"):
                try:
                    from scanner.scanner import scan_url
                    scan = summarize_scan(scan_url(site_url.strip()))
                except Exception as e:  # network errors etc. — never block the briefs
                    scan = {"url": site_url.strip(), "error": str(e), "trackers": []}
        data["scan"] = scan

        want_pdf = out_format != "PowerPoint only"
        want_pptx = out_format != "PDF only"
        with st.spinner("Generating briefs…"):
            try:
                out = {"company": company.strip(), "personas": personas, "scan": scan}
                if want_pdf:
                    out["pdfs"] = generate_pdfs(data, personas)
                    if len(personas) > 1:
                        out["combined_pdf"] = generate_combined_pdf(data, personas)
                if want_pptx:
                    out["pptx"] = generate_pptx(data, personas)
                out["zip"] = generate_all_zip(data, personas, include_pptx=want_pptx) if want_pdf else None
                st.session_state["deck_out"] = out
            except Exception as e:
                st.error(f"Generation error: {e}")

# ── Download panel ────────────────────────────────────────────────────────────
out = st.session_state.get("deck_out")
if out:
    slug = slugify(out["company"])
    scan = out.get("scan")
    scan_note = ""
    if scan and scan.get("error"):
        scan_note = (f"<br><span style='color:#E8B80A'>Site scan failed ({scan['error']}). "
                     "Briefs were generated without tracker detail.</span>")
    elif scan:
        scan_note = (f"<br>Site scan: {len(scan['trackers'])} tracker(s) found on {scan['url']}, "
                     f"{scan['n_no_baa']} without a BAA.")

    st.html(f"""
    <div class="download-panel">
      <div class="dp-title">Ready for {out['company']}</div>
      <div class="dp-sub">
        Send each PDF to the relevant stakeholder, share the combined PDF with your champion,
        or present from the PowerPoint deck.{scan_note}
      </div>
    </div>
    """)

    if out.get("pdfs"):
        keys = list(out["pdfs"].keys())
        for row_start in range(0, len(keys), 3):
            cols = st.columns(3)
            for col, key in zip(cols, keys[row_start:row_start + 3]):
                p = PERSONAS[key]
                c = _hex(p["accent"])
                with col:
                    st.markdown(
                        f'<div style="background:{c}18;border:1px solid {c}44;border-radius:4px;'
                        f'padding:0.7rem;text-align:center;margin-bottom:0.4rem">'
                        f'<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;'
                        f'text-transform:uppercase;color:{c}">{p["short"]}</div>'
                        f'<div style="font-size:0.65rem;color:rgba(232,237,245,0.4);line-height:1.5">{p["focus"]}</div>'
                        f'</div>', unsafe_allow_html=True)
                    st.download_button("↓  PDF", data=out["pdfs"][key],
                                       file_name=f"freshpaint_{key}_brief_{slug}.pdf",
                                       mime="application/pdf", use_container_width=True, key=f"dl_{key}")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if out.get("pptx"):
        with c1:
            st.download_button("↓  PowerPoint deck (.pptx)", data=out["pptx"],
                               file_name=f"freshpaint_stakeholder_deck_{slug}.pptx",
                               mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                               use_container_width=True)
    if out.get("combined_pdf"):
        with c2:
            st.download_button("↓  All briefs in one PDF", data=out["combined_pdf"],
                               file_name=f"freshpaint_stakeholder_briefs_{slug}.pdf",
                               mime="application/pdf", use_container_width=True)
    if out.get("zip"):
        with c3:
            st.download_button("↓  Everything (ZIP)", data=out["zip"],
                               file_name=f"freshpaint_stakeholder_kit_{slug}.zip",
                               mime="application/zip", use_container_width=True)

    st.markdown(
        '<div style="font-size:0.65rem;color:rgba(232,237,245,0.2);margin-top:0.75rem">'
        'Files are generated in memory and not stored. Regenerate anytime to update with new inputs.'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:2rem 1rem;margin-top:3rem;
            border-top:1px solid rgba(255,255,255,0.05);
            font-size:0.65rem;color:rgba(232,237,245,0.2);line-height:1.8">
  <a href="https://freshpaint.io" style="color:rgba(0,255,178,0.4);text-decoration:none">Freshpaint</a>
  · HIPAA-Compliant Healthcare Analytics ·
  <a href="https://freshpaint.io/blog" style="color:rgba(0,255,178,0.4);text-decoration:none">Blog</a>
  <br>Benchmarks are directional estimates. Regulatory content reviewed {LAST_REVIEWED}. Not legal or financial advice.
</div>
""", unsafe_allow_html=True)
