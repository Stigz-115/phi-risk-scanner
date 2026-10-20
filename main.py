"""Backward-compatible entry point. The app now starts from app.py (Streamlit Cloud's main file)."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
