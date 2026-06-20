# 프로젝트 설명 문서 작성 플랜

## Context
딥러닝 수업 프로젝트 결과물을 설명해야 함.
전체 흐름부터 구현 세부 내용까지 단계적으로 정리된 MD 문서 생성.
저장 위치: `/Users/k2/Documents/프로젝트/project-learning-summary.md`

---

## 문서 구성

### 1. 프로젝트 한 줄 요약
냉장고 사진 → YOLOv11 재료 탐지 → 레시피 추천 End-to-End 시스템

### 2. 전체 흐름 (사용자 시나리오)
사진 업로드 → 재료 확인 → 필터(DB·카테고리·식단) → 레시피 순위 → 상세 + 인분 조절

### 3. 기술 스택 표
| 영역 | 기술 |
|------|------|
| 딥러닝 | YOLOv11n (Ultralytics) |
| 백엔드 | FastAPI + Uvicorn |
| 프론트엔드 | Streamlit |
| 데이터 처리 | Python, Pandas |
| 번역 | OpenAI GPT-4o-mini |

### 4. 데이터셋
- YOLO 학습: Smart Refrigerator YOLOv11 (Roboflow), 3,049장, 30클래스, 80/10/10
- 30개 클래스: apple, banana, beef, blueberries, bread, butter, carrot, cheese,
  chicken, chicken_breast, chocolate, corn, eggs, flour, goat_cheese, green_beans,
  ground_beef, ham, heavy_cream, lime, milk, mushrooms, onion, potato, shrimp,
  spinach, strawberries, sugar, sweet_potato, tomato
- 레시피: 식약처(한식) 1,146개 + allrecipes(영어→한국어 번역 중) 1,090개

### 5. 모델 학습
- 모델: YOLOv11n (COCO pretrained → 파인튜닝)
- 설정: AdamW, lr=0.001, cos_lr, 100 epochs, batch=16, imgsz=640
- 결과: mAP@0.5 = 0.994, mAP@0.5:0.95 = 0.839, Recall = 0.989

### 6. 시스템 4층 구조
```
Client Layer  → Streamlit UI (7단계 화면)
App Layer     → FastAPI (5개 엔드포인트)
AI Core Layer → YOLO → Normalizer → Ranker → Pantry → Scaler
Storage Layer → best.pt, recipes_merged.csv, mapping.json, pantry.json
```

### 7. 각 모듈 설명 (core/)
- **normalizer.py**: YOLO 탐지 결과 → 30개 표준 클래스로 정규화 (mapping.json 기반)
- **ingredient_parser.py**: 레시피 재료 파싱 + **`supplement_from_directions`** (조리법 보강) + 섹션 헤더(`양념장 :` 등)
- **custom_match.py**: YOLO 30종 밖 **`custom_ingredients`** ↔ 레시피 unmapped 부분 매칭
- **pantry.py**: 재료 **4구간** — 🧊보유 / 🛒추가구매 / 🏠상비 / 📋**기타** — **4열 UI**
- **ranker.py**: score + **`count_rankable_recipes`** + **`rank_recipes(offset)`** 페이지네이션 · **`diets[]` AND**
- **scaler.py**: 원본 인분 → 요청 인분 비례 재료량 계산

### 8. FastAPI 엔드포인트 5개
- POST /predict — 이미지 → 재료 탐지
- POST /recipes — 재료+**custom**+필터+**offset** → **`total_rankable`** + 페이지 결과
- GET /recipe/{id} — 레시피 상세 + 재료 분류
- POST /scale — 인분 변경 → 재료량 재계산
- GET /health — 서버/모델 상태 확인

### 9. Streamlit UI 7단계
1 사진 업로드 → 2 **통합 재료 표**(−/+·단일 추가) → 3 레시피 DB → 4 카테고리
→ 5 **식단 토글 복수(AND)** → 6 **페이지네이션(20)** → 7 **4열** 상세

**v3.16 UI**: 통합 재료 · **custom** · 식단 **토글 AND** · **페이지당 20** · **4열(기타)** · `diet_combo_count()`

**v3.15 UI**: 2단계 YOLO 수동 보정 · 3~5단계 rankable 괄호 (`ui/filter_counts.py`)

**v3.14 UI**: 한국어 · 상세 3열 → **v3.16에서 4열** · 한식 별점 숨김 · 인분 자동 스케일

### 10. 레시피 추천 로직 상세
- coverage = 보유재료 ∩ 필수재료 / 필수재료
- shortage ≤ 2 (부족 재료 2개 이하만 추천)
- DB·카테고리·**`diets[]` AND** 필터 — `source` + taxonomy (§4.2.3)
- **custom_ingredients** Coverage · 6단계 **offset/total_rankable**
- 재료 파싱 — Allrecipes 쉼표·식약처 `(70g)` (§5.2)
- 한식 메타 — 별점/조리시간 없음 → UI 규칙 (§4.2.4)

### 11. 현재 진행 상황
| 단계 | 상태 |
|------|------|
| YOLO 모델 학습 | ✅ 완료 |
| FastAPI 서버 | ✅ 완료 |
| Core 모듈 | ✅ 완료 |
| Streamlit UI | ✅ 완료 |
| 레시피 한국어 번역 | 🔄 진행 중 |
| Docker | ⬜ 미착수 |

---

## 작성 파일
`/Users/k2/Documents/프로젝트/project-learning-summary.md`

깔끔한 한국어로, 비전공자도 이해할 수 있게 작성.
코드보다는 흐름과 개념 위주, 구체적인 수치(mAP, 레시피 수 등)는 포함.
