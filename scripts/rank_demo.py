#!/usr/bin/env python3
"""레시피 랭킹 CLI 데모."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ranker import _cli

if __name__ == "__main__":
    _cli()
