"""YOLOv11 추론 + 재료 정규화."""

from __future__ import annotations

import io
import os
from pathlib import Path

from core.normalizer import Detection, normalize_detections

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WEIGHTS = ROOT / "best.pt"


class IngredientPredictor:
    def __init__(
        self,
        weights_path: Path | str | None = None,
        conf: float | None = None,
    ) -> None:
        self.weights_path = Path(
            weights_path or os.environ.get("YOLO_WEIGHTS", str(DEFAULT_WEIGHTS))
        )
        self.conf = float(conf or os.environ.get("YOLO_CONF", "0.25"))
        self.model = None

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        if self.model is not None:
            return
        if not self.weights_path.is_file():
            raise FileNotFoundError(f"YOLO weights not found: {self.weights_path}")

        from ultralytics import YOLO

        self.model = YOLO(str(self.weights_path))

    def predict_bytes(self, images: list[bytes]) -> tuple[dict[str, int], list[dict]]:
        if not images:
            return {}, []

        self.load()
        assert self.model is not None

        from PIL import Image

        aggregate: dict[str, int] = {}
        raw: list[dict] = []

        for image_bytes in images:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            results = self.model.predict(
                source=image,
                conf=self.conf,
                verbose=False,
            )
            for result in results:
                names = result.names
                if result.boxes is None or len(result.boxes) == 0:
                    continue
                for box in result.boxes:
                    cls_id = int(box.cls.item())
                    conf = float(box.conf.item())
                    class_name = names[cls_id]
                    canonical = normalize_detections([Detection(class_name, conf)])
                    if not canonical:
                        continue
                    for cls, _ in canonical.items():
                        aggregate[cls] = aggregate.get(cls, 0) + 1
                        raw.append(
                            {
                                "class_name": cls,
                                "confidence": round(conf, 4),
                                "count": 1,
                            }
                        )

        return normalize_detections(aggregate), raw
