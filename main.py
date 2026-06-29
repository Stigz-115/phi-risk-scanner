"""
Entry point — multi-page navigation for Streamlit 1.35+
Uses st.navigation(position="hidden") + manual st.sidebar so we own
the sidebar entirely and can lock it open without fighting Streamlit internals.
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

# Hidden nav — routing only, we render our own sidebar links
pg = st.navigation(
    [scanner_page, roi_page, deck_page, privacy_page],
    position="hidden",
)

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

    /* ── Hide every known collapse/close button variant ──
       Targets: local dev, Streamlit Cloud, all known versions */
    button[data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    button[aria-label="Close sidebar"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="open sidebar"],
    section[data-testid="stSidebar"] button[kind="header"],
    div[data-testid="stSidebarNav"] ~ div button { display: none !important; }

    /* ── Suppress Streamlit Cloud's injected auto-nav ── */
    div[data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] nav { display: none !important; }

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

    # ── Sidebar footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="position:absolute;bottom:1.5rem;left:0;right:0;
                padding:0 1rem;border-top:1px solid rgba(255,255,255,0.05);
                padding-top:1rem">
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
