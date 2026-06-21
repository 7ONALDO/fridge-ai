#!/usr/bin/env python3
"""
냉장고 AI — Ablation Study 스크립트 (Kaggle / 로컬 겸용)

실험 4종:
  1) YOLO 아키텍처 비교  : YOLOv8n/s vs YOLOv11n/s
  2) Augmentation 전략   : None → Mosaic → +HSV/Flip → +MixUp → +Copy-Paste
  3) Transfer Learning   : from scratch vs COCO pretrained (full / freeze)
  4) Optimizer 비교      : SGD vs Adam vs AdamW (+Scheduler)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Kaggle 사용법:
  1) 데이터셋 추가 후 GPU 켜기
  2) 셀에서:
       !pip install -q ultralytics pyyaml
       # 실험 1번만 돌릴 때:
       !python training/ablation_yolo.py --exp 1
       # 전체 돌릴 때:
       !python training/ablation_yolo.py --exp all

환경변수:
  YOLO_DATA_ROOT  data.yaml이 있는 폴더 (미설정 시 /kaggle/input 자동 탐색)
  YOLO_EPOCHS     에폭 수 (기본: 50 — ablation은 기본학습보다 짧게)
  YOLO_IMGSZ      이미지 크기 (기본: 640)
  YOLO_DEVICE     GPU 번호 (기본: 0)
  YOLO_BATCH      배치 크기 (기본: 16, OOM 시 8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 공통 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EPOCHS  = int(os.environ.get("YOLO_EPOCHS",  "50"))   # ablation은 50 에폭으로 충분
IMGSZ   = int(os.environ.get("YOLO_IMGSZ",   "640"))
DEVICE  = int(os.environ.get("YOLO_DEVICE",  "0"))
BATCH   = int(os.environ.get("YOLO_BATCH",   "16"))   # OOM 시 8로 낮추기
PROJECT = os.environ.get("YOLO_PROJECT", "/kaggle/working/ablation")

# PROJECT 경로가 없으면 로컬로 대체
if not Path(PROJECT).parent.exists():
    PROJECT = str(Path(__file__).resolve().parent.parent / "ablation")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# data.yaml 탐색 (train_yolo.py와 동일 로직)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def find_data_yaml() -> Path:
    root = os.environ.get("YOLO_DATA_ROOT", "").strip()
    if root:
        candidate = Path(root)
        if candidate.is_file() and candidate.name == "data.yaml":
            return candidate.resolve()
        p = (candidate / "data.yaml").resolve()
        if p.is_file():
            return p
        raise SystemExit(f"[오류] YOLO_DATA_ROOT='{root}' 에서 data.yaml을 찾지 못했습니다.")

    # Kaggle: rglob으로 깊이 무관하게 탐색
    kaggle_input = Path("/kaggle/input")
    if kaggle_input.is_dir():
        candidates = sorted(kaggle_input.rglob("data.yaml"))
        if candidates:
            print(f"[data] {candidates[0]}")
            return candidates[0]
        raise SystemExit(
            "[오류] /kaggle/input 아래에 data.yaml이 없습니다.\n"
            "  → YOLO_DATA_ROOT 환경변수로 직접 지정하세요."
        )

    # 로컬: smart refrigerator 폴더 우선 탐색
    here = Path(__file__).resolve().parent
    for search_root in [here, here.parent, here.parent.parent]:
        for candidate in sorted(search_root.rglob("data.yaml")):
            parts = [p.lower() for p in candidate.parts]
            if any("smart" in p or "refrigerator" in p for p in parts):
                return candidate
    for search_root in [here, here.parent, here.parent.parent]:
        for candidate in sorted(search_root.rglob("data.yaml")):
            return candidate

    raise SystemExit("[오류] data.yaml을 찾지 못했습니다. YOLO_DATA_ROOT를 설정하세요.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 단일 실험 실행 + mAP 반환
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def measure_gpu_ms(best_pt: Path, imgsz: int = 640, n_warmup: int = 10, n_measure: int = 100) -> float:
    """GPU 추론 속도 측정 (ms/image). GPU 없거나 실패 시 0.0 반환."""
    try:
        import torch
        from ultralytics import YOLO
        if not torch.cuda.is_available():
            return 0.0
        import time
        model_inf = YOLO(str(best_pt))
        dummy = torch.zeros(1, 3, imgsz, imgsz).cuda()
        for _ in range(n_warmup):
            model_inf.predict(source=dummy, verbose=False)
        torch.cuda.synchronize()
        times = []
        for _ in range(n_measure):
            t0 = time.perf_counter()
            model_inf.predict(source=dummy, verbose=False)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - t0) * 1000)
        return round(sum(times) / len(times), 1)
    except Exception:
        return 0.0


def get_model_info(model_name: str) -> dict:
    """모델 파라미터 수와 크기(MB) 반환."""
    try:
        from ultralytics import YOLO
        m = YOLO(model_name)
        params = sum(p.numel() for p in m.model.parameters()) / 1e6  # 단위: M
        pt_path = Path(model_name)
        if not pt_path.is_file():
            # yolo11n.pt 등 — Ultralytics 캐시 경로에서 크기 조회
            cached = Path.home() / ".config" / "Ultralytics" / model_name
            if not cached.is_file():
                weights_dir = Path.cwd() / model_name
                pt_path = weights_dir if weights_dir.is_file() else pt_path
        size_mb = pt_path.stat().st_size / 1024 / 1024 if pt_path.is_file() else 0.0
        return {"params_m": round(params, 1), "size_mb": round(size_mb, 1)}
    except Exception:
        return {"params_m": 0.0, "size_mb": 0.0}


def run_experiment(name: str, model_name: str, train_kwargs: dict, data_yaml: Path) -> dict:
    """
    한 번의 학습을 실행하고 val mAP 결과를 반환.
    Ablation 간 비교는 val mAP 기준 (동일 split·동일 epoch).
    최종 모델(best.pt 100ep)과는 별도로 보고할 것.
    """
    from ultralytics import YOLO

    print(f"\n{'='*60}")
    print(f"  실험: {name}")
    print(f"  모델: {model_name}  /  에폭: {EPOCHS}")
    print(f"{'='*60}")

    model = YOLO(model_name)

    # 공통 기본값 + 실험별 오버라이드
    base = dict(
        data=str(data_yaml),
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=DEVICE,
        project=PROJECT,
        name=name,
        save=True,
        val=True,
        plots=False,   # ablation에서는 그래프 저장 생략 (속도 우선)
        verbose=False,
        patience=15,
    )
    base.update(train_kwargs)

    t0 = time.time()
    model.train(**base)
    elapsed = time.time() - t0

    # 실제 저장 경로 확인
    try:
        run_dir = Path(model.trainer.save_dir)
    except AttributeError:
        run_dir = Path(PROJECT) / name

    best_pt = run_dir / "weights" / "best.pt"

    # val mAP 추출 (trainer.metrics에서 가져오기)
    try:
        map50    = float(model.trainer.metrics.get("metrics/mAP50(B)",    0))
        map5095  = float(model.trainer.metrics.get("metrics/mAP50-95(B)", 0))
        recall   = float(model.trainer.metrics.get("metrics/recall(B)",   0))
        precision= float(model.trainer.metrics.get("metrics/precision(B)",0))
    except Exception:
        # fallback: best.pt로 val 재실행
        if best_pt.is_file():
            m2 = YOLO(str(best_pt))
            metrics = m2.val(data=str(data_yaml), device=DEVICE, verbose=False)
            map50   = metrics.box.map50
            map5095 = metrics.box.map
            recall  = metrics.box.mr
            precision = metrics.box.mp
        else:
            map50 = map5095 = recall = precision = 0.0

    result = {
        "name":      name,
        "model":     model_name,
        "map50":     round(map50,   4),
        "map5095":   round(map5095, 4),
        "recall":    round(recall,  4),
        "precision": round(precision, 4),
        "time_min":  round(elapsed / 60, 1),
        "best_pt":   str(best_pt),
    }

    # GPU 추론 속도 측정
    if best_pt.is_file():
        gpu_ms = measure_gpu_ms(best_pt, imgsz=IMGSZ)
        info   = get_model_info(model_name)
        result["gpu_ms"]   = gpu_ms
        result["params_m"] = info["params_m"]
        result["size_mb"]  = info["size_mb"]
        print(f"  → GPU 추론: {gpu_ms:.1f}ms  |  Params: {info['params_m']}M  |  Size: {info['size_mb']}MB")

    print(f"\n  → mAP@0.5: {map50:.4f}  |  mAP@0.5:0.95: {map5095:.4f}"
          f"  |  Recall: {recall:.4f}  |  {elapsed/60:.1f}분")
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실험 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def experiments_1(data_yaml: Path) -> list[dict]:
    """실험 1: YOLO 아키텍처 비교 (v8n/s vs v11n/s)"""
    print("\n\n★ 실험 1: YOLO 아키텍처 비교")
    common = dict(optimizer="AdamW", lr0=0.001, weight_decay=0.0005,
                  cos_lr=True, pretrained=True)
    configs = [
        ("exp1_yolov8n",  "yolov8n.pt"),
        ("exp1_yolov8s",  "yolov8s.pt"),
        ("exp1_yolov11n", "yolo11n.pt"),
        ("exp1_yolov11s", "yolo11s.pt"),
    ]
    results = []
    for name, model in configs:
        results.append(run_experiment(name, model, common.copy(), data_yaml))
    return results


def experiments_2(data_yaml: Path) -> list[dict]:
    """실험 2: Augmentation 전략 비교"""
    print("\n\n★ 실험 2: Augmentation 전략 비교")
    base = dict(model="yolo11n.pt", optimizer="AdamW", lr0=0.001,
                weight_decay=0.0005, cos_lr=True, pretrained=True)

    configs = [
        # (이름, aug 오버라이드)
        ("exp2_no_aug", dict(
            mosaic=0.0, hsv_h=0.0, hsv_s=0.0, hsv_v=0.0,
            fliplr=0.0, translate=0.0, scale=0.0, mixup=0.0,
        )),
        ("exp2_mosaic_only", dict(
            mosaic=1.0, hsv_h=0.0, hsv_s=0.0, hsv_v=0.0,
            fliplr=0.0, translate=0.0, scale=0.0, mixup=0.0,
        )),
        ("exp2_mosaic_hsv_flip", dict(
            mosaic=1.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
            fliplr=0.5, translate=0.1, scale=0.5, mixup=0.0,
        )),
        ("exp2_full_aug", dict(
            mosaic=1.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
            fliplr=0.5, translate=0.1, scale=0.5, mixup=0.1,
        )),
        # 5단계: MixUp + Copy-Paste 추가 (계획서 최고 단계)
        ("exp2_full_aug_cp", dict(
            mosaic=1.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
            fliplr=0.5, translate=0.1, scale=0.5, mixup=0.1,
            copy_paste=0.1,
        )),
    ]
    results = []
    for name, aug in configs:
        kwargs = base.copy()
        kwargs.update(aug)
        model_name = kwargs.pop("model")
        results.append(run_experiment(name, model_name, kwargs, data_yaml))
    return results


def experiments_3(data_yaml: Path) -> list[dict]:
    """실험 3: Transfer Learning 효과 (scratch vs pretrained vs freeze)"""
    print("\n\n★ 실험 3: Transfer Learning 효과")
    common = dict(optimizer="AdamW", lr0=0.001, weight_decay=0.0005,
                  cos_lr=True, mosaic=1.0, hsv_h=0.015, hsv_s=0.7,
                  hsv_v=0.4, fliplr=0.5)
    configs = [
        # yolo11n.yaml: 구조 정의 파일만 사용 → 진짜 random init (scratch)
        ("exp3_scratch",    "yolo11n.yaml", dict(pretrained=False, freeze=None)),
        # yolo11n.pt + pretrained=True: COCO 가중치 전체 파인튜닝
        ("exp3_finetune",   "yolo11n.pt",   dict(pretrained=True,  freeze=None)),
        # backbone 일부 freeze (레이어 0~9), head만 학습
        ("exp3_freeze_bb",  "yolo11n.pt",   dict(pretrained=True,  freeze=10)),
    ]
    results = []
    for name, model, extra in configs:
        kwargs = common.copy()
        kwargs.update(extra)
        results.append(run_experiment(name, model, kwargs, data_yaml))
    return results


def experiments_4(data_yaml: Path) -> list[dict]:
    """실험 4: Optimizer 비교 (SGD vs Adam vs AdamW)"""
    print("\n\n★ 실험 4: Optimizer 비교")
    base = dict(pretrained=True, mosaic=1.0, hsv_h=0.015, hsv_s=0.7,
                hsv_v=0.4, fliplr=0.5)
    configs = [
        # SGD: Ultralytics 기본 linear decay 사용 (StepLR과 유사 효과)
        ("exp4_sgd",   dict(optimizer="SGD",   lr0=0.01,  cos_lr=False, weight_decay=0.0005)),
        # Adam: scheduler 없음, weight_decay=0 (Adam 표준 설정)
        ("exp4_adam",  dict(optimizer="Adam",  lr0=0.001, cos_lr=False, weight_decay=0.0)),
        # AdamW + CosineAnnealingLR: 계획서 최종 선택
        ("exp4_adamw", dict(optimizer="AdamW", lr0=0.001, cos_lr=True,  weight_decay=0.0005)),
    ]
    results = []
    for name, opt in configs:
        kwargs = base.copy()
        kwargs.update(opt)
        results.append(run_experiment(name, "yolo11n.pt", kwargs, data_yaml))
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 결과 출력 및 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_table(title: str, results: list[dict]) -> None:
    """결과를 보기 좋은 표로 출력"""
    print(f"\n\n{'━'*85}")
    print(f"  📊 {title}")
    print(f"{'━'*85}")
    print(f"  {'실험명':<25} {'모델':<12} {'mAP@0.5':>8} {'mAP@0.5:0.95':>13} {'Recall':>8} {'GPU ms':>7} {'Params':>7} {'시간':>7}")
    print(f"  {'-'*25} {'-'*12} {'-'*8} {'-'*13} {'-'*8} {'-'*7} {'-'*7} {'-'*7}")
    for r in results:
        mark = " ★" if r == max(results, key=lambda x: x["map50"]) else ""
        gpu  = f"{r.get('gpu_ms', 0):.1f}ms" if r.get('gpu_ms', 0) > 0 else "  -"
        par  = f"{r.get('params_m', 0):.1f}M" if r.get('params_m', 0) > 0 else "  -"
        print(f"  {r['name']:<25} {r['model']:<12} {r['map50']:>8.4f} "
              f"{r['map5095']:>13.4f} {r['recall']:>8.4f} {gpu:>7} {par:>7} {r['time_min']:>6.1f}분{mark}")
    print(f"{'━'*85}")


def save_results(all_results: dict) -> None:
    """결과를 JSON으로 저장"""
    out_dir = Path(PROJECT)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ablation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n[저장] 결과 저장 완료: {out_path}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main() -> None:
    parser = argparse.ArgumentParser(description="냉장고 AI Ablation Study")
    parser.add_argument(
        "--exp", default="all",
        choices=["1", "2", "3", "4", "all"],
        help="실행할 실험 번호 (기본: all)"
    )
    args = parser.parse_args()

    try:
        from ultralytics import YOLO  # noqa: F401
    except ImportError:
        print("[오류] ultralytics가 없습니다. pip install ultralytics", file=sys.stderr)
        sys.exit(1)

    data_yaml = find_data_yaml()
    all_results = {}

    exp_map = {
        "1": ("YOLO 아키텍처 비교",    experiments_1),
        "2": ("Augmentation 전략 비교", experiments_2),
        "3": ("Transfer Learning 효과", experiments_3),
        "4": ("Optimizer 비교",         experiments_4),
    }

    targets = ["1", "2", "3", "4"] if args.exp == "all" else [args.exp]

    for key in targets:
        title, fn = exp_map[key]
        results = fn(data_yaml)
        all_results[f"exp{key}"] = results
        print_table(title, results)

    # 전체 요약 저장
    save_results(all_results)

    # Kaggle Output에 결과 JSON 복사 (쉽게 다운로드)
    kaggle_out = Path("/kaggle/working/ablation_results.json")
    if Path("/kaggle/working").exists():
        import shutil
        shutil.copy(
            Path(PROJECT) / "ablation_results.json",
            kaggle_out
        )
        print(f"[저장] Kaggle Output에 복사 완료: {kaggle_out}")

    print("\n\n🎉 Ablation Study 완료!")
    print("결과 JSON을 다운로드해서 발표 자료에 활용하세요.")


if __name__ == "__main__":
    main()
