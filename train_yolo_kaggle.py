#!/usr/bin/env python3
"""
Kaggle Notebook 또는 로컬에서 YOLOv11 학습 실행용 스크립트.

Kaggle 사용법:
  1) Notebook에 데이터셋 추가 (zip 루트에 data.yaml, train/, valid/, test/)
  2) GPU 켜기, 필요 시 Internet ON
  3) 터미널 또는 셀에서:
       !pip install -q ultralytics
       !python train_yolo_kaggle.py

환경변수 (선택):
  YOLO_DATA_ROOT  - data.yaml 이 있는 디렉터리 (미설정 시 /kaggle/input 아래 자동 탐색)
  YOLO_MODEL      - 사전학습 가중치 (기본: yolo11n.pt)
  YOLO_EPOCHS     - 에폭 (기본: 50)
  YOLO_IMGSZ      - 이미지 크기 (기본: 640)
  YOLO_BATCH      - 배치 (기본: 16, OOM 시 8 등으로 낮추기)
  YOLO_PROJECT    - 결과 루트 (Kaggle 기본: /kaggle/working/runs)
  YOLO_NAME       - 런 이름 (기본: detect_fridge)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def find_data_yaml(kaggle_input: Path) -> Path | None:
    """첫 번째로 발견되는 data.yaml 경로."""
    if not kaggle_input.is_dir():
        return None
    for child in sorted(kaggle_input.iterdir()):
        if child.is_dir():
            candidate = child / "data.yaml"
            if candidate.is_file():
                return candidate
    return None


def resolve_data_yaml() -> Path:
    root = os.environ.get("YOLO_DATA_ROOT", "").strip()
    if root:
        p = Path(root).expanduser().resolve() / "data.yaml"
        if p.is_file():
            return p
        if Path(root).is_file() and Path(root).name == "data.yaml":
            return Path(root).expanduser().resolve()
        raise SystemExit(f"YOLO_DATA_ROOT 로 data.yaml 을 찾지 못했습니다: {root}")

    kaggle = Path("/kaggle/input")
    found = find_data_yaml(kaggle)
    if found is not None:
        return found

    # 로컬: 이 스크립트 기준 프로젝트 상위의 데이터셋 폴더
    here = Path(__file__).resolve().parent
    local = (
        here.parent / "smart refrigerator.yolov11" / "data.yaml"
    ).resolve()
    if local.is_file():
        return local

    raise SystemExit(
        "data.yaml 을 찾지 못했습니다.\n"
        "  - Kaggle: 데이터셋을 Notebook에 추가했는지 확인하세요.\n"
        "  - 또는 YOLO_DATA_ROOT=/path/to/folder (data.yaml의 부모) 를 설정하세요."
    )


def main() -> None:
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ultralytics 가 없습니다. 먼저 실행: pip install ultralytics", file=sys.stderr)
        sys.exit(1)

    data_yaml = resolve_data_yaml()
    print(f"[data] {data_yaml}")

    model_name = os.environ.get("YOLO_MODEL", "yolo11n.pt").strip()
    epochs = int(os.environ.get("YOLO_EPOCHS", "50"))
    imgsz = int(os.environ.get("YOLO_IMGSZ", "640"))
    batch = int(os.environ.get("YOLO_BATCH", "16"))
    project = os.environ.get("YOLO_PROJECT", "/kaggle/working/runs").strip()
    name = os.environ.get("YOLO_NAME", "detect_fridge").strip()

    if not Path(project).parent.exists():
        project = str(Path(__file__).resolve().parent / "runs")

    model = YOLO(model_name)
    model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
    )

    # 학습 결과 weights 경로 안내 (project/name/weights/best.pt)
    run_dir = Path(project) / name
    weights = run_dir / "weights" / "best.pt"
    if weights.is_file():
        print(f"[done] best weights: {weights}")
    else:
        print(f"[done] run dir (best.pt 위치 확인): {run_dir}")


if __name__ == "__main__":
    main()
