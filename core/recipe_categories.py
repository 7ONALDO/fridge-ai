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

# 영→한 번역 ``cuisine_path`` L1 (recipes_merged.csv ↔ recipes_merged_ko.csv URL 매칭)
ALLRECIPES_L1_KO_ALIASES: dict[str, frozenset[str]] = {
    "Desserts": frozenset({"디저트"}),
    "Side Dish": frozenset({"반찬", "부식", "사이드디시", "사이드디쉬"}),
    "Salad": frozenset({"샐러드"}),
    "Drinks Recipes": frozenset({"음료", "음료 레시피", "음료레시피"}),
    "Appetizers and Snacks": frozenset(
        {
            "애피타이저와 스낵",
            "전채와 간식",
            "전채요리",
            "전채요리와 간식",
            "전채요리와 스낵",
        }
    ),
    "Bread": frozenset({"빵", "빠른빵레시피", "빵레시피"}),
    "Breakfast and Brunch": frozenset({"아침과 브런치", "아침식사와 브런치"}),
    "Main Dishes": frozenset({"메인요리"}),
    "Meat and Poultry": frozenset({"고기와 가금류", "고기요리", "육류와 가금류"}),
    "Soups, Stews and Chili Recipes": frozenset(
        {"수프", "수프, 스튜 및 칠리 레시피"}
    ),
    "Seafood": frozenset({"해산물"}),
    "Cuisine": frozenset({"요리"}),
    "Everyday Cooking": frozenset({"일상요리", "일상 요리"}),
}

ALLRECIPES_CATEGORY_COUNT = len(ALLRECIPES_L1)
FOODSAFETY_CATEGORY_COUNT = len(FOODSAFETY_SUBTYPES)
TOTAL_CATEGORY_COUNT = ALLRECIPES_CATEGORY_COUNT + FOODSAFETY_CATEGORY_COUNT


def allrecipes_l1_matches(category_key: str, path_l1: str) -> bool:
    """필터 키(영문 L1) ↔ DB ``cuisine_path`` 1단계(영문 또는 번역 한글)."""
    if path_l1 == category_key:
        return True
    aliases = ALLRECIPES_L1_KO_ALIASES.get(category_key)
    return bool(aliases and path_l1 in aliases)


def allrecipes_category_options() -> list[tuple[str, str]]:
    """Streamlit/API용 (API value, 한국어 라벨)."""
    return [(UI_NONE, UI_NONE)] + [(k, label) for k, label in ALLRECIPES_L1]


def foodsafety_category_options() -> list[tuple[str, str]]:
    return [(UI_NONE, "한식 전체")] + [(k, label) for k, label in FOODSAFETY_SUBTYPES]


def _short_foodsafety_label(label: str) -> str:
    return label.split(" (")[0] if " (" in label else label


def combined_category_options() -> list[tuple[str, str]]:
    """3단계 「전체」일 때 — 한식·양식 세부 카테고리를 한 목록에."""
    opts: list[tuple[str, str]] = [(UI_NONE, "전체 (카테고리 없이 검색)")]
    opts.append(("foodsafety:", "한식 전체"))
    for key, label in FOODSAFETY_SUBTYPES:
        opts.append((f"foodsafety:{key}", f"한식 · {_short_foodsafety_label(label)}"))
    opts.append(("allrecipes:", "양식 전체"))
    for key, label in ALLRECIPES_L1:
        opts.append((f"allrecipes:{key}", f"양식 · {label}"))
    return opts


def parse_composite_category(
    category: str | None,
) -> tuple[str | None, str | None]:
    """UI 복합 키 ``foodsafety:반찬`` → (source, category)."""
    if category in (None, UI_NONE, ""):
        return None, None
    if ":" in category:
        src, cat = category.split(":", 1)
        return src or None, cat or None
    return None, category
