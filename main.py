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

    section[data-testid="stSidebar"] {
        background: #060A12 !important;
        border-right: 1px solid rgba(0,255,178,0.12) !important;
        min-width: 230px !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem !important;
    }
    /* Hide the collapse chevron button inside the sidebar */
    section[data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
    }
    /* Also target by aria-label as fallback */
    button[aria-label="Close sidebar"],
    button[aria-label="Collapse sidebar"] {
        display: none !important;
    }
    /* page_link styling */
    a[data-testid="stPageLink-NavLink"] {
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        padding: 0.45rem 0.75rem !important;
        margin-bottom: 2px !important;
        color: rgba(232,237,245,0.6) !important;
        transition: background 0.15s, color 0.15s !important;
    }
    a[data-testid="stPageLink-NavLink"]:hover {
        background: rgba(0,255,178,0.08) !important;
        color: #00FFB2 !important;
    }
    a[data-testid="stPageLink-NavLink"][aria-current="page"] {
        background: rgba(0,255,178,0.1) !important;
        color: #00FFB2 !important;
        border-left: 2px solid #00FFB2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Wordmark
    st.markdown("""
    <div style="font-family:Syne,sans-serif;font-size:0.65rem;font-weight:800;
                letter-spacing:0.3em;text-transform:uppercase;color:rgba(0,255,178,0.7);
                padding:0 0.75rem 0.4rem;margin-bottom:0.1rem">
      Freshpaint
    </div>
    <div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;
                color:rgba(232,237,245,0.25);padding:0 0.75rem 1rem;
                border-bottom:1px solid rgba(0,255,178,0.1);margin-bottom:0.75rem">
      Pre-Sales Tools
    </div>
    """, unsafe_allow_html=True)

    st.page_link("app.py",                       label="PHI Risk Scanner",        icon="🔍")
    st.page_link("pages/2_ROI_Calculator.py",    label="ROI Calculator",          icon="📊")
    st.page_link("pages/3_Stakeholder_Deck.py",  label="Stakeholder Decks",       icon="📋")
    st.page_link("pages/4_State_Privacy.py",     label="State Privacy Scorecard", icon="🗺️")

pg.run()
