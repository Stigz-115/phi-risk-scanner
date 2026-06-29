"""
Entry point — sets up multi-page navigation for Streamlit 1.35+
"""
import streamlit as st

st.set_page_config(
    page_title="Freshpaint Tools",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

scanner_page = st.Page("app.py",                       title="PHI Risk Scanner",        icon="🔍", default=True)
roi_page     = st.Page("pages/2_ROI_Calculator.py",    title="ROI Calculator",          icon="📊")
deck_page    = st.Page("pages/3_Stakeholder_Deck.py",  title="Stakeholder Decks",       icon="📋")
privacy_page = st.Page("pages/4_State_Privacy.py",     title="State Privacy Scorecard", icon="🗺️")

pg = st.navigation({"Freshpaint Tools": [scanner_page, roi_page, deck_page, privacy_page]}, position="sidebar")

# Global CSS — sidebar toggle visibility + sidebar styling
st.markdown("""
<style>
/* ── Collapsed sidebar toggle: make it findable ── */
button[data-testid="collapsedControl"] {
    background: rgba(0,255,178,0.12) !important;
    border: 1px solid rgba(0,255,178,0.45) !important;
    border-radius: 4px !important;
    width: 28px !important;
    height: 52px !important;
    box-shadow: 0 0 12px rgba(0,255,178,0.15) !important;
    transition: background 0.2s, box-shadow 0.2s !important;
}
button[data-testid="collapsedControl"]:hover {
    background: rgba(0,255,178,0.22) !important;
    box-shadow: 0 0 20px rgba(0,255,178,0.3) !important;
}
button[data-testid="collapsedControl"] svg {
    fill: #00FFB2 !important;
    stroke: #00FFB2 !important;
}
/* ── Sidebar panel ── */
section[data-testid="stSidebar"] {
    background: #060A12 !important;
    border-right: 1px solid rgba(0,255,178,0.1) !important;
    min-width: 220px !important;
}
</style>
""", unsafe_allow_html=True)

pg.run()
