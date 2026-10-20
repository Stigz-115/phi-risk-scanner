"""
Entry point — multi-page navigation for Streamlit 1.35+
Uses st.navigation(position="hidden") + manual st.sidebar so we own the
sidebar's look. Streamlit's collapse/expand toggle stays visible so the
sidebar can always be reopened (e.g. after it auto-collapses on narrow screens).
"""
import streamlit as st

st.set_page_config(
    page_title="Freshpaint Tools",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Page definitions ──────────────────────────────────────────────────────────
scanner_page = st.Page("app.py",                       title="PHI Risk Scanner",        icon="🔍", default=True)
roi_page     = st.Page("pages/2_ROI_Calculator.py",    title="ROI Calculator",          icon="📊")
deck_page    = st.Page("pages/3_Stakeholder_Deck.py",  title="Stakeholder Decks",       icon="📋")
privacy_page = st.Page("pages/4_State_Privacy.py",     title="State Privacy Scorecard", icon="🗺️")
comp_page    = st.Page("pages/5_Competitive.py",        title="Competitive Comparison",  icon="⚔️")

# Hidden nav — routing only, we render our own sidebar links
pg = st.navigation(
    [scanner_page, roi_page, deck_page, privacy_page, comp_page],
    position="hidden",
)

# ── Password gate (set APP_PASSWORD in Streamlit Cloud Secrets or local env) ──
import os
def _secret(name: str):
    try:
        return st.secrets.get(name)         # Streamlit Cloud secrets
    except Exception:                       # no secrets.toml when running locally
        return None


_APP_PASSWORD = (
    _secret("APP_PASSWORD")
    or os.environ.get("APP_PASSWORD")       # local env var
    or "freshpaint"                         # fallback default
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { background-color: #05080F !important; color: #E8EDF5 !important; }
    .stApp { background: #05080F; }
    #MainMenu, header[data-testid="stHeader"], footer,
    section[data-testid="stSidebar"] { display: none !important; }
    .stTextInput input {
        background: #0C1628 !important; border: 1px solid rgba(0,255,178,0.25) !important;
        color: #E8EDF5 !important; border-radius: 3px !important;
    }
    .stButton > button {
        background: rgba(0,255,178,0.1) !important;
        border: 1px solid rgba(0,255,178,0.4) !important;
        color: #00FFB2 !important; border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .stButton > button:hover { background: rgba(0,255,178,0.18) !important; }
    </style>
    """, unsafe_allow_html=True)

    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown("<div style='height:14vh'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:0.65rem;font-weight:800;"
            "letter-spacing:0.3em;text-transform:uppercase;color:rgba(0,255,178,0.6);"
            "text-align:center;margin-bottom:0.5rem'>Freshpaint</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:1.9rem;font-weight:800;"
            "text-align:center;color:#E8EDF5;margin-bottom:0.2rem'>Pre-Sales Tools</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "text-align:center;color:rgba(232,237,245,0.3);margin-bottom:2rem'>"
            "Enter access password</div>",
            unsafe_allow_html=True,
        )
        pwd = st.text_input("Password", type="password", label_visibility="collapsed",
                            placeholder="Enter password…")
        if st.button("→  Continue", use_container_width=True):
            if pwd == _APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

# ── Custom sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* ── Sidebar container ── */
    section[data-testid="stSidebar"] {
        background: #060A12 !important;
        border-right: 1px solid rgba(0,255,178,0.12) !important;
        min-width: 230px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem !important;
    }

    /* ── Sidebar toggle: keep the collapse (<<) and expand (>>) controls visible ── */
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] button {
        color: #00FFB2 !important;
    }

    /* ── Suppress Streamlit Cloud's injected auto-nav only ── */
    div[data-testid="stSidebarNav"] { display: none !important; }

    /* ── page_link nav items ── */
    a[data-testid="stPageLink-NavLink"] {
        display: flex !important;
        align-items: center !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        padding: 0.5rem 0.85rem !important;
        margin: 1px 0.5rem !important;
        color: rgba(232,237,245,0.55) !important;
        text-decoration: none !important;
        transition: background 0.15s, color 0.15s !important;
        border-left: 2px solid transparent !important;
    }
    a[data-testid="stPageLink-NavLink"]:hover {
        background: rgba(0,255,178,0.07) !important;
        color: #E8EDF5 !important;
        border-left-color: rgba(0,255,178,0.3) !important;
    }
    a[data-testid="stPageLink-NavLink"][aria-current="page"] {
        background: rgba(0,255,178,0.1) !important;
        color: #00FFB2 !important;
        border-left-color: #00FFB2 !important;
        font-weight: 600 !important;
    }
    a[data-testid="stPageLink-NavLink"] p {
        font-size: 0.78rem !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Wordmark ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:0 1rem 1rem">
      <div style="font-family:Syne,sans-serif;font-size:0.7rem;font-weight:800;
                  letter-spacing:0.3em;text-transform:uppercase;
                  color:rgba(0,255,178,0.75);margin-bottom:0.15rem">
        Freshpaint
      </div>
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;
                  color:rgba(232,237,245,0.22);letter-spacing:0.05em">
        Pre-Sales Tools
      </div>
    </div>
    <div style="height:1px;background:rgba(0,255,178,0.1);margin:0 1rem 0.75rem"></div>
    """, unsafe_allow_html=True)

    # ── Nav links ─────────────────────────────────────────────────────────────
    st.page_link("app.py",                       label="PHI Risk Scanner",        icon="🔍")
    st.page_link("pages/2_ROI_Calculator.py",    label="ROI Calculator",          icon="📊")
    st.page_link("pages/3_Stakeholder_Deck.py",  label="Stakeholder Decks",       icon="📋")
    st.page_link("pages/4_State_Privacy.py",     label="State Privacy Scorecard", icon="🗺️")
    st.page_link("pages/5_Competitive.py",        label="Competitive Comparison",  icon="⚔️")

    # ── Sidebar footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin:1.5rem 0.5rem 0;padding:1rem 0.5rem 0;
                border-top:1px solid rgba(255,255,255,0.05)">
      <a href="https://freshpaint.io" target="_blank"
         style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;
                color:rgba(0,255,178,0.35);text-decoration:none;letter-spacing:0.05em">
        freshpaint.io ↗
      </a>
      <div style="font-size:0.55rem;color:rgba(232,237,245,0.15);
                  margin-top:0.25rem;line-height:1.5">
        Internal use only.<br>Not for distribution.
      </div>
    </div>
    """, unsafe_allow_html=True)

pg.run()
