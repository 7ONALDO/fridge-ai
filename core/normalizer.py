"""YOLO 탐지 결과 → 표준 재료 집합 정규화."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.ingredient_parser import load_mapping_en, load_mapping_ko

YOLO_CLASSES = frozenset(load_mapping_en().keys()) | frozenset(load_mapping_ko().keys())


@dataclass(frozen=True)
class Detection:
    class_name: str
    confidence: float = 1.0
    count: int = 1


def _canonical_class(name: str) -> str | None:
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    if key in YOLO_CLASSES:
        return key
    alt = key.replace("_", " ")
    for cls in YOLO_CLASSES:
        if cls.replace("_", " ") == alt:
            return cls
    return None


def normalize_detections(
    detections: Iterable[str | Detection | tuple[str, int]] | dict[str, int],
    *,
    min_confidence: float = 0.0,
) -> dict[str, int]:
    """
    YOLO 탐지 결과를 표준 재료 집합으로 변환.

    입력 형식:
      - ["onion", "chicken", "onion"]
      - [Detection("onion", 0.92), ...]
      - {"onion": 2, "chicken": 1}
      - [("onion", 2), ("chicken", 1)]
    """
    counts: dict[str, int] = {}

    if isinstance(detections, dict):
        items: Iterable[str | Detection | tuple[str, int]] = (
            (name, count) for name, count in detections.items()
        )
    else:
        items = detections

    for item in items:
        if isinstance(item, Detection):
            if item.confidence < min_confidence:
                continue
            cls = _canonical_class(item.class_name)
            if cls:
                counts[cls] = counts.get(cls, 0) + item.count
            continue

        if isinstance(item, tuple) and len(item) == 2:
            name, count = item
            cls = _canonical_class(str(name))
            if cls:
                counts[cls] = counts.get(cls, 0) + int(count)
            continue

        cls = _canonical_class(str(item))
        if cls:
            counts[cls] = counts.get(cls, 0) + 1

    return dict(sorted(counts.items()))


def normalize_to_set(detections: Iterable[str | Detection] | dict[str, int]) -> set[str]:
    """클래스별 개수 없이 보유 재료 집합만 필요할 때."""
    return set(normalize_detections(detections).keys())
