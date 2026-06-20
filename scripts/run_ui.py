#!/usr/bin/env python3
"""Streamlit UI 실행."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import subprocess

if __name__ == "__main__":
    app = ROOT / "ui" / "app.py"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app),
            "--server.port",
            "8501",
        ],
        check=True,
    )
