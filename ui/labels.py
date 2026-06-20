"""재료 클래스 표시명."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_ko_labels() -> dict[str, str]:
    path = ROOT / "data" / "mapping_ko.json"
    mapping = json.loads(path.read_text(encoding="utf-8"))
    labels: dict[str, str] = {}
    for yolo_class, aliases in mapping.items():
        ko = next((a for a in aliases if any("\uac00" <= c <= "\ud7a3" for c in a)), None)
        labels[yolo_class] = ko or yolo_class.replace("_", " ")
    return labels
