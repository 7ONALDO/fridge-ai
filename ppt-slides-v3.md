# 📊 PPT 슬라이드 스크립트 (19장, v3.16)

> **v3.16: 통합 재료 UI·custom·식단 토글 AND·페이지네이션(20)·4열 상세 — `fridge-recipe-plan-v3.md` 부록 O**
> **v3.15: 2단계 재료 수동 보정·3~5단계 필터 rankable 건수 — 부록 N**
> **v3.14: UI 한국어·3열 재료 구분·한식 별점/시간 표시·식약처 재료량 파싱 — 부록 M**

> 각 슬라이드의 **제목 · 본문 텍스트 · 시각 요소 제안 · 발표 포인트**를 한 번에 정리.
> 복사 → PPT 붙여넣기 후 디자인만 다듬으면 됨.
> **v3.6: 개발 일정 16주→8주 축소, Week 태그 본문에서 제거 (개발 일정에만 Week 사용)**
> **v3.7: SVG 다이어그램과 정합성 확보 — 슬라이드 5 AI Core를 Row 1 / Row 2 구조로 수정, 슬라이드 6에 사용자 여정 vs 데이터 흐름 구분 각주 추가**
> **v3.8: 실제 PPT 파일과 정합성 확보 — 기존 슬라이드 7(데이터 흐름 명세)을 슬라이드 7(Request Flow 15개 엣지) / 슬라이드 8(Storage Access 5개 엣지)로 분할, 기존 슬라이드 8~19를 9~20으로 재부여, 주 지표의 추론 속도 기준을 CPU에서 GPU로 변경**

---

## 🎨 전체 디자인 가이드 (먼저 읽어주세요)

| 항목 | 권장값 |
|---|---|
| 폰트 (한글) | Pretendard, 본명조, 나눔스퀘어 중 택 1 |
| 폰트 (영문) | Inter, Poppins |
| 색상 | 메인 `#4A6CF7` (딥블루), 포인트 `#FF6B6B` (코랄), 배경 흰색 |
| 본문 크기 | 18~22pt |
| 제목 크기 | 32~40pt |
| 여백 | 상하좌우 최소 1cm |
| 다이어그램 | 복잡한 건 한 장에 하나씩 |

---

# 📄 슬라이드 1 — 표지

### 제목
```
냉장고 AI: 이미지 기반 재료 인식 및
레시피 추천 End-to-End 시스템
```

### 부제
```
Deep Learning End-to-End Pipeline:
from Image Recognition to Serving
```

### 하단 정보
```
딥러닝실습 기말 프로젝트 계획서
인공지능학과 [학번] [이름]
담당교수: 구영현 교수님
2026. 04. 19
```

### 시각 요소
- 냉장고 일러스트 or 냉장고 사진 (우측)
- 왼쪽에 제목, 오른쪽에 이미지 (7:3 비율)

---

# 📄 슬라이드 2 — 프로젝트 개요

### 제목
```
프로젝트 개요
Project Overview
```

### 본문 (3단 구성)

**문제 정의**
- 가정 내 식재료 유기 및 메뉴 결정 비용 문제
- 기존 서비스는 재료 **수동 입력** 필요 → 진입 장벽

**목표**
- 냉장고 사진 → 레시피 추천까지 **자동화된 End-to-End 시스템** 구축
- 사용자는 사진 업로드와 선호 선택만 수행

**차별점**
- 재료 인식에 **직접 학습한 CV 모델** 활용
- **런타임은 외부 API 의존 없이** 로컬 추론으로 동작
- 재료 정규화 + 커버리지 기반 랭킹
- Docker 기반 **재현 가능한 배포**

### 시각 요소
- 3개 박스 가로 배치 또는 아이콘 + 짧은 설명

---

# 📄 슬라이드 3 — 프로젝트 범위 정의 *(중요)*

### 제목
```
프로젝트 범위 정의
Scope of This Project
```

### 본문 — 핵심 선언 (박스로 강조)

```
📌 본 프로젝트의 핵심 딥러닝 과제는
   "YOLOv11 기반 이미지 재료 인식 (Object Detection)"이며,
   
   레시피 추천은 인식 결과를 활용한
   "규칙 기반 랭킹 시스템"으로 구현된다.
```

### 본문 — 범위 구분

**✅ 범위 내 (딥러닝 과제)**
- YOLOv11 기반 30종 재료 객체 탐지
- Transfer Learning, Augmentation, Optimizer Ablation
- FastAPI + Streamlit + Docker 배포

**❌ 범위 외 (의도적 제외)**
- 협업 필터링 / GNN 기반 추천 모델
- 사용자 개인화 / 선호 학습
- 레시피 생성 모델 (Inverse Cooking 등)
- Cold-start / Session-based RecSys

### 본문 — 설계 근거 (하단 작게)

① 사용자 상호작용 로그 부재 → 협업 필터링 적용 불가
② 수업 범위 (CNN · Transfer Learning · Augmentation) 에 집중
③ 규칙 기반 랭킹이 해석 가능성·디버깅에 유리

### 시각 요소
- **상단 박스**: 핵심 선언 (회색 배경, 두꺼운 글씨)
- **중단 2단 구성**: 좌측 범위 내 (초록), 우측 범위 외 (회색)
- **하단**: 설계 근거 3줄 (폰트 작게)

### 발표 포인트 *(매우 중요)*
> "프로젝트명에 '추천'이 들어가지만, 본 과제의 딥러닝 기여는 재료 인식에 있습니다. 추천 모델링은 의도적으로 범위에서 제외하고, 인식 결과의 활용 사례로 규칙 기반 랭킹을 구현했습니다."

---

# 📄 슬라이드 4 — 핵심 요구사항 (README)

### 제목
```
핵심 요구사항
Key Requirements from README
```

### 본문 (표 형식)

| 단계 | 기능 |
|---|---|
| 입력 | 냉장고 사진 **다중 업로드** |
| 인식 | 30개 재료 클래스 자동 탐지·개수 집계 |
| 보정 | **2단계** 통합 표 — **−/+·삭제** · 이름 **단일 입력**(YOLO/custom 자동) |
| 필터 | **DB → 카테고리 → 식단(토글 복수 AND)** — 괄호·**선택 조합 N건** |
| 추천 | **페이지당 20건** · `total_rankable` · 이전/다음 |
| 상세 | 출처별 메타, 서빙 인원, **재료 4열**(보유·구매·상비·**기타**) |
| 재료 4구간 | 보유 / 추가 구매 (≤2) / Pantry / **기타(unmapped+custom)** |
| 스케일링 | 서빙 인원 변경 시 **비례 조정** (자동) |
| 조리법 | 번호 매긴 단계별 안내 |

### 발표 포인트
> "7개 화면의 플로우를 모두 구현하며, 난이도 항목은 범위에서 제외"

---

# 📄 슬라이드 5 — 시스템 아키텍처 (Layered)

### 제목
```
시스템 아키텍처
System Architecture (Layered)
```

### 시각 요소 (중요 — 다이어그램 1장으로 구성)

```
┌─────────────────────────────────────────┐
│  Client Layer                           │
│  Streamlit Web UI (7 화면)              │
└─────────────────────────────────────────┘
              ↕ HTTP/JSON
┌─────────────────────────────────────────┐
│  Application Layer (FastAPI)            │
│  /predict · /recipes · /recipe/{id}     │
│  /scale  · /health                      │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│  AI Core Layer                          │
│  Row 1: YOLOv11 → Normalizer → Ranker   │
│         (/predict, /recipes 흐름)        │
│  Row 2: Pantry Classifier  |  Scaler    │
│         (/recipe/{id})     (/scale)     │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│  Storage Layer                          │
│  best.pt · recipes.csv · mapping.json   │
│  · pantry.json                          │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│  Infrastructure — Docker Compose        │
└─────────────────────────────────────────┘
```

### 발표 포인트
> "5계층으로 분리하여 유지보수성과 재사용성 확보. AI Core 내부는 Row 1(연속 파이프라인)과 Row 2(엔드포인트별 독립 호출)로 구분됩니다."

---

# 📄 슬라이드 6 — Flow Chart

### 제목
```
데이터 Flow Chart
End-to-End Processing Flow
```

### 시각 요소 (PPT SmartArt 또는 Mermaid 캡처)

> 📌 **이 다이어그램은 "사용자 여정 관점"의 흐름**입니다. 실제 API 호출 관계(엄밀한 데이터 흐름)는 계획서 §2.3 Request Flow 표(15개 엣지) 및 별도 상세 Flow Chart SVG를 참고하세요. Top-K 추천 리스트 이후 "레시피 선택 → 상세화면"은 단일 체인이 아니라 UI에서 `/recipe/{id}`와 `/scale`을 **별도로 호출**하는 경로입니다.

```
사용자 사진 업로드 (N장)
         ↓
   YOLOv11 객체 탐지
   (30 classes, bbox)
         ↓
    재료 정규화
   (동의어 매핑)
         ↓
재료 집계 결과 화면 ←─ [화면 2]
         ↓
DB → 카테고리 → 식단(복수 AND)  ←─ [화면 3,4,5]
         ↓
    레시피 랭킹
 (Coverage + Shortage + custom)
         ↓
  페이지 추천 (20건/페이지)  ←─ [화면 6]
         ↓
     레시피 선택
         ↓
[상세] 4구간 **4열** + 인분 **자동** 스케일  ←─ [화면 7]
    (/recipe/{id})          (/scale)
```

### 발표 포인트
> "요구사항의 7개 화면이 각각 어느 단계에 대응되는지 명시. 상세 화면에서는 Pantry Classifier와 Scaler가 각자 독립된 엔드포인트에서 호출됩니다."

---

# 📄 슬라이드 7 — 요청 흐름 (Request Flow 15개 엣지)

### 제목
```
엣지별 데이터 흐름 명세
Data Flow Specification — 인터페이스 명확화
```

### 부제
```
요청 흐름 — Request Flow (15 엣지)
```

### 본문 (15개 엣지 전체)

| # | 경로 | 데이터 형식 | 예시 |
|:-:|---|---|---|
| 1 | User → UI | 이미지 파일 N장 | `[img1.jpg, img2.jpg, img3.jpg]` |
| 2 | User → UI | 필터 선택 이벤트 | `{source, category, diets:[]}` |
| 3 | UI → /predict | multipart/form-data | `files: List[bytes]` |
| 4 | /predict → YOLOv11 | numpy array | `shape=(640,640,3), uint8` |
| 5 | YOLOv11 → Normalizer | Detection 리스트 | `[{class, conf, bbox}, ...]` |
| 6 | Normalizer → /predict | 표준 재료 집합 | `{"onion":2, "carrot":3, ...}` |
| 7 | UI → /recipes | 재료+필터 JSON | `{ingredients, custom_ingredients, filters, top_k, offset}` |
| 8 | /recipes → Ranker | Query 객체 | `Query(ingredients, custom, filters, offset)` |
| 9 | Ranker → /recipes | 페이지+총건수 | `{results, total_rankable, offset, page_size}` |
| 10 | UI → /recipe/{id} | URL 파라미터 | `GET /recipe/427` |
| 11 | /recipe/{id} → Pantry | Recipe 객체 | `Recipe(id, ingredients, ...)` |
| 12 | Pantry → /recipe/{id} | 4구간 분류 | `{owned, to_buy, pantry, extra}` |
| 13 | UI → /scale | 인분 + ID | `{recipe_id, new_servings}` |
| 14 | /scale → Scaler | 배율 계산 | `ratio = new/original` |
| 15 | Scaler → /scale | 스케일된 재료 | `[{name, qty, unit}, ...]` |

### 발표 포인트
> "15개 엣지 전체를 명시하여 각 모듈 간 인터페이스를 엄밀히 정의. 이를 기반으로 병렬 개발과 독립 테스트가 가능합니다."

### 시각 요소 팁
- 표를 슬라이드 전체에 크게 배치 (본문 영역 100% 활용)
- 엣지 번호(①~⑮)는 계획서 §2.3 Request Flow 표와 1:1 대응
- 상세 Flow Chart SVG와 병기하면 이해도 ↑

---

# 📄 슬라이드 8 — 저장소 접근 (Storage Access 5개 엣지)

### 제목
```
저장소 접근 — Storage Access
Storage Access — 파일 로드 시점과 내용
```

### 부제
```
파일별 접근 시점 및 내용 (S1 ~ S5)
```

### 본문 (5개 저장소 접근 경로)

| # | 경로 | 접근 시점 | 내용 |
|:-:|---|---|---|
| S1 | YOLOv11 ← `best.pt` | 서버 시작 시 1회 | 학습 완료 가중치 (30 classes) |
| S2 | Normalizer ← `mapping.json` | 요청마다 | 동의어 ~150쌍 JSON 딕셔너리 |
| S3 | Ranker ← `recipes.csv` | 시작 시 DataFrame 로드 | 1,090행 × 15열 |
| S4 | Pantry Classifier ← `pantry.json` | 요청마다 | 상비 재료 목록 (water, salt, …) |
| S5 | Scaler ← `recipes.csv` | 요청마다 | 해당 recipe의 ingredients 필드 |

### 하단 요약
> "각 모듈 간 인터페이스를 명확히 정의 → 병렬 개발과 디버깅 용이"

### 발표 포인트
> "YOLOv11 가중치는 서버 시작 시 한 번 로드하고, 레시피 DataFrame도 메모리 상주시켜 응답 지연을 최소화합니다. 반면 mapping/pantry는 요청마다 읽어 최신 설정 반영이 용이합니다."

### 시각 요소 팁
- 각 저장소 접근 방식(1회 로드 / 요청마다)을 색상으로 구분하면 직관적
- "메모리 상주 vs 즉시 조회" 구분 아이콘 활용 가능

---

# 📄 슬라이드 9 — 사용할 데이터셋

### 제목
```
사용할 데이터셋
Datasets
```

### 본문 (표)

| 모듈 | 데이터셋 | 규모 | 역할 |
|---|---|---|---|
| **객체 탐지** | Roboflow Smart Refrigerator | **3,049장 / 30 classes** | YOLOv11 학습 |
| **레시피 DB** | Recipes Dataset (Allrecipes) | **1,090건 / 15열** | 필터·랭킹 |
| 인분 파싱 | test_recipes.csv | 59건 / 구조화 수량 | 스케일링 검증 |
| **한식 보강** | **식약처 Open API** | **한식 레시피** | **한식 태그** |

### 시각 요소
- 데이터셋 샘플 이미지 3~4장 (냉장고 사진 + 레시피 CSV 스크린샷)

### 발표 포인트
> "이미지 학습량 3만+ instance, 레시피 1,090건으로 충분한 규모 확보"

---

# 📄 슬라이드 10 — 데이터 한계 및 대응

### 제목
```
데이터의 한계와 대응 전략
Limitations & Mitigation
```

### 본문

**📸 이미지 인식 영역**

| 한계 | 대응 |
|---|---|
| **한식 특화 재료 부재** (김치·두부·된장 등 — 30클래스 한계) | 한계 명시 + 향후 과제로 제시 |
| 기본 분할(94/3.4/1.7) 불균형 | **80/10/10 재분할** |
| 냉장고 조명·각도 편향 | Augmentation 강화 (HSV, CLAHE 등) |

**📋 레시피 데이터 영역**

| 한계 | 대응 |
|---|---|
| **영문 기반** 레시피 DB (한식 태그 약함) | **식약처 API로 한식 레시피 배치 수집** |
| `ingredients` 필드 **비구조화** | 정규식 파싱 파이프라인 구축 |
| 식단 필터 엄밀성 한계 (저탄·저지방) | `nutrition` 필드 임계값 기반 근사 |

### 발표 포인트
> "이미지 인식의 한식 재료 부재는 데이터셋 자체의 한계이나, 레시피 측면에서는 식약처 API로 한식 DB를 보강하여 필터 기능을 실질적으로 구현합니다."

---

# 📄 슬라이드 11 — 데이터 전처리

### 제목
```
데이터 전처리 파이프라인
Data Preprocessing Pipeline
```

### 본문 (2단 구성)

**이미지**
- Letterbox 640×640 리사이즈
- Train/Val/Test 80/10/10 재분할
- Augmentation:
  - Mosaic · HSV · Flip · Translate (기본)
  - MixUp · CutMix · Copy-Paste (실험 대상)

**텍스트**
- 자연어 `ingredients` 파싱 (정규식)
- 수량·단위·이름 분리
- 동의어 매핑 JSON (수작업 ~150쌍)
- Pantry(staple) 분리

### 시각 요소
- 코드 스니펫 1개 (파싱 예시)

---

# 📄 슬라이드 12 — 모델 전략 (단일 YOLOv11)

### 제목
```
모델 전략: 왜 단일 YOLOv11인가?
Why Single Model Strategy?
```

### 본문 — 상단 핵심 메시지

```
🔍 데이터셋 분석 결과:
   30 클래스에 이미 세분 재료가 포함됨
```

### 본문 — 세분 클래스 예시 (표 or 박스)

| 상위 개념 | 세분 클래스 |
|---|---|
| 🐔 닭고기 | `chicken` ↔ `chicken_breast` |
| 🥩 소고기 | `beef` ↔ `ground_beef` |
| 🧀 치즈 | `cheese` ↔ `goat_cheese` |
| 🥔 감자류 | `potato` ↔ `sweet_potato` |

### 본문 — 결론 및 이점

```
✅ 추가 분류기 불필요
   → 단일 YOLOv11으로 세부 재료 인식 가능
```

| 이점 | 상세 |
|---|---|
| ① 파이프라인 단순화 | 단일 모델 유지보수 |
| ② 추론 속도 향상 | 단일 forward pass |
| ③ 학습·디버깅 효율 | 실험 반복 속도 ↑ |
| ④ 오류 전파 감소 | Stage 1 오차 누적 방지 |
| ⑤ 학습 데이터 효율 | 단일 모델에 집중 투입 |

### 시각 요소
- **상단**: 🔍 아이콘 + 핵심 메시지 박스 (회색 배경)
- **중단**: 세분 클래스 표 (이모지 포함)
- **하단**: 5대 이점 표 (번호 강조)

### 발표 포인트 *(중요)*
> "초기 설계 단계에서 YOLOv11 + EfficientNet 2단계를 고려했으나, 데이터셋을 분석한 결과 30 클래스에 이미 `chicken`과 `chicken_breast`, `beef`와 `ground_beef` 같은 세분 재료가 포함되어 있음을 확인했습니다. 따라서 추가 분류기 없이도 단일 탐지 모델만으로 충분하며, 이는 의도적으로 단순화한 설계 결정입니다."

---

# 📄 슬라이드 13 — 사용 모델 상세

### 제목
```
사용 모델 상세
Model Specifications
```

### 본문 (표)

| 구분 | 주력 | Baseline |
|---|---|---|
| 모델 | **YOLOv11n / v11s** | YOLOv8n / v8s |
| 사전학습 | COCO | COCO |
| 입력 크기 | 640×640 RGB | 640×640 RGB |
| 출력 | 30 class × bbox × conf | 동일 |
| Optimizer | AdamW (wd=5e-4) | 동일 |
| Scheduler | CosineAnnealingLR | 동일 |
| Loss | CIoU + BCE | CIoU + BCE |

### 발표 포인트
> "YOLOv8을 baseline으로 두어 최신 모델 선택의 **정량 근거** 확보"

---

# 📄 슬라이드 14 — 비즈니스 로직 모듈

### 제목
```
비즈니스 로직 모듈
Business Logic Modules
```

### 본문 (4개 모듈)

**1. 재료 정규화**
- 동의어 매핑 사전 기반 (150쌍)
- 한↔영 양방향, 단복수 정리

**2. 레시피 랭킹 (Coverage + custom)**
```
Score = 0.5 × Coverage + 0.3 × (1/(shortage+1)) + 0.2 × rating
Hard filter: source · category · diets[] AND · overlap · shortage ≤ 2
count_rankable_recipes() / diet_combo_count() — 필터 UI (N)
rank_recipes(top_k, offset) — 6단계 페이지네이션
```

**3. 재료 4구간 분류**
- 보유 / 추가 구매(≤2) / Pantry / **기타(unmapped+custom)**

**4. 인분 스케일러**
- 주재료: `qty × (M/N)`
- 양념: `qty × (M/N)^0.7`

---

# 📄 슬라이드 15 — 성능 평가 지표

### 제목
```
성능 평가 방안
Evaluation Metrics
```

### 본문 (3 영역)

> 📌 **재료 인식이 핵심 딥러닝 과제 → 탐지 성능이 주 지표, 추천 품질은 보조 지표**

**🎯 주 지표 — YOLOv11 탐지 성능**

| 지표 | 목표 |
|---|---|
| mAP@0.5 | ≥ 0.70 |
| mAP@0.5:0.95 | ≥ 0.45 |
| 클래스별 Recall | ≥ 0.70 |
| GPU 추론 속도 | ≤ 10ms/image |

> ※ 30 클래스 전체 달성 어려울 경우 **빈도 상위 20 클래스 평균**을 대안 지표로 활용

**📊 보조 지표 — 추천 시스템 (규칙 기반 랭킹)**

| 지표 | 목표 | 근거 |
|---|---|---|
| Coverage Ratio (평균) | **≥ 0.60** | 60% 이상 보유 시 요리 가능 |
| 부족재료 ≤ 2 만족률 | **≥ 80%** | README 추가구매 ≤ 2 반영 |
| Top-K Precision (K=5) | **≥ 0.70** | 추천 시스템 합리적 목표 |
| 정성 평가 | **≥ 4.0 / 5.0** | 4점 이상 = 실서비스 가능 |

> ※ "유효 추천" = ① 필터 일치 + ② 부족재료 ≤ 2 + ③ 인식 재료 1개 이상 포함

**⚙️ 시스템 통합**

| 지표 | 목표 |
|---|---|
| End-to-End 응답 | ≤ 5초 |
| Docker 이미지 | ≤ 3GB |
| Docker 기동 | 1회 명령 |

---

# 📄 슬라이드 16 — Ablation Study (핵심)

### 제목
```
Ablation Study
설계 기법의 기여도 검증
```

### 본문 (4개 실험 요약)

**실험 1: YOLO 아키텍처 비교**
YOLOv8n/s vs **YOLOv11n/s** → mAP, Params, Speed

**실험 2: Augmentation 전략** ⭐
None → Mosaic → +HSV/Flip → +MixUp/CutMix

**실험 3: Transfer Learning** ⭐
From scratch vs Fine-tune vs Freeze backbone

**실험 4: Optimizer**
SGD vs Adam vs AdamW + Scheduler 비교

### 발표 포인트
> "각 기법이 실제로 성능에 기여하는지 정량 검증"

---

# 📄 슬라이드 17 — 개발 일정

### 제목
```
개발 일정 (8주 / 2개월)
Development Timeline — 8 Weeks Plan
```

---

### 본문 — Month 1: 모델 개발 (Week 1~4)

| 주차 | 작업 | 산출물 |
|:-:|---|---|
| **Week 1** | 데이터 EDA, data.yaml 재분할, 식약처 API 인증키 발급 및 배치 수집, 재료 매핑 사전 구축 (mapping.json), pantry.json 정의, ingredients 파싱 파이프라인 구현 및 검증 | EDA 노트북, 한식 레시피 DB, 동의어 사전 ~150쌍, 파싱 정확도 리포트 |
| **Week 2** | YOLOv8n baseline + YOLOv11n 학습, WandB 세팅 | Baseline 비교표 |
| **Week 3** | Augmentation Ablation (실험 2), Optimizer·Initialization Ablation (실험 4) | Ablation 표 2, 4 |
| **Week 4** | Transfer Learning Ablation (실험 3), 모델 확정, 오탐·미탐 샘플 시각화 및 에러 분석 | Ablation 표 1, 3, 최종 모델 가중치 |

---

### 본문 — Month 2: 앱 개발 & 배포 (Week 5~8)

| 주차 | 작업 | 산출물 |
|:-:|---|---|
| **Week 5** | FastAPI 4개 엔드포인트 구현, 레시피 랭킹·Pantry 분류·Scaler 로직 | API 서버 + Swagger, 비즈니스 모듈 |
| **Week 6** | Streamlit UI 7개 화면 구현, 통합 테스트, 로깅, 에러 핸들링 | Frontend, 통합 리포트 |
| **Week 7** | Dockerfile + docker-compose, ONNX 변환, 정성 평가 설문, 성능 벤치마크 | 배포 이미지, 평가 결과 |
| **Week 8** | README, 발표 PPT, 시연 영상 촬영, 최종 제출 | 최종 산출물 |

---

### 주요 마일스톤

| 시점 | 상태 | 달성 목표 |
|---|:-:|---|
| Week 2 말 | ✅ | Baseline 완성 |
| Week 4 말 | ✅ | 최종 모델 확정 |
| Week 6 말 | ✅ | End-to-End 통합 완료 |
| Week 8 말 | 🎯 | 배포 + 최종 발표 |

---

### 💡 PPT 제작 시 팁

**Month 1 표 / Month 2 표는 한 슬라이드에 세로로 배치**하거나, **공간이 부족하면 2장으로 분할** 권장:
- 슬라이드 17a: Month 1 (Week 1~4)
- 슬라이드 17b: Month 2 (Week 5~8) + 마일스톤

### 시각 요소
- **Gantt 차트 스타일**로 Month 1 (파랑) / Month 2 (주황) 색상 구분
- Week 1의 작업이 많으므로 **Week 1 행만 조금 더 넓게** 설정 권장
- 주차는 굵게, 산출물은 파란색 계열로 강조

### 발표 포인트
> "8주를 Month 1 (모델 개발) / Month 2 (앱 개발 & 배포) 로 나누어, 전반부에 모델 작업을 완료하고 후반부에는 구현과 배포에 전념하는 구조입니다. Week 1에 데이터 준비 작업을 집중하여 이후 모델·앱 개발이 원활하게 이어지도록 설계했습니다."

---

# 📄 슬라이드 18 — 활용 방안

### 제목
```
활용 방안
Applications & Impact
```

### 본문 (3단)

**가정 내 활용**
- 푸드 로스 절감
- 메뉴 결정 시간 단축
- 요리 레퍼토리 확장

**서비스 확장 시나리오**

| 단계 | 기능 |
|---|---|
| v1 | 이미지 → 재료 → 레시피 추천 (**현재**) |
| v2 | 유통기한 OCR |
| v3 | 개인화 추천 |
| v4 | 모바일 앱 (ONNX Mobile) |
| v5 | 스마트 냉장고 IoT |

**사회적 가치**
- UN SDG 12 (책임 있는 소비·생산) 기여
- 식재료 폐기 비용 절감
- 요리 초보자 진입장벽 완화

---

# 📄 슬라이드 19 — 참고문헌

### 제목
```
참고문헌
References
```

### 본문 (번호 매긴 리스트, 폰트 작게)

1. Ultralytics (2024). *YOLOv11 Documentation*. docs.ultralytics.com
2. Jocher, G. et al. (2023). *YOLOv8*.
3. Salvador, A. et al. (2017). *Cross-Modal Embeddings for Cooking Recipes*. CVPR.
4. Marín, J. et al. (2021). *Recipe1M+*. IEEE TPAMI.
5. Tan & Le (2019). *EfficientNet*. ICML.
6. Roboflow Smart Refrigerator Dataset (YOLOv11 format).
7. Recipes Dataset (Allrecipes 기반, 로컬).
8. 식품의약품안전처 Open API. foodsafetykorea.go.kr
9. AWS (2024). *From Fridge to Table*.
10. FastAPI, Streamlit, Albumentations Docs.

---

# 📄 슬라이드 20 (선택) — 감사합니다

### 제목
```
감사합니다
Thank You
```

### 본문
```
Q&A

인공지능학과 [학번] [이름]
이메일: [주소]
GitHub: [링크]
```

---

## 📌 PPT 제작 실전 팁

### ✅ 반드시 지켜야 할 것
1. **한 슬라이드 = 하나의 메시지** — 욕심내서 정보 밀어넣지 말 것
2. **텍스트 < 시각 요소** — 표·다이어그램·아이콘 활용
3. **일관된 폰트·색상** — 3색 이하, 2폰트 이하
4. **여백 확보** — 답답해 보이지 않게
5. **슬라이드 번호** — 하단에 "n / 19" 표기 (감사 슬라이드 포함 시 20)

### 🎯 심사자가 좋아하는 것
- **Before / After 비교**: "Baseline → 개선 후" 형태
- **구체적 숫자**: "3,049장", "150쌍", "mAP ≥ 0.70"
- **시각적 증거**: 데이터셋 샘플 이미지, 실제 파이프라인 예시
- **솔직한 한계 인정**: 오히려 신뢰도 ↑

### ⚠️ 피해야 할 것
- 과도한 애니메이션
- 너무 작은 글씨 (18pt 미만)
- 저화질 이미지
- 단조로운 텍스트 나열 (불릿 과다)

### 🔧 추천 작업 순서
1. **텍스트 먼저 전부 채우기** (디자인 X)
2. **다이어그램 삽입** (슬라이드 5, 6)
3. **일관된 디자인 적용** (폰트, 색상)
4. **이미지·아이콘 추가**
5. **슬라이드 순서 점검**
6. **발표 연습 → 시간 체크** (15분 내외)

---

## 🎤 발표 시 강조할 3가지

1. **"본 과제의 핵심 딥러닝 기여는 재료 인식"** (슬라이드 3) ⭐ 가장 먼저
2. **"모델 선택에 정량 근거 — Ablation 4종"** (슬라이드 16)
3. **"End-to-End 실제 배포 가능한 시스템"** (슬라이드 5, 17)

---

*이 스크립트를 기반으로 PPT를 만들면 19장 분량으로 완성 가능 (감사합니다 포함 시 20장).*
*추가로 특정 슬라이드의 다이어그램을 시각화하거나 디자인 템플릿이 필요하면 말씀해주세요.*
