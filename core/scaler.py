"""인분 변경 시 재료량 스케일링."""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.ingredient_parser import ParsedIngredient, parse_ingredients

SEASONING_UNITS = frozenset(
    {
        "tsp",
        "teaspoon",
        "teaspoons",
        "tbsp",
        "tablespoon",
        "tablespoons",
        "pinch",
        "pinches",
        "dash",
        "dashes",
        "작은술",
        "큰술",
        "클",
    }
)

SEASONING_KEYWORDS = (
    "salt",
    "pepper",
    "garlic",
    "ginger",
    "gochugaru",
    "sesame",
    "vinegar",
    "soy",
    "소금",
    "후추",
    "마늘",
    "생강",
    "고춧가루",
    "참기름",
    "간장",
    "식초",
)


@dataclass
class ScaledIngredient:
    name: str
    raw_name: str
    quantity: float | None
    unit: str | None
    yolo_class: str | None = None
    scale_mode: str = "main"


def _parse_servings(value: str | int | float | None) -> int:
    if value is None:
        return 1
    if isinstance(value, (int, float)):
        return max(int(value), 1)
    text = str(value).strip()
    if not text:
        return 1
    m = re.search(r"\d+", text)
    return max(int(m.group()), 1) if m else 1


def _is_seasoning(item: ParsedIngredient) -> bool:
    if item.is_staple:
        return True
    unit = (item.unit or "").lower()
    if unit in SEASONING_UNITS:
        return True
    token = f"{item.name} {item.raw_name}".lower()
    return any(kw in token for kw in SEASONING_KEYWORDS)


def scale_ingredients(
    recipe_ingredients: str | list[ParsedIngredient],
    original_servings: str | int | float | None,
    new_servings: int,
    *,
    source: str = "auto",
) -> list[ScaledIngredient]:
    """
    인분 N → M 변경 시 재료량 조정.

    - 주재료: qty × (M / N)
    - 양념: qty × (M / N)^0.7
    - pantry(staple): 결과에서 제외
    """
    if new_servings < 1:
        raise ValueError("new_servings must be >= 1")

    base = _parse_servings(original_servings)
    ratio = new_servings / base

    if isinstance(recipe_ingredients, str):
        items = parse_ingredients(recipe_ingredients, source=source)
    else:
        items = list(recipe_ingredients)

    scaled: list[ScaledIngredient] = []
    for item in items:
        if item.is_staple:
            continue
        if item.quantity is None:
            scaled.append(
                ScaledIngredient(
                    name=item.name,
                    raw_name=item.raw_name,
                    quantity=None,
                    unit=item.unit,
                    yolo_class=item.yolo_class,
                    scale_mode="main",
                )
            )
            continue

        if _is_seasoning(item):
            factor = ratio**0.7
            mode = "seasoning"
        else:
            factor = ratio
            mode = "main"

        scaled.append(
            ScaledIngredient(
                name=item.name,
                raw_name=item.raw_name,
                quantity=round(item.quantity * factor, 2),
                unit=item.unit,
                yolo_class=item.yolo_class,
                scale_mode=mode,
            )
        )

    return scaled
