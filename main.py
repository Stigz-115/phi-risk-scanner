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

scanner_page = st.Page("app.py",                     title="PHI Risk Scanner", icon="🔍", default=True)
roi_page     = st.Page("pages/2_ROI_Calculator.py",  title="ROI Calculator",   icon="📊")

pg = st.navigation({"Freshpaint Tools": [scanner_page, roi_page]}, position="sidebar")
pg.run()
