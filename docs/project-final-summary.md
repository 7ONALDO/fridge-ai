# 냉장고 AI — 프로젝트 전체 정리

> **한 줄 요약**: 냉장고 사진을 찍으면 AI가 재료를 자동으로 인식하고, 지금 가진 재료로 만들 수 있는 레시피를 추천해주는 End-to-End 딥러닝 시스템

---

## 1. 전체 흐름 (사용자 입장)

```
📷 냉장고 사진 업로드
        ↓
🤖 AI가 재료 자동 인식   ← YOLOv11 (30가지 재료 탐지)
        ↓
✅ 재료 확인 — 통합 표에서 −/+·삭제, 이름 하나로 추가 (김치 등 custom 포함)
        ↓
🍽️ 원하는 조건 선택   ← DB 출처 / 카테고리 / 식단 복수(AND) · 토글 버튼
        ↓
📋 레시피 추천 목록   ← 페이지당 20건 · 전체 탐색 (total_rankable)
        ↓
📖 레시피 상세 보기   ← 재료 4구간(기타 포함) + 조리 방법 + 인분 조절
```

---

## 2. 기술 스택

| 영역 | 기술 | 역할 |
|------|------|------|
| 딥러닝 모델 | YOLOv11n (Ultralytics) | 냉장고 사진에서 재료 탐지 |
| 백엔드 API | FastAPI + Uvicorn | 추론 서버, 레시피 검색 |
| 프론트엔드 | Streamlit | 웹 UI (7단계 화면) |
| 데이터 처리 | Python (csv, json) | 레시피 파싱, 점수 계산 |
| 번역 | OpenAI GPT-4o-mini | 영문 레시피 → 한국어 |
| **배포 (로컬)** | Docker Compose | API+UI 컨테이너 한 번에 기동 |
| **배포 (공개)** | Google Cloud Run | 인터넷 URL로 시연 |

---

## 2-1. 배포 현황

| 환경 | 앱 | API |
|------|-----|-----|
| **Cloud Run** | https://fridge-ui-579587565890.asia-northeast3.run.app | https://fridge-api-579587565890.asia-northeast3.run.app/docs |
| **로컬 Docker** | http://127.0.0.1:8501 | http://127.0.0.1:8000/docs |

**배포 흐름 요약**

1. `Dockerfile`로 API·UI **공용 이미지** 빌드 (`best.pt` 포함)
2. **로컬**: `docker-compose.yml` → `fridge-api` + `fridge-ui` 2컨테이너
3. **클라우드**: Cloud Build → Artifact Registry → Cloud Run 2서비스 (서울 리전)

상세: [`../README.md`](../README.md) · [`fridge-recipe-plan-v3.md`](fridge-recipe-plan-v3.md) §5.7

## 3. 데이터셋

### 3-1. YOLO 학습 데이터
- **출처**: Roboflow — Smart Refrigerator YOLOv11
- **총 이미지**: 3,049장
- **분할 비율**: 학습(train) 80% / 검증(val) 10% / 테스트(test) 10%
- **클래스 수**: 30개

**탐지 가능한 30가지 재료:**

| 영문 | 한국어 | 영문 | 한국어 | 영문 | 한국어 |
|------|--------|------|--------|------|--------|
| apple | 사과 | ham | 햄 | onion | 양파 |
| banana | 바나나 | heavy_cream | 생크림 | potato | 감자 |
| beef | 소고기 | lime | 라임 | shrimp | 새우 |
| blueberries | 블루베리 | milk | 우유 | spinach | 시금치 |
| bread | 빵 | mushrooms | 버섯 | strawberries | 딸기 |
| butter | 버터 | chicken | 닭고기 | sugar | 설탕 |
| carrot | 당근 | chicken_breast | 닭가슴살 | sweet_potato | 고구마 |
| cheese | 치즈 | chocolate | 초콜릿 | tomato | 토마토 |
| corn | 옥수수 | eggs | 달걀 | flour | 밀가루 |
| goat_cheese | 염소치즈 | green_beans | 완두콩 | ground_beef | 다진소고기 |

### 3-2. 레시피 데이터
- **식약처(foodsafety)**: 한식 레시피 1,146개 — 처음부터 한국어, **완성 요리 사진** (`foodsafetykorea.go.kr/uploadimg/...`), **별점·조리시간(분) 없음**
- **allrecipes**: 영어 레시피 1,090개 — **사용자 별점**·prep/cook/total 시간·Allrecipes 썸네일
- **합계**: `recipes_merged.csv` ~2,107건

---

## 4. 모델 학습

### 4-1. 왜 YOLOv11n인가?
- **YOLO(You Only Look Once)**: 이미지를 한 번만 훑어서 여러 물체를 동시에 탐지하는 객체 탐지 모델
- **n (nano) 버전**: 가장 가볍고 빠른 버전 → 노트북/서버에서도 빠른 추론 가능
- COCO 데이터셋(80가지 일반 물체)으로 이미 학습된 가중치를 **냉장고 재료 30개 탐지**에 맞게 파인튜닝

### 4-2. 학습 설정

| 항목 | 값 | 이유 |
|------|----|----|
| Optimizer | AdamW | 안정적인 수렴, L2 정규화 내장 |
| Learning Rate | 0.001 (cosine 감소) | 마지막까지 부드럽게 수렴 |
| Epochs | 100 (Early stopping 20) | 충분한 학습 + 과적합 방지 |
| Batch Size | 16 | GPU 메모리와 속도 균형 |
| Image Size | 640×640 | YOLO 표준 입력 크기 |
| Augmentation | Mosaic, HSV, Flip | 다양한 각도·밝기 학습 |
| Pretrained | COCO 사전학습 | 전이학습으로 빠른 수렴 |

### 4-3. 학습 결과

| 지표 | 의미 | 결과 | 목표 |
|------|------|------|------|
| mAP@0.5 | 탐지 정확도 (IOU 50% 기준) | **0.994** | ≥ 0.70 |
| mAP@0.5:0.95 | 더 엄격한 정확도 | **0.839** | ≥ 0.45 |
| Recall | 실제 재료를 놓치지 않는 비율 | **0.989** | ≥ 0.70 |
| Precision | 탐지 결과 중 맞은 비율 | **0.995** | 참고 |

> ⚠️ **주의**: val/test 데이터에 augmentation이 적용된 이미지가 포함되어 수치가 실제보다 높을 수 있음

---

## 5. 시스템 구조 (4층 아키텍처)

```
┌──────────────────────────────────────────────┐
│  Client Layer — Streamlit UI                 │
│  사진 업로드, 재료 확인, 필터 선택, 레시피 화면 │
└─────────────────┬────────────────────────────┘
                  │ HTTP (multipart/JSON)
┌─────────────────▼────────────────────────────┐
│  Application Layer — FastAPI                 │
│  /predict  /recipes  /recipe/{id}  /scale    │
└─────────────────┬────────────────────────────┘
                  │ Python 함수 호출
┌─────────────────▼────────────────────────────┐
│  AI Core Layer — core/ 모듈들                │
│  YOLO → Normalizer → Ranker                  │
│                  → Pantry → Scaler           │
└─────────────────┬────────────────────────────┘
                  │ 파일 읽기
┌─────────────────▼────────────────────────────┐
│  Storage Layer — 데이터 파일들               │
│  best.pt  /  recipes_merged.csv              │
│  mapping.json  /  pantry.json                │
└──────────────────────────────────────────────┘
```

---

## 6. 핵심 모듈 상세 설명 (core/)

### normalizer.py — 탐지 결과 정규화
YOLO가 탐지한 클래스명을 **표준 30개 클래스**로 통일.

```
"사과"        →  "apple"
"apple juice" →  "apple"
"닭가슴살"    →  "chicken_breast"
```

`data/mapping_ko.json` 파일에 각 클래스별 동의어 목록이 저장되어 있음.

---

### ingredient_parser.py — 레시피 재료 파싱
레시피의 재료 문자열을 구조화된 데이터로 분해.

```
입력: "3 tablespoons butter"
출력: { 이름: butter, 양: 3.0, 단위: tablespoons, YOLO클래스: butter }

입력: "돼지고기(70g), 콩나물(150g)"
출력: { 이름: 돼지고기, 양: 70.0, 단위: g, … }
```

| 출처 | 파싱 특징 |
|------|-----------|
| **Allrecipes** | 한 줄 쉼표 목록 — **새 재료가 시작하는 쉼표**에서만 분리 |
| **식약처** | `재료명(70g)`, `연두부 75g(3/4모)` 형식 지원 |
| **식약처** | `양념장 :`, `•필수 재료 :` | 섹션 헤더 제거 후 재료 파싱 |
| **공통** | 조리법에만 등장 | `supplement_from_directions()` 사전 기반 보강 |
| **상비** | `pantry.json` — 후추 vs red pepper flakes 오매칭 방지 |
| **복합명** | `버섯마늘소금` 등 | 내포 상비(소금) 분리, YOLO 오매칭 방지 |

---

### custom_match.py — 자유 입력 재료 매칭 *(v3.16)*

YOLO 30종 밖 사용자 입력(`custom_ingredients`)을 레시피 **unmapped** 항목과 부분 문자열 매칭.

```
입력: {"김치": 1}
레시피: "배추김치" → 매칭 → Coverage·7단계 기타/보유에 반영
```

---

### pantry.py — 재료 4구간 분류 *(v3.16)*

레시피 재료를 냉장고 보유 여부에 따라 4가지로 분류:

| 구간 | 내용 | UI 표시 규칙 |
|------|------|-------------|
| 🧊 보유 (owned) | YOLO 탐지 + custom 매칭 | 인분 기준 **필요량** |
| 🛒 추가 구매 (to_buy) | 없어서 사야 하는 YOLO 재료 | **부족 1~2개일 때만** + 필요량. **상비·기타 제외** |
| 🏠 상비재 (pantry) | `pantry.json` (소금·간장·기름 등) | **추가 구매·기타에 포함 안 함** |
| 📋 기타 (extra) | YOLO 30종 밖 레시피 재료 (unmapped) | custom과 매칭 시 `extra_matched` |

---

### ranker.py — 레시피 점수 계산
보유 재료와 레시피 필요 재료를 비교해 점수를 매김:

```
점수 = 0.5 × coverage  +  0.3 × (1 / shortage+1)  +  0.2 × rating

coverage  = (YOLO + custom + unmapped 매칭) / 레시피 필수재료
shortage  = 없는 YOLO 클래스 수 (2개 초과 시 추천 제외)
overlap   = (YOLO ∪ custom) ∩ 필수재료 ≥ 1 (없으면 제외)
rating    = Allrecipes: 실제 별점 / 한식: **없음** → 랭킹용 3.0 (UI 비표시)
```

**v3.15~v3.16 — 추천 자격·페이지네이션:**

| 함수 | 역할 |
|------|------|
| `_qualifies_for_ranking()` | 필터 + overlap + shortage ≤ 2 판정 |
| `count_rankable_recipes()` | 6단계·5단계 조합 건수 (3~5단계 괄호) |
| `rank_recipes(top_k, offset)` | 동일 자격 후 점수순 → **페이지 슬라이스** |
| `diet_combo_count()` | 5단계 **복수 식단 AND** 조합 건수 |

**필터 종류 (v3.16):**
- **DB 출처**: 전체 / 한식(식약처) / Allrecipes
- **카테고리** (출처별): Allrecipes L1 · 식약처 유형 (반찬, 국&찌개, …)
- **식단** (복수 AND): 채식 / 비건 / 유제품 없음 / 고단백 / 저탄수 / 저지방 / 무설탕 — **토글 버튼**

---

### scaler.py — 인분 조절
레시피 원본 인분 수 → 원하는 인분 수로 재료량 비례 계산.

```
원본: 닭고기 300g (4인분)  →  원하는 인분: 2인  →  닭고기 150g
```

---

## 7. API 엔드포인트 5개

| 경로 | 메서드 | 입력 | 출력 |
|------|--------|------|------|
| `/predict` | POST | 냉장고 사진 (1장 이상) | 인식된 재료 목록 + 개수 |
| `/recipes` | POST | `ingredients` + `custom_ingredients` + 필터 + `top_k`/`offset` | 페이지 결과 + `total_rankable` |
| `/recipe/{id}` | GET | 레시피 ID + 보유·custom 재료 | 레시피 상세 + 재료 **4구간** |
| `/scale` | POST | 레시피 ID + 목표 인분 | 조정된 재료량 목록 |
| `/health` | GET | 없음 | 모델 로드 상태 + 레시피 수 |

---

## 8. Streamlit UI 7단계

```
[1단계] 사진 업로드
  냉장고 사진 1장 이상 업로드 → "재료 인식하기" 버튼

[2단계] 재료 확인
  YOLO + custom 통합 **단일 표**
  표에서 **−/+·삭제** · 검색 · **이름 하나로 추가** (양파→YOLO, 김치→custom)

[3단계] 레시피 DB 선택
  전체 / 한식 / Allrecipes — 괄호 = rankable 건수

[4단계] 카테고리
  출처별 유형 — 괄호 = rankable (카테고리 합 = 전체)

[5단계] 식단 선호
  **토글 버튼 7종** 복수 선택(AND)
  괄호 = **단독** 적용 건수 · **「선택 조합: N건」** = 6단계 총 수

[6단계] 레시피 추천 목록
  **페이지당 20건** · 이전/다음 · `총 N건 · a–b번째`
  점수·커버리지 카드 + "상세 보기"

[7단계] 레시피 상세
  출처별: 양식=시간+별점 / 한식=조리방법만
  재료 **4열** (보유 | 구매 | 상비 | **기타**)
  인분 변경 → 재료량 자동 계산 · 조리 방법
```

---

## 9. 프로젝트 파일 구조

```
fridge-ai/
├── best.pt                    ← YOLO 가중치
├── Dockerfile · docker-compose.yml
├── api/ · core/ · ui/ · data/
├── scripts/                   ← run_api.py, run_ui.py, docker-up.sh …
├── training/                  ← train_yolo_byclaude.py, ablation_yolo.py
├── presentation/              ← Ablation JSON, 학습 그래프
└── docs/                      ← 계획서·PPT·요약 (docs/README.md)
```

---

## 10. 실행 방법

### 로컬 개발 (코드 수정용)

```bash
cd ~/Documents/fridge-ai
source .venv/bin/activate

# 터미널 1 — API 서버 시작
python3 scripts/run_api.py
# → http://localhost:8000/docs  (Swagger UI 확인 가능)

# 터미널 2 — 웹 UI 시작
python3 scripts/run_ui.py
# → http://localhost:8501  (브라우저에서 사용)
```

### Docker (로컬 한 번에)

```bash
cd ~/Documents/fridge-ai
./scripts/docker-up.sh
# → http://127.0.0.1:8501 (UI) · http://127.0.0.1:8000/docs (API)
```

### Cloud Run (공개 URL · 발표용)

- **앱**: https://fridge-ui-579587565890.asia-northeast3.run.app
- **API**: https://fridge-api-579587565890.asia-northeast3.run.app/docs

---

## 11. 현재 진행 상황

| 단계 | 상태 | 비고 |
|------|------|------|
| YOLO 데이터셋 준비 | ✅ 완료 | 3,049장, 30클래스, 80/10/10 |
| YOLO 모델 학습 | ✅ 완료 | mAP@0.5 = 0.994 |
| Core 모듈 구현 | ✅ 완료 | 파서, 랭커, 팬트리, 스케일러 |
| FastAPI 서버 | ✅ 완료 | 5개 엔드포인트 |
| Streamlit UI | ✅ 완료 | 7단계, v3.16 — 통합 재료·식단 토글·페이지네이션·4열 상세 |
| 레시피 한국어 번역 | 🔄 진행 중 | GPT-4o-mini, 1,090개 |
| Docker 컨테이너화 | ✅ 완료 | `Dockerfile`, `docker-compose.yml`, 로컬 Compose 기동 |
| Cloud Run 배포 | ✅ 완료 | `fridge-api` + `fridge-ui`, GCP `fridge-ai-demo`, 서울 리전 |
| 발표 자료 | ⬜ 미착수 | Week 8 예정 — Cloud Run UI URL로 시연 |

---

## 12. 한계 및 개선 가능성

| 한계 | 설명 | 개선 방향 |
|------|------|----------|
| 탐지 클래스 30개 제한 | 김치·두부 등 한식 재료 | **custom_ingredients** + 7단계 기타 열 (부분 매칭) |
| val/test에 augmentation 포함 | 성능 수치가 실제보다 높게 나올 수 있음 | 원본 이미지로 재평가 필요 |
| 키워드 기반 필터링 | ML 기반보다 정확도 낮음 | 임베딩 기반 의미 매칭으로 개선 가능 |
| 한식 조리 시간·별점 | 식약처 API에 없음 | UI에서 숨김·조리방법만 표시 |
| 레시피 ~2,107개 | 상업 서비스 대비 적음 | 크롤링 또는 공공 API로 확장 |
