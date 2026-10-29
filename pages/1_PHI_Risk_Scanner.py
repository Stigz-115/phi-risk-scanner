"""
PHI Risk Scanner — Streamlit Application
A free public tool that scans healthcare websites for HIPAA-risky tracking technologies.
"""

import streamlit as st
from scanner.scanner import scan_url
from scanner.pdf_report import generate_pdf
from scanner.registry import RISK_LABELS

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #05080F !important;
    color: #E8EDF5 !important;
}

.stApp {
    background: #05080F;
}

/* Subtle grid overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,255,178,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,178,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}

/* ── Hero header ── */
.phi-hero {
    background: linear-gradient(135deg, #05080F 0%, #0B1628 50%, #05080F 100%);
    border-bottom: 1px solid rgba(0,255,178,0.15);
    padding: 3rem 2rem 2.5rem;
    margin: 0 -4rem 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.phi-hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 500px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,255,178,0.08) 0%, transparent 70%);
    pointer-events: none;
}

.fp-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: rgba(0,255,178,0.6);
    margin-bottom: 0.6rem;
}

.phi-hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 0.6rem;
    color: #E8EDF5;
    letter-spacing: -0.02em;
}

.phi-hero h1 span {
    color: #00FFB2;
}

.phi-hero p {
    font-size: 0.85rem;
    color: rgba(232,237,245,0.55);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.6;
    letter-spacing: 0.01em;
}

/* ── Input area ── */
.scan-box {
    background: rgba(12, 22, 42, 0.8);
    border: 1px solid rgba(0,255,178,0.2);
    border-radius: 4px;
    padding: 2rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(8px);
}

.scan-box label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em;
    color: rgba(0,255,178,0.7) !important;
    text-transform: uppercase;
}

/* Override Streamlit text input */
.stTextInput input {
    background: rgba(5, 8, 15, 0.9) !important;
    border: 1px solid rgba(0,255,178,0.25) !important;
    border-radius: 3px !important;
    color: #E8EDF5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s !important;
}

.stTextInput input:focus {
    border-color: rgba(0,255,178,0.6) !important;
    box-shadow: 0 0 0 2px rgba(0,255,178,0.08) !important;
}

.stTextInput input::placeholder { color: rgba(232,237,245,0.25) !important; }

/* ── Buttons ── */
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
    cursor: pointer !important;
}

.stButton > button:hover {
    background: #00E5A0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,255,178,0.25) !important;
}

.stButton > button:active { transform: translateY(0) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #00FFB2 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border: 1px solid rgba(0,255,178,0.4) !important;
    border-radius: 3px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.15s !important;
}

.stDownloadButton > button:hover {
    background: rgba(0,255,178,0.08) !important;
    border-color: rgba(0,255,178,0.8) !important;
}

/* ── Risk score hero card ── */
.risk-hero {
    padding: 2.5rem 2rem;
    border-radius: 4px;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.risk-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 0.4rem;
}

.risk-score {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    margin-bottom: 0.8rem;
}

.risk-sub {
    font-size: 0.75rem;
    opacity: 0.6;
    letter-spacing: 0.05em;
}

/* ── Stat pills ── */
.stat-row {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.stat-pill {
    flex: 1;
    min-width: 110px;
    background: rgba(12,22,42,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px;
    padding: 1.1rem 1rem;
    text-align: center;
}

.stat-pill-num {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.stat-pill-label {
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(232,237,245,0.4);
}

/* ── Section headers ── */
.section-head {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: rgba(0,255,178,0.6);
    border-bottom: 1px solid rgba(0,255,178,0.1);
    padding-bottom: 0.5rem;
    margin: 2rem 0 1rem;
}

/* ── Tracker cards ── */
.tracker-card {
    background: rgba(12, 22, 42, 0.7);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 1.25rem 1.25rem 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
    transition: border-color 0.2s, transform 0.2s;
}

.tracker-card:hover {
    border-color: rgba(255,255,255,0.14);
    transform: translateX(2px);
}

.tracker-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 4px 0 0 4px;
}

.tc-critical::before { background: #FF2D55; }
.tc-high::before     { background: #FF8C00; }
.tc-medium::before   { background: #FFD60A; }
.tc-low::before      { background: #00E676; }

.tc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tc-name {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #E8EDF5;
}

.tc-company {
    font-size: 0.7rem;
    color: rgba(232,237,245,0.35);
    letter-spacing: 0.05em;
    margin-bottom: 0.6rem;
}

.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 2px;
}

.rb-critical { background: rgba(255,45,85,0.15);  color: #FF2D55; border: 1px solid rgba(255,45,85,0.3); }
.rb-high     { background: rgba(255,140,0,0.15);  color: #FF8C00; border: 1px solid rgba(255,140,0,0.3); }
.rb-medium   { background: rgba(255,214,10,0.12); color: #FFD60A; border: 1px solid rgba(255,214,10,0.3); }
.rb-low      { background: rgba(0,230,118,0.12);  color: #00E676; border: 1px solid rgba(0,230,118,0.3); }

.baa-tag {
    display: inline-flex;
    align-items: center;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    margin-right: 0.5rem;
}

.baa-no  { background: rgba(255,45,85,0.1);  color: #FF2D55; border: 1px solid rgba(255,45,85,0.2); }
.baa-yes { background: rgba(0,230,118,0.1);  color: #00E676; border: 1px solid rgba(0,230,118,0.2); }

.tc-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}

.tc-meta-note {
    font-size: 0.7rem;
    color: rgba(232,237,245,0.4);
    font-style: italic;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.phi-list {
    margin: 0.6rem 0;
    padding: 0;
    list-style: none;
}

.phi-list li {
    font-size: 0.75rem;
    color: rgba(232,237,245,0.65);
    padding: 0.15rem 0;
    padding-left: 1rem;
    position: relative;
}

.phi-list li::before {
    content: '·';
    position: absolute;
    left: 0.2rem;
    color: rgba(232,237,245,0.25);
}

.reg-list {
    margin: 0.5rem 0 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

.reg-pill {
    font-size: 0.62rem;
    background: rgba(255,140,0,0.08);
    color: #FF8C00;
    border: 1px solid rgba(255,140,0,0.2);
    border-radius: 2px;
    padding: 0.15rem 0.5rem;
    letter-spacing: 0.04em;
}

.tc-snippet {
    font-size: 0.65rem;
    color: rgba(0,255,178,0.4);
    background: rgba(0,255,178,0.04);
    border: 1px solid rgba(0,255,178,0.1);
    border-radius: 2px;
    padding: 0.3rem 0.6rem;
    margin-top: 0.6rem;
    font-style: normal;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* ── Clean state ── */
.clean-state {
    text-align: center;
    padding: 3rem 2rem;
    background: rgba(0,230,118,0.04);
    border: 1px solid rgba(0,230,118,0.15);
    border-radius: 4px;
    margin-bottom: 2rem;
}

.clean-state h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #00E676;
    margin-bottom: 0.5rem;
}

.clean-state p {
    font-size: 0.8rem;
    color: rgba(232,237,245,0.5);
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Regulation table ── */
.reg-row {
    display: flex;
    gap: 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    padding: 0.7rem 0;
    align-items: flex-start;
}

.reg-row:first-child { border-top: 1px solid rgba(255,255,255,0.04); }

.reg-name {
    font-size: 0.75rem;
    font-weight: 600;
    color: #E8EDF5;
    min-width: 200px;
    flex-shrink: 0;
}

.reg-desc {
    font-size: 0.73rem;
    color: rgba(232,237,245,0.45);
    line-height: 1.5;
}

/* ── GTM warning ── */
.gtm-warn {
    background: rgba(255,140,0,0.07);
    border: 1px solid rgba(255,140,0,0.25);
    border-left: 3px solid #FF8C00;
    border-radius: 4px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.75rem;
    color: rgba(232,237,245,0.7);
    line-height: 1.6;
}

.gtm-warn strong { color: #FF8C00; }

/* ── Error state ── */
.error-box {
    background: rgba(255,45,85,0.07);
    border: 1px solid rgba(255,45,85,0.25);
    border-left: 3px solid #FF2D55;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    font-size: 0.8rem;
    color: rgba(232,237,245,0.8);
    line-height: 1.6;
}

/* ── Footer ── */
.phi-footer {
    text-align: center;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    font-size: 0.68rem;
    color: rgba(232,237,245,0.25);
    line-height: 1.8;
    letter-spacing: 0.03em;
}

.phi-footer a { color: rgba(0,255,178,0.5); text-decoration: none; }
.phi-footer a:hover { color: rgba(0,255,178,0.9); }

/* ── Spinner override ── */
.stSpinner > div { border-top-color: #00FFB2 !important; }

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00FFB2, #00B4FF) !important;
}

/* ── Disclaimer strip ── */
.disclaimer {
    background: rgba(255,214,10,0.05);
    border: 1px solid rgba(255,214,10,0.15);
    border-radius: 3px;
    padding: 0.6rem 1rem;
    font-size: 0.68rem;
    color: rgba(255,214,10,0.6);
    letter-spacing: 0.03em;
    line-height: 1.5;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="phi-hero">
  <div class="fp-wordmark">Freshpaint · Free Tool</div>
  <h1>PHI <span>Risk</span> Scanner</h1>
  <p>
    Paste any healthcare website URL. We scan for tracking technologies
    that may be sending Protected Health Information to third parties
    without a HIPAA-compliant Business Associate Agreement.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Scan input ────────────────────────────────────────────────────────────────
st.markdown('<div class="scan-box">', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])
with col_input:
    url_input = st.text_input(
        "Healthcare website URL",
        placeholder="https://www.yourhealthcareenrollment.com",
        label_visibility="visible",
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    scan_clicked = st.button("Scan Now →", use_container_width=True)

st.markdown("""
<div style="font-size:0.68rem; color:rgba(232,237,245,0.3); margin-top:0.5rem; line-height:1.6">
  Scans publicly accessible HTML only · Does not execute JavaScript · Results are a screening tool, not legal advice
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Run scan ──────────────────────────────────────────────────────────────────
if scan_clicked and url_input.strip():
    with st.spinner("Scanning for trackers…"):
        result = scan_url(url_input.strip())
    st.session_state["scan_result"] = result
    st.session_state["scan_url_input"] = url_input.strip()

elif scan_clicked and not url_input.strip():
    st.markdown('<div class="error-box">Please enter a URL to scan.</div>', unsafe_allow_html=True)

# ── Display results ───────────────────────────────────────────────────────────
if "scan_result" in st.session_state:
    result = st.session_state["scan_result"]

    # ── Error state ────────────────────────────────────────────────────────
    if result.error:
        tip = ""
        if "403" in result.error or "blocking" in result.error:
            tip = (
                "<br><br><strong>Tips:</strong><br>"
                "· Try an interior page: <code>https://example.com/services</code> or <code>/about</code><br>"
                "· Some homepages sit behind Cloudflare — sub-pages often don't<br>"
                "· Make sure the URL is publicly accessible (no login required)"
            )
        st.markdown(
            f'<div class="error-box"><strong>Scan failed</strong><br>{result.error}{tip}</div>',
            unsafe_allow_html=True,
        )

    else:
        findings = result.findings
        overall = result.overall_risk

        RISK_BG = {
            "critical": "rgba(255,45,85,0.08)",
            "high":     "rgba(255,140,0,0.08)",
            "medium":   "rgba(255,214,10,0.06)",
            "low":      "rgba(0,230,118,0.06)",
            "clean":    "rgba(0,255,178,0.06)",
        }
        RISK_COLOR = {
            "critical": "#FF2D55",
            "high":     "#FF8C00",
            "medium":   "#FFD60A",
            "low":      "#00E676",
            "clean":    "#00FFB2",
        }

        # ── Risk hero ──────────────────────────────────────────────────────
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            lvl = f.get("risk_level", "low")
            counts[lvl] = counts.get(lvl, 0) + 1

        sub_msgs = {
            "critical": "Immediate action required. HIPAA breach risk is present.",
            "high":     "Significant risk. Review and remediate promptly.",
            "medium":   "Moderate risk. Audit tracker configuration.",
            "low":      "Minimal detected risk. Monitor periodically.",
            "clean":    "No known trackers detected via static analysis.",
        }

        color = RISK_COLOR[overall]
        bg    = RISK_BG[overall]
        label = RISK_LABELS.get(overall, overall.upper())
        sub   = sub_msgs.get(overall, "")

        st.markdown(f"""
        <div class="risk-hero" style="background:{bg}; border:1px solid {color}22;">
          <div class="risk-label" style="color:{color}">Overall Risk Score</div>
          <div class="risk-score" style="color:{color}">{label}</div>
          <div class="risk-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Stat pills ─────────────────────────────────────────────────────
        pill_data = [
            (str(len(findings)),        "#E8EDF5",  "Trackers Found"),
            (str(counts["critical"]),    "#FF2D55",  "Critical"),
            (str(counts["high"]),        "#FF8C00",  "High Risk"),
            (str(counts["medium"]),      "#FFD60A",  "Medium Risk"),
            (str(result.total_external_scripts), "rgba(232,237,245,0.3)", "External Scripts"),
        ]
        pills_html = '<div class="stat-row">'
        for num, color2, lbl in pill_data:
            pills_html += f"""
            <div class="stat-pill">
              <div class="stat-pill-num" style="color:{color2}">{num}</div>
              <div class="stat-pill-label">{lbl}</div>
            </div>"""
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)

        # ── GTM warning ────────────────────────────────────────────────────
        if result.gtm_container_ids:
            ids_str = ", ".join(result.gtm_container_ids)
            st.markdown(f"""
            <div class="gtm-warn">
              <strong>⚠ Google Tag Manager detected</strong> — Container(s): <code>{ids_str}</code><br>
              GTM acts as a container for other tags. Additional trackers may be firing that are
              not visible in page source. A dynamic scan is required to enumerate all GTM tags.
              GTM container contents inherit full access to all page data, including form inputs.
            </div>
            """, unsafe_allow_html=True)

        # ── Tracker findings ───────────────────────────────────────────────
        if findings:
            st.markdown('<div class="section-head">Tracker Findings</div>', unsafe_allow_html=True)

            for f in findings:
                risk = f["risk_level"]
                baa  = f["baa_available"]
                baa_class = "baa-yes" if baa else "baa-no"
                baa_text  = "BAA Available" if baa else "No BAA"

                phi_items = "".join(f"<li>{item}</li>" for item in f["phi_capture"])
                reg_pills = "".join(
                    f'<span class="reg-pill">{r[:55]}{"…" if len(r)>55 else ""}</span>'
                    for r in f["regulatory_mentions"][:3]
                )

                snippet = f.get("detected_snippet", "")
                via_map = {
                    "script_src": "Script src",
                    "inline_fingerprint": "Inline JS",
                    "pixel_img": "Tracking pixel",
                    "noscript_block": "Noscript block",
                }
                via_label = via_map.get(f.get("detected_via", ""), "Detected")

                st.markdown(f"""
                <div class="tracker-card tc-{risk}">
                  <div class="tc-header">
                    <div class="tc-name">{f['name']}</div>
                    <span class="risk-badge rb-{risk}">■ {RISK_LABELS.get(risk, risk.upper())}</span>
                  </div>
                  <div class="tc-company">{f['company']}</div>
                  <div class="tc-meta">
                    <span class="baa-tag {baa_class}">{baa_text}</span>
                    <span class="tc-meta-note">{f['baa_notes'][:100]}{'…' if len(f['baa_notes'])>100 else ''}</span>
                  </div>
                  <div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;
                              color:rgba(232,237,245,0.3);margin-bottom:0.25rem">PHI Captured</div>
                  <ul class="phi-list">{phi_items}</ul>
                  {'<div style="font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:rgba(232,237,245,0.3);margin-top:0.6rem;margin-bottom:0.25rem">Enforcement Context</div><ul class="reg-list">' + reg_pills + '</ul>' if reg_pills else ''}
                  <div class="tc-snippet">{via_label}: {snippet}</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            # Clean state
            st.markdown("""
            <div class="clean-state">
              <h2>✓ No Known Trackers Detected</h2>
              <p>
                Static analysis found no known third-party tracking technologies in this page's
                source code. Note: this scan does not execute JavaScript — dynamically injected
                trackers or tags inside a GTM container may not appear here.
                Consider a full dynamic scan for complete coverage.
              </p>
            </div>
            """, unsafe_allow_html=True)

        # ── Regulatory landscape ───────────────────────────────────────────
        st.markdown('<div class="section-head">Applicable Regulatory Framework</div>', unsafe_allow_html=True)

        regs = [
            ("HIPAA Privacy Rule (45 CFR §164.514)",
             "Disclosure of PHI to third-party trackers without a BAA is an impermissible disclosure, regardless of whether the data is used for advertising."),
            ("HHS OCR Bulletin — December 2022",
             "Explicitly identifies Meta Pixel and Google Analytics as tools that create HIPAA liability on healthcare websites. URL path parameters alone can constitute PHI."),
            ("HHS/FTC Joint Warning — July 2023",
             "Letters sent to 130 healthcare orgs warning that standard tracking pixels may violate HIPAA and FTC Act Section 5. Google and Meta are named."),
            ("FTC Health Breach Notification Rule",
             "Applies to health apps and websites not covered by HIPAA. Breach of health data triggers mandatory consumer notification."),
            ("CCPA/CPRA (California)",
             "Health data is 'sensitive personal information.' Consumers have the right to limit sharing. Applies to any org processing CA residents' data."),
            ("TX THIPA / WA My Health MY Data Act / VA VCDPA",
             "State-level laws expanding health privacy protections beyond HIPAA. Washington's MHMD law is notably broad and carries a private right of action."),
        ]

        rows_html = ""
        for name, desc in regs:
            rows_html += f"""
            <div class="reg-row">
              <div class="reg-name">{name}</div>
              <div class="reg-desc">{desc}</div>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)

        # ── Download + CTA ─────────────────────────────────────────────────
        st.markdown('<div class="section-head">Next Steps</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="disclaimer">
          ⚠  This report covers publicly accessible page source only.
          Dynamically injected trackers, GTM container contents, and post-login pages
          require a full dynamic scan. Results are a compliance screening tool, not legal advice.
        </div>
        """, unsafe_allow_html=True)

        dl_col, cta_col = st.columns([1, 1])

        with dl_col:
            try:
                pdf_bytes = generate_pdf(vars(result))
                st.download_button(
                    label="↓  Download Full PDF Report",
                    data=pdf_bytes,
                    file_name=f"phi_risk_report_{result.scan_timestamp.replace(' ','_').replace(':','-')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")

        with cta_col:
            st.markdown("""
            <div style="background:rgba(0,255,178,0.06); border:1px solid rgba(0,255,178,0.2);
                        border-radius:4px; padding:1.25rem; text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;
                          color:#00FFB2;margin-bottom:0.4rem">
                Replace every tracker. Keep all your data.
              </div>
              <div style="font-size:0.72rem;color:rgba(232,237,245,0.5);line-height:1.6;margin-bottom:0.8rem">
                Freshpaint intercepts and sanitizes tracking events before they reach
                non-compliant tools. Signed BAA included.
              </div>
              <a href="https://www.freshpaint.io" target="_blank"
                 style="font-size:0.7rem;font-weight:700;color:#00FFB2;letter-spacing:0.1em;
                        text-transform:uppercase;text-decoration:none;
                        border:1px solid rgba(0,255,178,0.4);padding:0.4rem 1rem;border-radius:2px">
                Talk to Freshpaint →
              </a>
            </div>
            """, unsafe_allow_html=True)

        # ── Scan metadata ──────────────────────────────────────────────────
        st.markdown(f"""
        <div style="font-size:0.65rem;color:rgba(232,237,245,0.2);margin-top:1.5rem;
                    text-align:right;letter-spacing:0.05em">
          Scanned: {result.canonical_url} &nbsp;·&nbsp;
          {result.scan_timestamp} &nbsp;·&nbsp;
          {result.duration_seconds}s &nbsp;·&nbsp;
          {result.total_external_scripts} external scripts checked
        </div>
        """, unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="display:flex; gap:1.5rem; flex-wrap:wrap; margin:1rem 0 2rem">
      <div style="flex:1;min-width:200px;background:rgba(12,22,42,0.6);border:1px solid rgba(255,255,255,0.06);
                  border-radius:4px;padding:1.25rem">
        <div style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;
                    color:#00FFB2;margin-bottom:0.5rem">What we detect</div>
        <div style="font-size:0.78rem;color:rgba(232,237,245,0.6);line-height:1.7">
          Meta Pixel · Google Analytics · TikTok Pixel · LinkedIn Insight · Twitter Pixel ·
          Hotjar · FullStory · Microsoft Clarity · HubSpot · Google Tag Manager ·
          Segment · Heap · Mixpanel · Amplitude · 15 more…
        </div>
      </div>
      <div style="flex:1;min-width:200px;background:rgba(12,22,42,0.6);border:1px solid rgba(255,255,255,0.06);
                  border-radius:4px;padding:1.25rem">
        <div style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;
                    color:#00FFB2;margin-bottom:0.5rem">What you get</div>
        <div style="font-size:0.78rem;color:rgba(232,237,245,0.6);line-height:1.7">
          Risk-rated tracker inventory · BAA availability status ·
          PHI capture breakdown · Enforcement case references · 
          Regulatory applicability map · Downloadable PDF report
        </div>
      </div>
      <div style="flex:1;min-width:200px;background:rgba(12,22,42,0.6);border:1px solid rgba(255,255,255,0.06);
                  border-radius:4px;padding:1.25rem">
        <div style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;
                    color:#00FFB2;margin-bottom:0.5rem">Why it matters</div>
        <div style="font-size:0.78rem;color:rgba(232,237,245,0.6);line-height:1.7">
          HHS OCR has explicitly flagged Meta Pixel and Google Analytics as HIPAA risks.
          Class-action settlements have exceeded $12M. The FTC has levied $7.8M+ in fines.
          The exposure is real — and usually fixable in days.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="phi-footer">
  <a href="https://freshpaint.io">Freshpaint</a> &nbsp;·&nbsp;
  Privacy-Compliant Healthcare Analytics &nbsp;·&nbsp;
  <a href="https://freshpaint.io/blog">Blog</a> &nbsp;·&nbsp;
  <a href="https://freshpaint.io/privacy">Privacy</a>
  <br>
  This tool performs static HTML analysis only. It does not execute JavaScript, submit forms,
  or access authenticated content. Results are a compliance screening tool and do not constitute
  legal advice. Consult qualified legal counsel for HIPAA compliance decisions.
</div>
""", unsafe_allow_html=True)
