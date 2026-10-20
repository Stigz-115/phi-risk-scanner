"""
State Privacy Exposure Scorecard — interactive US map + per-state risk breakdown.
Shows which state privacy laws apply to the prospect's geographic footprint
and aggregates an overall exposure score with Freshpaint remediation context.
"""

import streamlit as st
import plotly.graph_objects as go
from scanner.state_privacy import (
    STATE_DATA, NO_LAW_STATES, ALL_STATES, score_all_states, aggregate_exposure,
    LAST_REVIEWED, STATUS_LABELS, days_since_review, load_watch
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
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,255,178,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,178,0.02) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none; z-index: 0;
}
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
.block-container { padding-top: 0 !important; max-width: 1200px !important; }
div[data-testid="stMultiSelect"] > div { background: #0C1628 !important; border: 1px solid rgba(0,255,178,0.2) !important; border-radius: 4px; }
div[data-testid="stMultiSelect"] span { background: rgba(0,255,178,0.1) !important; color: #00FFB2 !important; }
div[data-testid="stSelectbox"] > div { background: #0C1628 !important; }
.stButton > button { background: transparent !important; border: 1px solid rgba(0,255,178,0.4) !important; color: #00FFB2 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important; border-radius: 3px !important; }
.stButton > button:hover { background: rgba(0,255,178,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.html("""
<div style="background:linear-gradient(135deg,#05080F 0%,#0B1628 50%,#05080F 100%);
            border-bottom:1px solid rgba(0,255,178,0.12);
            padding:2.5rem 2rem 2rem;margin:0 -4rem 2rem;text-align:center;position:relative;overflow:hidden">
  <div style="position:absolute;top:-50px;left:50%;transform:translateX(-50%);
              width:600px;height:180px;
              background:radial-gradient(ellipse,rgba(0,255,178,0.06) 0%,transparent 70%);
              pointer-events:none"></div>
  <div style="font-family:Syne,sans-serif;font-size:0.65rem;font-weight:700;
              letter-spacing:0.35em;text-transform:uppercase;color:rgba(0,255,178,0.6);margin-bottom:0.5rem">
    Freshpaint · Pre-Sales Intelligence
  </div>
  <h1 style="font-family:Syne,sans-serif;font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;
             line-height:1.1;margin:0 0 0.5rem;color:#E8EDF5;letter-spacing:-0.02em">
    State Privacy <span style="color:#00FFB2">Exposure</span> Scorecard
  </h1>
  <p style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:rgba(232,237,245,0.45);
            max-width:600px;margin:0 auto;line-height:1.7">
    Select the states where your organization operates or targets patients.
    We'll map applicable privacy laws, score your regulatory exposure,
    and show where Freshpaint closes the gap.
  </p>
</div>
""")

# ── State selector ────────────────────────────────────────────────────────────
ALL_KNOWN = sorted(list(STATE_DATA.keys()) + NO_LAW_STATES)
STATE_NAMES = {abbr: ALL_STATES[abbr]["name"] for abbr in ALL_KNOWN}

# Build display options: "CA — California" sorted by name
OPTIONS = sorted(
    [f"{abbr} — {STATE_NAMES[abbr]}" for abbr in ALL_KNOWN],
    key=lambda x: x.split(" — ")[1]
)
ABBR_FROM_OPTION = {o: o.split(" — ")[0] for o in OPTIONS}

_ALL_SCORES = score_all_states()
_TOP5 = [a for a, _ in sorted(_ALL_SCORES.items(), key=lambda kv: kv[1]["score"], reverse=True)[:5]]
_IN_EFFECT = [a for a, d in STATE_DATA.items() if d.get("status") == "in_effect"]

_QUICK = {
    "Top 5 Risk States": _TOP5,
    "All Laws In Effect": _IN_EFFECT,
    "All Active Law States": list(STATE_DATA.keys()),
    "Clear All": [],
}


def _apply_quick_fill():
    choice = st.session_state.get("_sp_quick")
    if choice in _QUICK:
        st.session_state["_sp_states"] = [o for o in OPTIONS if ABBR_FROM_OPTION[o] in _QUICK[choice]]
    st.session_state["_sp_quick"] = "— Quick Add —"


col_sel, col_btn = st.columns([4, 1])
with col_sel:
    selected_options = st.multiselect(
        "States of operation",
        options=OPTIONS,
        key="_sp_states",
        placeholder="Select states where you operate, market, or serve patients…",
        label_visibility="collapsed",
    )
with col_btn:
    st.selectbox(
        "Quick fill",
        ["— Quick Add —", *_QUICK.keys()],
        key="_sp_quick",
        on_change=_apply_quick_fill,
        label_visibility="collapsed",
    )

selected_abbrs = [ABBR_FROM_OPTION[o] for o in selected_options]

# ── Data freshness + legislation watch ───────────────────────────────────────
_age = days_since_review()
_watch = load_watch()
_stale = _age is not None and _age > 45
_fresh_color = "#E8B80A" if _stale else "rgba(0,255,178,0.55)"
_watch_line = ""
if _watch:
    _n_moved = len(_watch.get("changed", []))
    _watch_line = (f" · Legislation watch run {_watch.get('generated_at', '')[:10]}: "
                   f"{_n_moved} tracked bill{'s' if _n_moved != 1 else ''} moved")
st.html(f"""
<div style="font-size:0.65rem;color:{_fresh_color};text-align:center;margin:0.25rem 0 0.5rem;
            letter-spacing:0.05em">
  State law data reviewed {LAST_REVIEWED}{' — review overdue' if _stale else ''}{_watch_line}
</div>
""")

if _watch.get("changed"):
    with st.expander(f"Legislation watch — {len(_watch['changed'])} bill(s) moved since last review"):
        for bill in _watch["changed"][:25]:
            st.markdown(
                f"**{bill.get('state')} {bill.get('number')}** — {bill.get('title', '')}  \n"
                f"Status: *{bill.get('status_label', '')}* · Last action {bill.get('last_action_date', '')}: "
                f"{bill.get('last_action', '')} · [LegiScan]({bill.get('url', '')})"
            )

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

# ── Map ───────────────────────────────────────────────────────────────────────
all_scores = _ALL_SCORES

# Build map data
map_abbrs, map_colors, map_hover, map_text = [], [], [], []
TIER_COLORS = {
    "critical": "#D42B4A",
    "high":     "#E8630A",
    "moderate": "#E8B80A",
    "low":      "#2A6049",
    "None":     "#111927",
}

for abbr, sc in all_scores.items():
    is_selected = abbr in selected_abbrs
    color = sc["color"] if is_selected else (
        sc["color"] + "44" if sc["tier"] != "None" else "#0C1628"
    )
    map_abbrs.append(abbr)
    map_colors.append(color)

    d = ALL_STATES.get(abbr, {})
    law = d.get("law", "No Active Law")
    eff = d.get("effective", "—")
    sel_marker = " ✓ SELECTED" if is_selected else ""
    map_hover.append(
        f"<b>{d.get('name', abbr)}</b>{sel_marker}<br>"
        f"<span style='color:#aaa'>{law}</span><br>"
        f"Risk Score: <b>{sc['score']}</b> / 100 &nbsp; [{sc['tier_label']}]<br>"
        f"Effective: {eff}"
    )
    map_text.append(abbr)

fig = go.Figure(go.Choropleth(
    locations=map_abbrs,
    z=[all_scores[a]["score"] for a in map_abbrs],
    locationmode="USA-states",
    colorscale=[
        [0.0,  "#0C1628"],
        [0.01, "#162640"],
        [0.3,  "#2A6049"],
        [0.55, "#E8B80A"],
        [0.75, "#E8630A"],
        [1.0,  "#D42B4A"],
    ],
    zmin=0, zmax=100,
    showscale=False,
    marker_line_color="rgba(0,255,178,0.15)",
    marker_line_width=0.8,
    hovertemplate="%{customdata}<extra></extra>",
    customdata=map_hover,
))

# Overlay selected states with border highlight
if selected_abbrs:
    sel_scores = [all_scores[a]["score"] for a in selected_abbrs]
    fig.add_trace(go.Choropleth(
        locations=selected_abbrs,
        z=sel_scores,
        locationmode="USA-states",
        colorscale=[
            [0.0,  "#162640"],
            [0.3,  "#2A6049"],
            [0.55, "#E8B80A"],
            [0.75, "#E8630A"],
            [1.0,  "#D42B4A"],
        ],
        zmin=0, zmax=100,
        showscale=False,
        marker_line_color="#00FFB2",
        marker_line_width=2.0,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=[map_hover[map_abbrs.index(a)] for a in selected_abbrs],
    ))

fig.update_layout(
    geo=dict(
        scope="usa",
        projection_type="albers usa",
        showlakes=False,
        showland=False,
        bgcolor="#05080F",
        framewidth=0,
    ),
    paper_bgcolor="#05080F",
    plot_bgcolor="#05080F",
    margin=dict(l=0, r=0, t=0, b=0),
    height=420,
    hoverlabel=dict(
        bgcolor="#0C1628",
        bordercolor="rgba(0,255,178,0.3)",
        font=dict(color="#E8EDF5", size=12),
    ),
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Legend ────────────────────────────────────────────────────────────────────
st.html("""
<div style="display:flex;gap:1.5rem;justify-content:center;margin:-0.5rem 0 1.5rem;flex-wrap:wrap">
  <span style="font-size:0.65rem;color:rgba(232,237,245,0.4)">
    <span style="display:inline-block;width:10px;height:10px;background:#D42B4A;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Critical (80–100)
  </span>
  <span style="font-size:0.65rem;color:rgba(232,237,245,0.4)">
    <span style="display:inline-block;width:10px;height:10px;background:#E8630A;border-radius:2px;margin-right:5px;vertical-align:middle"></span>High (55–79)
  </span>
  <span style="font-size:0.65rem;color:rgba(232,237,245,0.4)">
    <span style="display:inline-block;width:10px;height:10px;background:#E8B80A;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Moderate (30–54)
  </span>
  <span style="font-size:0.65rem;color:rgba(232,237,245,0.4)">
    <span style="display:inline-block;width:10px;height:10px;background:#2A6049;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Low (1–29)
  </span>
  <span style="font-size:0.65rem;color:rgba(232,237,245,0.4)">
    <span style="display:inline-block;width:10px;height:10px;background:#111927;border-radius:2px;margin-right:5px;vertical-align:middle"></span>No Active Law
  </span>
  <span style="font-size:0.65rem;color:rgba(0,255,178,0.6)">
    <span style="display:inline-block;width:10px;height:10px;border:2px solid #00FFB2;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Your selected states
  </span>
</div>
""")

# ── Scorecard (only if states selected) ──────────────────────────────────────
if not selected_abbrs:
    st.html("""
    <div style="text-align:center;padding:3rem 1rem;color:rgba(232,237,245,0.25);
                font-size:0.78rem;border:1px dashed rgba(0,255,178,0.1);border-radius:6px">
      Select states above to generate your exposure scorecard
    </div>
    """)
else:
    report = aggregate_exposure(selected_abbrs)

    TIER_BG = {
        "critical": "rgba(212,43,74,0.12)",
        "high":     "rgba(232,99,10,0.12)",
        "moderate": "rgba(232,184,10,0.12)",
        "low":      "rgba(42,96,73,0.15)",
        "none":     "rgba(255,255,255,0.04)",
    }
    TIER_BORDER = {
        "critical": "#D42B4A",
        "high":     "#E8630A",
        "moderate": "#E8B80A",
        "low":      "#2A6049",
        "none":     "rgba(255,255,255,0.1)",
    }
    tier = report["tier"]
    score = report["total_score"]
    bc = TIER_BG.get(tier, TIER_BG["none"])
    brd = TIER_BORDER.get(tier, TIER_BORDER["none"])
    tlabel = report["tier_label"]

    # ── Aggregate hero ────────────────────────────────────────────────────────
    st.html(f"""
    <div style="background:{bc};border:1px solid {brd};border-radius:8px;
                padding:2rem 2.5rem;margin-bottom:1.5rem;display:flex;
                align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1.5rem">
      <div>
        <div style="font-family:Syne,sans-serif;font-size:0.6rem;font-weight:700;
                    letter-spacing:0.3em;text-transform:uppercase;color:{brd};margin-bottom:0.35rem">
          Aggregate Exposure Score
        </div>
        <div style="font-family:Syne,sans-serif;font-size:3.5rem;font-weight:800;
                    color:#E8EDF5;line-height:1;margin-bottom:0.25rem">
          {score}<span style="font-size:1.5rem;color:rgba(232,237,245,0.35)">/100</span>
        </div>
        <div style="font-size:0.8rem;font-weight:700;color:{brd}">{tlabel}</div>
      </div>
      <div style="display:flex;gap:2.5rem;flex-wrap:wrap">
        <div style="text-align:center">
          <div style="font-size:2rem;font-weight:700;color:#D42B4A;font-family:Syne,sans-serif">{report['n_critical']}</div>
          <div style="font-size:0.6rem;color:rgba(232,237,245,0.4);text-transform:uppercase;letter-spacing:0.1em">Critical</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:2rem;font-weight:700;color:#E8630A;font-family:Syne,sans-serif">{report['n_high']}</div>
          <div style="font-size:0.6rem;color:rgba(232,237,245,0.4);text-transform:uppercase;letter-spacing:0.1em">High</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:2rem;font-weight:700;color:#E8B80A;font-family:Syne,sans-serif">{report['n_moderate']}</div>
          <div style="font-size:0.6rem;color:rgba(232,237,245,0.4);text-transform:uppercase;letter-spacing:0.1em">Moderate</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:2rem;font-weight:700;color:#00FFB2;font-family:Syne,sans-serif">{report['n_private_right']}</div>
          <div style="font-size:0.6rem;color:rgba(232,237,245,0.4);text-transform:uppercase;letter-spacing:0.1em">Sue-able</div>
        </div>
      </div>
    </div>
    """)

    # ── Per-state breakdown ───────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Syne,sans-serif;font-size:0.7rem;font-weight:700;"
        "letter-spacing:0.2em;text-transform:uppercase;color:rgba(232,237,245,0.4);"
        "margin-bottom:0.75rem'>State-by-State Breakdown</div>",
        unsafe_allow_html=True,
    )

    for b in report["breakdown"]:
        color = b["color"]
        tier_bg = TIER_BG.get(b["tier"], TIER_BG["none"])
        pr_badge = (
            '<span style="background:rgba(212,43,74,0.2);color:#D42B4A;'
            'font-size:0.58rem;font-weight:700;padding:2px 6px;border-radius:2px;'
            'letter-spacing:0.08em;text-transform:uppercase;margin-left:6px">'
            'Private Right of Action</span>'
            if b["private_right"] >= 2 else ""
        )
        tc_badge = (
            '<span style="background:rgba(232,99,10,0.2);color:#E8630A;'
            'font-size:0.58rem;font-weight:700;padding:2px 6px;border-radius:2px;'
            'letter-spacing:0.08em;text-transform:uppercase;margin-left:6px">'
            'Pixel/Tracker Coverage</span>'
            if b["tracker_coverage"] >= 2 else ""
        )

        st.html(f"""
        <div style="background:{tier_bg};border:1px solid {color}44;border-left:3px solid {color};
                    border-radius:4px;padding:1rem 1.25rem;margin-bottom:0.6rem">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;
                      gap:1rem;flex-wrap:wrap;margin-bottom:0.6rem">
            <div>
              <span style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;
                           color:#E8EDF5">{b['name']}</span>
              <span style="font-size:0.65rem;color:rgba(232,237,245,0.35);margin-left:8px">{b['abbr']}</span>
              {pr_badge}{tc_badge}
              <div style="font-size:0.7rem;color:rgba(232,237,245,0.5);margin-top:0.2rem">{b['law']}</div>
              <div style="font-size:0.6rem;color:rgba(232,237,245,0.35);margin-top:0.25rem">
                {b['status_label']} · Penalty: {b['penalty']} · HIPAA exemption: {b['hipaa_exemption']}
              </div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div style="font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;
                          color:{color};line-height:1">{b['score']}</div>
              <div style="font-size:0.6rem;color:{color};font-weight:700;
                          text-transform:uppercase;letter-spacing:0.1em">{b['tier_label']}</div>
              <div style="font-size:0.6rem;color:rgba(232,237,245,0.3);margin-top:2px">Effective: {b['effective']}</div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1.5rem">
            <div>
              <div style="font-size:0.58rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.1em;color:rgba(232,237,245,0.3);margin-bottom:2px">Key Risk</div>
              <div style="font-size:0.7rem;color:rgba(232,237,245,0.7);line-height:1.5">{b['key_risk']}</div>
            </div>
            <div>
              <div style="font-size:0.58rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.1em;color:rgba(0,255,178,0.4);margin-bottom:2px">Freshpaint Mitigation</div>
              <div style="font-size:0.7rem;color:rgba(232,237,245,0.7);line-height:1.5">{b['freshpaint']}</div>
            </div>
          </div>
        </div>
        """)

    # ── Risk dimension radar ──────────────────────────────────────────────────
    if len(report["breakdown"]) >= 2:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:0.7rem;font-weight:700;"
            "letter-spacing:0.2em;text-transform:uppercase;color:rgba(232,237,245,0.4);"
            "margin-bottom:0.75rem'>Risk Dimension Comparison</div>",
            unsafe_allow_html=True,
        )

        DIM_LABELS = ["Health Law\nSpecificity", "Private Right\nof Action", "AG\nEnforcement",
                      "Penalty\nExposure", "Tracker\nCoverage"]
        DIM_KEYS = ["health_specificity", "private_right", "enforcement", "penalty_exposure", "tracker_coverage"]

        bar_fig = go.Figure()
        PALETTE = ["#00FFB2", "#D42B4A", "#E8630A", "#E8B80A", "#1A8BFF", "#A855F7"]

        # Only show top 6 states in bar chart to keep it readable
        top_states = report["breakdown"][:6]

        for i, b in enumerate(top_states):
            d = STATE_DATA.get(b["abbr"], {})
            vals = [d.get(k, 0) for k in DIM_KEYS]
            bar_fig.add_trace(go.Bar(
                name=b["abbr"],
                x=DIM_LABELS,
                y=vals,
                marker_color=PALETTE[i % len(PALETTE)],
                marker_opacity=0.85,
                text=[str(v) for v in vals],
                textposition="outside",
                textfont=dict(size=9, color="rgba(232,237,245,0.5)"),
            ))

        bar_fig.update_layout(
            barmode="group",
            paper_bgcolor="#05080F",
            plot_bgcolor="#05080F",
            font=dict(color="rgba(232,237,245,0.6)", size=10, family="IBM Plex Mono"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=9)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0, 3.8],
                       tickvals=[0, 1, 2, 3], ticktext=["0", "1", "2", "3 (Max)"]),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10), bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
        )
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

    # ── CTA ───────────────────────────────────────────────────────────────────
    top = report.get("top_risk")
    top_name = top["name"] if top else "your highest-risk state"
    top_law = top["law"] if top else "applicable state law"

    st.html(f"""
    <div style="background:linear-gradient(135deg,rgba(0,255,178,0.06),rgba(26,139,255,0.06));
                border:1px solid rgba(0,255,178,0.2);border-radius:8px;
                padding:1.75rem 2rem;margin-top:1.5rem;text-align:center">
      <div style="font-family:Syne,sans-serif;font-size:0.6rem;font-weight:700;
                  letter-spacing:0.3em;text-transform:uppercase;
                  color:rgba(0,255,178,0.5);margin-bottom:0.5rem">Next Step</div>
      <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;
                  color:#E8EDF5;margin-bottom:0.5rem">
        Your footprint triggers <span style="color:#00FFB2">{report['n_critical'] + report['n_high']}</span> high-risk state law{'s' if report['n_critical'] + report['n_high'] != 1 else ''}
      </div>
      <div style="font-size:0.75rem;color:rgba(232,237,245,0.45);max-width:560px;
                  margin:0 auto 1.25rem;line-height:1.7">
        {top_name} alone ({top_law}) exposes you to litigation and enforcement
        before OCR even opens a file. Freshpaint closes these gaps in a single integration.
      </div>
      <div style="display:inline-flex;gap:0.75rem;flex-wrap:wrap;justify-content:center">
        <a href="https://freshpaint.io/demo" target="_blank"
           style="background:#00FFB2;color:#05080F;font-family:IBM Plex Mono,monospace;
                  font-size:0.75rem;font-weight:700;padding:0.6rem 1.5rem;
                  border-radius:3px;text-decoration:none;letter-spacing:0.05em">
          Request a Demo
        </a>
        <a href="https://freshpaint.io" target="_blank"
           style="background:transparent;color:#00FFB2;border:1px solid rgba(0,255,178,0.4);
                  font-family:IBM Plex Mono,monospace;font-size:0.75rem;font-weight:700;
                  padding:0.6rem 1.5rem;border-radius:3px;text-decoration:none;letter-spacing:0.05em">
          Learn More
        </a>
      </div>
    </div>
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.html(f"""
<div style="text-align:center;padding:2rem 1rem;margin-top:3rem;
            border-top:1px solid rgba(255,255,255,0.05);
            font-size:0.62rem;color:rgba(232,237,245,0.18);line-height:1.8">
  <a href="https://freshpaint.io" style="color:rgba(0,255,178,0.35);text-decoration:none">Freshpaint</a>
  · HIPAA-Compliant Healthcare Analytics ·
  <a href="https://freshpaint.io/blog" style="color:rgba(0,255,178,0.35);text-decoration:none">Blog</a>
  <br>State law data last reviewed {LAST_REVIEWED}; new legislation is checked monthly via LegiScan.
  Risk scores are directional. Not legal advice.
</div>
""")
