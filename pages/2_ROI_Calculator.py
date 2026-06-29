"""
ROI Impact Calculator — "What does going dark actually cost?"
Models the annual revenue impact of removing tracking pixels without replacing them.
"""

import streamlit as st
import plotly.graph_objects as go

# ── CSS (same design system as PHI Risk Scanner) ──────────────────────────────
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
    position: fixed; top:0; left:0; right:0; bottom:0;
    background-image:
        linear-gradient(rgba(0,255,178,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,178,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none; z-index: 0;
}
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
.block-container { padding-top: 0 !important; max-width: 1200px !important; }

/* ── Hero ── */
.roi-hero {
    background: linear-gradient(135deg, #05080F 0%, #0B1628 50%, #05080F 100%);
    border-bottom: 1px solid rgba(0,255,178,0.15);
    padding: 2.8rem 2rem 2.2rem;
    margin: 0 -4rem 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.roi-hero::before {
    content: '';
    position: absolute; top:-60px; left:50%; transform:translateX(-50%);
    width:500px; height:200px;
    background: radial-gradient(ellipse, rgba(0,255,178,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.fp-wordmark {
    font-family: 'Syne', sans-serif; font-size:0.7rem; font-weight:700;
    letter-spacing:0.35em; text-transform:uppercase;
    color:rgba(0,255,178,0.6); margin-bottom:0.6rem;
}
.roi-hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.2rem); font-weight:800;
    line-height:1.1; margin:0 0 0.6rem; color:#E8EDF5; letter-spacing:-0.02em;
}
.roi-hero h1 span { color:#00FFB2; }
.roi-hero p {
    font-size:0.83rem; color:rgba(232,237,245,0.5);
    max-width:560px; margin:0 auto; line-height:1.7;
}

/* ── Input panel ── */
.input-panel {
    background: rgba(12,22,42,0.75);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px;
    padding: 1.5rem;
    height: 100%;
}
.panel-title {
    font-family: 'Syne', sans-serif; font-size:0.65rem; font-weight:700;
    letter-spacing:0.3em; text-transform:uppercase;
    color:rgba(0,255,178,0.6);
    border-bottom: 1px solid rgba(0,255,178,0.1);
    padding-bottom: 0.6rem; margin-bottom:1.2rem;
}

/* ── Streamlit input overrides ── */
.stSlider > div > div > div { background: rgba(0,255,178,0.15) !important; }
.stSlider [data-testid="stThumbValue"] { color: #00FFB2 !important; }
div[data-testid="stSlider"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: rgba(232,237,245,0.45) !important;
}
.stNumberInput input {
    background: rgba(5,8,15,0.9) !important;
    border: 1px solid rgba(0,255,178,0.2) !important;
    border-radius: 3px !important;
    color: #E8EDF5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stSelectbox > div > div {
    background: rgba(5,8,15,0.9) !important;
    border: 1px solid rgba(0,255,178,0.2) !important;
    border-radius: 3px !important;
    color: #E8EDF5 !important;
}

/* ── Result cards ── */
.result-hero {
    background: rgba(0,255,178,0.06);
    border: 1px solid rgba(0,255,178,0.25);
    border-radius: 4px;
    padding: 1.8rem;
    text-align: center;
    margin-bottom: 1rem;
}
.result-label {
    font-size: 0.65rem; letter-spacing:0.2em; text-transform:uppercase;
    color:rgba(0,255,178,0.6); margin-bottom:0.4rem;
}
.result-value {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 4vw, 3.4rem);
    font-weight: 800; line-height:1; color:#00FFB2;
    letter-spacing: -0.02em;
}
.result-sub { font-size:0.72rem; color:rgba(232,237,245,0.4); margin-top:0.4rem; }

.metric-card {
    background: rgba(12,22,42,0.8);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 0.6rem;
    position: relative;
}
.metric-card::before {
    content: '';
    position: absolute; left:0; top:0; bottom:0; width:3px;
    border-radius: 4px 0 0 4px;
}
.mc-roas::before   { background: #FF2D55; }
.mc-attr::before   { background: #FF8C00; }
.mc-rmkt::before   { background: #FFD60A; }
.mc-total::before  { background: #00FFB2; }

.mc-label {
    font-size: 0.65rem; letter-spacing:0.12em; text-transform:uppercase;
    color:rgba(232,237,245,0.35); margin-bottom:0.25rem;
}
.mc-value {
    font-family: 'Syne', sans-serif; font-size:1.4rem; font-weight:800; line-height:1;
}
.mc-desc { font-size:0.7rem; color:rgba(232,237,245,0.4); margin-top:0.25rem; line-height:1.5; }

/* ── ROI callout ── */
.roi-callout {
    background: rgba(0,255,178,0.05);
    border: 1px solid rgba(0,255,178,0.2);
    border-radius: 4px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}
.roi-stat { text-align:center; flex:1; min-width:100px; }
.roi-stat-num {
    font-family: 'Syne', sans-serif; font-size:2.2rem; font-weight:800;
    color:#00FFB2; line-height:1;
}
.roi-stat-label { font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
    color:rgba(232,237,245,0.35); margin-top:0.3rem; }

/* ── Divider ── */
.section-head {
    font-family: 'Syne', sans-serif; font-size:0.65rem; font-weight:700;
    letter-spacing:0.3em; text-transform:uppercase;
    color:rgba(0,255,178,0.6);
    border-bottom: 1px solid rgba(0,255,178,0.1);
    padding-bottom:0.5rem; margin:2rem 0 1rem;
}

/* ── Assumption strip ── */
.assumption-strip {
    background: rgba(255,214,10,0.04);
    border: 1px solid rgba(255,214,10,0.12);
    border-radius: 3px;
    padding: 0.6rem 1rem;
    font-size: 0.67rem;
    color: rgba(255,214,10,0.55);
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* ── CTA ── */
.cta-block {
    background: rgba(12,22,42,0.8);
    border: 1px solid rgba(0,255,178,0.2);
    border-radius: 4px;
    padding: 2rem;
    text-align: center;
    margin-top: 2rem;
}

/* ── Footer ── */
.phi-footer {
    text-align:center; padding:2rem 1rem; margin-top:3rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    font-size:0.65rem; color:rgba(232,237,245,0.2); line-height:1.8; letter-spacing:0.03em;
}
.phi-footer a { color:rgba(0,255,178,0.4); text-decoration:none; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="roi-hero">
  <div class="fp-wordmark">Freshpaint · ROI Calculator</div>
  <h1>What does <span>"going dark"</span> cost?</h1>
  <p>
    Healthcare organizations removing trackers without replacing them lose
    algorithmic optimization, attribution clarity, and remarketing reach.
    Quantify the annual revenue impact — and the ROI of fixing it.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Model constants (industry benchmarks) ─────────────────────────────────────
ORG_PROFILES = {
    "Digital Health / DTC":       {"roas_mult": 1.30, "attr_mult": 1.20, "label": "high pixel dependency"},
    "Telehealth":                  {"roas_mult": 1.35, "attr_mult": 1.25, "label": "high pixel dependency"},
    "Specialty Practice / Group":  {"roas_mult": 1.10, "attr_mult": 1.05, "label": "medium pixel dependency"},
    "Hospital / Health System":    {"roas_mult": 0.90, "attr_mult": 1.10, "label": "lower pixel dependency"},
    "Payer / Insurance":           {"roas_mult": 1.05, "attr_mult": 1.30, "label": "attribution-heavy"},
}

# ── Layout: inputs left, results right ───────────────────────────────────────
left, right = st.columns([1, 1.25], gap="large")

with left:
    st.markdown('<div class="panel-title">Your Numbers</div>', unsafe_allow_html=True)

    monthly_spend = st.number_input(
        "Monthly ad spend ($)",
        min_value=1_000, max_value=5_000_000,
        value=50_000, step=5_000,
        help="Total monthly digital advertising budget across all channels",
    )

    org_type = st.selectbox(
        "Organization type",
        options=list(ORG_PROFILES.keys()),
        index=0,
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title" style="margin-top:1rem">Channel Mix</div>', unsafe_allow_html=True)

    google_pct = st.slider("Google Ads  %", 0, 100, 40, 5,
        help="Percentage of budget on Google Search/Display/YouTube")
    meta_pct   = st.slider("Meta (Facebook/Instagram)  %", 0, 100, 30, 5,
        help="Percentage of budget on Facebook/Instagram ads")
    other_pct  = max(0, 100 - google_pct - meta_pct)
    st.markdown(
        f'<div style="font-size:0.7rem;color:rgba(232,237,245,0.35);margin-top:-0.5rem;margin-bottom:0.5rem">'
        f'Other channels (TikTok, LinkedIn, Programmatic): <strong style="color:rgba(232,237,245,0.6)">{other_pct}%</strong></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-title" style="margin-top:1.5rem">Assumptions</div>', unsafe_allow_html=True)

    remarketing_pct = st.slider(
        "Budget on remarketing / retargeting  %", 0, 60, 25, 5,
        help="Portion of your budget targeting people who already visited your site",
    )
    patient_ltv = st.number_input(
        "Average patient lifetime value ($)",
        min_value=100, max_value=100_000,
        value=2_500, step=100,
        help="Average revenue per patient over their care relationship",
    )

    st.markdown('<div class="panel-title" style="margin-top:1.5rem">Sensitivity</div>', unsafe_allow_html=True)

    roas_deg_pct = st.slider(
        "ROAS degradation without signals  %", 5, 40, 20, 1,
        help="How much worse your campaigns perform without conversion signal data. "
             "Industry benchmark: 15–25%. Higher if you rely on Smart Bidding.",
    )
    attr_waste_pct = st.slider(
        "Budget waste from attribution blindness  %", 5, 30, 15, 1,
        help="Extra spend wasted when you can't tell which channels actually drive results. "
             "Forrester benchmark: 15–20%.",
    )
    remarketing_lift = st.slider(
        "Remarketing conversion lift vs. cold  %", 50, 400, 200, 25,
        help="How much better remarketing converts vs. cold prospecting. "
             "Healthcare benchmark: 2–4x (= 100–300% lift).",
    )

    freshpaint_cost = st.slider(
        "Freshpaint annual cost ($)",
        min_value=15_000, max_value=200_000,
        value=40_000, step=5_000,
        help="Use your quoted price or a typical range: $25K–$150K/year",
    )

# ── Calculations ──────────────────────────────────────────────────────────────
profile    = ORG_PROFILES[org_type]
annual_spend = monthly_spend * 12

pixel_fraction  = (google_pct + meta_pct) / 100
pixel_spend_ann = annual_spend * pixel_fraction

roas_loss = pixel_spend_ann * (roas_deg_pct / 100) * profile["roas_mult"]

attr_loss = annual_spend * (attr_waste_pct / 100) * profile["attr_mult"]

rmkt_spend_ann      = annual_spend * (remarketing_pct / 100)
rmkt_lift_factor    = remarketing_lift / 100
rmkt_loss           = rmkt_spend_ann * rmkt_lift_factor / (1 + rmkt_lift_factor)

total_dark_cost = roas_loss + attr_loss + rmkt_loss

net_savings     = total_dark_cost - freshpaint_cost
roi_multiple    = total_dark_cost / freshpaint_cost if freshpaint_cost > 0 else 0
payback_months  = (freshpaint_cost / (total_dark_cost / 12)) if total_dark_cost > 0 else 0

# Patients lost estimate
blended_deg = (roas_loss + rmkt_loss) / annual_spend if annual_spend > 0 else 0
patients_lost_est = (annual_spend * blended_deg) / patient_ltv if patient_ltv > 0 else 0

# ── Results panel ─────────────────────────────────────────────────────────────
with right:
    # Hero number
    st.markdown(f"""
    <div class="result-hero">
      <div class="result-label">Annual cost of going dark</div>
      <div class="result-value">${total_dark_cost:,.0f}</div>
      <div class="result-sub">
        based on ${monthly_spend:,}/mo spend · {org_type}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Three cost drivers
    st.markdown(f"""
    <div class="metric-card mc-roas">
      <div class="mc-label">ROAS Signal Degradation</div>
      <div class="mc-value" style="color:#FF2D55">${roas_loss:,.0f}<span style="font-size:0.9rem;color:rgba(232,237,245,0.3)">/yr</span></div>
      <div class="mc-desc">
        Without conversion signals, Google Smart Bidding and Meta Advantage+ lose optimization data.
        Applied to {google_pct + meta_pct}% of pixel-dependent spend · {roas_deg_pct}% degradation rate
        · {profile["roas_mult"]:.1f}x {profile["label"]} multiplier.
      </div>
    </div>

    <div class="metric-card mc-attr">
      <div class="mc-label">Attribution Blindness Waste</div>
      <div class="mc-value" style="color:#FF8C00">${attr_loss:,.0f}<span style="font-size:0.9rem;color:rgba(232,237,245,0.3)">/yr</span></div>
      <div class="mc-desc">
        Without cross-channel attribution, budget flows to last-click channels (brand search)
        and away from upper-funnel channels that actually drive volume.
        {attr_waste_pct}% waste rate · Forrester benchmark: 15–20%.
      </div>
    </div>

    <div class="metric-card mc-rmkt">
      <div class="mc-label">Remarketing Audience Loss</div>
      <div class="mc-value" style="color:#FFD60A">${rmkt_loss:,.0f}<span style="font-size:0.9rem;color:rgba(232,237,245,0.3)">/yr</span></div>
      <div class="mc-desc">
        Remarketing converts {remarketing_lift}% better than cold prospecting.
        Without pixel data, retargeting audiences degrade within 30–90 days.
        {remarketing_pct}% of budget on remarketing.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ROI callout
    payback_str = f"{payback_months:.1f} mo" if payback_months < 12 else f"{payback_months/12:.1f} yr"
    net_str     = f"${net_savings:,.0f}" if net_savings >= 0 else f"-${abs(net_savings):,.0f}"
    net_color   = "#00FFB2" if net_savings >= 0 else "#FF2D55"

    st.markdown(f"""
    <div class="roi-callout">
      <div class="roi-stat">
        <div class="roi-stat-num">{roi_multiple:.1f}x</div>
        <div class="roi-stat-label">Freshpaint ROI</div>
      </div>
      <div class="roi-stat">
        <div class="roi-stat-num" style="color:{net_color}">{net_str}</div>
        <div class="roi-stat-label">Net Annual Savings</div>
      </div>
      <div class="roi-stat">
        <div class="roi-stat-num">{payback_str}</div>
        <div class="roi-stat-label">Payback Period</div>
      </div>
      <div class="roi-stat">
        <div class="roi-stat-num">~{int(patients_lost_est):,}</div>
        <div class="roi-stat-label">Patients Lost/yr</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">Cost Breakdown vs. Fix</div>', unsafe_allow_html=True)

fig = go.Figure()

# Stacked cost of going dark
fig.add_trace(go.Bar(
    name="ROAS Signal Loss",
    x=["Cost of Going Dark"],
    y=[roas_loss],
    marker_color="#FF2D55",
    text=[f"${roas_loss:,.0f}"],
    textposition="inside",
    textfont=dict(color="white", size=11, family="IBM Plex Mono"),
))
fig.add_trace(go.Bar(
    name="Attribution Waste",
    x=["Cost of Going Dark"],
    y=[attr_loss],
    marker_color="#FF8C00",
    text=[f"${attr_loss:,.0f}"],
    textposition="inside",
    textfont=dict(color="white", size=11, family="IBM Plex Mono"),
))
fig.add_trace(go.Bar(
    name="Remarketing Loss",
    x=["Cost of Going Dark"],
    y=[rmkt_loss],
    marker_color="#FFD60A",
    text=[f"${rmkt_loss:,.0f}"],
    textposition="inside",
    textfont=dict(color="#05080F", size=11, family="IBM Plex Mono"),
))
# Freshpaint cost
fig.add_trace(go.Bar(
    name="Freshpaint Annual Cost",
    x=["Freshpaint Fix"],
    y=[freshpaint_cost],
    marker_color="#00FFB2",
    text=[f"${freshpaint_cost:,.0f}"],
    textposition="inside",
    textfont=dict(color="#05080F", size=11, family="IBM Plex Mono"),
))
# Net savings annotation bar
if net_savings > 0:
    fig.add_trace(go.Bar(
        name="Net Savings",
        x=["Freshpaint Fix"],
        y=[net_savings],
        marker_color="rgba(0,255,178,0.12)",
        marker_line=dict(color="rgba(0,255,178,0.4)", width=1),
        text=[f"${net_savings:,.0f} saved"],
        textposition="inside",
        textfont=dict(color="#00FFB2", size=10, family="IBM Plex Mono"),
    ))

fig.update_layout(
    barmode="stack",
    plot_bgcolor="#05080F",
    paper_bgcolor="#05080F",
    font=dict(family="IBM Plex Mono", color="#E8EDF5"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(size=10), bgcolor="rgba(0,0,0,0)",
    ),
    margin=dict(l=20, r=20, t=40, b=20),
    height=360,
    yaxis=dict(
        tickprefix="$", tickformat=",.0f",
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=10),
    ),
    xaxis=dict(tickfont=dict(size=11, family="Syne")),
    showlegend=True,
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Benchmark assumptions strip ───────────────────────────────────────────────
st.markdown("""
<div class="assumption-strip">
  ⚠  Benchmarks: ROAS degradation from Google/Meta internal healthcare data (2023) ·
  Attribution waste from Forrester "State of Marketing Attribution" ·
  Remarketing lift from WordStream Healthcare Advertising Benchmarks.
  Adjust sliders to reflect your observed performance. This model is directional, not a guarantee.
</div>
""", unsafe_allow_html=True)

# ── Detailed breakdown table ──────────────────────────────────────────────────
st.markdown('<div class="section-head">Full Model Detail</div>', unsafe_allow_html=True)

rows = [
    ("Annual ad spend",             f"${annual_spend:,.0f}",    f"${monthly_spend:,}/mo × 12"),
    ("Pixel-dependent spend",       f"${pixel_spend_ann:,.0f}", f"{google_pct + meta_pct}% of total (Google + Meta)"),
    ("ROAS degradation",            f"{roas_deg_pct}%",         f"{profile['roas_mult']:.1f}x org multiplier ({profile['label']})"),
    ("  → Annual ROAS loss",        f"${roas_loss:,.0f}",       "Pixel spend × degradation rate × org multiplier"),
    ("Attribution waste rate",      f"{attr_waste_pct}%",       f"{profile['attr_mult']:.1f}x org multiplier"),
    ("  → Annual attribution loss", f"${attr_loss:,.0f}",       "Total spend × waste rate × org multiplier"),
    ("Remarketing spend",           f"${rmkt_spend_ann:,.0f}",  f"{remarketing_pct}% of total budget"),
    ("Remarketing lift",            f"{remarketing_lift}%",     "Conversion rate advantage over cold prospecting"),
    ("  → Annual remarketing loss", f"${rmkt_loss:,.0f}",       "Efficiency value of lost remarketing audiences"),
    ("Total annual dark cost",      f"${total_dark_cost:,.0f}", "Sum of all three loss drivers"),
    ("Freshpaint annual cost",      f"${freshpaint_cost:,.0f}", "Adjust slider above"),
    ("Net annual savings",          net_str,                    "Dark cost minus Freshpaint investment"),
    ("ROI multiple",                f"{roi_multiple:.1f}x",     "Dark cost ÷ Freshpaint cost"),
    ("Payback period",              payback_str,                "Freshpaint cost ÷ monthly dark cost"),
    ("Est. patients lost/yr",       f"~{int(patients_lost_est):,}", f"Efficiency loss ÷ ${patient_ltv:,} LTV"),
]

table_html = """
<table style="width:100%;border-collapse:collapse;font-size:0.75rem">
  <thead>
    <tr style="border-bottom:1px solid rgba(0,255,178,0.2)">
      <th style="text-align:left;padding:0.5rem 0.75rem;color:rgba(0,255,178,0.6);
                 letter-spacing:0.1em;font-size:0.62rem;text-transform:uppercase">Line Item</th>
      <th style="text-align:right;padding:0.5rem 0.75rem;color:rgba(0,255,178,0.6);
                 letter-spacing:0.1em;font-size:0.62rem;text-transform:uppercase">Value</th>
      <th style="text-align:left;padding:0.5rem 0.75rem;color:rgba(0,255,178,0.6);
                 letter-spacing:0.1em;font-size:0.62rem;text-transform:uppercase">Basis</th>
    </tr>
  </thead>
  <tbody>
"""
for i, (label, value, basis) in enumerate(rows):
    bg = "rgba(12,22,42,0.6)" if i % 2 == 0 else "transparent"
    is_total = "total" in label.lower() or "ROI" in label or "payback" in label.lower() or "net" in label.lower() or "patients" in label.lower()
    val_color = "#00FFB2" if is_total else "#E8EDF5"
    weight = "700" if is_total else "400"
    table_html += f"""
    <tr style="background:{bg};border-bottom:1px solid rgba(255,255,255,0.03)">
      <td style="padding:0.45rem 0.75rem;color:rgba(232,237,245,0.6)">{label}</td>
      <td style="padding:0.45rem 0.75rem;text-align:right;color:{val_color};font-weight:{weight};
                 font-family:'Syne',sans-serif">{value}</td>
      <td style="padding:0.45rem 0.75rem;color:rgba(232,237,245,0.3);font-size:0.68rem">{basis}</td>
    </tr>"""
table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cta-block">
  <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;
              color:#E8EDF5;margin-bottom:0.5rem">
    At your spend level, Freshpaint pays for itself in
    <span style="color:#00FFB2">{payback_str}</span>.
  </div>
  <div style="font-size:0.78rem;color:rgba(232,237,245,0.45);max-width:560px;
              margin:0 auto 1.2rem;line-height:1.7">
    Freshpaint intercepts tracking events, strips PHI, and routes clean data to your existing
    ad platforms and analytics stack — so your campaigns keep their optimization signals
    and your attribution stays intact. BAA included.
  </div>
  <a href="https://www.freshpaint.io" target="_blank"
     style="display:inline-block;font-size:0.75rem;font-weight:700;color:#05080F;
            background:#00FFB2;padding:0.7rem 2rem;border-radius:3px;text-decoration:none;
            letter-spacing:0.1em;text-transform:uppercase">
    Talk to Freshpaint →
  </a>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="phi-footer">
  <a href="https://freshpaint.io">Freshpaint</a> · HIPAA-Compliant Healthcare Analytics ·
  <a href="https://freshpaint.io/blog">Blog</a><br>
  Model uses industry benchmark ranges. Actual impact varies by org, channel mix, and campaign maturity.
  Not financial or legal advice.
</div>
""", unsafe_allow_html=True)
