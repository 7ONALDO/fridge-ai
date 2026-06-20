"""레시피 랭킹 — Coverage + Shortage + rating."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from core.custom_match import (
    count_unmapped_matched,
    custom_names_set,
    unmapped_recipe_items,
)
from core.ingredient_parser import ParsedIngredient, parse_ingredients, supplement_from_directions
from core.normalizer import normalize_detections
from core.recipe_categories import UI_NONE

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECIPES = ROOT / "data" / "recipes_merged.csv"

ALPHA, BETA, GAMMA = 0.5, 0.3, 0.2
MAX_SHORTAGE = 2
EXCLUDE_REQUIREMENT = re.compile(
    r"(broth|stock|bouillon|consomme|육수|멸치육수|다시마)",
    re.IGNORECASE,
)

DIET_FORBIDDEN: dict[str, frozenset[str]] = {
    "vegan": frozenset(
        {
            "chicken",
            "chicken_breast",
            "beef",
            "ground_beef",
            "ham",
            "shrimp",
            "eggs",
            "milk",
            "butter",
            "cheese",
            "goat_cheese",
            "heavy_cream",
        }
    ),
    "vegetarian": frozenset(
        {"chicken", "chicken_breast", "beef", "ground_beef", "ham", "shrimp"}
    ),
    "dairy-free": frozenset(
        {"milk", "butter", "cheese", "goat_cheese", "heavy_cream"}
    ),
    "high-protein": frozenset(),  # nutrition 기반으로 별도 처리
}

@dataclass
class RecipeFilters:
    """레시피 Hard filter.

    source: ``foodsafety`` | ``allrecipes`` | None(전체)
    category: Allrecipes ``cuisine_path`` L1 (예: ``Desserts``) 또는
              식약처 하위 유형 (예: ``반찬``, ``국&찌개``)
    """

    source: str | None = None
    category: str | None = None
    diet: str | None = None  # 단일 선택(하위 호환)
    diets: list[str] = field(default_factory=list)

    def active_diets(self) -> list[str]:
        if self.diets:
            return [d for d in self.diets if d and d != UI_NONE]
        if self.diet and self.diet != UI_NONE:
            return [self.diet]
        return []


@dataclass
class RecipeRecord:
    recipe_id: int
    recipe_name: str
    prep_time: str
    cook_time: str
    total_time: str
    servings: str
    yield_: str
    ingredients: str
    directions: str
    rating: float
    url: str
    cuisine_path: str
    nutrition: str
    img_src: str
    source: str
    parsed: list[ParsedIngredient] = field(repr=False)
    requirements: frozenset[str] = field(repr=False)
    unmapped: list[ParsedIngredient] = field(repr=False)

    @property
    def parse_source(self) -> str:
        return "korean" if self.source == "foodsafety" else "english"


@dataclass
class RankedRecipe:
    recipe_id: int
    recipe_name: str
    score: float
    coverage: float
    shortage: int
    missing: list[str]
    detected_used: int
    rating: float
    img_src: str
    url: str
    cuisine_path: str
    source: str


def _parse_rating(value: str) -> float:
    try:
        rating = float(value)
    except (TypeError, ValueError):
        rating = 0.0
    if rating <= 0:
        return 3.0  # 식약처 등 미평가 레시피 중립값
    return max(0.0, min(rating, 5.0))


def _normalize_rating(value: float) -> float:
    return value / 5.0


def _recipe_requirements(parsed: list[ParsedIngredient]) -> frozenset[str]:
    reqs: set[str] = set()
    for item in parsed:
        if item.is_staple:
            continue
        if not item.yolo_class:
            continue
        if EXCLUDE_REQUIREMENT.search(item.raw_name):
            continue
        reqs.add(item.yolo_class)
    return frozenset(reqs)


def _compute_metrics(
    detected: set[str], requirements: frozenset[str]
) -> tuple[float, int, list[str]]:
    if not requirements:
        return 0.0, 0, []
    owned = detected & requirements
    missing = sorted(requirements - detected)
    coverage = len(owned) / len(requirements)
    shortage = len(missing)
    return coverage, shortage, missing


def _score_recipe(
    coverage: float, shortage: int, rating: float
) -> float:
    return (
        ALPHA * coverage
        + BETA * (1.0 / (shortage + 1))
        + GAMMA * _normalize_rating(rating)
    )


def _path_parts(cuisine_path: str) -> list[str]:
    return [p for p in cuisine_path.strip("/").split("/") if p]


def _match_source(recipe: RecipeRecord, source: str | None) -> bool:
    if not source:
        return True
    return recipe.source == source


def _match_category(recipe: RecipeRecord, category: str | None) -> bool:
    """출처별 ``cuisine_path`` prefix 매칭."""
    if not category or category.strip() in (UI_NONE, "전체", "all", ""):
        return True

    key = category.strip()
    parts = _path_parts(recipe.cuisine_path)

    if recipe.source == "foodsafety":
        if len(parts) < 2 or parts[0] != "한식":
            return False
        return parts[1] == key

    # allrecipes — L1 또는 L2 (``Desserts/Pies``)
    if "/" in key:
        segs = key.split("/", 1)
        return len(parts) >= 2 and parts[0] == segs[0] and parts[1] == segs[1]
    return bool(parts) and parts[0] == key


def _parse_nutrition_number(nutrition: str, label: str) -> float | None:
    m = re.search(rf"{label}\s*([\d.]+)\s*g", nutrition, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def _match_diet(recipe: RecipeRecord, diet: str) -> bool:
    key = diet.strip().lower()
    if not key:
        return True

    classes = {item.yolo_class for item in recipe.parsed if item.yolo_class}

    if key in ("vegan", "vegetarian", "dairy-free", "유제품 없음", "채식", "비건"):
        mapping = {
            "vegan": "vegan",
            "vegetarian": "vegetarian",
            "dairy-free": "dairy-free",
            "유제품 없음": "dairy-free",
            "채식": "vegetarian",
            "비건": "vegan",
        }
        rule_key = mapping.get(key, key)
        forbidden = DIET_FORBIDDEN.get(rule_key)
        if forbidden:
            return not (classes & forbidden)

    nutrition = recipe.nutrition or ""

    if key in ("low-carb", "저탄수화물"):
        carbs = _parse_nutrition_number(nutrition, "carbohydrate")
        if carbs is None:
            carbs = _parse_nutrition_number(nutrition, "탄수화물")
        if carbs is not None:
            return carbs <= 20
        return "sugar" not in classes and "bread" not in classes and "potato" not in classes

    if key in ("low-fat", "저지방"):
        fat = _parse_nutrition_number(nutrition, "fat")
        if fat is None:
            fat = _parse_nutrition_number(nutrition, "지방")
        if fat is not None:
            return fat <= 10
        return not (classes & {"butter", "heavy_cream", "cheese"})

    if key in ("sugar-free", "무설탕"):
        if "sugar" in classes:
            return False
        sugars = _parse_nutrition_number(nutrition, "sugars")
        if sugars is None:
            sugars = _parse_nutrition_number(nutrition, "당")
        return sugars is None or sugars <= 1

    if key in ("high-protein", "고단백"):
        protein = _parse_nutrition_number(nutrition, "protein")
        if protein is None:
            protein = _parse_nutrition_number(nutrition, "단백질")
        return protein is None or protein >= 15

    return True


def passes_filters(recipe: RecipeRecord, filters: RecipeFilters | None) -> bool:
    if filters is None:
        return True
    if not _match_source(recipe, filters.source):
        return False
    if not _match_category(recipe, filters.category):
        return False
    for diet_key in filters.active_diets():
        if not _match_diet(recipe, diet_key):
            return False
    return True


class RecipeStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_RECIPES
        self.recipes: list[RecipeRecord] = []
        self._by_id: dict[int, RecipeRecord] = {}
        self._load()

    def _load(self) -> None:
        seen_urls: set[str] = set()
        recipe_id = 0

        with self.path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = (row.get("url") or "").strip()
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)

                source = (row.get("source") or "allrecipes").strip()
                parse_source = "korean" if source == "foodsafety" else "english"
                ingredients = row.get("ingredients") or ""
                directions = (row.get("directions") or "").strip()
                parsed = parse_ingredients(ingredients, source=parse_source)
                parsed = supplement_from_directions(
                    parsed, directions, source=parse_source
                )

                record = RecipeRecord(
                    recipe_id=recipe_id,
                    recipe_name=(row.get("recipe_name") or "").strip(),
                    prep_time=(row.get("prep_time") or "").strip(),
                    cook_time=(row.get("cook_time") or "").strip(),
                    total_time=(row.get("total_time") or "").strip(),
                    servings=(row.get("servings") or "").strip(),
                    yield_=(row.get("yield") or "").strip(),
                    ingredients=ingredients,
                    directions=(row.get("directions") or "").strip(),
                    rating=_parse_rating(row.get("rating") or ""),
                    url=url,
                    cuisine_path=(row.get("cuisine_path") or "").strip(),
                    nutrition=(row.get("nutrition") or "").strip(),
                    img_src=(row.get("img_src") or "").strip(),
                    source=source,
                    parsed=parsed,
                    requirements=_recipe_requirements(parsed),
                    unmapped=unmapped_recipe_items(parsed),
                )
                self.recipes.append(record)
                self._by_id[recipe_id] = record
                recipe_id += 1

    def get(self, recipe_id: int) -> RecipeRecord:
        if recipe_id not in self._by_id:
            raise KeyError(f"recipe_id {recipe_id} not found")
        return self._by_id[recipe_id]


def _detected_set(
    detected: set[str] | dict[str, int] | list[str],
) -> set[str]:
    if isinstance(detected, dict):
        return set(detected.keys())
    if isinstance(detected, set):
        return detected
    return set(normalize_detections(detected).keys())


def _combined_coverage(
    detected_set: set[str],
    yolo_requirements: frozenset[str],
    unmapped: list[ParsedIngredient],
    custom: dict[str, int] | list[str] | None,
) -> float:
    yolo_total = len(yolo_requirements)
    unmapped_total = len(unmapped)
    total = yolo_total + unmapped_total
    if total == 0:
        return 0.0
    yolo_owned = len(detected_set & yolo_requirements)
    unmapped_owned = count_unmapped_matched(unmapped, custom)
    return (yolo_owned + unmapped_owned) / total


def _effective_detected_used(
    detected_set: set[str],
    yolo_requirements: frozenset[str],
    unmapped: list[ParsedIngredient],
    custom: dict[str, int] | list[str] | None,
) -> int:
    return len(detected_set & yolo_requirements) + count_unmapped_matched(
        unmapped, custom
    )


def _qualifies_for_ranking(
    recipe: RecipeRecord,
    detected_set: set[str],
    filters: RecipeFilters | None,
    *,
    custom: dict[str, int] | list[str] | None = None,
    require_overlap: bool = True,
    min_detected_used: int = 1,
) -> bool:
    if not passes_filters(recipe, filters):
        return False
    yolo_req = recipe.requirements
    unmapped = recipe.unmapped
    if not yolo_req and not unmapped:
        return False

    used = _effective_detected_used(detected_set, yolo_req, unmapped, custom)
    if require_overlap and used < min_detected_used:
        return False

    if yolo_req:
        _, shortage, _ = _compute_metrics(detected_set, yolo_req)
        if shortage > MAX_SHORTAGE:
            return False
    return True


def count_rankable_recipes(
    detected: set[str] | dict[str, int] | list[str],
    *,
    filters: RecipeFilters | None = None,
    store: RecipeStore | None = None,
    custom: dict[str, int] | list[str] | None = None,
    require_overlap: bool = True,
    min_detected_used: int = 1,
) -> int:
    """6단계 추천 목록과 동일 조건으로 매칭되는 레시피 수."""
    detected_set = _detected_set(detected)
    if not detected_set and not custom_names_set(custom):
        return 0
    store = store or RecipeStore()
    return sum(
        1
        for recipe in store.recipes
        if _qualifies_for_ranking(
            recipe,
            detected_set,
            filters,
            custom=custom,
            require_overlap=require_overlap,
            min_detected_used=min_detected_used,
        )
    )


def rank_recipes(
    detected: set[str] | dict[str, int] | list[str],
    *,
    filters: RecipeFilters | None = None,
    top_k: int = 5,
    offset: int = 0,
    store: RecipeStore | None = None,
    custom: dict[str, int] | list[str] | None = None,
    require_overlap: bool = True,
    min_detected_used: int = 1,
) -> list[RankedRecipe]:
    """탐지 재료 + 직접 입력 재료 + 필터 → Top-K 레시피 (offset부터 page)."""
    detected_set = _detected_set(detected)

    store = store or RecipeStore()
    ranked: list[RankedRecipe] = []

    for recipe in store.recipes:
        if not _qualifies_for_ranking(
            recipe,
            detected_set,
            filters,
            custom=custom,
            require_overlap=require_overlap,
            min_detected_used=min_detected_used,
        ):
            continue

        coverage = _combined_coverage(
            detected_set, recipe.requirements, recipe.unmapped, custom
        )
        shortage, missing = 0, []
        if recipe.requirements:
            _, shortage, missing = _compute_metrics(
                detected_set, recipe.requirements
            )
        detected_used = _effective_detected_used(
            detected_set, recipe.requirements, recipe.unmapped, custom
        )
        score = _score_recipe(coverage, shortage, recipe.rating)
        ranked.append(
            RankedRecipe(
                recipe_id=recipe.recipe_id,
                recipe_name=recipe.recipe_name,
                score=round(score, 4),
                coverage=round(coverage, 4),
                shortage=shortage,
                missing=missing,
                detected_used=detected_used,
                rating=recipe.rating,
                img_src=recipe.img_src,
                url=recipe.url,
                cuisine_path=recipe.cuisine_path,
                source=recipe.source,
            )
        )

    ranked.sort(
        key=lambda r: (r.score, r.detected_used, r.coverage, r.rating),
        reverse=True,
    )
    start = max(offset, 0)
    end = start + top_k if top_k > 0 else None
    return ranked[start:end]


def _cli() -> None:
    parser = argparse.ArgumentParser(description="레시피 랭킹 CLI 데모")
    parser.add_argument(
        "--ingredients",
        default="onion,chicken",
        help="쉼표로 구분한 YOLO 클래스 (예: onion,chicken)",
    )
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument(
        "--min-used",
        type=int,
        default=1,
        help="탐지 재료 중 최소 몇 개를 레시피가 사용해야 하는지",
    )
    parser.add_argument(
        "--source",
        default=None,
        choices=["foodsafety", "allrecipes"],
        help="레시피 DB 출처",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Allrecipes L1 (Desserts) 또는 식약처 유형 (반찬, 국&찌개)",
    )
    parser.add_argument("--diet", default=None)
    args = parser.parse_args()

    detected = normalize_detections(
        [x.strip() for x in args.ingredients.split(",") if x.strip()]
    )
    filters = RecipeFilters(
        source=args.source, category=args.category, diet=args.diet
    )

    print(f"냉장고 재료: {detected}")
    if any([args.source, args.category, args.diet]):
        print(
            f"필터: source={args.source}, category={args.category}, diet={args.diet}"
        )
    print(f"\nTop-{args.top} 레시피")
    print("-" * 72)

    results = rank_recipes(
        detected,
        filters=filters,
        top_k=args.top,
        min_detected_used=args.min_used,
    )
    if not results:
        print("조건에 맞는 레시피가 없습니다.")
        return

    for i, r in enumerate(results, 1):
        missing = ", ".join(r.missing) if r.missing else "-"
        print(
            f"{i}. [{r.score:.3f}] {r.recipe_name}\n"
            f"   coverage={r.coverage:.0%}  shortage={r.shortage}  "
            f"used={r.detected_used}  rating={r.rating}  missing=[{missing}]\n"
            f"   {r.cuisine_path}  ({r.source})"
        )


if __name__ == "__main__":
    _cli()
