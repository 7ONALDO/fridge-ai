# 프로젝트 진행·결과 리뷰

> Cursor 작업 기록 요약. 상세는 [`fridge-recipe-plan-v3.md`](fridge-recipe-plan-v3.md) · [`project-final-summary.md`](project-final-summary.md) 참고.

## 현재 상태

| 항목 | 상태 |
|------|------|
| FastAPI + Streamlit E2E | ✅ |
| Docker + Cloud Run | ✅ |
| YOLO 데이터셋 | 3,196장 · train 2,895 / valid 150 / test 151 |
| YOLO 공식 성능 (test 151장) | mAP@0.5 **0.870**, mAP@0.5:0.95 **0.569**, Recall **0.879** |
| 런타임 레시피 DB | **`data/recipes_merged_ko.csv`** (한식 + 번역 Allrecipes) |
| 공개 UI | https://fridge-ui-579587565890.asia-northeast3.run.app |
| 남은 작업 | PPT · 시연 영상 · 스크린샷 (Week 8) · Cloud Run 재배포(최신 코드 반영 시) |

## v3.18 변경 요약 (2026-06)

| 영역 | 내용 |
|------|------|
| **DB** | API·Docker 기본값 → `recipes_merged_ko.csv` |
| **파서** | 번역 레시피 한글 파서 · 노이즈 필터(손질 문구·`간 것` 등) · `(40g)` 괄호 회귀 수정 · `supplement_from_directions` OFF |
| **카테고리** | `ALLRECIPES_L1_KO_ALIASES` — 번역 `cuisine_path` L1 매칭 |
| **custom_match** | `RICE_EQUIV` — `쌀`↔`멥쌀`·`쌀밥` (1글자 custom 허용) |
| **6단계 UI** | 레시피명 **부분 검색** — `filters.name_query` |
| **ranker** | `RecipeFilters.name_query` · `passes_filters()` |
| **UI** | 조리법 `~` 마크다운 이스케이프 (`_safe_markdown_text`) |

상세 diff: 계획서 **부록 Q**.

## 참고 문서

- 실행·배포: [../README.md](../README.md)
- 계획서 §3.2 (split) · §5.2 (파서) · §6.1 (성능) · 부록 Q: [fridge-recipe-plan-v3.md](fridge-recipe-plan-v3.md)
- 비전공자용 요약: [project-final-summary.md](project-final-summary.md)
