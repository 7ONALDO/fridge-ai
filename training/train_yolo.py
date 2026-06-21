#!/usr/bin/env python3
"""
냉장고 AI — YOLOv11 학습 스크립트 (Kaggle / 로컬 겸용)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Kaggle 사용법:
  1) Kaggle Notebook에 Roboflow 데이터셋 추가 (또는 직접 업로드)
  2) 우측 패널 → Accelerator → GPU T4 x2 선택
  3) 새 셀에서 실행:

       !pip install -q ultralytics pyyaml
       !python training/train_yolo.py

로컬 사용법:
  YOLO_DATA_ROOT=/path/to/dataset python training/train_yolo.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
환경변수 (선택 — 기본값으로도 바로 실행 가능):
  YOLO_DATA_ROOT  data.yaml이 있는 폴더 경로 (미설정 시 /kaggle/input 자동 탐색)
  YOLO_MODEL      사전학습 가중치 파일명 (기본: yolo11n.pt)
  YOLO_EPOCHS     학습 에폭 수       (기본: 100)
  YOLO_IMGSZ      입력 이미지 크기   (기본: 640)
  YOLO_BATCH      배치 크기          (기본: 16 / OOM 시 8로 낮추기)
  YOLO_DEVICE     GPU 번호           (기본: 0)
  YOLO_PROJECT    결과 저장 루트     (기본: /kaggle/working/runs)
  YOLO_NAME       실험 이름          (기본: fridge_yolo11n)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 환경 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_env(key: str, default: str) -> str:
    return os.environ.get(key, default).strip()


MODEL      = get_env("YOLO_MODEL",   "yolo11n.pt")
EPOCHS     = int(get_env("YOLO_EPOCHS",  "100"))
IMGSZ      = int(get_env("YOLO_IMGSZ",   "640"))
BATCH      = int(get_env("YOLO_BATCH",   "16"))
DEVICE     = int(get_env("YOLO_DEVICE",  "0"))
PROJECT    = get_env("YOLO_PROJECT", "/kaggle/working/runs")
NAME       = get_env("YOLO_NAME",    "fridge_yolo11n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. data.yaml 경로 자동 탐색
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def find_data_yaml() -> Path:
    """
    우선순위:
      1) 환경변수 YOLO_DATA_ROOT
      2) Kaggle: /kaggle/input/**/data.yaml
      3) 로컬: 스크립트 상위 폴더에서 data.yaml 탐색
    """
    # 1) 환경변수
    root = get_env("YOLO_DATA_ROOT", "")
    if root:
        candidate = Path(root)
        if candidate.is_file() and candidate.name == "data.yaml":
            return candidate.resolve()
        p = (candidate / "data.yaml").resolve()
        if p.is_file():
            return p
        raise SystemExit(
            f"[오류] YOLO_DATA_ROOT='{root}' 에서 data.yaml을 찾지 못했습니다."
        )

    # 2) Kaggle 환경 — 중첩 폴더 구조도 처리 (1단계 또는 2단계 아래에 data.yaml)
    # 실제 구조 예시:
    #   /kaggle/input/smart refrigerator.yolov11/data.yaml          (1단계)
    #   /kaggle/input/smart refrigerator.yolov11/smart refrigerator.yolov11/data.yaml (2단계)
    kaggle_input = Path("/kaggle/input")
    if kaggle_input.is_dir():
        # 1단계 탐색
        for child in sorted(kaggle_input.iterdir()):
            candidate = child / "data.yaml"
            if candidate.is_file():
                print(f"[data] Kaggle 데이터셋 발견 (1단계): {candidate}")
                return candidate
        # 2단계 탐색 (Kaggle에서 폴더가 한 번 더 중첩되는 경우)
        for child in sorted(kaggle_input.iterdir()):
            if child.is_dir():
                for grandchild in sorted(child.iterdir()):
                    candidate = grandchild / "data.yaml"
                    if candidate.is_file():
                        print(f"[data] Kaggle 데이터셋 발견 (2단계): {candidate}")
                        return candidate
        raise SystemExit(
            "[오류] /kaggle/input 아래에 data.yaml이 없습니다.\n"
            "  → Notebook 우측 패널 'Add data'로 데이터셋을 추가하세요.\n"
            "  → 또는 아래 셀을 추가해서 경로를 직접 지정하세요:\n"
            "     import os; os.environ['YOLO_DATA_ROOT'] = '/kaggle/input/데이터셋폴더/data.yaml의_부모폴더'"
        )

    # 3) 로컬 탐색 — 'smart refrigerator' 폴더 우선, 없으면 스크립트 주변 탐색
    here = Path(__file__).resolve().parent
    # 폴더명에 'smart' 또는 'refrigerator'가 있는 경우 우선 반환
    for search_root in [here, here.parent, here.parent.parent]:
        for candidate in sorted(search_root.rglob("data.yaml")):
            parts_lower = [p.lower() for p in candidate.parts]
            if any("smart" in p or "refrigerator" in p for p in parts_lower):
                print(f"[data] 로컬(smart refrigerator 폴더)에서 발견: {candidate}")
                return candidate
    # 우선 탐색 실패 시 첫 번째 data.yaml 반환 (경고 출력)
    for search_root in [here, here.parent, here.parent.parent]:
        for candidate in sorted(search_root.rglob("data.yaml")):
            print(f"[data] 로컬에서 발견 (YOLO_DATA_ROOT 설정 권장): {candidate}")
            return candidate

    raise SystemExit(
        "[오류] data.yaml을 찾지 못했습니다.\n"
        "  → YOLO_DATA_ROOT=/path/to/dataset 환경변수를 설정하세요."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 데이터 분할 비율 검증 및 재분할 (선택)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_split(data_yaml: Path) -> None:
    """
    Roboflow 기본 분할(94/3.4/1.7)이 너무 편향된 경우 경고만 출력.
    실제 재분할은 Roboflow 웹사이트에서 export 옵션으로 하는 것이 가장 안전합니다.
    """
    try:
        import yaml
    except ImportError:
        print("[split] PyYAML이 없어 분할 비율 확인을 건너뜁니다.")
        print("  → pip install pyyaml 로 설치하면 확인 가능합니다.")
        return

    with open(data_yaml) as f:
        cfg = yaml.safe_load(f)

    root = data_yaml.parent
    splits = {}
    for split in ("train", "val", "test"):
        p = cfg.get(split, "")
        folder = (root / p).resolve() if p else None
        if folder and folder.is_dir():
            count = sum(1 for _ in folder.rglob("*.jpg"))
            count += sum(1 for _ in folder.rglob("*.png"))
            splits[split] = count

    total = sum(splits.values())
    if total == 0:
        print("[split] 이미지 수를 확인할 수 없습니다.")
        return

    print("\n[split] 현재 데이터 분할 현황:")
    for split, cnt in splits.items():
        pct = cnt / total * 100
        print(f"  {split:5s}: {cnt:5d}장  ({pct:.1f}%)")

    val_pct = splits.get("val", 0) / total * 100
    if val_pct < 8:
        print(
            "\n[경고] val 비율이 낮습니다 (권장: 10% 이상).\n"
            "  → Roboflow에서 80/10/10으로 재export 하는 것을 권장합니다."
        )
    print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 학습 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def train(data_yaml: Path) -> Path:
    """
    YOLOv11 파인튜닝 (COCO pretrained → 냉장고 30 classes).

    주요 설정:
      - optimizer : AdamW  (weight_decay=5e-4)
      - scheduler : CosineAnnealingLR  (cos_lr=True)
      - augmentation: Mosaic, HSV, Flip, Translate (기본값 활성화)
    """
    from ultralytics import YOLO

    print("=" * 60)
    print(f"  모델    : {MODEL}  (COCO pretrained → 파인튜닝)")
    print(f"  데이터  : {data_yaml}")
    print(f"  에폭    : {EPOCHS}")
    print(f"  배치    : {BATCH}")
    print(f"  이미지  : {IMGSZ}x{IMGSZ}")
    print(f"  GPU     : cuda:{DEVICE}")
    print(f"  저장    : {PROJECT}/{NAME}")
    print("=" * 60)

    model = YOLO(MODEL)  # COCO pretrained 가중치 자동 다운로드

    result = model.train(
        data=str(data_yaml),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=DEVICE,

        # ── 전이학습 설정 ──────────────────────────────
        pretrained=True,        # COCO 사전학습 가중치 활용

        # ── Optimizer (AdamW) ──────────────────────────
        optimizer="AdamW",
        lr0=0.001,              # 초기 학습률
        weight_decay=0.0005,    # L2 정규화 (계획서: wd=5e-4)

        # ── Scheduler (CosineAnnealingLR) ──────────────
        cos_lr=True,

        # ── Augmentation (기본 활성화) ──────────────────
        # Mosaic, HSV, Flip, Translate는 YOLOv11 기본 활성화
        # MixUp / CutMix 등 고급 증강은 Ablation 실험에서 별도 설정
        mosaic=1.0,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,

        # ── 저장 설정 ──────────────────────────────────
        project=PROJECT,
        name=NAME,
        save=True,              # best.pt / last.pt 저장
        save_period=10,         # 10 에폭마다 체크포인트 저장

        # ── 기타 ──────────────────────────────────────
        patience=20,            # Early stopping (20 에폭 동안 개선 없으면 중단)
        val=True,               # 학습 중 매 에폭 검증 수행
        plots=True,             # 학습 곡선, confusion matrix 등 자동 저장
        verbose=True,
    )

    # ── 피드백 #2: 실제 저장 경로를 trainer에서 직접 가져옴 ──────────────
    # Ultralytics는 name 중복 시 fridge_yolo11n2 처럼 자동으로 이름을 바꾸므로
    # Path(PROJECT)/NAME 으로 하드코딩하면 best.pt를 못 찾을 수 있음
    try:
        actual_run_dir = Path(model.trainer.save_dir)
    except AttributeError:
        # fallback: result 객체 또는 최신 폴더로 탐색
        actual_run_dir = Path(PROJECT) / NAME
        if not actual_run_dir.is_dir():
            candidates = sorted(Path(PROJECT).glob(f"{NAME}*/"), key=lambda p: p.stat().st_mtime)
            if candidates:
                actual_run_dir = candidates[-1]

    best = actual_run_dir / "weights" / "best.pt"
    print(f"\n[train] 실제 저장 경로: {actual_run_dir}")
    return best


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 학습 후 검증 (mAP 출력)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate(best_pt: Path, data_yaml: Path) -> None:
    """학습된 best.pt로 test set 검증 후 mAP 출력."""
    from ultralytics import YOLO

    if not best_pt.is_file():
        print(f"[경고] best.pt 를 찾지 못했습니다: {best_pt}")
        return

    print("\n" + "=" * 60)
    print("  검증 시작 (best.pt → test set)")
    print("=" * 60)

    model = YOLO(str(best_pt))
    metrics = model.val(
        data=str(data_yaml),
        split="test",       # test set으로 최종 평가
        device=DEVICE,
        imgsz=IMGSZ,
        verbose=True,
    )

    # ── GPU 추론 속도 측정 ────────────────────────────
    gpu_ms = measure_inference_speed(best_pt)

    # ── 결과 출력 ─────────────────────────────────────
    print("\n" + "─" * 50)
    print("  ✅ 최종 성능 지표 (test set 기준)")
    print("─" * 50)
    print(f"  mAP@0.5       : {metrics.box.map50:.4f}   (목표: ≥ 0.70)")
    print(f"  mAP@0.5:0.95  : {metrics.box.map:.4f}   (목표: ≥ 0.45)")
    print(f"  Recall        : {metrics.box.mr:.4f}   (전체 평균, 목표: ≥ 0.70)")
    print(f"  Precision     : {metrics.box.mp:.4f}   (참고용 — mAP 안에 포함됨)")
    print(f"  GPU 추론 속도  : {gpu_ms:.1f} ms/image  (목표: ≤ 10ms)")
    print("─" * 50)
    print("  ※ 지표 해설:")
    print("     mAP    = Precision + Recall 둘 다 반영한 종합 지표 (주 지표)")
    print("     Recall = 실제 재료를 빠뜨리지 않고 찾는 능력 (보조 지표)")
    print("     Precision은 mAP에 이미 포함되어 있어 별도 목표 미설정")
    print(f"  ※ 클래스별 Recall → runs/.../results.csv 또는 WandB 로그 확인")
    print("─" * 50)
    print(f"  best.pt 위치  : {best_pt}")
    print("─" * 50)

    # ── 목표 달성 여부 체크 ───────────────────────────
    ok_map50  = metrics.box.map50 >= 0.70
    ok_map    = metrics.box.map   >= 0.45
    ok_recall = metrics.box.mr    >= 0.70
    ok_speed  = gpu_ms <= 10.0 if gpu_ms > 0 else True  # 측정 실패 시 스킵

    if ok_map50 and ok_map and ok_recall and ok_speed:
        print("\n  🎉 목표 지표 모두 달성!")
    else:
        print("\n  ⚠️  미달 항목:")
        if not ok_map50:
            print(f"     mAP@0.5 {metrics.box.map50:.3f} < 0.70")
            print("     → epochs 늘리기 / augmentation 강화 / yolo11s.pt 업그레이드")
        if not ok_map:
            print(f"     mAP@0.5:0.95 {metrics.box.map:.3f} < 0.45")
            print("     → 더 정밀한 bbox 학습 필요 (imgsz 늘리기, 더 많은 epochs)")
        if not ok_recall:
            print(f"     Recall {metrics.box.mr:.3f} < 0.70")
            print("     → 클래스 불균형 확인 / Copy-Paste 증강 추가")
        if not ok_speed and gpu_ms > 0:
            print(f"     GPU 추론 속도 {gpu_ms:.1f}ms > 10ms")
            print("     → yolo11n으로 다운그레이드 / ONNX 변환 고려")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5-1. GPU 추론 속도 측정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def measure_inference_speed(best_pt: Path, n_warmup: int = 10, n_measure: int = 100) -> float:
    """
    GPU 추론 속도를 ms/image 단위로 측정해 반환.

    워밍업(n_warmup회) 후 n_measure회 평균을 계산.
    GPU가 없거나 측정 실패 시 0.0 반환.
    """
    import time

    print("\n[속도] GPU 추론 속도 측정 중...")

    try:
        import torch
        from ultralytics import YOLO

        if not torch.cuda.is_available():
            print("[속도] GPU 없음 — 추론 속도 측정 건너뜁니다.")
            return 0.0

        model_inf = YOLO(str(best_pt))
        # 더미 입력 (배치 1, 640×640 RGB)
        dummy = torch.zeros(1, 3, IMGSZ, IMGSZ).cuda()

        # 워밍업 (CUDA 초기화 시간 제외)
        for _ in range(n_warmup):
            model_inf.predict(source=dummy, verbose=False)

        # 실제 측정
        torch.cuda.synchronize()  # GPU 작업 완료 대기
        times = []
        for _ in range(n_measure):
            t0 = time.perf_counter()
            model_inf.predict(source=dummy, verbose=False)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - t0) * 1000)

        avg_ms = sum(times) / len(times)
        p95_ms = sorted(times)[int(n_measure * 0.95)]  # 95th percentile
        print(f"[속도] 평균: {avg_ms:.1f}ms  |  P95: {p95_ms:.1f}ms  ({n_measure}회 측정)")
        return avg_ms

    except Exception as e:
        print(f"[속도] 측정 실패 ({e}) — 건너뜁니다.")
        return 0.0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Kaggle 결과 저장 경로 안내
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_download_guide(best_pt: Path) -> None:
    print("\n" + "=" * 60)
    print("  📥 best.pt 다운로드 방법")
    print("=" * 60)
    print("  Kaggle Notebook 우측 패널 → 'Output' 탭에서")
    print(f"  {best_pt}")
    print("  파일을 클릭해 직접 다운로드하세요.\n")
    print("  또는 아래 셀을 추가해서 경로를 확인하세요:")
    print("  ┌─────────────────────────────────────────┐")
    print("  │ import os                               │")
    print(f"  │ print(os.path.exists('{best_pt}')) │")
    print("  └─────────────────────────────────────────┘")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main() -> None:
    # ultralytics 설치 확인
    try:
        import ultralytics  # noqa: F401
    except ImportError:
        print("[오류] ultralytics가 없습니다.", file=sys.stderr)
        print("  → 먼저 실행: pip install ultralytics", file=sys.stderr)
        sys.exit(1)

    # PROJECT 경로가 /kaggle/working 기준인데 로컬이면 현재 폴더로 대체
    global PROJECT
    if not Path(PROJECT).parent.exists():
        PROJECT = str(Path(__file__).resolve().parent.parent / "runs")

    data_yaml = find_data_yaml()  # data.yaml 탐색
    check_split(data_yaml)        # 분할 비율 확인
    best_pt = train(data_yaml)    # 학습 실행
    validate(best_pt, data_yaml)  # 검증 및 mAP 출력
    print_download_guide(best_pt) # 다운로드 안내


if __name__ == "__main__":
    main()
