"""
app.py - Streamlit Web Dashboard Entrypoint
Run with: streamlit run app.py
"""

import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()
else:
    # When Streamlit executes the file at module level
    run_streamlit_app()
