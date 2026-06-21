# YOLO 학습 · Ablation

Kaggle 또는 로컬에서 모델 학습·실험용 스크립트입니다. **앱 실행(`run_api.py`)과는 별도**입니다.

| 파일 | 용도 |
|------|------|
| `train_yolo.py` | 본 학습 → `best.pt` (프로젝트 루트로 복사) |
| `train_yolo_kaggle.py` | Kaggle용 간단 학습 |
| `ablation_yolo.py` | Ablation 4종 (`--exp 1`~`4` 또는 `all`) |

```bash
cd ~/Documents/fridge-ai

# 본 학습 (로컬)
YOLO_DATA_ROOT="smart refrigerator.yolov11" python training/train_yolo.py

# Ablation 실험 1
YOLO_DATA_ROOT="smart refrigerator.yolov11" YOLO_EPOCHS=50 python training/ablation_yolo.py --exp 1
```

결과 JSON은 `presentation/ablation/` 에 저장합니다. 상세: [`../docs/fridge-recipe-plan-v3.md`](../docs/fridge-recipe-plan-v3.md) §6.2.
