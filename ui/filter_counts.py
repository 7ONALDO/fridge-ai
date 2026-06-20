"""필터 UI 옵션별 추천 가능 레시피 건수 (6단계와 동일 조건)."""

from __future__ import annotations

from core.ranker import (
    DEFAULT_RECIPES,
    RecipeFilters,
    RecipeStore,
    count_rankable_recipes,
)
from core.recipe_categories import ALLRECIPES_L1, FOODSAFETY_SUBTYPES, UI_NONE

DIET_KEYS = [
    UI_NONE,
    "vegetarian",
    "vegan",
    "dairy-free",
    "high-protein",
    "low-carb",
    "low-fat",
    "sugar-free",
]

_store: RecipeStore | None = None


def _get_store() -> RecipeStore:
    global _store
    if _store is None:
        _store = RecipeStore(DEFAULT_RECIPES)
    return _store


def _norm_source(source: str | None) -> str | None:
    if source in (None, UI_NONE):
        return None
    return source


def _norm_category(category: str | None) -> str | None:
    if category in (None, UI_NONE):
        return None
    return category.strip()


def _norm_diet(diet: str | None) -> str | None:
    if diet in (None, UI_NONE):
        return None
    return diet


def _norm_diets(diets: list[str] | None) -> list[str]:
    if not diets:
        return []
    return [d for d in diets if d and d != UI_NONE]


def _count(
    ingredients: dict[str, int],
    custom_ingredients: dict[str, int] | None = None,
    *,
    source: str | None = None,
    category: str | None = None,
    diet: str | None = None,
    diets: list[str] | None = None,
) -> int:
    active = _norm_diets(diets)
    if not active:
        one = _norm_diet(diet)
        active = [one] if one else []
    filters = RecipeFilters(
        source=_norm_source(source),
        category=_norm_category(category),
        diets=active,
    )
    return count_rankable_recipes(
        ingredients,
        filters=filters,
        store=_get_store(),
        custom=custom_ingredients or {},
    )


def source_counts(
    ingredients: dict[str, int],
    custom_ingredients: dict[str, int] | None = None,
) -> dict[str | None, int]:
    return {
        UI_NONE: _count(ingredients, custom_ingredients),
        "foodsafety": _count(ingredients, custom_ingredients, source="foodsafety"),
        "allrecipes": _count(ingredients, custom_ingredients, source="allrecipes"),
    }


def category_counts(
    ingredients: dict[str, int],
    source: str | None,
    custom_ingredients: dict[str, int] | None = None,
) -> dict[str, int]:
    src = _norm_source(source)
    if src == "foodsafety":
        keys = [UI_NONE] + [k for k, _ in FOODSAFETY_SUBTYPES]
    elif src == "allrecipes":
        keys = [UI_NONE] + [k for k, _ in ALLRECIPES_L1]
    else:
        return {UI_NONE: _count(ingredients, custom_ingredients)}
    return {
        key: _count(ingredients, custom_ingredients, source=src, category=key)
        for key in keys
    }


def diet_counts(
    ingredients: dict[str, int],
    source: str | None,
    category: str | None,
    custom_ingredients: dict[str, int] | None = None,
) -> dict[str, int]:
    return {
        key: _count(
            ingredients,
            custom_ingredients,
            source=source,
            category=category,
            diet=key if key != UI_NONE else None,
        )
        for key in DIET_KEYS
    }


def diet_combo_count(
    ingredients: dict[str, int],
    source: str | None,
    category: str | None,
    diets: list[str],
    custom_ingredients: dict[str, int] | None = None,
) -> int:
    return _count(
        ingredients,
        custom_ingredients,
        source=source,
        category=category,
        diets=diets,
    )
