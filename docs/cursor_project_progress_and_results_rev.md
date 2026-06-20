# Project progress and results review
_Exported on 2026. 6. 9. at 23시 30분 58초 GMT+9 from Cursor (3.7.19)_

---

> ## 📌 최종 업데이트
>
> **Month 2(앱·배포) 대부분 완료.** Docker 로컬 Compose + **Google Cloud Run** 공개 배포까지 끝난 상태.
>
> | 항목 | 상태 |
> |------|------|
> | FastAPI + Streamlit E2E | ✅ |
> | Docker (`Dockerfile`, `docker-compose.yml`) | ✅ |
> | Cloud Run (`fridge-api` + `fridge-ui`) | ✅ |
> | 공개 UI | https://fridge-ui-579587565890.asia-northeast3.run.app |
> | 남은 작업 | PPT·시연 영상·스크린샷 (Week 8) |
>
> 상세: [`../README.md`](../README.md) · [`fridge-recipe-plan-v3.md`](fridge-recipe-plan-v3.md) §5.7 · [`project-final-summary.md`](project-final-summary.md)

---

**User**

@/Users/k2/Documents/프로젝트 @fridge-recipe-plan-v3.md   @train_yolo_byclaude.py  지금 이 코드를 통해서@best.pt  결과를 도출했어 진행사항 확인해줘

---

**Cursor**

계획 문서와 학습 결과물을 대조해 진행 상황을 확인합니다.


## 진행 상황 요약

`train_yolo_byclaude.py`로 Kaggle에서 학습한 뒤 `best.pt`를 프로젝트 루트에 두신 상태입니다. 계획서(`fridge-recipe-plan-v3.md`) 8주 로드맵 기준으로 보면 **Month 1(모델)의 핵심 학습은 완료**, **Week 1 데이터 파이프라인·Month 2 앱/배포는 아직 미착수**에 가깝습니다.

---

### 완료된 항목

| 항목 | 상태 | 근거 |
|------|------|------|
| YOLO 데이터셋 준비 | ✅ | `smart refrigerator.yolov11` — train 2,439 / valid 305 / test 305 (총 3,049장, 30클래스) |
| 80/10/10 재분할 | ✅ | `split_dataset_801010.py` 적용된 분할 |
| YOLOv11n 학습 | ✅ | `best.pt` (5.2MB, 5/17 생성) |
| 학습 설정 (계획서와 일치) | ✅ | `yolo11n`, AdamW, cos_lr, COCO pretrained, 100 epochs, batch 16, imgsz 640 |
| 학습 스크립트 | ✅ | `train_yolo_byclaude.py` (Kaggle/로컬 겸용) |
| 계획서·발표 자료 | ✅ | `fridge-recipe-plan-v3.md`, `ppt-slides-v3.md`, 아키텍처 SVG |
| 레시피 원본 데이터 | ✅ | `Recipes Dataset/recipes.csv` (약 7,153건) |

---

### `best.pt` 성능 (로컬 test set 재검증)

프로젝트에 `.venv`를 만들고 Ultralytics로 **test 305장** 기준 재평가했습니다.

| 지표 | 결과 | 계획 목표 | 달성 |
|------|------|-----------|------|
| mAP@0.5 | **0.994** | ≥ 0.70 | ✅ |
| mAP@0.5:0.95 | **0.839** | ≥ 0.45 | ✅ |
| Recall (평균) | **0.989** | ≥ 0.70 | ✅ |
| Precision | 0.995 | (참고) | ✅ |
| 추론 속도 (M2 Max CPU) | ~38 ms/img | GPU ≤ 10ms | CPU 기준 참고 |

학습 메타데이터(체크포인트 내): `yolo11n.pt`, `fridge_yolo11n`, Kaggle 데이터 경로, AdamW, 100 epochs.

**참고:** mAP가 0.99 수준이면 데이터가 쉽거나 train/test 유사도가 높을 수 있습니다. 발표용으로는 **혼동 행렬·오탐/미탐 샘플 시각화**(Week 4 산출물)를 한 번 더 하는 것이 좋습니다.

---

### 8주 로드맵 대비 진행률

```text
Week 1  데이터·매핑·식약처 API     [████░░░░░░] ~40%
Week 2  YOLO baseline + WandB     [██████░░░░] ~60%  ← 현재 위치
Week 3  Augmentation Ablation     [░░░░░░░░░░]  0%
Week 4  Transfer + 모델 확정      [██░░░░░░░░] ~20%  (best.pt만 있음)
Week 5  FastAPI                   [░░░░░░░░░░]  0%
Week 6  Streamlit E2E             [░░░░░░░░░░]  0%
Week 7  Docker / ONNX             [░░░░░░░░░░]  0%
Week 8  README / PPT / 시연       [███░░░░░░░] ~30%  (문서만)
```

#### Week 1 — 부분 완료
- ✅ `data.yaml`, 80/10/10 분할
- ❌ EDA 노트북
- ❌ `mapping.json` (~150 동의어)
- ❌ `pantry.json`
- ❌ 식약처 API 배치 수집·한식 DB 병합
- ❌ `ingredients` 파싱 파이프라인

#### Week 2 — 핵심만 완료
- ✅ **YOLOv11n** + `best.pt`
- ❌ **YOLOv8n baseline** (비교 실험 없음)
- ❌ **WandB** 로그/실험 기록

#### Week 3~4 — 미완
- Ablation 4종(아키텍처·증강·전이학습·옵티마이저) 표가 계획서에 `?` 상태
- `runs/` 학습 로그·`results.csv`는 Kaggle에만 있을 가능성 (로컬에는 없음)

#### Week 5~8 — 미착수
- FastAPI (`/predict`, `/recipes`, `/recipe/{id}`, `/scale`) 없음
- Streamlit UI 7화면 없음
- Docker / docker-compose 없음
- `mapping.json`, `pantry.json` 없어 S2~S5 스토리지 연동 불가

---

### 계획서 마일스톤 체크

| 마일스톤 | 계획 | 실제 |
|----------|------|------|
| Week 2 말: Baseline (v8+v11, WandB) | ✅ | **v11만 완료** (~60%) |
| Week 4 말: 최종 모델 + Ablation 4종 | ✅ | **가중치만 확보**, Ablation 미실시 |
| Week 6 말: FastAPI + Streamlit E2E | ✅ | **미시작** |
| Week 8 말: 배포·제출 | 🎯 | 문서 위주 |

---

### 다음에 하면 좋은 작업 (우선순위)

1. **Week 1 마무리** — `mapping.json`, `pantry.json`, 재료 파싱 스크립트 (YOLO 30클래스 ↔ 레시피 재료 연결의 전제)
2. **FastAPI + `best.pt` 연동** — `/predict`부터 E2E 최소 데모 (Week 5~6)
3. **발표/보고용** — Kaggle `runs/fridge_yolo11n/results.csv`·학습 곡선 다운로드, 오탐/미탐 이미지 몇 장 저장
4. **(선택) Week 2 보완** — YOLOv8n 1회 학습 또는 WandB 1 run으로 baseline 표 채우기
5. **(선택) Ablation** — 시간이 부족하면 계획서 표에 **현재 설정 1행만** 실측값으로 채우고, 나머지는 “추가 실험 예정”으로 명시

---

### 한 줄 정리

**냉장고 재료 탐지 모델(YOLOv11n `best.pt`)은 계획 목표를 크게 상회하는 성능으로 학습 완료**되었고, **레시피 추천·API·UI·배포 쪽은 아직 설계 문서 단계**입니다. 지금은 계획상 **Week 2 말 ~ Week 4 초** 구간으로 보시면 됩니다.

Kaggle 학습 로그(`results.csv`, confusion matrix)나 `mapping.json` 초안 작성까지 이어서 진행할까요?

---

**User**

@/Users/k2/Documents/프로젝트/ 로
@fridge-recipe-plan-v3.md 여기서 다음 단계로 ablation study를 하려고 하는데 @ablation_yolo.py 이렇게 클로드가 코드 작성해줬는데 이상없지?

---

**Cursor**

ablation 스크립트와 계획서의 실험 정의를 대조해 검토합니다.


Ultralytics API와 실험 설정 호환성을 추가로 확인합니다.


`ablation_yolo.py`를 계획서 §6.2와 `train_yolo_byclaude.py`와 맞춰 봤고, 1 epoch 스모크 테스트로 메트릭 추출도 확인했습니다.

## 결론

**전체적으로 실행 가능하고, 계획서 4개 실험 구조와도 잘 맞습니다.** 그대로 Kaggle에서 `--exp 1`부터 돌려도 됩니다.

다만 **발표/보고서에 그대로 쓰기 전에 알아둘 점**이 몇 가지 있습니다. 치명적 버그는 아니고, **해석·공정 비교** 쪽 이슈입니다.

---

## 잘 된 점

| 항목 | 평가 |
|------|------|
| 실험 1~4 구성 | 계획서 표와 1:1 대응 (v8n/s vs v11n/s, 증강 단계, scratch/pretrain/freeze, SGD/Adam/AdamW) |
| 공정 비교 | 실험 1·3·4에서 AdamW·증강 등을 맞춰 **비교 변수만** 바꿈 |
| `find_data_yaml()` | Kaggle `rglob` + 로컬 smart refrigerator 우선 — 실사용에 유리 |
| 메트릭 추출 | `trainer.metrics['metrics/mAP50(B)']` 등 **키 이름 정확** (스모크 테스트 확인) |
| fallback | `trainer.metrics` 실패 시 `best.pt`로 `val()` 재실행 |
| 결과 저장 | `ablation_results.json` + 표 출력 → PPT 표 채우기 좋음 |
| 실행 시간 | Ablation 50 epoch — 전체 14 run은 부담이지만 의도는 타당 |

---

## 알아둘 점 (수정 권장은 “선택”)

### 1. 평가 split: val vs test

```101:101:ablation_yolo.py
    test set 평가는 ablation에서 생략 — val mAP로 상호 비교.
```

- Ablation **끼리 비교**에는 val로 통일해도 됩니다.
- 이미 만든 `best.pt`(100 epoch, test mAP 0.99)와 **숫자를 직접 비교하면 안 됩니다** (epoch·split·설정이 다름).
- 발표용: “Ablation은 val 50 epoch, 최종 모델은 test 100 epoch”라고 한 줄만 적어두면 됩니다.

### 2. 계획서 대비 빠진/다른 설정

| 계획서 | 코드 | 영향 |
|--------|------|------|
| 실험 2: `+ Copy-Paste` | MixUp까지만 4단계 | 표 5행째는 비어 있음 → 추가 run 또는 “미실시” 명시 |
| 실험 4: SGD + **StepLR** | `cos_lr=False`만 (선형 감쇠) | Ultralytics 기본 스케줄 — 보고서에 “StepLR 대신 기본 linear decay”라고 쓰면 충분 |
| 실험 1: GPU Inference, Size | 미측정 | 표의 Params/Size/GPU 열은 **수동 기입** 또는 나중에 한 번만 측정 |

### 3. 실험 3 — `from scratch`

`yolo11n.pt` + `pretrained=False`는 Ultralytics가 **가중치를 비운 뒤** 구조만 쓰므로 scratch로 써도 됩니다.

더 명확하게 하려면:

```python
("exp3_scratch", "yolo11n.yaml", dict(pretrained=False, freeze=None)),
```

### 4. `freeze=10` — “백본 전체”는 근사치

주석의 “backbone = 10 layers”는 **대략적인 설정**입니다. 레이어 0~9만 얼리므로, 보고서에는 “backbone 일부 freeze (freeze=10)” 정도가 안전합니다. `freeze`가 너무 크면 전체 freeze 에러가 나는데, 10은 보통 괜찮습니다.

### 5. 리소스

- `--exp all` → **14번 × 50 epoch** → Kaggle 9시간 제한에 걸릴 수 있음  
  → `--exp 1`, `2` … 나눠 실행 권장  
- `yolov8s` / `yolo11s` + `batch=16` → T4에서 OOM 가능 → `YOLO_BATCH=8` 환경변수는 **아직 없음** (필요 시 `run_experiment`의 `batch`만 env로 빼면 됨)

### 6. 실험 2 `exp2_no_aug`

`mosaic=0`, `fliplr=0` 등은 의도에 맞습니다. 다만 Ultralytics **기본 letterbox·정규화**는 남습니다. “None = 학습 시 인위적 증강 최소화”로 설명하면 됩니다.

---

## 실행 전 체크리스트

```bash
# 로컬
cd "/Users/k2/Documents/프로젝트"
YOLO_DATA_ROOT="smart refrigerator.yolov11" YOLO_EPOCHS=50 .venv/bin/python ablation_yolo.py --exp 1

# Kaggle
!pip install -q ultralytics pyyaml
!python ablation_yolo.py --exp 1   # 먼저 1개만
```

- GPU 켜기  
- `ablation/ablation_results.json` (또는 Kaggle Output) 다운로드  
- 표 채울 때 **같은 실험 번호 내에서만** mAP 순위 비교  

---

## 한 줄 요약

**이상 없이 돌아가는 Ablation 스크립트입니다.** 계획서와의 차이는 Copy-Paste 미포함, SGD 스케줄 표현, val 기준 평가, GPU/용량 미측정 정도이고, **코드 버그라기보다 보고서에 한 줄씩 보완 설명하면 되는 수준**입니다.

원하시면 `Copy-Paste` 5번째 실험 추가, `YOLO_BATCH` env, 최종 1등 설정만 `test` split 재평가하는 패치를 짧게 넣어 드릴 수 있습니다.

---

**User**

@/Users/k2/Documents/프로젝트/ 로
@fridge-recipe-plan-v3.md @ablation_yolo.py 너가 말한거 토대로 코드 수정했는데 정합성 판단해줘

---

**Cursor**

수정된 `ablation_yolo.py`를 계획서와 이전 피드백 기준으로 대조 검토합니다.


치명적 구조 문제가 보여 문법·실행 가능 여부를 확인합니다.


`run_experiment` 함수 정의가 편집 중 깨져 실행되지 않습니다. 수정합니다.


수정본을 계획서 §6.2·이전 피드백과 대조했습니다. **의도는 잘 반영됐지만, `run_experiment` 함수 정의가 편집 중 깨져 있어 실행이 불가능한 상태**였습니다. 그 부분은 복구해 두었습니다.

---

## 정합성 판단 요약

| 구분 | 판단 |
|------|------|
| 계획서 실험 1~4 구조 | ✅ 잘 맞음 |
| 이전 피드백 반영 | ✅ 대부분 반영 |
| **실행 가능성** | ❌ → **`run_experiment` 누락 버그 수정 완료** |
| 계획서와 100% 동일 | ⚠️ CutMix·수렴 속도·val/test 표기만 보완 설명 필요 |

---

## 잘 반영된 수정 (이전 피드백 대비)

| 피드백 | 수정 내용 | 계획서 대응 |
|--------|-----------|-------------|
| `YOLO_BATCH` | env + `run_experiment`에 `batch=BATCH` | OOM 대응 ✅ |
| Copy-Paste | `exp2_full_aug_cp` (`copy_paste=0.1`) | 실험 2 5행 ✅ |
| scratch 명확화 | `yolo11n.yaml` + `pretrained=False` | 실험 3 Random init ✅ |
| GPU / Params / Size | `measure_gpu_ms`, `get_model_info`, 표·JSON | 실험 1 표 열 ✅ |
| SGD 스케줄 | 주석으로 linear decay 명시 | 실험 4 (StepLR과 표현 차이만 문서화) ✅ |
| freeze 설명 | “레이어 0~9” 주석 | 실험 3 backbone freeze ✅ |

실험 2는 이제 **5단계**로 계획서와 맞습니다.

```269:274:ablation_yolo.py
        # 5단계: MixUp + Copy-Paste 추가 (계획서 최고 단계)
        ("exp2_full_aug_cp", dict(
            mosaic=1.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
            fliplr=0.5, translate=0.1, scale=0.5, mixup=0.1,
            copy_paste=0.1,
        )),
```

실험 3 scratch도 의도대로입니다.

```292:297:ablation_yolo.py
        # yolo11n.yaml: 구조 정의 파일만 사용 → 진짜 random init (scratch)
        ("exp3_scratch",    "yolo11n.yaml", dict(pretrained=False, freeze=None)),
        # yolo11n.pt + pretrained=True: COCO 가중치 전체 파인튜닝
        ("exp3_finetune",   "yolo11n.pt",   dict(pretrained=True,  freeze=None)),
        # backbone 일부 freeze (레이어 0~9), head만 학습
        ("exp3_freeze_bb",  "yolo11n.pt",   dict(pretrained=True,  freeze=10)),
```

---

## 치명적 문제 (수정함)

`get_model_info()` 안에 `run_experiment` 본문이 들어가 있어 **`def run_experiment(...)`가 없었고**, import는 되지만 `NameError`가 났을 상태였습니다.

- `def run_experiment(...)` 복구
- `get_model_info`는 파라미터/파일 크기만 담당하도록 분리
- docstring에 “Ablation은 val 기준, 최종 `best.pt`(100ep·test)와 별도 보고” 명시

지금은 `py_compile` 및 `run_experiment` 정의 확인까지 통과합니다.

---

## 계획서와 남는 차이 (보고서에 한 줄씩 쓰면 됨)

### 1. 실험 2 — CutMix

| 계획서 | 코드 |
|--------|------|
| `+ MixUp / CutMix` (한 행) | `mixup=0.1`만 (`cutmix` 미사용) |

Ultralytics는 `cutmix` 인자를 지원합니다. 표를 계획서와 완전히 맞추려면 `exp2_full_aug`에 `cutmix=0.1`을 넣거나, 보고서에 “CutMix는 MixUp 단계에 포함하지 않음”이라고 적으면 됩니다.

### 2. 실험 3 — 수렴 속도

계획서 표의 “수렴 속도”는 코드에 `time_min`으로 저장되지만 **표에는 안 나옵니다**. JSON의 `time_min`을 실험 3 표에 넣거나, “수렴 속도 = 학습 시간(분)”으로 정의하면 됩니다.

### 3. 평가 split

여전히 **val mAP**로 Ablation 간 비교 (의도적으로 OK).  
기존 `best.pt`(test, 100 epoch, mAP ~0.99)와 **숫자를 한 표에 섞지 말 것**.

### 4. 실험 4 — StepLR

SGD는 `cos_lr=False` → Ultralytics **linear decay** (StepLR과 유사). 주석은 적절하고, 발표 슬라이드에도 동일하게 쓰면 됩니다.

### 5. `get_model_info`의 `size_mb`

`.pt`가 아직 다운로드되지 않으면 `0.0`일 수 있습니다. 실험 1은 계획서에 12MB/10MB 등 **고정값**이 있으므로, 0이면 계획서 표 값을 쓰고 JSON의 `params_m`만 자동 채워도 됩니다.

### 6. 실행 규모

`--exp all` → **15 runs × 50 epoch** (실험 2가 5개). Kaggle은 `--exp 2`처럼 나눠 실행 권장.

---

## 계획서 §6.2 매핑표

| 실험 | 계획서 | 코드 | 정합성 |
|------|--------|------|--------|
| 1 | v8n/s, v11n/s, Params, GPU, Size | 4모델 + `params_m`, `gpu_ms`, `size_mb` | ✅ |
| 2 | 5단계 증강 | 5 configs (Copy-Paste 포함) | ✅ (CutMix만 ⚠️) |
| 3 | scratch / finetune / freeze | yaml scratch + pt finetune + freeze=10 | ✅ |
| 4 | SGD / Adam / AdamW | 3 configs + 주석 | ✅ (StepLR 표현만 문서) |

---

## 최종 판단

**수정 방향은 계획서·피드백과 잘 맞습니다.**  
다만 편집 과정에서 `run_experiment`가 빠져 **실행 불가**였고, 그건 지금 고쳐 두었습니다.

이 상태에서 Kaggle에서:

```bash
!python ablation_yolo.py --exp 1
```

부터 돌리면 됩니다. CutMix 추가나 실험 3 표에 `time_min` 컬럼 넣는 것도 원하면 이어서 패치해 드리겠습니다.

---

**User**

@/Users/k2/Documents/프로젝트/ 
@ablation_results_1.json @ablation_results_3.json 일단 1과 3의 결과야 아직 2랑 4도 더 돌려야돼. 결과 괜찮은지 확인해줘

---

**Cursor**

실험 1·3 결과 JSON을 읽고 계획서 목표와 대조합니다.


실험 1·3 JSON을 계획서 목표(§6.1·§6.2)와 맞춰 봤습니다. **전부 목표치( mAP@0.5 ≥ 0.70 등)는 크게 넘고**, Ablation으로 쓸 **스토리도 나옵니다.** 다만 수치가 전반적으로 매우 높고(≈0.99), 실험 1·3 해석 시 몇 가지는 발표에서 짚어 두는 편이 좋습니다.

---

## 1. 목표치 달성 여부 (§6.1)

| 지표 | 목표 | 실험 1 (전 모델) | 실험 3 (전 조건) |
|------|------|----------------|------------------|
| mAP@0.5 | ≥ 0.70 | 0.991 ~ 0.994 | 0.976 ~ 0.991 |
| mAP@0.5:0.95 | ≥ 0.45 | 0.803 ~ 0.848 | 0.703 ~ 0.807 |
| Recall | ≥ 0.70 | 0.987 ~ 0.992 | 0.944 ~ 0.987 |
| GPU 추론 | ≤ 10 ms | JSON에 없음* | 8.5 ~ 8.8 ms ✅ |

\*실험 1 JSON에는 `gpu_ms`가 없고, 실험 3만 있습니다. 실험 1 표는 실험 3의 yolo11n 수치(≈8.5 ms)를 참고하거나, `best.pt`로 한 번 더 재측정하면 됩니다.

**결론: “성능이 부족하다”는 문제는 없습니다.** 오히려 **과제·발표용으로는 충분히 좋은 수준**입니다.

---

## 2. 실험 1 — 아키텍처 비교

| 모델 | mAP@0.5 | mAP@0.5:0.95 | Recall | 학습 시간 |
|------|---------|--------------|--------|-----------|
| YOLOv8n | **0.9919** | 0.8035 | 0.987 | 23.6분 |
| YOLOv8s | 0.9933 | **0.8479** | 0.9897 | 38.2분 |
| **YOLOv11n** | 0.9914 | 0.8074 | 0.9868 | 25.1분 |
| **YOLOv11s** | **0.9936** ★ | 0.8469 | **0.9924** | 39.5분 |

### 해석 (발표용)

1. **네 모델 차이는 매우 작음** (mAP@0.5 기준 약 0.2%p).  
   → “v11이 v8을 압도한다”보다는 **“이 데이터셋에서는 모두 고성능, 배포 관점에서 n/s 트레이드오프”**가 맞는 말입니다.

2. **최고 성능**: `yolo11s` (mAP@0.5 1위), **mAP@0.5:0.95**는 `yolov8s`가 근소하게 1위.

3. **최종 모델 후보로 yolo11n을 고르는 근거는 여전히 타당**  
   - `yolo11n` vs `yolov8n`: mAP@0.5는 v8n이 0.0005 높지만 사실상 동급.  
   - 계획서대로 **파라미터 2.6M·가벼움·이미 `best.pt`로 100 epoch 학습 완료** → **배포·속도·일관성** 측면에서 n이 합리적.  
   - `yolo11s` / `yolov8s`는 성능은 조금 더 좋을 수 있으나 **학습 시간 +40~60%**, 모델도 더 큼.

4. **실험 3 `exp3_finetune`과 `exp1_yolov11n` 수치가 동일** (0.9914 / 0.8074)  
   → 같은 설정·에폭이면 **재현성 OK**로 보면 됩니다.

---

## 3. 실험 3 — Transfer Learning

| 조건 | mAP@0.5 | mAP@0.5:0.95 | Recall | 시간(분) | GPU ms |
|------|---------|--------------|--------|----------|--------|
| Scratch (`yaml`, no pretrain) | 0.9850 | 0.7352 | 0.9579 | 24.8 | 8.5 |
| **COCO full fine-tune** | **0.9914** ★ | **0.8074** ★ | **0.9868** | 24.1 | 8.7 |
| COCO + freeze backbone (0~9) | 0.9759 | 0.7033 | 0.9443 | **19.1** ★ | 8.8 |

### 해석 (계획서 질문에 답이 되는지)

| 계획서 질문 | 결과 | 판단 |
|-------------|------|------|
| 사전학습이 도움이 되는가? | Fine-tune > Scratch (mAP@0.5 +0.64%p, mAP@0.5:0.95 +7.2%p) | ✅ **유의미한 방향** (절대값 차이는 작지만 일관됨) |
| Backbone freeze가 좋은가? | Freeze가 **가장 낮음**, full fine-tune이 최고 | ✅ **최종 선택은 full fine-tune이 맞음** (계획서의 AdamW·pretrained 전략과 일치) |
| 수렴 속도 | Freeze가 **가장 빠름**(19.1분) but 성능 희생 | ✅ 트레이드오프로 설명 가능 |

**발표 한 줄 예시:**  
> “COCO 사전학습 full fine-tuning이 scratch·backbone freeze 대비 mAP와 Recall에서 가장 좋았고, freeze는 학습은 빠르지만 성능이 떨어져 최종 모델에는 full fine-tune을 채택했다.”

Scratch도 0.985로 높아서, **이 데이터는 scratch만으로도 거의 학습 가능**하다는 점은 한계/논의로 한 줄 넣으면 좋습니다 (Roboflow 도메인·클래스 난이도).

---

## 4. “괜찮은지” — 종합 판단

| 항목 | 판단 |
|------|------|
| 수치 품질 | ✅ 목표 대비 매우 여유 |
| Ablation 논리 | ✅ 실험 1(아키텍처), 실험 3(전이학습) 모두 **표 채우기·스토리 가능** |
| 최종 모델 선택 정당화 | ✅ **yolo11n + COCO full fine-tune** (실험 3·기존 `best.pt`와 정합) |
| 주의할 점 | ⚠️ 전 모델 mAP≈0.99 → **val·50 epoch 기준**, test·100 epoch `best.pt`와 표기 구분 |
| 실험 1 JSON | ⚠️ `gpu_ms` / `params_m` 없음 → PPT 표는 계획서 고정값(3.2M, 2.6M 등) + 실험 3 GPU 수치 보완 |

**2·4를 더 돌려도 됩니다.** 1·3만으로도 “아키텍처는 n/s 트레이드오프, 전이학습은 full fine-tune 승”까지는 이미 정리 가능합니다.

---

## 5. 실험 2·4 돌릴 때 기대

- **실험 2**: 증강을 끄면(`no_aug`) 지금보다 **mAP가 떨어지는지**가 핵심. 전부 0.99면 증강 효과가 작다고 쓰면 됩니다.  
- **실험 4**: `exp4_adamw`가 **exp3_finetune / exp1_yolov11n과 비슷한지** 보면 optimizer 선택 근거가 완성됩니다.

---

## 6. PPT 표에 바로 넣을 숫자 (실험 1·3)

**실험 1**

| Model | mAP@0.5 | mAP@0.5:0.95 | Recall |
|-------|---------|--------------|--------|
| YOLOv8n | 0.992 | 0.804 | 0.987 |
| YOLOv8s | 0.993 | 0.848 | 0.990 |
| YOLOv11n | 0.991 | 0.807 | 0.987 |
| YOLOv11s | **0.994** | 0.847 | **0.992** |

**실험 3**

| 초기 가중치 | Freeze | mAP@0.5 | mAP@0.5:0.95 | 시간(분) |
|-------------|--------|---------|--------------|----------|
| Random | - | 0.985 | 0.735 | 24.8 |
| COCO pretrained | Full | **0.991** | **0.807** | 24.1 |
| COCO pretrained | Backbone | 0.976 | 0.703 | **19.1** |

실험 2·4 JSON 나오면 같은 형식으로 표 정리해 드릴 수 있습니다.

---

**User**

@/Users/k2/Documents/프로젝트/ 로
@ablation_results_2.json 이결과는 어떤지 확인해줘 2에 대한 결과야

---

**Cursor**

실험 2(Augmentation) 결과를 계획서 §6.2와 실험 1·3과 맞춰 정리했습니다.

---

## 요약

**Ablation으로 쓰기에 매우 좋은 결과입니다.**  
증강을 끄면 성능이 확실히 떨어지고, **Mosaic만 켜도 큰 폭으로 회복**됩니다. 다만 “단계를 더 쌓을수록 항상 좋아진다”는 식으로 쓰면 안 되고, **Mosaic이 핵심·이후 단계는 mAP@0.5:0.95 기준으로는 오히려 소폭 하락**이라고 쓰는 게 맞습니다.

---

## 계획서 목표 (§6.1) 대비

| 단계 | mAP@0.5 | mAP@0.5:0.95 | Recall | 목표 달성 |
|------|---------|--------------|--------|-----------|
| None (`no_aug`) | 0.957 | 0.669 | 0.908 | ✅ (전 지표 ≥ 목표) |
| Mosaic 단독 | 0.993 | 0.844 | 0.989 | ✅ |
| + HSV/Flip/Translate | 0.991 | 0.807 | 0.987 | ✅ |
| + MixUp | 0.992 | 0.798 | 0.987 | ✅ |
| + Copy-Paste | 0.992 | 0.798 | 0.987 | ✅ |

증강 없어도 목표(0.70 / 0.45 / Recall 0.70)는 넘지만, **다른 설정 대비로는 확실히 열세**입니다.

---

## 단계별 결과 (계획서 표 순서)

| 계획서 증강 전략 | 실험명 | mAP@0.5 | mAP@0.5:0.95 | Recall | 학습(분) |
|------------------|--------|---------|--------------|--------|----------|
| None | `exp2_no_aug` | 0.9572 | 0.6693 | 0.9080 | 16.2 |
| Mosaic 단독 | `exp2_mosaic_only` | **0.9926** ★ | **0.8442** ★ | **0.9889** | 23.1 |
| + HSV / Flip / Translate | `exp2_mosaic_hsv_flip` | 0.9914 | 0.8074 | 0.9868 | 24.0 |
| + MixUp | `exp2_full_aug` | 0.9915 | 0.7982 | 0.9871 | 24.3 |
| + Copy-Paste | `exp2_full_aug_cp` | 0.9915 | 0.7982 | 0.9871 | 24.4 |

GPU 추론은 전부 **8.3~8.6 ms** (목표 ≤10 ms 충족).

---

## 해석 (발표·보고서용)

### 1. 증강 효과는 분명함 (가장 중요)

`no_aug` → `mosaic_only`만 보면:

- mAP@0.5: **0.957 → 0.993** (+3.6%p)
- mAP@0.5:0.95: **0.669 → 0.844** (+17.5%p)
- Recall: **0.908 → 0.989**

→ **“Data augmentation, 특히 Mosaic이 이 냉장고 데이터셋 학습에 필수”**라고 말할 근거가 됩니다.

### 2. 최고 성능은 “Mosaic 단독”

5단계 중 **mAP@0.5·mAP@0.5:0.95·Recall 모두 1위는 `mosaic_only`**입니다.  
HSV/Flip/Translate·MixUp·Copy-Paste를 더해도 **0.993을 넘기지 못했고**, mAP@0.5:0.95는 **0.844 → 0.798**으로 오히려 낮아집니다.

→ 발표 문장 예:

> “단계적 증강 중 Mosaic이 성능 기여가 가장 크고, 이후 증강은 val 기준으로 추가 이득이 제한적이거나 mAP@0.5:0.95에서는 소폭 하락했다.”

### 3. `mosaic_hsv_flip` = 본 학습 설정과 일치

수치가 실험 1 `yolo11n`, 실험 3 `finetune`과 **완전히 동일**합니다.

| 항목 | mAP@0.5 | mAP@0.5:0.95 |
|------|---------|--------------|
| exp2_mosaic_hsv_flip | 0.9914 | 0.8074 |
| exp1_yolov11n / exp3_finetune | 0.9914 | 0.8074 |

→ `train_yolo_byclaude.py` 기본 증강(Mosaic + HSV + Flip 등)과 **재현·정합 OK**.  
최종 `best.pt` 학습 설정을 “실험 2의 3단계”로 설명해도 됩니다.

### 4. MixUp / Copy-Paste는 차이 없음

`exp2_full_aug`와 `exp2_full_aug_cp`가 **소수 넷째 자리까지 동일**합니다.

- 50 epoch·val 기준으로 **추가 이득이 거의 없음**
- 동일 수렴/동일 best 가중치에 가깝다고 보는 것이 자연스러움

보고서에는 예:

> “MixUp·Copy-Paste는 본 설정·에폭에서는 성능 차이를 만들지 않아, 최종 학습에는 Mosaic+기하/색상 증강을 유지했다.”

### 5. 학습 시간

| 설정 | 시간 |
|------|------|
| no_aug | 16.2분 (가장 빠름) |
| mosaic_only | 23.1분 |
| 나머지 | ~24분 |

증강이 많을수록 epoch당 부담이 커지지만, **성능 최고 ≠ 가장 무거운 증강**입니다.

---

## 실험 1·3과 함께 보면

| 비교 | 내용 |
|------|------|
| 증강 없음 (exp2) | mAP@0.5 **0.957** |
| 증강 있음 (대부분) | **~0.991~0.993** |
| scratch (exp3) | 0.985 (pretrain 없음) |
| no_aug만큼 크게 떨어지는 건 **증강 제거** | 전이학습 제거보다 영향이 큼 |

→ **“이 프로젝트에서 성능을 가르는 요인: Mosaic급 증강 > (소폭) 사전학습”** 정도로 정리 가능합니다.

---

## 주의할 점 (발표 때 한 줄)

1. **val · 50 epoch** 기준 (실험 1·3과 동일). test·100 epoch `best.pt`와 표를 섞지 말 것.  
2. **단조 증가 곡선이 아님** — “증강을 많이 넣을수록 항상 좋다”고 쓰지 말 것.  
3. **CutMix**는 코드에 없고 MixUp만 있음 (계획서 표와 표현만 맞추면 됨).

---

## 종합 판단

| 항목 | 판단 |
|------|------|
| 결과 품질 | ✅ 목표 대비 충분, Ablation 스토리 명확 |
| 계획서 실험 2 | ✅ 5단계 모두 채움 |
| 최종 설정 정당화 | ✅ **Mosaic + HSV/Flip/Translate** (`mosaic_hsv_flip`) — 본학습·실험 1·3과 일치 |
| PPT 한 줄 결론 | “증강 필수, Mosaic이 핵심; 본 프로젝트 최종 증강은 YOLO 기본 기하·색상 스택” |

실험 4만 남기면 optimizer 표까지 Ablation이 완성됩니다. `ablation_results_4.json` 나오면 같은 형식으로 이어서 정리해 드리겠습니다.

---

**User**

@/Users/k2/Documents/프로젝트 로
@ablation_results_2.json @ablation_results_4.json 결과 어떤지 확인해줘

---

**Cursor**

실험 2·4 JSON을 계획서 목표와 실험 1·3 결과와 맞춰 봤습니다. **둘 다 Ablation·발표용으로 충분히 쓸 만한 결과**입니다.

---

## 한 줄 요약

| 실험 | 핵심 메시지 |
|------|-------------|
| **실험 2 (증강)** | 증강 없으면 크게 하락 → **Mosaic이 핵심**. 이후 단계는 추가 이득 거의 없음 |
| **실험 4 (옵티마이저)** | SGD·Adam·AdamW **모두 고성능**, 차이는 **0.06%p 수준** → **AdamW 선택은 수치·설계 일관성**으로 정당화 |

---

## 실험 2 — Augmentation

| 계획서 단계 | 실험명 | mAP@0.5 | mAP@0.5:0.95 | Recall | 시간 |
|-------------|--------|---------|--------------|--------|------|
| None | `no_aug` | 0.957 | 0.669 | 0.908 | 16.2분 |
| Mosaic 단독 | `mosaic_only` | **0.993** ★ | **0.844** ★ | **0.989** | 23.1분 |
| + HSV/Flip/Translate | `mosaic_hsv_flip` | 0.991 | 0.807 | 0.987 | 24.0분 |
| + MixUp | `full_aug` | 0.992 | 0.798 | 0.987 | 24.3분 |
| + Copy-Paste | `full_aug_cp` | 0.992 | 0.798 | 0.987 | 24.4분 |

**목표(≥0.70 / ≥0.45 / Recall≥0.70)**: 전 단계 ✅ (no_aug 포함)

### 해석

1. **증강 효과는 분명함**  
   `no_aug` → `mosaic_only`: mAP@0.5 **+3.6%p**, mAP@0.5:0.95 **+17.5%p**  
   → “증강, 특히 Mosaic 필수”라고 쓸 근거가 됩니다.

2. **최고 성능은 Mosaic 단독**  
   HSV/Flip·MixUp·Copy-Paste를 더해도 mAP@0.5:0.95는 **0.844 → 0.798**으로 오히려 낮아짐.  
   → “단계를 더 쌓을수록 항상 좋아진다”고 쓰면 안 됩니다.

3. **`mosaic_hsv_flip` = 본학습 설정**  
   수치가 실험 1 `yolo11n`, 실험 3 `finetune`, 실험 4 `adamw`와 **동일** (0.9914 / 0.8074).  
   → `train_yolo_byclaude.py`와 **재현·정합 OK**.

4. **MixUp / Copy-Paste**  
   `full_aug`와 `full_aug_cp`가 **완전 동일** → 50 epoch·val 기준 **추가 이득 없음**.

**발표 한 줄:**  
> Mosaic이 성능 기여의 대부분을 차지하며, 최종 학습은 YOLO 기본 기하·색상 증강(`mosaic_hsv_flip`)을 채택했다.

---

## 실험 4 — Optimizer

| 계획서 | 실험명 | LR | Scheduler | mAP@0.5 | mAP@0.5:0.95 | Recall | 시간 |
|--------|--------|-----|-----------|---------|--------------|--------|------|
| SGD + Momentum | `exp4_sgd` | 0.01 | linear decay* | **0.9920** ★ | **0.8167** ★ | 0.985 | 25.5분 |
| Adam | `exp4_adam` | 0.001 | 없음 | 0.9916 | 0.8089 | 0.988 | 25.0분 |
| **AdamW** | `exp4_adamw` | 0.001 | Cosine | 0.9914 | 0.8074 | 0.987 | 25.0분 |

\*코드 주석대로 StepLR 대신 Ultralytics linear decay

**목표**: 세 옵티마이저 모두 ✅  
**GPU**: 8.6~8.8 ms (≤10 ms ✅)

### 해석

1. **숫자상 1위는 SGD**  
   mAP@0.5 **0.9920**, mAP@0.5:0.95 **0.8167** — AdamW 대비 +0.06%p / +0.9%p.

2. **차이는 매우 작음**  
   세 설정 모두 **~0.991~0.992** 구간 → 이 데이터·50 epoch에서는 **옵티마이저 선택이 성능을 크게 가르지 않음**.

3. **AdamW를 최종 선택한 이유는 여전히 설득 가능**  
   - Ablation 수치와 **본학습·실험 2·3과 완전 일치** (0.9914 / 0.8074)  
   - 계획서·`train_yolo_byclaude.py`와 **설계 일관성**  
   - weight decay 분리 + cosine LR (일반적인 fine-tuning 관행)  
   - SGD 대비 성능 차이가 **실질적으로 무시 가능**

4. **Adam**  
   Recall은 0.9881로 AdamW보다 약간 높지만, mAP@0.5:0.95는 AdamW보다 낮음 → **종합 1위는 아님**.

**발표 한 줄 (정직하게):**  
> Optimizer ablation에서 SGD·Adam·AdamW 모두 목표를 크게 상회했으며, SGD가 mAP@0.5:0.95에서 근소 우위를 보였으나 차이는 1%p 미만이어서, 본 프로젝트는 계획대로 AdamW + CosineAnnealingLR을 최종 학습에 사용했다.

---

## 4개 실험 종합 (Ablation 완성)

| 실험 | 결론 (최종 모델 정당화) |
|------|-------------------------|
| 1 아키텍처 | v11n/v8n 동급, **yolo11n** = 가벼움·배포 |
| 2 증강 | **Mosaic 필수**, 최종 = mosaic + HSV/Flip |
| 3 전이학습 | **COCO full fine-tune** > scratch > freeze |
| 4 옵티마이저 | **AdamW** = 본학습과 동일, SGD와 실질 동급 |

**최종 학습 스택 (Ablation과 일치):**  
`yolo11n.pt` + COCO pretrained + AdamW + cos_lr + mosaic/HSV/flip (+ 본학습 100 epoch)

---

## PPT에 넣을 표 (실험 2·4)

**실험 2**

| 증강 전략 | mAP@0.5 | Recall |
|-----------|---------|--------|
| None | 0.957 | 0.908 |
| Mosaic 단독 | **0.993** | **0.989** |
| + HSV/Flip/Translate | 0.991 | 0.987 |
| + MixUp | 0.992 | 0.987 |
| + Copy-Paste | 0.992 | 0.987 |

**실험 4**

| Optimizer | mAP@0.5 | mAP@0.5:0.95 |
|-----------|---------|--------------|
| SGD | **0.992** | **0.817** |
| Adam | 0.992 | 0.809 |
| **AdamW (채택)** | 0.991 | 0.807 |

---

## 주의 (발표 시)

1. 전부 **val · 50 epoch** — test·100 epoch `best.pt`와 표기 구분  
2. 실험 2: **단조 증가 아님** (Mosaic 단독이 일부 지표 1위)  
3. 실험 4: **SGD가 수치 1위** — AdamW 채택 이유를 “미세 차이 + 설계 일관성”으로 설명

**종합: 실험 2·4 모두 Ablation 목적에 부합하고, 4종 실험으로 계획서 §6.2 표를 채울 수 있는 수준입니다.**  
1·2·3·4 JSON을 하나로 합친 **최종 Ablation 요약표**가 필요하면 말해 주세요.

---

**User**

@/Users/k2/Documents/프로젝트/ 다음 단계는 무엇을 구축하면되지?

---

**Cursor**

계획서와 현재 산출물을 대조해 다음 단계를 정리합니다.


Ablation 4종과 `best.pt`까지 끝났으니, 계획서 기준으로 **Month 1(모델)은 사실상 완료**이고 **Month 2(앱·배포)**로 넘어가면 됩니다.

---

## 지금 위치

| 완료 | 미완 |
|------|------|
| YOLO 학습 (`best.pt`) | `mapping.json`, `pantry.json` |
| Ablation 1~4 + JSON | 재료 파싱 파이프라인 |
| 데이터셋, `recipes.csv` | FastAPI / Streamlit |
| 계획서·PPT 초안 | Docker, `requirements.txt` |
| | 식약처 API 한식 보강 (선택) |

앱 코드(FastAPI·Streamlit·Docker)는 **아직 없음** → 다음 핵심은 **End-to-End 서비스 구축**입니다.

---

## 추천 순서 (우선순위)

```mermaid
flowchart LR
    A[1. 데이터 레이어] --> B[2. FastAPI]
    B --> C[3. Streamlit UI]
    C --> D[4. Docker]
    D --> E[5. PPT·시연]
```

### 1단계 — 데이터·비즈니스 레이어 (1~2일) ← **지금 여기부터**

API/UI 전에 Storage Layer(S2~S5)를 먼저 만듭니다.

| 산출물 | 역할 | 계획서 |
|--------|------|--------|
| `mapping.json` | YOLO 30클래스 ↔ 레시피 재료 동의어 | §4.2.2, S2 |
| `pantry.json` | water, salt, pepper 등 상비 재료 | §5.4, S4 |
| `ingredient_parser.py` | `recipes.csv`의 `ingredients` 문자열 파싱 | §4.2.1 |
| `normalizer.py` | 탐지 결과 → 표준 재료명 | §5.2 |
| `ranker.py` | Coverage + 부족재료 점수 랭킹 | §5.3 |
| `pantry.py` | 보유/구매/pantry 3구간 분류 | §5.4 |
| `scaler.py` | 인분 비례 조정 (양념 ^0.7) | §5.5 |

**최소 목표:** YOLO 클래스 30개를 `mapping.json`에 1:1 매핑하고, pantry 10~20개만 넣어도 데모 가능.

**식약처 API:** 시간이 부족하면 **나중에**. 우선 `Recipes Dataset/recipes.csv` + `cuisine_path` 필터로 한식/요리 종류 필터를 돌려도 됩니다.

---

### 2단계 — FastAPI (3~5일) · Week 5

계획서 §5.6 엔드포인트:

| API | 기능 |
|-----|------|
| `GET /health` | 서버·모델 로드 확인 |
| `POST /predict` | 이미지 N장 → YOLO(`best.pt`) → 재료 목록·개수 |
| `POST /recipes` | 재료 + 필터 → Top-K 레시피 |
| `GET /recipe/{id}` | 상세 + 3구간 재료 분류 |
| `POST /scale` | 인분 변경 → 용량 재계산 |

**권장 폴더 구조:**

```text
프로젝트/
├── api/
│   ├── main.py          # FastAPI 앱
│   ├── predictor.py     # best.pt 로드·추론
│   └── schemas.py       # Pydantic 요청/응답
├── core/
│   ├── normalizer.py
│   ├── ranker.py
│   ├── pantry.py
│   └── scaler.py
├── data/
│   ├── mapping.json
│   ├── pantry.json
│   └── recipes.csv      # symlink 또는 복사
├── weights/best.pt
└── requirements.txt
```

**1차 마일스톤:** Swagger에서 사진 업로드 → 재료 JSON이 나오면 성공.

---

### 3단계 — Streamlit UI (3~5일) · Week 6

README/계획서 기준 **7화면**:

1. 사진 다중 업로드  
2. 인식 재료 목록 (+ 검색)  
3. 식사 종류 선택  
4. 요리 종류 선택  
5. 식단/선호 선택  
6. 추천 레시피 목록  
7. 레시피 상세 (시간·인분·3구간 재료·조리법)

Streamlit → FastAPI HTTP 호출로 연결.

**마일스톤:** 사진 → 필터 → 레시피 클릭 → 인분 변경까지 한 번에 동작.

---

### 4단계 — Docker + 재현성 (2~3일) · Week 7

| 산출물 | 내용 |
|--------|------|
| `requirements.txt` | ultralytics, fastapi, uvicorn, streamlit, pandas 등 |
| `Dockerfile` | API + UI (또는 서비스 2개) |
| `docker-compose.yml` | `docker compose up` 한 번에 기동 |
| (선택) ONNX 변환 | 배포·속도 증명용 |

계획서 목표: Docker 이미지 ≤3GB, 1회 명령 기동.

---

### 5단계 — 발표·제출 (Week 8)

| 작업 | 내용 |
|------|------|
| PPT | Ablation 1~4 표 숫자 반영 (`ablation_results_*.json`) |
| PPT | 최종 모델 선택 근거 (yolo11n + full fine-tune + mosaic/HSV) |
| README | 설치·실행 방법 |
| 시연 영상 | Streamlit E2E 2~3분 |

Ablation은 **끝났으니 PPT §6.2 표만 채우면** 모델 파트는 마무리됩니다.

---

## 병행하면 좋은 것 (짧게)

- **오탐/미탐 샘플 5~10장** 저장 (Week 4 산출물, 발표용)
- **Ablation 통합 JSON** 1개로 합치기 (관리 편의)
- `best.pt` **test set** 최종 수치 1줄 (Ablation val과 구분)

---

## 현실적인 2주 타임라인

| 주 | 집중 |
|----|------|
| **이번 주** | `mapping.json` + `pantry.json` + FastAPI `/predict`, `/recipes` |
| **다음 주** | `/recipe/{id}`, `/scale` + Streamlit 7화면 |
| **그다음** | Docker + PPT·시연 |

---

## 한 줄 결론

**다음 단계 = “모델 뒤의 앱” 구축**입니다.  
가장 먼저 **`mapping.json` + `pantry.json` + FastAPI(`/predict`부터)** 를 만들고, 그다음 Streamlit → Docker 순으로 가면 계획서 Week 5~8과 정확히 맞습니다.

원하면 **`mapping.json` 초안(30클래스) + FastAPI 뼈대**부터 코드로 만들어 드릴 수 있습니다.

---

**User**

@/Users/k2/Documents/프로젝트/ 
@Recipes Dataset @Recipes Dataset/recipes.csv @Recipes Dataset/test_recipes.csv 

ecipes.csv의 ingredients 필드(자연어 문자열)와
test_recipes.csv의 ingredients 필드(구조화된 JSON)를 함께 분석해서,
YOLO 30개 클래스에 대한 mapping.json을 만들어줘.

YOLO 30 클래스:
apple, banana, beef, blueberries, bread, butter,
carrot, cheese, chicken, chicken_breast, chocolate, corn, eggs,
flour, goat_cheese, green_beans, ground_beef, ham, heavy_cream,
lime, milk, mushrooms, onion, potato, shrimp, spinach,
strawberries, sugar, sweet_potato, tomato

조건:
- 각 클래스당 영문 별칭 3~5개 포함
- test_recipes.csv의 구조화된 name 필드에서 실제 등장하는 표현 우선 반영
- recipes.csv에서 자주 등장하는 표현도 포함
- 형식:
{
  "chicken_breast": ["chicken breast", "boneless chicken breast", "skinless chicken breast"],
  ...
}

---

**Cursor**

두 CSV의 ingredients 필드를 분석한 뒤 YOLO 30클래스용 `mapping.json`을 만듭니다.


분석 결과를 반영해 `data/mapping.json`을 작성합니다.


`chicken`/`corn` 별칭이 과매칭되어 수정합니다.


`data/mapping.json`을 만들었습니다. 두 CSV를 분석해 **클래스당 영문 별칭 5개**를 넣었고, `test_recipes.csv`의 `Ingredients` JSON(`name` 필드)과 `recipes.csv`의 자연어 `ingredients`에서 자주 나오는 표현을 반영했습니다.

**파일 위치:** [`data/mapping.json`](file:///Users/k2/Documents/프로젝트/data/mapping.json)

---

## 작성 기준

| 우선순위 | 출처 | 예시 |
|----------|------|------|
| 1 | `test_recipes.csv` 구조화 `name` | `skinless, boneless chicken breast halves`, `panko bread crumbs`, `heavy cream` |
| 2 | `recipes.csv` 고빈도 표현 | `granny smith apples`, `all-purpose flour`, `ground beef`, `baby spinach` |
| 3 | YOLO 클래스명·일반 동의어 | `chevre`, `prosciutto`, `granulated sugar` |

---

## 클래스별 별칭 요약 (데이터 근거)

| 클래스 | test_recipes | recipes.csv | 대표 별칭 |
|--------|:------------:|:-----------:|-----------|
| chicken_breast | 54건 | 27 레시피 | `skinless boneless chicken breast halves`, `chicken breast halves` |
| butter | 22 | 399 | `butter`, `unsalted butter`, `melted butter` |
| onion | 22 | 135 | `chopped onion`, `diced onion`, `yellow onion` |
| cheese | 19 | 106 | `parmesan cheese`, `cheddar cheese`, `mozzarella cheese` |
| bread | 12 | 39 | `panko bread crumbs`, `french baguette`, `bread crumbs` |
| tomato | 11 | 52 | `crushed tomatoes`, `diced tomatoes`, `grape tomatoes` |
| eggs | 10 | 306 | `egg`, `eggs`, `large eggs`, `beaten egg` |
| sugar | 10 | 730 | `white sugar`, `brown sugar`, `granulated sugar` |
| flour | 13 | 342 | `all-purpose flour`, `unbleached all-purpose flour` |
| apple | 1 | 299 | `granny smith apple`, `thinly sliced apples` |
| beef | 1 | 14 | `beef sirloin`, `chuck roast`, `round steak` |
| corn | 1 | (정확 매칭) | `whole kernel corn`, `sweet corn` — **`cornstarch` 제외** |

`test_recipes.csv`는 59개 레시피라 **banana, blueberries, goat_cheese, shrimp** 등은 test에 거의 없고, `recipes.csv` 빈도로 별칭을 보완했습니다.

---

## 설계상 조정 2건

1. **`chicken` vs `chicken_breast` 분리**  
   `chicken`에 단독 `"chicken"`을 넣으면 가슴살까지 중복 매칭됩니다.  
   → `chicken`은 `whole chicken`, `chicken thighs`, `chicken wings` 등 **부위·형태가 명확한 표현만** 사용.

2. **`corn` vs `cornstarch`**  
   짧은 `"corn"`은 `cornstarch`에 걸립니다.  
   → `"sweet corn"`, `"whole kernel corn"` 등 **긴 표현만** 사용.

---

## 사용 예 (Normalizer)

```python
import json, re
from pathlib import Path

mapping = json.loads(Path("data/mapping.json").read_text())

def normalize_ingredient(text: str) -> list[str]:
    n = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    n = " ".join(n.split())
    matched = []
    for yolo_cls, aliases in mapping.items():
        for alias in aliases:
            a = " ".join(re.sub(r"[^a-z0-9 ]", " ", alias.lower()).split())
            if a in n:
                matched.append(yolo_cls)
                break
    return matched
```

---

## 참고

- `cheese`에 `cream cheese` 포함 → YOLO `cheese`와 레시피 `cream cheese` 매칭용 (pantry와 겹치면 `pantry.json`에서 나중에 분리 가능).
- `milk`는 `coconut milk`, `condensed milk` 등은 **의도적으로 제외** (일반 우유만).
- `tomato`에 `crushed tomatoes`, `tomato sauce` 포함 → 가공 토마토도 tomato 클래스로 연결.

다음으로 **`pantry.json`**이나 **`normalizer.py`**를 이 mapping에 맞춰 만들까요?

---

**User**

지금 바로 해야 할 것 (Week 5 — 데이터·비즈니스 레이어)
✅ mapping.json 완성
⬜ pantry.json 작성
⬜ ingredient_parser.py (recipes.csv 파싱)
⬜ normalizer.py (YOLO 클래스 → 표준 재료명)
⬜ ranker.py (Coverage + Shortage 점수 계산)
⬜ pantry.py (보유/구매/pantry 3구간 분류)
⬜ scaler.py (인분 비례 조정)

FastAPI 구현 (Week 5 후반)
⬜ main.py (FastAPI 앱)
⬜ predictor.py (best.pt 로드·추론)
⬜ schemas.py (Pydantic 요청/응답 형식)
⬜ GET  /health
⬜ POST /predict  (사진 → 재료 목록)
⬜ POST /recipes  (재료+필터 → Top-K)
⬜ GET  /recipe/{id}  (상세 + 3구간 분류)
⬜ POST /scale  (인분 변경 → 재료 용량)

Streamlit UI (Week 6)
⬜ 화면 1: 사진 다중 업로드
⬜ 화면 2: 인식 재료 목록 + 검색
⬜ 화면 3: 식사 종류 선택
⬜ 화면 4: 요리 종류 선택
⬜ 화면 5: 식단/선호 선택
⬜ 화면 6: 추천 레시피 목록
⬜ 화면 7: 레시피 상세 (시간·인분·3구간·조리법)

Docker + 배포 (Week 7)
⬜ requirements.txt
⬜ Dockerfile
⬜ docker-compose.yml
⬜ (선택) ONNX 변환


@/Users/k2/Documents/프로젝트 지금 할게 이렇게 남은건가?

---

**Cursor**

프로젝트 현재 상태를 확인해 남은 작업 목록과 대조합니다.


네, **지금 할 일 목록이 맞습니다.** 프로젝트 폴더 기준으로 보면 **Month 1(모델)은 끝**, **Month 2(앱·배포)는 거의 전부 미착수** 상태입니다.

---

## 이미 완료된 것 (체크리스트 밖 · Month 1)

| 항목 | 산출물 |
|------|--------|
| YOLO 학습 | `best.pt` |
| Ablation 1~4 | `ablation_results_1~4.json`, `ablation_yolo.py` |
| 데이터셋 | `smart refrigerator.yolov11/` (80/10/10) |
| 레시피 원본 | `Recipes Dataset/recipes.csv`, `test_recipes.csv` |
| 계획·발표 자료 | `fridge-recipe-plan-v3.md`, `ppt-slides-v3.md`, SVG/PNG |
| **mapping.json** | `data/mapping.json` ✅ |

---

## 지금 목록 = 남은 작업 (정확함)

### Week 5 — 데이터·비즈니스 레이어
| 상태 | 항목 |
|:----:|------|
| ✅ | `mapping.json` |
| ⬜ | `pantry.json` |
| ⬜ | `ingredient_parser.py` |
| ⬜ | `normalizer.py` |
| ⬜ | `ranker.py` |
| ⬜ | `pantry.py` |
| ⬜ | `scaler.py` |

→ `core/` + `data/` 아래 Python·JSON **6개**가 다음 블록입니다.

### Week 5 후반 — FastAPI
| 상태 | 항목 |
|:----:|------|
| ⬜ | `api/main.py`, `predictor.py`, `schemas.py` |
| ⬜ | `/health`, `/predict`, `/recipes`, `/recipe/{id}`, `/scale` |

→ 위 `core/` 모듈이 있어야 API를 깔끔하게 붙일 수 있습니다.

### Week 6 — Streamlit
| 상태 | 7화면 전부 ⬜ |

### Week 7 — Docker
| 상태 | `requirements.txt`, `Dockerfile`, `docker-compose.yml` 전부 ⬜ |

---

## 목록에 없지만 Week 8 전에 하면 좋은 것

| 항목 | 이유 |
|------|------|
| PPT Ablation 표 숫자 반영 | JSON은 있음, 슬라이드만 미반영 가능 |
| 오탐/미탐 샘플 5~10장 | Week 4 산출물·발표용 |
| `recipes.csv` → `data/recipes.csv` 복사/링크 | API가 경로 고정하기 쉬움 |
| 식약처 API 한식 보강 | 계획서 필수급이지만 **시간 없으면 v1 생략 가능** |

---

## 권장 진행 순서 (한 줄)

```text
pantry.json → ingredient_parser.py → normalizer.py
→ ranker.py + pantry.py + scaler.py
→ FastAPI 5 endpoints → Streamlit 7 screens → Docker
```

**1차 목표:** Swagger에서 `POST /predict` + `POST /recipes`까지 동작.

---

## 요약

- 적어주신 ⬜ 항목 = **실제로 아직 없는 작업**이 맞습니다.
- ✅는 **`mapping.json` 하나** + (이전에 끝낸) **모델·Ablation** 정도입니다.
- 다음 손대는 곳: **`data/pantry.json` → `core/ingredient_parser.py`**.

원하면 **`pantry.json` + `core/` 6개 파일 뼈대**부터 바로 만들어 드릴 수 있습니다.

---

**User**

식양처 API 한식 보강하고 싶은데 방법 알려줘

---

**Cursor**

계획서의 식약처 API 섹션과 공식 API 문서를 확인합니다.


식약처(식품안전나라) **COOKRCP01 — 조리식품 레시피 DB** API로 한식 레시피를 보강하는 방법을 정리했습니다. 계획서 §3.4와 동일한 흐름입니다.

---

## 전체 흐름

```mermaid
flowchart LR
    A[인증키 발급] --> B[1회 배치 수집]
    B --> C[korean_recipes.csv 변환]
    C --> D[recipes.csv와 병합]
    D --> E[로컬 DB만 사용 / API 호출 없음]
```

**런타임(FastAPI·Streamlit)에서는 API를 호출하지 않습니다.**  
프로젝트 시작 시 한 번 받아 `data/recipes_korean.csv` 등으로 저장해 두는 방식이 맞습니다.

---

## 1단계 — 인증키 발급

1. [식품안전나라 데이터활용](https://www.foodsafetykorea.go.kr/apiMain.do) 접속  
2. **회원가입 → 로그인**  
3. **Open API 이용신청**  
   - 서비스: **조리식품의 레시피 DB** (`COOKRCP01`)  
   - 상세: [COOKRCP01 API 안내](https://www.foodsafetykorea.go.kr/api/openApiInfo.do?menu_grp=MENU_GRP31&menu_no=661&show_cnt=10&start_idx=1&svc_no=COOKRCP01)  
4. **마이페이지 → 인증키 발급정보**에서 `keyId` 확인  
   - 보통 **자동 승인** (즉시 사용 가능한 경우가 많음)

**주의 (2026년 공지):** 식품안전나라 Open API가 **제한적 운영** 기간이 있을 수 있습니다. 수집 전 [apiMain.do](https://www.foodsafetykorea.go.kr/apiMain.do) 공지를 확인하세요.

---

## 2단계 — API 호출 형식

| 항목 | 값 |
|------|-----|
| Base URL | `http://openapi.foodsafetykorea.go.kr/api` |
| 서비스 ID | `COOKRCP01` |
| 형식 | `GET /api/{인증키}/COOKRCP01/json/{startIdx}/{endIdx}` |

**샘플 (인증키 없이 테스트):**

```
http://openapi.foodsafetykorea.go.kr/api/sample/COOKRCP01/json/1/5
```

**실제 호출 예:**

```
http://openapi.foodsafetykorea.go.kr/api/여기에_인증키/COOKRCP01/json/1/1000
```

### 제한

| 규칙 | 내용 |
|------|------|
| 1회 최대 | **1000건** (`startIdx`~`endIdx`) |
| 일일 호출 | **1000회** (공식 메타) |
| 전체 건수 | 약 **1,000건 내외** → **1~2번 호출**이면 전량 수집 가능 |

### 선택 필터 (URL 뒤에 붙임)

```
.../json/1/1000/RCP_PAT2=밥
```

| 파라미터 | 의미 |
|----------|------|
| `RCP_NM` | 메뉴명 |
| `RCP_PAT2` | 요리종류 (반찬, 국&찌개, 밥, 후식 등) |
| `RCP_PARTS_DTLS` | 재료 검색 |
| `CHNG_DT` | 변경일 이후만 (예: `20170101`) |

---

## 3단계 — API 필드 → `recipes.csv` 매핑

현재 `recipes.csv` 컬럼:

`recipe_name`, `prep_time`, `cook_time`, `total_time`, `servings`, `yield`, `ingredients`, `directions`, `rating`, `url`, `cuisine_path`, `nutrition`, `timing`, `img_src`

| API 필드 | recipes.csv | 비고 |
|----------|-------------|------|
| `RCP_NM` | `recipe_name` | 예: "두부 표고 완자탕" |
| `RCP_WAY2` | `prep_time` / `cook_time` | 끓이기·찌기 등 → 대략 매핑 |
| `INFO_WGT` | `servings` / `yield` | 1인분 g 기준 |
| `RCP_PARTS_DTLS` | `ingredients` | **한글 재료 문자열** |
| `MANUAL01`~`MANUAL20` | `directions` | 번호 붙여 `\n` 연결 |
| `RCP_PAT2` | `cuisine_path` | **`/한식/{RCP_PAT2}`** 권장 |
| `INFO_ENG`, `INFO_CAR`… | `nutrition` | 문자열로 합치기 |
| `ATT_FILE_NO_MK` | `img_src` | 이미지 URL |
| `RCP_SEQ` | (내부 id) | `url`에 `foodsafetykorea.go.kr` + seq |
| — | `rating` | 비움 또는 0 |

**재료 예 (`RCP_PARTS_DTLS`):**

```
두부 90g(1/3모), 달걀 25g(1/2개), 표고버섯 10g(1장), 밀가루 10g(2작은술)
```

→ YOLO 30클래스와 직접 1:1은 안 됩니다. **`mapping.json`은 영문**, 식약처는 **한글**이라 **한글↔YOLO 매핑 레이어**가 추가로 필요합니다 (아래 5단계).

---

## 4단계 — 배치 수집 스크립트 (예시)

프로젝트에 `scripts/fetch_foodsafety_recipes.py` 같은 파일로 두고 **1회만** 실행하면 됩니다.

```python
#!/usr/bin/env python3
"""식약처 COOKRCP01 → korean_recipes.csv (1회 배치)"""
import csv
import json
import os
import time
import urllib.request
from pathlib import Path

API_KEY = os.environ["FOODSAFETY_API_KEY"]  # .env에 저장, git에 올리지 말 것
BASE = "http://openapi.foodsafetykorea.go.kr/api"
OUT = Path("data/korean_recipes_raw.json")
CSV = Path("data/recipes_korean.csv")

def fetch_range(start: int, end: int) -> list[dict]:
    url = f"{BASE}/{API_KEY}/COOKRCP01/json/{start}/{end}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    body = data.get("COOKRCP01", {})
    if body.get("RESULT", {}).get("CODE") != "INFO-000":
        raise RuntimeError(body.get("RESULT"))
    row = body.get("row", [])
    return row if isinstance(row, list) else [row]

def to_recipes_csv_row(item: dict) -> dict:
    steps = []
    for i in range(1, 21):
        step = (item.get(f"MANUAL{i:02d}") or "").strip()
        if step:
            steps.append(f"{len(steps)+1}. {step}")
    nutrition = (
        f"열량 {item.get('INFO_ENG','')}kcal, "
        f"탄수화물 {item.get('INFO_CAR','')}g, "
        f"단백질 {item.get('INFO_PRO','')}g, "
        f"지방 {item.get('INFO_FAT','')}g, "
        f"나트륨 {item.get('INFO_NA','')}mg"
    )
    return {
        "recipe_name": item.get("RCP_NM", ""),
        "prep_time": "",
        "cook_time": item.get("RCP_WAY2", ""),  # 조리방법(끓이기/찌기 등)
        "total_time": "",
        "servings": 1,
        "yield": item.get("INFO_WGT", ""),
        "ingredients": item.get("RCP_PARTS_DTLS", ""),
        "directions": "\n".join(steps),
        "rating": "",
        "url": f"https://www.foodsafetykorea.go.kr/recipe/{item.get('RCP_SEQ','')}",
        "cuisine_path": f"/한식/{item.get('RCP_PAT2','')}",
        "nutrition": nutrition,
        "timing": "",
        "img_src": item.get("ATT_FILE_NO_MK", ""),
        "source": "foodsafety",
        "rcp_seq": item.get("RCP_SEQ", ""),
    }

def main():
    all_rows = []
    start = 1
    batch = 1000
    while True:
        end = start + batch - 1
        chunk = fetch_range(start, end)
        if not chunk:
            break
        all_rows.extend(chunk)
        if len(chunk) < batch:
            break
        start += batch
        time.sleep(0.5)  # 호출 간격

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    fields = [
        "recipe_name", "prep_time", "cook_time", "total_time", "servings", "yield",
        "ingredients", "directions", "rating", "url", "cuisine_path", "nutrition",
        "timing", "img_src", "source", "rcp_seq",
    ]
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for item in all_rows:
            w.writerow(to_recipes_csv_row(item))
    print(f"saved {len(all_rows)} recipes → {CSV}")

if __name__ == "__main__":
    main()
```

**실행:**

```bash
export FOODSAFETY_API_KEY="발급받은_인증키"
python scripts/fetch_foodsafety_recipes.py
```

---

## 5단계 — `recipes.csv`와 병합

```python
import pandas as pd

eng = pd.read_csv("Recipes Dataset/recipes.csv")
kor = pd.read_csv("data/recipes_korean.csv")

# 영문 DB에 source 컬럼 없으면 추가
eng["source"] = "allrecipes"
merged = pd.concat([eng, kor], ignore_index=True)
merged.to_csv("data/recipes.csv", index=False)
```

**필터 UI에서 한식 쓰려면:**

- `cuisine_path`에 `/한식/...` 넣기 (위 스크립트 반영)
- Streamlit "요리 종류 = 한식" → `cuisine_path.str.contains("한식")`

---

## 6단계 — 한글 재료 ↔ YOLO (중요)

식약처 재료는 **한글** (`달걀`, `표고버섯`, `두부`)이고, 지금 `mapping.json`은 **영문 별칭**입니다.

추가로 **`data/mapping_ko.json`** 같은 한글 매핑이 필요합니다.

```json
{
  "eggs": ["달걀", "계란", "노른자", "흰자"],
  "mushrooms": ["표고버섯", "버섯", "새송이버섯"],
  "tofu": ["두부", "순두부", "연두부"],
  "tomato": ["토마토", "방울토마토"],
  "apple": ["사과"],
  "potato": ["감자", "russet"는 없음],
  "sweet_potato": ["고구마", "단호박은 별도"],
  "shrimp": ["새우", "새우살", "칵테일새우"],
  "chicken_breast": ["닭가슴살", "닭가슴"],
  "chicken": ["닭", "닭고기", "닭다리"],
  "beef": ["소고기", "쇠고기", "등심"],
  "ground_beef": ["다진 쇠고기", "다진고기"],
  "onion": ["양파", "대파는 별도"],
  "carrot": ["당근"],
  "spinach": ["시금치", "채소"],
  "sugar": ["설탕", "흑설탕", "백설탕"],
  "butter": ["버터"],
  "milk": ["우유"],
  "flour": ["밀가루", "찹쌀가루는 별도"],
  "cheese": ["치즈", "모짜렐라", "체다"],
  "ham": ["햄"],
  "lime": ["레몬즙은 lime 아님 — 레몬은 별도 클래스 없음"]
}
```

**YOLO에 없는 한식 재료**(김치, 두부, 된장, 고추장 등)는 **인식 불가** → 계획서 한계(§8.2)에 명시하고, pantry/제외 목록으로 처리하는 것이 현실적입니다.

---

## 7단계 — 요리 종류 필터 활용

식약처 `RCP_PAT2` 예: **반찬, 국&찌개, 밥, 후식, 찌개, …**

README 필터와 대략 매핑:

| UI 필터 | `RCP_PAT2` / 키워드 |
|---------|---------------------|
| 아침/점심/저녁 | `밥`, `국&찌개`, `찌개` |
| 간식/디저트 | `후식`, `간식` |
| 한식 | `cuisine_path=/한식/` |

식사 시간대는 API에 없어서 **규칙 기반**(요리종류 + 메뉴명 키워드)으로 보완하면 됩니다.

---

## 실무 체크리스트

| 순서 | 작업 |
|:----:|------|
| 1 | [COOKRCP01](https://www.foodsafetykorea.go.kr/api/openApiInfo.do?svc_no=COOKRCP01) 신청 → 인증키 |
| 2 | `sample/COOKRCP01/json/1/5` 로 응답 JSON 구조 확인 |
| 3 | 배치 스크립트로 전량 수집 → `data/recipes_korean.csv` |
| 4 | `recipes.csv`와 병합 → `data/recipes.csv` |
| 5 | `mapping_ko.json` 추가 (한글 재료 → YOLO 클래스) |
| 6 | FastAPI는 **로컬 CSV만** 읽기 (API 키 불필요) |

---

## 한 줄 요약

**식약처 API는 “한 번 긁어서 CSV로 저장”하는 용도**이고, 발급 → `COOKRCP01` JSON 수집 → `recipes.csv` 스키마 변환 → 영문 DB와 병합 → **`mapping_ko.json`으로 한글 재료를 YOLO 클래스에 연결**하면 한식 보강이 됩니다.

원하면 다음으로 **`fetch_foodsafety_recipes.py` + `mapping_ko.json` 초안**을 프로젝트에 바로 추가해 드릴 수 있습니다.

---

**User**

요청주소
요청주소	URL	http://openapi.foodsafetykorea.go.kr/api/keyId/serviceId/dataType/startIdx/endIdx
샘플	http://openapi.foodsafetykorea.go.kr/api/sample/COOKRCP01/xml/1/5
URL설명	추가요청인자가 없을 경우	http://openapi.foodsafetykorea.go.kr/api/인증키/서비스명/요청파일타입/요청시작위치/요청종료위치
추가요청인자가 있을 경우	http://openapi.foodsafetykorea.go.kr/api/인증키/서비스명/요청파일타입/요청시작위치/요청종료위치/변수명=값&변수명=값2
예시	http://openapi.foodsafetykorea.go.kr/api/sample/COOKRCP01/xml/1/5/RCP_NM=값 &RCP_PARTS_DTLS=값 &CHNG_DT=값 &RCP_PAT2=값

일단 API 요청 주소가 이러한데 이제 어떻게 하면 돼?

---

**Cursor**

샘플 API를 호출해 응답 구조를 확인한 뒤, 인증키 발급부터 데이터 수집까지 순서대로 안내합니다.


인증키만 있으면, 아래 순서대로 진행하면 됩니다. 샘플 API는 이미 확인했고 **전체 레시피는 1,146건**입니다.

---

## 지금 할 일 (4단계)

### ① 인증키 발급 (아직 없다면)

1. [식품안전나라 Open API](https://www.foodsafetykorea.go.kr/apiMain.do) → 회원가입·로그인  
2. **Open API 이용신청** → **조리식품의 레시피 DB (COOKRCP01)** 선택  
3. **마이페이지 → 인증키 발급정보**에서 `keyId` 복사  

---

### ② 브라우저로 연결 테스트

**인증키 없이 (샘플):**

```
http://openapi.foodsafetykorea.go.kr/api/sample/COOKRCP01/json/1/3
```

JSON이 보이면 API 형식은 정상입니다. (방금 확인: `total_count: 1146`, `CODE: INFO-000`)

**본인 인증키로:**

```
http://openapi.foodsafetykorea.go.kr/api/여기에_인증키/COOKRCP01/json/1/5
```

- `xml` 대신 **`json`** 권장  
- `1` = 시작 번호, `5` = 끝 번호 → **5건**만 받음  

---

### ③ 전체 수집 (1,146건 → API 2번)

| 호출 | URL |
|------|-----|
| 1차 | `.../COOKRCP01/json/1/1000` |
| 2차 | `.../COOKRCP01/json/1001/1146` |

**규칙:** 1회 최대 **1,000건** (`ERROR-336` 방지)

터미널 예시:

```bash
# 인증키 설정 (git에 올리지 말 것)
export FOODSAFETY_API_KEY="발급받은_키"

# 5건 테스트
curl "http://openapi.foodsafetykorea.go.kr/api/${FOODSAFETY_API_KEY}/COOKRCP01/json/1/5"

# 전체 1차 (1000건)
curl -o data/korean_batch1.json \
  "http://openapi.foodsafetykorea.go.kr/api/${FOODSAFETY_API_KEY}/COOKRCP01/json/1/1000"

# 전체 2차 (나머지 146건)
curl -o data/korean_batch2.json \
  "http://openapi.foodsafetykorea.go.kr/api/${FOODSAFETY_API_KEY}/COOKRCP01/json/1001/1146"
```

---

### ④ JSON → `recipes.csv` 형식으로 변환

응답 구조:

```json
{
  "COOKRCP01": {
    "total_count": "1146",
    "row": [ { "RCP_NM": "...", "RCP_PARTS_DTLS": "...", ... } ],
    "RESULT": { "CODE": "INFO-000" }
  }
}
```

**꼭 쓸 필드:**

| API | 용도 |
|-----|------|
| `RCP_NM` | 레시피 이름 |
| `RCP_PARTS_DTLS` | 재료 (한글) |
| `MANUAL01`~`MANUAL20` | 조리법 |
| `RCP_PAT2` | 요리종류 (반찬, 밥, 국&찌개…) |
| `ATT_FILE_NO_MK` | 음식 사진 URL |
| `INFO_ENG`, `INFO_CAR`… | 영양 정보 |

변환 후 `data/recipes_korean.csv`로 저장하고, 기존 `Recipes Dataset/recipes.csv`와 합치면 됩니다.  
`cuisine_path`는 **`/한식/{RCP_PAT2}`** 로 넣으면 UI “한식” 필터에 쓸 수 있습니다.

---

## 필터가 필요할 때 (추가 파라미터)

문서 예시:

```
.../json/1/100/RCP_PAT2=밥
```

| 파라미터 | 예 |
|----------|-----|
| `RCP_PAT2` | `밥`, `반찬`, `국&찌개` |
| `RCP_NM` | 메뉴명 검색 |
| `CHNG_DT` | `20240101` (이후 변경분만) |

한식만 모을 때는 **전량 받은 뒤 `RCP_PAT2`로 필터**해도 되고, URL에 `RCP_PAT2=밥`처럼 붙여도 됩니다.

---

## 이후 프로젝트 연결

```text
식약처 API (1회) → recipes_korean.csv
        ↓
recipes.csv와 병합 → data/recipes.csv
        ↓
FastAPI /recipes 는 로컬 CSV만 읽음 (런타임 API 호출 X)
```

**주의:** 식약처 재료는 **한글**(`달걀`, `표고버섯`)이라, 영문 `mapping.json`과 연결하려면 **`mapping_ko.json`**(한글→YOLO 클래스)이 추가로 필요합니다.

---

## 한 줄 정리

1. **인증키 발급**  
2. **`/api/인증키/COOKRCP01/json/1/5`** 로 5건 테스트  
3. **`1/1000` + `1001/1146`** 두 번 호출해 전량 저장  
4. **CSV 변환 → `recipes.csv` 병합**  

원하면 프로젝트에 **`scripts/fetch_foodsafety_recipes.py`**(②~④ 자동)와 **`mapping_ko.json` 초안**을 바로 만들어 드릴 수 있습니다. 인증키는 `.env`에만 두고 코드에는 넣지 않으면 됩니다.

---

**User**

1	keyId	STRING(필수)	인증키	OepnAPI 에서 발급된 인증키
2	serviceId	STRING(필수)	서비스명	요청대상인 해당 서비스명
3	dataType	STRING(필수)	요청파일 타입	xml : xml파일 , json : json파일
4	startIdx	STRING(필수)	요청시작위치	정수입력
5	endIdx	STRING(필수)	요청종료위치	정수입력
6	RCP_NM	STRING(선택)	메뉴명	추가 파라미터값
7	RCP_PARTS_DTLS	STRING(선택)	재료정보1	추가 파라미터값
8	CHNG_DT	STRING(선택)	변경일자(YYYYMMDD)	변경일자 기준 이후 자료를 출력한다.
정수입력 : 20170101 (2017년 1월 1일)
9	RCP_PAT2	STRING(선택)	요리종류(ex) 반찬, 국, 후식 등)	추가 파라미터값


지금 너가 여기서 우리 프로젝트에 필요한거 다 쓴거지?

---

**Cursor**

**요청 파라미터(보내는 것)** 기준으로 보면, **필수 5개는 다 쓰는 게 맞고**, **선택 4개는 전부 쓸 필요는 없습니다.**

---

## 요청 파라미터 — 프로젝트에서 쓰는지

| # | 파라미터 | 필수 | 우리 프로젝트 | 설명 |
|---|----------|:----:|:-------------:|------|
| 1 | `keyId` | ✅ | **사용** | 발급받은 인증키 → URL에 넣음 |
| 2 | `serviceId` | ✅ | **사용** | `COOKRCP01` (조리식품 레시피 DB) |
| 3 | `dataType` | ✅ | **사용** | `json` 권장 (`xml` 아님) |
| 4 | `startIdx` | ✅ | **사용** | `1`, `1001` … 페이지 시작 |
| 5 | `endIdx` | ✅ | **사용** | `1000`, `1146` … 페이지 끝 |
| 6 | `RCP_NM` | 선택 | **보통 안 씀** | 메뉴명으로 **검색**할 때만 (예: `김치`) |
| 7 | `RCP_PARTS_DTLS` | 선택 | **보통 안 씀** | 재료로 **검색**할 때만 |
| 8 | `CHNG_DT` | 선택 | **보통 안 씀** | **증분 업데이트**할 때만 (예: `20240101` 이후) |
| 9 | `RCP_PAT2` | 선택 | **선택 사용** | 요리종류 필터 (예: `밥`, `반찬`) — 전량 받을 땐 불필요 |

**실제 URL 예 (필수만):**

```
http://openapi.foodsafetykorea.go.kr/api/{keyId}/COOKRCP01/json/1/1000
```

**선택 파라미터 쓸 때만 URL 뒤에 붙임:**

```
.../json/1/100/RCP_PAT2=밥
.../json/1/100/RCP_NM=된장
```

---

## “다 썼냐?”에 대한 답

| 구분 | 답 |
|------|-----|
| **필수 5개** | ✅ 전부 사용 — 이걸로 1,146건 전량 수집 가능 |
| **선택 4개** | ❌ 처음 한 번 긁을 때는 **안 써도 됨** — 전체 받은 뒤 CSV에서 필터하면 됨 |
| **응답 필드** (RCP_NM, MANUAL01… 등) | ✅ 변환 스크립트에서 **가져와서** `recipes.csv`에 매핑 — URL 파라미터가 아님 |

즉, **API 요청 스펙 9개를 URL에 전부 넣는 게 아니라**, 필수 5개 + (필요 시) 선택 1~2개만 쓰는 구조입니다.

---

## 우리 프로젝트에 실제로 필요한 것

### 1) 요청 (1회 배치)

- `keyId` + `COOKRCP01` + `json` + `1/1000`, `1001/1146`  
→ **2번 호출**이면 전체 한식 레시피 DB 확보

### 2) 응답에서 꺼낼 필드 (이게 “프로젝트에 필요한 데이터”)

| API 응답 필드 | recipes.csv / 앱 |
|---------------|------------------|
| `RCP_NM` | `recipe_name` |
| `RCP_PARTS_DTLS` | `ingredients` |
| `MANUAL01`~`MANUAL20` | `directions` |
| `RCP_PAT2` | `cuisine_path` → `/한식/반찬` 등 |
| `RCP_WAY2` | `cook_time` 대용 (끓이기/찌기…) |
| `INFO_WGT`, `INFO_ENG`… | `servings`, `nutrition` |
| `ATT_FILE_NO_MK` | `img_src` |
| `RCP_SEQ` | 내부 ID / `url` |

### 3) 아직 별도 작업 (API 파라미터 아님)

- **`mapping_ko.json`** — 한글 재료 → YOLO 30클래스  
- **`recipes.csv`와 병합**  
- FastAPI는 **로컬 CSV만** 읽기 (런타임에 API 호출 X)

---

## 선택 파라미터를 쓰면 좋은 경우

| 파라미터 | 쓸 때 |
|----------|--------|
| `RCP_PAT2=밥` | 밥·죽류만 먼저 테스트하고 싶을 때 |
| `CHNG_DT=20250101` | 나중에 **새 레시피만** 추가 수집할 때 |
| `RCP_NM` / `RCP_PARTS_DTLS` | 특정 메뉴·재료만 검색할 때 |

처음 한식 보강 목적이면 **필수 5개만으로 전량 수집** → CSV 변환 → 병합이면 충분합니다.

---

**한 줄:** 필수 파라미터는 다 쓰는 게 맞고, 선택 4개는 **프로젝트 필수는 아님**. 응답 JSON 안의 `RCP_NM`, `RCP_PARTS_DTLS`, `MANUAL**` 등이 앱에 필요한 데이터입니다.

---

**User**

"인증키 받았어. scripts/fetch_foodsafety_recipes.py 만들어줘.
 API 2번 호출 (1~1000, 1001~1146)해서
 data/recipes_korean.csv로 저장하고
 기존 recipes.csv랑 병합하는 코드까지 포함해줘."

---

**Cursor**

기존 `recipes.csv` 스키마를 확인한 뒤 수집·병합 스크립트를 작성합니다.


`scripts/fetch_foodsafety_recipes.py`를 만들었고, **sample 인증키로 테스트까지 완료**했습니다 (1,146건 수집 + 병합 2,236건).

---

## 실행 방법

```bash
cd "/Users/k2/Documents/프로젝트"

# 발급받은 인증키 설정 (터미널 세션마다 1회)
export FOODSAFETY_API_KEY="여기에_본인_인증키"

python3 scripts/fetch_foodsafety_recipes.py
```

`.env`를 쓰려면:

```bash
echo 'FOODSAFETY_API_KEY=본인_인증키' >> .env   # git에 올리지 말 것
export $(grep FOODSAFETY_API_KEY .env | xargs)
python3 scripts/fetch_foodsafety_recipes.py
```

---

## 스크립트가 하는 일

| 단계 | 내용 |
|------|------|
| 1 | `GET .../json/1/1000` |
| 2 | `GET .../json/1001/1146` (`total_count` 기준) |
| 3 | `data/recipes_korean.csv` 저장 (한식 1,146건) |
| 4 | `Recipes Dataset/recipes.csv` 로드 (영문 1,090건) |
| 5 | `data/recipes_merged.csv` 병합 저장 (2,236건) |
| 6 | `data/korean_recipes_raw.json` 원본 JSON 보관 |

---

## 생성 파일

| 파일 | 설명 |
|------|------|
| `data/recipes_korean.csv` | 식약처만 |
| `data/recipes_merged.csv` | Allrecipes + 식약처 **병합본** (FastAPI에서 이걸 쓰면 됨) |
| `data/korean_recipes_raw.json` | API 원본 |

병합 CSV 컬럼은 기존 `recipes.csv` + **`source`**, **`rcp_seq`**  
- 영문: `source=allrecipes`  
- 한식: `source=foodsafety`, `cuisine_path=/한식/반찬` 등

---

## 테스트 결과 (sample 키)

```
allrecipes 1090 + foodsafety 1146 = 2236건
```

본인 인증키로 같은 명령을 실행하면 동일하게 동작합니다.

---

## 다음 단계

1. **`mapping_ko.json`** — 한글 재료(`달걀`, `표고버섯`) → YOLO 클래스  
2. FastAPI `ranker.py`에서 **`data/recipes_merged.csv`** 경로 사용  

`mapping_ko.json`도 이어서 만들까요?

---

**User**

@scripts/fetch_foodsafety_recipes.py 	9ad014455d2a4dbabb63


이거 내 인증키인데 이걸로 한거야?

---

**Cursor**

**아니요.** 제가 테스트할 때는 **`sample`(공식 샘플 키)** 로 돌렸습니다. 말씀하신 `9ad014455d2a4dbabb63` 인증키로는 **아직 실행하지 않았습니다.**

```
FOODSAFETY_API_KEY=sample python3 scripts/fetch_foodsafety_recipes.py
```

`sample` 키도 전체 1,146건을 받을 수 있어서, 지금 `data/recipes_korean.csv` / `data/recipes_merged.csv` 내용은 **본인 키와 동일한 공공 데이터**일 가능성이 높습니다. 다만 **공식 수집 기록·발표용**으로는 본인 키로 한 번 더 실행하는 편이 좋습니다.

---

## 본인 키로 실행

```bash
cd "/Users/k2/Documents/프로젝트"
export FOODSAFETY_API_KEY="9ad014455d2a4dbabb63"
python3 scripts/fetch_foodsafety_recipes.py
```

성공하면 터미널에 예를 들어 이렇게 나옵니다:

```
[fetch] 1~1000  http://openapi.foodsafetykorea.go.kr/api/9ad014455d2a4dbabb63/COOKRCP01/json/1/1000...
[fetch] 1001~1146 ...
✅ 완료
```

`INFO-000` / `1146건` / `2236건 병합`이면 정상입니다.

---

## 보안 참고

인증키를 채팅에 올리셨습니다. 가능하면:

- `.env`에만 저장하고 **git에 커밋하지 않기**
- 노출이 걱정되면 식품안전나라에서 **키 재발급** 검토

`.gitignore`에 `.env` 추가가 필요하면 말해 주세요.

---

**User**

내 키로 실행하고 싶은데 어떻게 해야돼. 그리고 gitignore에 .env 추가

---

**Cursor**

`.gitignore`에 `.env`를 추가하고, 스크립트가 `.env`를 자동으로 읽도록 한 뒤 본인 키로 실행합니다.


설정해 두었고, 본인 키로 수집도 완료했습니다.

## 1. `.gitignore`에 `.env` 추가

프로젝트 루트에 `.gitignore`를 만들었습니다. `.env`는 Git에 올라가지 않습니다.

## 2. 본인 키로 실행하는 방법

프로젝트 루트에 `.env` 파일을 만들고 아래처럼 넣으면 됩니다.

```
FOODSAFETY_API_KEY=9ad014455d2a4dbabb63
```

이미 `.env`에 키를 넣어 두었고, 스크립트가 시작할 때 자동으로 읽습니다. 실행:

```bash
cd "/Users/k2/Documents/프로젝트"
python3 scripts/fetch_foodsafety_recipes.py
```

환경변수로 직접 넣어도 됩니다.

```bash
export FOODSAFETY_API_KEY="9ad014455d2a4dbabb63"
python3 scripts/fetch_foodsafety_recipes.py
```

## 3. 실행 결과 (본인 키)

| 파일 | 건수 |
|------|------|
| `data/recipes_korean.csv` | 1,146건 |
| `data/recipes_merged.csv` | 2,236건 (영문 1,090 + 한식 1,146) |

---

**보안 참고:** API 키는 채팅에 노출된 적이 있으니, 가능하면 [식품안전나라 Open API](https://www.foodsafetykorea.go.kr/api/openApiInfo.do)에서 키를 재발급하는 것을 권장합니다. `.env`는 `.gitignore`에 있어 커밋되지 않습니다.

---

**User**

이제 다음 스텝이 뭐야

---

**Cursor**

프로젝트 계획서와 현재 진행 상태를 확인해 다음 단계를 정리합니다.


지금은 **Month 1(모델)은 거의 끝**났고, **Month 2 Week 5(앱/API)** 로 넘어갈 시점입니다.

## 현재까지 완료

| 항목 | 상태 |
|------|------|
| YOLOv11n 학습 + Ablation 4종 | ✅ `best.pt`, mAP ~0.99 |
| `mapping.json` (영문 30클래스 ↔ 재료 별칭) | ✅ |
| 식약처 API 수집 + 병합 | ✅ `recipes_merged.csv` (2,236건) |
| `.env` / `.gitignore` | ✅ |

## 아직 없는 것 (Week 1 잔여 + Week 5 본업)

Week 5 API를 만들려면 아래가 먼저 필요합니다.

### 1단계 — 설정·파싱 기반 (1~2일)

```
data/pantry.json          ← 물·소금·후추·기름 등 상비 재료 목록
data/mapping_ko.json      ← 한식 재료(양파, 당근…) → YOLO 클래스 매핑
core/ingredient_parser.py ← ingredients 문자열 → {name, qty, unit} 파싱
```

한식 레시피 1,146건이 들어왔으니 **`mapping_ko.json`이 특히 중요**합니다. 없으면 한식 재료가 YOLO 클래스와 매칭되지 않습니다.

### 2단계 — 비즈니스 로직 (`core/`)

| 파일 | 역할 |
|------|------|
| `normalizer.py` | YOLO 탐지 결과 + 동의어 → 표준 재료 집합 |
| `ranker.py` | Coverage + 부족재료 점수, 필터, Top-K (`recipes_merged.csv` 사용) |
| `pantry.py` | 보유 / 추가구매(≤2) / pantry 3구간 분류 |
| `scaler.py` | 인분 변경 시 재료량 비례 조정 |

### 3단계 — FastAPI (Week 5 산출물)

```
api/main.py       ← /predict, /recipes, /recipe/{id}, /scale, /health
api/predictor.py  ← YOLO 추론 (best.pt)
api/schemas.py    ← Pydantic 요청/응답
```

### 4단계 이후 (Week 6~8)

- **Week 6**: Streamlit UI 7화면 + 통합 테스트  
- **Week 7**: Docker + docker-compose  
- **Week 8**: README, 발표 PPT, 시연 영상  

---

## 추천 진행 순서

```mermaid
flowchart LR
    A[pantry.json + mapping_ko.json] --> B[ingredient_parser.py]
    B --> C[ranker / pantry / scaler]
    C --> D[FastAPI 4 endpoints]
    D --> E[Streamlit UI]
    E --> F[Docker]
```

**지금 당장 할 일**: `pantry.json` + `mapping_ko.json` + `ingredient_parser.py` → 그다음 `ranker.py` 프로토타입으로 “냉장고에 onion, chicken 있으면 어떤 레시피가 뜨는지” CLI로 먼저 확인.

---

계획서 기준으로는 **Week 5 — FastAPI + core 모듈**이 다음 마일스톤입니다. Week 6 말 목표인 End-to-End 통합까지 약 2주 남았습니다.

원하시면 **1단계(`pantry.json`, `mapping_ko.json`, `ingredient_parser.py`)부터** 바로 구현해 드릴 수 있습니다.

---

**User**

1단계 바로 구현해줘

---

**Cursor**

1단계 구현을 위해 기존 매핑·레시피 CSV 형식과 YOLO 클래스 목록을 확인합니다.


1단계 파일들을 작성하고 파서 검증을 실행합니다.


영문 파싱 정규식을 수정 중입니다.


1단계 구현을 마쳤습니다.

## 생성된 파일

| 파일 | 역할 |
|------|------|
| `data/pantry.json` | 상비 재료 22종 (물·소금·간장·마늘 등, 한/영 별칭) |
| `data/mapping_ko.json` | YOLO 30클래스 ↔ 한국어 재료명 매핑 |
| `core/ingredient_parser.py` | 재료 문자열 파싱 + YOLO/pantry 매칭 |
| `core/__init__.py` | 공개 API export |

## 파서 사용법

```python
from core.ingredient_parser import parse_ingredients, ingredient_names

# 한식 (식약처 CSV)
items = parse_ingredients(ingredients_text, source="korean")

# 영문 (Allrecipes CSV)
items = parse_ingredients(ingredients_text, source="english")

for item in items:
    print(item.raw_name, item.quantity, item.unit, item.yolo_class, item.is_staple)
```

검증 실행:

```bash
python3 core/ingredient_parser.py
```

## 검증 결과

| 데이터 | 파싱 성공 | YOLO 클래스 매칭 |
|--------|-----------|------------------|
| 한식 1,146건 | 99.7% (1,142건) | 92.7% |
| 영문 1,090건 | 100% | 95.0% |

## 참고

- **연두부·부추** 등 YOLO 30클래스에 없는 한식 재료는 `yolo_class=None`으로 남습니다. 계획서 한계로 두었습니다.
- **설탕·버터**처럼 YOLO로도 잡히는 재료는 pantry가 아닌 YOLO 클래스로 분류됩니다.
- 한식 4건은 양념장만 있는 레시피 등 형식 특수 케이스로 파싱 결과가 비어 있습니다.

---

다음 단계는 **2단계 — `ranker.py`, `pantry.py`, `scaler.py`** 입니다. 계속 진행할까요?

---

**User**

 계획서 한계로 두었다는게 정리해둔거야?

---

**Cursor**

계획서에 해당 한계가 명시돼 있는지 확인 중입니다.


네, **계획서에 정리해 둔 내용**입니다. 제가 “계획서 한계”라고 한 건 코드에서 그냥 무시한 게 아니라, 문서에 적힌 **의도된 제약**을 따른 것입니다.

`fridge-recipe-plan-v3.md`에 두 군데 명시돼 있습니다.

**§3.5 데이터 한계 및 대응**

| 한계 | 대응 |
|------|------|
| **한식 특화 재료 부재** (김치, 두부, 된장 등) | YOLO 클래스에 없는 재료는 **인식 불가 → 한계로 명시** |

**§8.2 본 프로젝트의 한계**

| 한계 | 원인 | 향후 과제 |
|------|------|-----------|
| **한식 특화 재료 부재** | YOLO 30 클래스가 **서구 재료 중심** | 한식 데이터셋 추가 구축 |

또 **§3.4**에서는 식약처 API는 **한식 레시피·필터 보강**용이고, 런타임에는 로컬 DB만 쓴다고 적혀 있습니다. 즉 “한식 재료를 YOLO로 다 인식한다”가 아니라 “한식 **메뉴/레시피**를 늘린다”는 쪽입니다.

---

**코드와의 관계**

- `mapping_ko.json`은 YOLO 30클래스에 **있는** 한국어 이름만 매핑합니다 (양파→onion, 새우→shrimp 등).
- **연두부, 부추, 된장**처럼 30클래스에 없는 재료는 `yolo_class=None`으로 두는 게 계획서와 맞습니다.
- 랭킹할 때는 “냉장고에서 **인식된** 재료”만 Coverage 계산에 쓰고, 인식 못 하는 한식 재료는 **부족 재료**로 잡히거나 pantry(소금·간장 등)로 분류됩니다.

발표/보고서에는 §8.2 표를 그대로 쓰면 됩니다. “연두부·부추는 데이터셋 한계로 사진 인식 불가, 레시피 DB는 식약처 API로 보강” 정도로 한 줄만 덧붙이면 충분합니다.

---

**User**

2단계 비즈니스 로직을 구현해줘.

1. core/normalizer.py
   - YOLO 탐지 결과(클래스명 리스트) → 표준 재료 집합
   - mapping.json + mapping_ko.json 활용

2. core/ranker.py
   - recipes_merged.csv 로드
   - Coverage + Shortage 점수 계산
   - 필터(식사/요리/식단) 적용
   - Top-K 반환
   공식:
   Score = 0.5 × Coverage
         + 0.3 × (1 / (부족재료수 + 1))
         + 0.2 × rating_normalized
   Hard filter: 부족재료 > 2 → 제외

3. core/pantry.py
   - 레시피 재료를 보유/추가구매(≤2)/pantry 3구간으로 분류

4. core/scaler.py
   - 인분 변경 시 재료량 비례 조정
   - 주재료: qty × (M/N)
   - 양념: qty × (M/N)^0.7

구현 후 CLI로 테스트:
"냉장고에 onion, chicken 있을 때 레시피 Top-5 출력"


다음 단계 이렇게 하는게 맞나? 정합성 검토해줘

---

**Cursor**

계획서·기존 파서와의 정합성을 확인한 뒤 4개 모듈을 구현합니다.


4개 모듈과 CLI 데모를 구현합니다.


‘chicken broth/stock’ 오매칭과 정렬 기준을 수정합니다.


한식 레시피 rating 0 처리와 `min_used` 옵션을 추가합니다.


2단계 비즈니스 로직을 구현했고, 계획서와의 정합성도 함께 정리했습니다.

## 구현 완료

| 파일 | 역할 |
|------|------|
| `core/normalizer.py` | YOLO 클래스명 → `{onion: 2, chicken: 1}` 표준 집합 |
| `core/ranker.py` | `recipes_merged.csv` 로드, 점수·필터, Top-K |
| `core/pantry.py` | 보유 / 추가구매 / pantry 3구간 분류 |
| `core/scaler.py` | 인분 스케일 (주재료 선형, 양념 ^0.7, pantry 제외) |
| `scripts/rank_demo.py` | CLI 데모 |

### CLI 테스트

```bash
# 기본 (탐지 재료 1개만 써도 되는 레시피 포함)
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5

# onion + chicken 둘 다 쓰는 레시피만
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5 --min-used 2
```

`--min-used 2` 결과 예시:

```
1. [0.920] 닭고기 완자삼계죽  coverage=100%  shortage=0  used=2
2. [0.920] 닭날개튀김        coverage=100%  shortage=0  used=2
3. [0.671] Mexican Chicken Soup  coverage=67%  shortage=1  missing=[tomato]
...
```

---

## 정합성 검토 — 다음 단계 맞나?

**결론: 방향은 맞습니다.** `fridge-recipe-plan-v3.md` Week 5 흐름과 일치합니다.

```
normalizer → ranker     (/predict, /recipes)
pantry, scaler          (/recipe/{id}, /scale)  ← Row 2 독립 모듈
```

다음은 **FastAPI 4엔드포인트**(`api/main.py`, `predictor.py`, `schemas.py`)가 맞습니다.

### 계획서와 일치하는 부분

| 항목 | 구현 |
|------|------|
| Score 공식 | `0.5×Coverage + 0.3×(1/(shortage+1)) + 0.2×rating/5` |
| Hard filter | `shortage > 2` 제외 |
| Coverage | `\|탐지 ∩ 레시피\| / \|레시피\|` (pantry·YOLO 미매핑 제외) |
| pantry 3구간 | `classify_ingredients()` — 추가구매 UI용 `[:2]` |
| scaler | 주재료 `×(M/N)`, 양념 `×(M/N)^0.7`, pantry 미표시 |
| 데이터 | `recipes_merged.csv` (식약처 병합본 — 계획보다 실제 구현에 맞음) |

### 계획서 대비 실무 보완 (의도적)

1. **`chicken broth/stock` 제외** — `broth|stock|육수`는 레시피 필수 재료에서 빼서 오매칭 방지  
2. **식약처 rating=0** → 중립값 3.0 (미평가 레시피 페널티 완화)  
3. **CSV 중복 URL 제거** — `recipes_merged.csv`에 allrecipes 4중 행 있음  
4. **`--min-used`** — 계획엔 없지만, “onion+chicken 둘 다 쓰는 레시피” 데모용 옵션  

### 알아둘 한계 (계획서 §3.5, §8.2)

- Coverage 분모는 **YOLO 30클래스에 매핑되는 재료만** → 연두부·부추 등은 분모에서 빠짐  
- 양고기·돼지고기 등 **YOLO에 없는 주재료**는 shortage에도 안 잡힘 → 한식 레시피는 Coverage가 과대평가될 수 있음  
- 필터(식사/요리/식단)는 **키워드·블랙리스트 근사** — §8.2 “식단 필터 규칙 기반” 한계와 동일  

### `onion, chicken` Top-5가 직관과 다른 이유

계획 공식은 **레시피 재료 커버리지** 기준이라, onion만 쓰는 샐러드가 chicken+onion 둘 다 쓰는 요리보다 score가 높을 수 있습니다.  
데모용으로는 `--min-used 2`를 쓰는 게 맞고, FastAPI에도 `min_detected_used` 파라미터를 노출하면 UI와 맞출 수 있습니다.

---

## 추천 다음 단계 (Week 5 후반)

1. `api/schemas.py` — `PredictResponse`, `RecipeQuery`, `RankedRecipe`  
2. `api/predictor.py` — `best.pt` 로드 + `normalize_detections`  
3. `api/main.py` — `/predict`, `/recipes`, `/recipe/{id}`, `/scale`  
4. Streamlit (Week 6)

FastAPI까지 이어서 구현할까요?

---

**User**

잠만 CLI로 테스트 하는법 알려줘

---

**Cursor**

## CLI 테스트 방법

프로젝트 루트에서 실행하세요.

```bash
cd "/Users/k2/Documents/프로젝트"
```

---

### 1. 레시피 랭킹 (onion + chicken Top-5)

**기본** — onion 또는 chicken 중 하나만 써도 되는 레시피 포함:

```bash
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5
```

**둘 다 쓰는 레시피만** (데모용):

```bash
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5 --min-used 2
```

**필터 추가** (선택):

```bash
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5 --cuisine 한식
python3 scripts/rank_demo.py --ingredients onion,chicken --top 5 --meal dinner --diet vegetarian
```

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--ingredients` | YOLO 클래스 (쉼표 구분) | `onion,chicken,carrot` |
| `--top` | 상위 N개 | `5` |
| `--min-used` | 탐지 재료 중 최소 사용 개수 | `2` |
| `--meal` | breakfast / lunch / dinner / snack / dessert | `dinner` |
| `--cuisine` | 한식 / 일식 / 이탈리안 / 중식 / 아메리칸 | `한식` |
| `--diet` | vegan, vegetarian, dairy-free, 저탄수화물 등 | `vegetarian` |

---

### 2. 재료 파서 검증

```bash
python3 core/ingredient_parser.py
```

한식·영문 CSV 파싱 성공률과 샘플 출력이 나옵니다.

---

### 3. 식약처 레시피 수집 (API)

`.env`에 `FOODSAFETY_API_KEY`가 있으면:

```bash
python3 scripts/fetch_foodsafety_recipes.py
```

---

### Python에서 직접 호출

```python
from core.normalizer import normalize_detections
from core.ranker import rank_recipes, RecipeFilters

detected = normalize_detections(["onion", "chicken"])
results = rank_recipes(detected, top_k=5, min_detected_used=2)

for r in results:
    print(r.recipe_name, r.score, r.coverage, r.missing)
```

---

`ModuleNotFoundError: No module named 'core'`가 나오면 **`scripts/rank_demo.py`를 쓰거나**, 프로젝트 루트에서 실행했는지 확인하세요. `scripts/rank_demo.py`는 경로를 자동으로 잡습니다.

---

**User**

근데 내가 지금 쓰는 레시피가 두개인거 알지? 하나는 데이터베이스에 있고 하나는 api 끌고 오는거지?

---

**Cursor**

현재 레시피 데이터 구조를 코드 기준으로 확인 중입니다.


맞아요, **원천은 두 개**입니다. 다만 **앱/랭커가 쓰는 건 하나로 합친 로컬 파일**입니다.

## 두 레시피 소스

| 구분 | 경로 | 내용 | 언제 쓰나 |
|------|------|------|-----------|
| **1. 로컬 DB** | `Recipes Dataset/recipes.csv` | Allrecipes 영문 ~1,090건 | 처음부터 프로젝트에 있음 |
| **2. API 수집** | 식약처 Open API (`COOKRCP01`) | 한식 ~1,146건 | `fetch_foodsafety_recipes.py`로 **1회 배치 수집** |

API로 받은 건 바로 쓰지 않고 파일로 저장합니다.

```
data/recipes_korean.csv   ← 식약처만
data/recipes_merged.csv   ← 영문 + 한식 병합본 (~2,236건)
```

`source` 컬럼으로 구분됩니다.

- `allrecipes` — 로컬 CSV에서 온 것  
- `foodsafety` — API에서 받아 저장한 것  

---

## 런타임(랭킹·CLI)에서는?

**API를 다시 부르지 않습니다.** 계획서(v3)대로:

- **구축 단계**: API로 한 번 긁어서 CSV 저장  
- **실행 단계**: `data/recipes_merged.csv`만 읽음  

`core/ranker.py`도 `recipes_merged.csv`만 로드합니다.

```15:15:core/ranker.py
DEFAULT_RECIPES = ROOT / "data" / "recipes_merged.csv"
```

그래서 “소스는 두 개, **실제 추천 DB는 merged 하나**”가 맞습니다.

---

## 정리

```
[로컬 recipes.csv]  ──┐
                      ├──→ recipes_merged.csv ──→ ranker / (나중에 FastAPI)
[식약처 API 1회]   ──┘      ↑
                      recipes_korean.csv
```

API 키는 **`fetch_foodsafety_recipes.py` 실행할 때만** 필요하고, `rank_demo.py`나 랭커 테스트에는 필요 없습니다.

레시피를 다시 받고 싶을 때만:

```bash
python3 scripts/fetch_foodsafety_recipes.py
```

이렇게 하면 `recipes_korean.csv`와 `recipes_merged.csv`가 갱신됩니다.

---

**User**

Week 5 FastAPI를 구현해줘.
지금 다음단계로 이거 하는거 맞아?


추천 다음 단계 (Week 5 후반)
api/schemas.py — PredictResponse, RecipeQuery, RankedRecipe
api/predictor.py — best.pt 로드 + normalize_detections
api/main.py — /predict, /recipes, /recipe/{id}, /scale
Streamlit (Week 6)
FastAPI까지 이어서 구현할까요?

api/schemas.py: Pydantic 요청/응답 모델
api/predictor.py: best.pt 로드 + YOLO 추론 + normalizer 연결
api/main.py:
  - POST /predict  (이미지 N장 → 재료 목록)
  - POST /recipes  (재료+필터 → Top-K)
  - GET  /recipe/{id}  (상세 + pantry 3구간)
  - POST /scale  (인분 변경)
  - GET  /health

1차 목표: Swagger에서 
POST /predict에 냉장고 사진 올리면 
재료 JSON이 나오면 성공.

---

**Cursor**

Week 5 FastAPI 구현을 시작합니다. `best.pt` 위치와 기존 YOLO 추론 코드를 확인합니다.


Week 5 FastAPI 구현 진행 중입니다.


Week 5 FastAPI 구현을 마쳤습니다. **지금 단계가 맞습니다** — 계획서 Week 5 → Week 6 Streamlit 순서와 일치합니다.

## 생성된 파일

```
api/
  schemas.py    — Pydantic 요청/응답
  predictor.py  — best.pt + YOLO 추론 + normalizer
  main.py       — 5개 엔드포인트
scripts/run_api.py
requirements.txt
```

## 서버 실행

```bash
cd "/Users/k2/Documents/프로젝트"
.venv/bin/pip install -r requirements.txt   # 최초 1회
python3 scripts/run_api.py
```

브라우저: **http://127.0.0.1:8000/docs** (Swagger)

## Swagger에서 `/predict` 테스트 (1차 목표)

1. `POST /predict` 열기 → **Try it out**
2. `files`에 냉장고/식재료 사진 1장 이상 선택  
   (테스트용: `smart refrigerator.yolov11/valid/images/` 안 이미지)
3. **Execute**

성공 응답 예:

```json
{
  "ingredients": {
    "onion": 1,
    "chicken": 1,
    "tomato": 1,
    ...
  },
  "detections": [...],
  "image_count": 1
}
```

`ingredients`가 표준 YOLO 클래스별 개수 JSON이면 성공입니다.

## 전체 엔드포인트

| 메서드 | 경로 | 역할 |
|--------|------|------|
| GET | `/health` | 모델·레시피 DB 상태 |
| POST | `/predict` | 이미지 N장 → 재료 JSON |
| POST | `/recipes` | 재료+필터 → Top-K |
| GET | `/recipe/{id}?detected=onion,chicken` | 상세 + pantry 3구간 |
| POST | `/scale` | 인분 변경 |

### curl 예시

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "files=@smart refrigerator.yolov11/valid/images/DSC_5851_JPG_jpg.rf.teFoK1YopQGX276sDKxX.jpg"
```

## 환경변수 (선택)

| 변수 | 기본값 |
|------|--------|
| `YOLO_WEIGHTS` | `best.pt` |
| `YOLO_CONF` | `0.25` |
| `RECIPES_CSV` | `data/recipes_merged.csv` |

---

## 다음 단계

**Week 6 — Streamlit UI** (업로드 → 재료 확인 → 필터 → 추천 → 상세)

서버는 백그라운드에서 이미 떠 있을 수 있습니다. Swagger 바로 열어보시면 됩니다.

---

**User**

POST /predict 엔드포인트에서
Swagger UI에 파일 업로드 버튼이 안 나오고
텍스트 입력창이 나오는 문제가 있어.

api/main.py의 /predict 파라미터를 아래처럼 수정해줘:

from fastapi import UploadFile, File
from typing import List

@app.post("/predict")
async def predict(files: List[UploadFile] = File(...)):
    ...

---

**Cursor**

Swagger에서 파일 업로드가 보이도록 `List[UploadFile]`로 바꾸고, `from __future__ import annotations`가 OpenAPI 스키마를 깨뜨리지 않게 조정합니다.


수정했습니다.

## 변경 내용

`api/main.py`:

1. `from typing import List` 추가  
2. `/predict` 파라미터를 `List[UploadFile] = File(...)` 로 변경  
3. `from __future__ import annotations` 제거 — 이게 있으면 FastAPI가 `File`을 JSON 텍스트 필드로 잘못 인식하는 경우가 많습니다.

```python
from typing import List

@app.post("/predict", ...)
async def predict(
    files: List[UploadFile] = File(..., description="냉장고 사진 1장 이상"),
    predictor: IngredientPredictor = Depends(get_predictor),
) -> PredictResponse:
```

OpenAPI 스키마도 `multipart/form-data` + `files` 배열(바이너리)로 정상 생성되는 것 확인했습니다.

## 확인 방법

서버가 `--reload`로 떠 있으면 자동 반영됩니다. 아니면 다시 실행하세요.

```bash
python3 scripts/run_api.py
```

http://127.0.0.1:8000/docs → `POST /predict` → **Try it out**  
`files` 옆에 **Choose Files** 버튼이 보이면 성공입니다.

---

**User**

@/Users/k2/.cursor/projects/Users-k2-Documents/terminals/1.txt:168-172 

이렇게 떠

---

**Cursor**

`(base)` 환경에 `uvicorn`이 없어서 발생한 오류입니다. 의존성을 설치합니다.


`(base)` conda 환경에 `uvicorn`이 없어서 난 오류입니다. 프로젝트 `requirements.txt`로 패키지 설치해 두었습니다.

다시 실행하세요:

```bash
cd "/Users/k2/Documents/프로젝트"
python3 scripts/run_api.py
```

Swagger: **http://127.0.0.1:8000/docs**

---

**참고:** 터미널에 `(base)`가 보이면 conda 기본 Python을 쓰는 겁니다. 프로젝트 전용 가상환경을 쓰려면:

```bash
cd "/Users/k2/Documents/프로젝트"
source .venv/bin/activate
pip install -r requirements.txt   # .venv에 아직 없을 때만
python3 scripts/run_api.py
```

둘 중 하나만 쓰면 됩니다. 지금은 `(base)`에도 설치돼 있어서 `python3 scripts/run_api.py`만 실행해도 됩니다.

---

**User**

@/Users/k2/.cursor/projects/Users-k2-Documents/terminals/1.txt:138-148 

(.venv)에서 실행해도 문제 없는거야?

---

**Cursor**

네, **`.venv`에서 실행하는 게 맞고 권장되는 방식**입니다.

터미널에 `(.venv) (base)`가 같이 보이는 건:

- **`(.venv)`** — 프로젝트 가상환경이 활성화됨 → `python3`가 `.venv/bin/python3`를 사용
- **`(base)`** — conda base도 켜져 있음 → 이름만 남아 있는 것

실제로 쓰는 Python은 **`.venv` 쪽**입니다. 로그도 정상입니다.

```
Application startup complete.
GET /docs → 200 OK
```

## 확인 방법 (선택)

```bash
which python3
# .../프로젝트/.venv/bin/python3 이면 OK

python3 -c "import uvicorn, fastapi; print('ok')"
```

## 정리

| 실행 방식 | 권장 |
|-----------|------|
| `source .venv/bin/activate` 후 `python3 scripts/run_api.py` | ✅ 권장 |
| `(base)`만 켜고 `python3 scripts/run_api.py` | 동작은 할 수 있으나 패키지가 base에 깔림 |

지금처럼 **`.venv` 활성화 → 서버 실행**이면 문제 없습니다. Swagger는 http://127.0.0.1:8000/docs 에서 `POST /predict` 테스트하면 됩니다.

