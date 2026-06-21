┌─────────────────────────────────────────────────────────────────┐
│  Client Layer — Streamlit Web UI (7단계)                        │
│  업로드 / 통합 재료표 / DB·카테고리·식단 / 레시피명 검색 / 상세   │
└─────────────────────────────────────────────────────────────────┘
         │ ▲
  [이미지 N장]  [JSON: 재료·custom·필터·name_query, 추천·상세]
         ▼ │
┌─────────────────────────────────────────────────────────────────┐
│  Application Layer — FastAPI                                    │
│  /predict · /recipes · /recipe/{id} · /scale · /health         │
└─────────────────┬───────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI Core Layer                                                  │
│  Row 1: YOLOv11 → Normalizer → Ranker (ingredient_parser,      │
│         custom_match, name_query)                               │
│  Row 2: Pantry (4구간·custom_match) · Scaler (RecipeStore)      │
└────┬────────────────┬───────────────────┬──────────────────────┘
     │ S1             │ S2, S3, S5        │ S4
     ▼                ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Storage Layer                                                  │
│  best.pt · recipes_merged_ko.csv (~2,236) · mapping.json +      │
│  mapping_ko.json · pantry.json                                  │
└─────────────────────────────────────────────────────────────────┘
         │
   [Docker Compose (로컬) / Cloud Run (공개 URL)]
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Infrastructure Layer — Docker · Google Cloud Run               │
└─────────────────────────────────────────────────────────────────┘

### 공개 URL
- UI: https://fridge-ui-579587565890.asia-northeast3.run.app
- API: https://fridge-api-579587565890.asia-northeast3.run.app/docs

> 상세: [`fridge-recipe-plan-v3.md`](fridge-recipe-plan-v3.md) §2.1~2.3 (v3.18)
