#!/bin/bash
# PHI Risk Scanner — start script
# Usage: bash start.sh
export APP_PORT=${APP_PORT:-8501}
streamlit run main.py --server.port "$APP_PORT" --server.headless true
