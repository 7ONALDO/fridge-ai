"""레시피 DB 출처·카테고리 필터 정의 (UI ↔ ranker 공통).

Allrecipes: ``Recipes Dataset/recipes.csv`` 의 ``cuisine_path`` 1단계(L1)
식약처: ``/한식/{RCP_PAT2}`` 하위 유형 (API ``RCP_PAT2``)

카테고리 개수 (필터 값):
  - 한식(식약처): **6** (반찬, 일품, 후식, 밥, 국&찌개, 기타)
  - Allrecipes: **13** (L1)
  - 합계 **19** (출처별로 택1 — 동시에 섞이지 않음)
"""

from __future__ import annotations

UI_NONE = "(선택 안 함)"

# (API value, UI 라벨)
RECIPE_SOURCE_OPTIONS: list[tuple[str | None, str]] = [
    (None, "전체 (한식 + 양식)"),
    ("foodsafety", "한식 (식약처)"),
    ("allrecipes", "양식·기타 (해외 레시피)"),
]

# Allrecipes cuisine_path L1 — Recipes Dataset/recipes.csv 기준 (1,090건)
ALLRECIPES_L1: list[tuple[str, str]] = [
    ("Desserts", "디저트·베이킹"),
    ("Side Dish", "반찬·사이드"),
    ("Salad", "샐러드"),
    ("Drinks Recipes", "음료·스무디"),
    ("Appetizers and Snacks", "간식·애피타이저"),
    ("Bread", "빵"),
    ("Breakfast and Brunch", "아침·브런치"),
    ("Main Dishes", "메인 요리"),
    ("Meat and Poultry", "고기·가금"),
    ("Soups, Stews and Chili Recipes", "수프·스튜"),
    ("Seafood", "해산물"),
    ("Cuisine", "세계 요리"),
    ("Everyday Cooking", "일상 요리"),
]

# 식약처 /한식/{유형} — recipes_merged.csv foodsafety 기준
FOODSAFETY_SUBTYPES: list[tuple[str, str]] = [
    ("반찬", "반찬"),
    ("일품", "일품 (면·국수·만두·덮밥 등 한 그릇 요리)"),
    ("후식", "후식·디저트"),
    ("밥", "밥·죽"),
    ("국&찌개", "국·찌개"),
    ("기타", "기타"),
]

# UI 도움말 (Streamlit caption용)
FOODSAFETY_CATEGORY_HELP: dict[str, str] = {
    "일품": (
        "식약처 분류 **일품** — 밥+반찬이 아닌 **한 그릇으로 내는 요리**. "
        "예: 국수, 냉면, 만두, 덮밥, 볶음밥, 파스타형 요리 등 (약 171건)."
    ),
}

ALLRECIPES_CATEGORY_COUNT = len(ALLRECIPES_L1)
FOODSAFETY_CATEGORY_COUNT = len(FOODSAFETY_SUBTYPES)
TOTAL_CATEGORY_COUNT = ALLRECIPES_CATEGORY_COUNT + FOODSAFETY_CATEGORY_COUNT


def allrecipes_category_options() -> list[tuple[str, str]]:
    """Streamlit/API용 (API value, 한국어 라벨)."""
    return [(UI_NONE, UI_NONE)] + [(k, label) for k, label in ALLRECIPES_L1]


def foodsafety_category_options() -> list[tuple[str, str]]:
    return [(UI_NONE, "한식 전체")] + [(k, label) for k, label in FOODSAFETY_SUBTYPES]
