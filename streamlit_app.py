"""
Compatibility entry point for the Streamlit workspace.

The dashboard lives in app.py. Running this file loads the same UI
without changing backend workflow code.

    streamlit run streamlit_app.py
    streamlit run app.py
"""

from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parent / "app.py"),
    run_name="__main__",
)
