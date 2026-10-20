"""
Competitive Comparison Tool — Freshpaint vs. common alternatives.
Select up to 3 competitors for a side-by-side feature matrix,
objection handling, and win narrative.
"""

import streamlit as st
from scanner.competitors import (
    COMPETITORS, FEATURES, FEATURE_CATS, SCORE_COLOR, SCORE_ICON,
    compare, freshpaint_advantages,
)

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
    content:'';position:fixed;top:0;left:0;right:0;bottom:0;
    background-image:
        linear-gradient(rgba(0,255,178,0.02) 1px,transparent 1px),
        linear-gradient(90deg,rgba(0,255,178,0.02) 1px,transparent 1px);
    background-size:48px 48px;pointer-events:none;z-index:0;
}
#MainMenu, footer, [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container{padding-top:0 !important;max-width:1300px !important;}
div[data-testid="stMultiSelect"]>div{
    background:#0C1628 !important;
    border:1px solid rgba(0,255,178,0.2) !important;border-radius:4px;}
div[data-testid="stMultiSelect"] span{
    background:rgba(0,255,178,0.1) !important;color:#00FFB2 !important;}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.html("""
<div style="background:linear-gradient(135deg,#05080F 0%,#0B1628 50%,#05080F 100%);
            border-bottom:1px solid rgba(0,255,178,0.12);
            padding:2.5rem 2rem 2rem;margin:0 -4rem 2rem;
            text-align:center;position:relative;overflow:hidden">
  <div style="position:absolute;top:-50px;left:50%;transform:translateX(-50%);
              width:600px;height:180px;
              background:radial-gradient(ellipse,rgba(0,255,178,0.06) 0%,transparent 70%);
              pointer-events:none"></div>
  <div style="font-family:Syne,sans-serif;font-size:0.65rem;font-weight:700;
              letter-spacing:0.35em;text-transform:uppercase;
              color:rgba(0,255,178,0.6);margin-bottom:0.5rem">
    Freshpaint · Competitive Intelligence
  </div>
  <h1 style="font-family:Syne,sans-serif;font-size:clamp(1.8rem,4vw,2.8rem);
             font-weight:800;line-height:1.1;margin:0 0 0.5rem;
             color:#E8EDF5;letter-spacing:-0.02em">
    Competitive <span style="color:#00FFB2">Comparison</span>
  </h1>
  <p style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;
            color:rgba(232,237,245,0.4);max-width:580px;margin:0 auto;line-height:1.7">
    Select competitors to compare against Freshpaint across compliance,
    marketing, analytics, and operational dimensions.
  </p>
</div>
""")

# ── Competitor selector ───────────────────────────────────────────────────────
SELECTABLE = {k: v for k, v in COMPETITORS.items() if k != "freshpaint"}
OPTIONS = {v["name"]: k for k, v in SELECTABLE.items()}

selected_names = st.multiselect(
    "Compare Freshpaint against",
    options=list(OPTIONS.keys()),
    default=["Google Analytics 4", "Segment (Twilio)"],
    max_selections=3,
    placeholder="Select up to 3 competitors…",
    label_visibility="collapsed",
)
selected_keys = [OPTIONS[n] for n in selected_names]

if not selected_keys:
    st.html("""
    <div style="text-align:center;padding:3rem 1rem;
                color:rgba(232,237,245,0.25);font-size:0.78rem;
                border:1px dashed rgba(0,255,178,0.1);border-radius:6px;margin-top:1rem">
      Select at least one competitor above to generate a comparison
    </div>
    """)
    st.stop()

# ── Competitor header cards ───────────────────────────────────────────────────
all_keys = ["freshpaint"] + selected_keys
cols = st.columns(len(all_keys), gap="small")

for col, key in zip(cols, all_keys):
    c = COMPETITORS[key]
    is_fp = key == "freshpaint"
    border = f"2px solid {c['color']}" if is_fp else f"1px solid {c['color']}55"
    bg     = f"rgba(0,255,178,0.06)" if is_fp else "rgba(12,22,42,0.8)"
    badge  = '<span style="background:rgba(0,255,178,0.15);color:#00FFB2;font-size:0.58rem;font-weight:700;padding:2px 7px;border-radius:2px;letter-spacing:0.1em;text-transform:uppercase;margin-left:6px">OUR PICK</span>' if is_fp else ""

    adv_count = len(freshpaint_advantages(key)) if not is_fp else 0
    adv_badge = f'<span style="font-size:0.6rem;color:#D42B4A;margin-top:0.3rem;display:block">Freshpaint wins {adv_count}/{len(FEATURES)} features</span>' if not is_fp else ""

    col.html(f"""
    <div style="background:{bg};border:{border};border-radius:6px;
                padding:1.25rem 1rem;text-align:center;height:100%">
      <div style="width:42px;height:42px;border-radius:50%;
                  background:{c['color']}22;border:1.5px solid {c['color']}88;
                  display:flex;align-items:center;justify-content:center;
                  font-family:Syne,sans-serif;font-weight:800;font-size:0.75rem;
                  color:{c['color']};margin:0 auto 0.75rem">{c['logo_char']}</div>
      <div style="font-family:Syne,sans-serif;font-size:0.95rem;font-weight:700;
                  color:#E8EDF5;margin-bottom:0.1rem">{c['name']}{badge}</div>
      <div style="font-size:0.6rem;color:{c['color']};text-transform:uppercase;
                  letter-spacing:0.1em;font-weight:600;margin-bottom:0.5rem">{c['category']}</div>
      <div style="font-size:0.65rem;color:rgba(232,237,245,0.4);line-height:1.5;
                  margin-bottom:0.75rem">{c['tagline']}</div>
      <div style="display:flex;flex-direction:column;gap:3px;align-items:flex-start;
                  font-size:0.62rem;color:rgba(232,237,245,0.35)">
        <span><span style="color:rgba(232,237,245,0.5);font-weight:600">BAA:</span> {c['baa']}</span>
        <span><span style="color:rgba(232,237,245,0.5);font-weight:600">Deploy:</span> {c['deploy']}</span>
        <span><span style="color:rgba(232,237,245,0.5);font-weight:600">Price:</span> {c['pricing']}</span>
      </div>
      {adv_badge}
    </div>
    """)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Feature matrix ────────────────────────────────────────────────────────────
matrix = compare(selected_keys)

st.markdown(
    "<div style='font-family:Syne,sans-serif;font-size:0.7rem;font-weight:700;"
    "letter-spacing:0.2em;text-transform:uppercase;color:rgba(232,237,245,0.4);"
    "margin-bottom:0.75rem'>Feature Comparison Matrix</div>",
    unsafe_allow_html=True,
)

# Build table HTML
col_w_feat = 28
col_w_each = int((100 - col_w_feat) / len(all_keys))

# Header row
hdr_cells = f'<th style="width:{col_w_feat}%;text-align:left;padding:0.5rem 0.75rem;font-size:0.6rem;color:rgba(0,255,178,0.5);font-weight:700;letter-spacing:0.12em;text-transform:uppercase;border-bottom:1px solid rgba(0,255,178,0.15)">Feature</th>'
for key in all_keys:
    c = COMPETITORS[key]
    is_fp = key == "freshpaint"
    hdr_cells += f'<th style="width:{col_w_each}%;text-align:center;padding:0.5rem 0.4rem;font-size:0.62rem;color:{c["color"]};font-weight:700;letter-spacing:0.05em;border-bottom:1px solid rgba(0,255,178,0.15);{"background:rgba(0,255,178,0.04);" if is_fp else ""}">{c["name"]}</th>'

table_html = f'<table style="width:100%;border-collapse:collapse;font-size:0.72rem"><thead><tr>{hdr_cells}</tr></thead><tbody>'

current_cat = None
for i, row in enumerate(matrix["rows"]):
    # Category separator
    if row["category"] != current_cat:
        current_cat = row["category"]
        table_html += f'<tr><td colspan="{len(all_keys)+1}" style="padding:0.6rem 0.75rem 0.3rem;font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:rgba(0,255,178,0.35);background:rgba(0,255,178,0.02);border-top:1px solid rgba(0,255,178,0.08)">{current_cat}</td></tr>'

    row_bg = "rgba(12,22,42,0.5)" if i % 2 == 0 else "transparent"
    cells = f'<td style="padding:0.5rem 0.75rem;color:rgba(232,237,245,0.7);background:{row_bg};border-bottom:1px solid rgba(255,255,255,0.025)" title="{row["desc"]}">{row["label"]}</td>'

    for key in all_keys:
        score = row["scores"][key]
        color = SCORE_COLOR[score]
        icon  = SCORE_ICON[score]
        is_fp = key == "freshpaint"
        fp_score = row["scores"]["freshpaint"]
        # Highlight cells where FP wins vs this competitor
        highlight = ""
        if not is_fp and fp_score > score:
            highlight = "background:rgba(212,43,74,0.06);"
        elif not is_fp and fp_score == score:
            highlight = ""
        cell_bg = f"rgba(0,255,178,0.04);{highlight}" if is_fp else highlight
        cells += (
            f'<td style="text-align:center;padding:0.5rem 0.4rem;{cell_bg}'
            f'border-bottom:1px solid rgba(255,255,255,0.025)">'
            f'<span style="color:{color};font-weight:700;font-size:0.85rem">{icon}</span>'
            f'<span style="color:{color};font-size:0.58rem;display:block;margin-top:1px;opacity:0.8">{["No","Partial","Yes"][score]}</span>'
            f'</td>'
        )
    table_html += f"<tr>{cells}</tr>"

table_html += "</tbody></table>"

# Legend
legend = ''.join([
    f'<span style="font-size:0.62rem;color:rgba(232,237,245,0.35);margin-right:1.25rem">'
    f'<span style="color:{SCORE_COLOR[s]};font-weight:700">{SCORE_ICON[s]}</span> = {["No","Partial","Yes"][s]}</span>'
    for s in [2, 1, 0]
])
legend += '<span style="font-size:0.62rem;color:rgba(212,43,74,0.5)">Red tint = Freshpaint advantage</span>'

st.html(f"""
<div style="background:rgba(12,22,42,0.6);border:1px solid rgba(0,255,178,0.1);
            border-radius:6px;overflow:hidden">
  {table_html}
  <div style="padding:0.5rem 0.75rem;border-top:1px solid rgba(255,255,255,0.04)">{legend}</div>
</div>
""")

# ── Objection handler ─────────────────────────────────────────────────────────
has_objections = any("key_objection" in COMPETITORS[k] for k in selected_keys)
if has_objections:
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:0.7rem;font-weight:700;"
        "letter-spacing:0.2em;text-transform:uppercase;color:rgba(232,237,245,0.4);"
        "margin-bottom:0.75rem'>Objection Handling</div>",
        unsafe_allow_html=True,
    )

    obj_cols = st.columns(len(selected_keys), gap="small")
    for col, key in zip(obj_cols, selected_keys):
        c = COMPETITORS[key]
        if "key_objection" not in c:
            continue
        with col:
            st.html(f"""
            <div style="background:rgba(12,22,42,0.7);border:1px solid {c['color']}33;
                        border-left:3px solid {c['color']};border-radius:4px;padding:1rem 1.1rem">
              <div style="font-size:0.58rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.12em;color:{c['color']};margin-bottom:0.4rem">
                When they say:
              </div>
              <div style="font-size:0.8rem;font-weight:700;color:#E8EDF5;
                          margin-bottom:0.75rem;line-height:1.4">
                "{c['key_objection']}"
              </div>
              <div style="font-size:0.58rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.12em;color:rgba(0,255,178,0.5);margin-bottom:0.4rem">
                You say:
              </div>
              <div style="font-size:0.72rem;color:rgba(232,237,245,0.7);line-height:1.6">
                {c['counter']}
              </div>
            </div>
            """)

# ── Honest gaps ───────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-family:Syne,sans-serif;font-size:0.7rem;font-weight:700;"
    "letter-spacing:0.2em;text-transform:uppercase;color:rgba(232,237,245,0.4);"
    "margin-bottom:0.75rem'>Where Competitors Have Real Strengths</div>",
    unsafe_allow_html=True,
)

gap_cols = st.columns(len(selected_keys), gap="small")
for col, key in zip(gap_cols, selected_keys):
    c = COMPETITORS[key]
    wins_html = "".join(
        f'<div style="font-size:0.68rem;color:rgba(232,237,245,0.6);padding:0.25rem 0;'
        f'border-bottom:1px solid rgba(255,255,255,0.04)">+ {w}</div>'
        for w in c.get("win_reasons", [])
    )
    verified_html = ""
    if c.get("last_verified"):
        links = " · ".join(f'<a href="{u}" target="_blank" style="color:rgba(0,255,178,0.4)">source {i + 1}</a>'
                           for i, u in enumerate(c.get("sources", [])))
        verified_html = (f'<div style="margin-top:0.4rem;font-size:0.58rem;color:rgba(232,237,245,0.25)">'
                         f'Researched {c["last_verified"]} from public sources · {links}</div>')
    col.html(f"""
    <div style="background:rgba(12,22,42,0.6);border:1px solid rgba(255,255,255,0.06);
                border-radius:4px;padding:1rem 1.1rem">
      <div style="font-family:Syne,sans-serif;font-size:0.8rem;font-weight:700;
                  color:{c['color']};margin-bottom:0.6rem">{c['name']}</div>
      {wins_html}
      <div style="margin-top:0.6rem;font-size:0.65rem;color:rgba(232,237,245,0.35);
                  line-height:1.55;border-top:1px solid rgba(255,255,255,0.04);
                  padding-top:0.5rem">
        <span style="color:rgba(212,43,74,0.6);font-weight:700">Gap: </span>{c['honest_gaps']}
      </div>
      {verified_html}
    </div>
    """)

# ── CTA ───────────────────────────────────────────────────────────────────────
total_adv = sum(len(freshpaint_advantages(k)) for k in selected_keys)
total_feat = len(FEATURES) * len(selected_keys)
if "ours_privacy" in selected_keys:
    summary_line = ("Ours Privacy matches Freshpaint's core architecture, so win on total cost at the tier the "
                    "prospect actually needs, healthcare track record, and references in their segment.")
else:
    summary_line = ("No other vendor in this comparison combines HIPAA BAA, automatic PHI redaction, ad signal "
                    "preservation, and healthcare-first support in a single deployment.")

st.html(f"""
<div style="background:linear-gradient(135deg,rgba(0,255,178,0.06),rgba(26,139,255,0.04));
            border:1px solid rgba(0,255,178,0.2);border-radius:8px;
            padding:1.75rem 2rem;margin-top:2rem;text-align:center">
  <div style="font-family:Syne,sans-serif;font-size:0.6rem;font-weight:700;
              letter-spacing:0.3em;text-transform:uppercase;
              color:rgba(0,255,178,0.5);margin-bottom:0.5rem">Summary</div>
  <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;
              color:#E8EDF5;margin-bottom:0.5rem">
    Freshpaint leads on <span style="color:#00FFB2">{total_adv} of {total_feat}</span> comparison points
  </div>
  <div style="font-size:0.75rem;color:rgba(232,237,245,0.4);max-width:560px;
              margin:0 auto 1.25rem;line-height:1.7">
    {summary_line}
  </div>
  <div style="display:inline-flex;gap:0.75rem;flex-wrap:wrap;justify-content:center">
    <a href="https://freshpaint.io/demo" target="_blank"
       style="background:#00FFB2;color:#05080F;font-family:IBM Plex Mono,monospace;
              font-size:0.75rem;font-weight:700;padding:0.6rem 1.5rem;
              border-radius:3px;text-decoration:none;letter-spacing:0.05em">
      Request a Demo
    </a>
    <a href="https://freshpaint.io/blog" target="_blank"
       style="background:transparent;color:#00FFB2;
              border:1px solid rgba(0,255,178,0.4);
              font-family:IBM Plex Mono,monospace;font-size:0.75rem;font-weight:700;
              padding:0.6rem 1.5rem;border-radius:3px;text-decoration:none;
              letter-spacing:0.05em">
      Read the Blog
    </a>
  </div>
</div>
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.html("""
<div style="text-align:center;padding:2rem 1rem;margin-top:3rem;
            border-top:1px solid rgba(255,255,255,0.05);
            font-size:0.62rem;color:rgba(232,237,245,0.18);line-height:1.8">
  <a href="https://freshpaint.io" style="color:rgba(0,255,178,0.35);text-decoration:none">Freshpaint</a>
  · HIPAA-Compliant Healthcare Analytics ·
  Competitor data maintained by Freshpaint sales team. Not legal advice.
</div>
""")
