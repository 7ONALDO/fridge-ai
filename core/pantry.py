"""레시피 재료 → 보유 / 추가구매 / pantry 3구간 분류."""

from __future__ import annotations

from dataclasses import dataclass

from core.custom_match import (
    custom_matches_item,
    custom_names_set,
    unmapped_recipe_items,
)
from core.ingredient_parser import ParsedIngredient, parse_ingredients
from core.normalizer import normalize_to_set


@dataclass
class ClassifiedIngredients:
    owned: list[ParsedIngredient]
    to_buy: list[ParsedIngredient]
    pantry: list[ParsedIngredient]
    extra: list[ParsedIngredient]
    extra_matched: list[ParsedIngredient]

    @property
    def to_buy_display(self) -> list[ParsedIngredient]:
        """UI 표시용 — 추가 구매 1~2개일 때만 전부 표시, 그 외는 빈 목록."""
        n = len(self.to_buy)
        if n == 0 or n > 2:
            return []
        return list(self.to_buy)


def _match_key(item: ParsedIngredient) -> str | None:
    return item.yolo_class or item.canonical or item.name


def classify_ingredients(
    recipe_ingredients: str | list[ParsedIngredient],
    detected: set[str] | dict[str, int] | list[str],
    *,
    source: str = "auto",
    custom: dict[str, int] | list[str] | None = None,
) -> ClassifiedIngredients:
    """
    레시피 재료를 3구간으로 분류.

    detected: normalize_detections() 결과 dict 또는 클래스 집합
    """
    if isinstance(detected, dict):
        owned_classes = set(detected.keys())
    elif isinstance(detected, set):
        owned_classes = detected
    else:
        owned_classes = normalize_to_set(detected)

    if isinstance(recipe_ingredients, str):
        items = parse_ingredients(recipe_ingredients, source=source)
    else:
        items = list(recipe_ingredients)

    owned: list[ParsedIngredient] = []
    to_buy: list[ParsedIngredient] = []
    pantry: list[ParsedIngredient] = []

    seen_buy: set[str] = set()
    custom_names = custom_names_set(custom)

    for item in items:
        key = _match_key(item)
        if not key:
            continue

        if item.is_staple:
            pantry.append(item)
        elif item.yolo_class and item.yolo_class in owned_classes:
            owned.append(item)
        elif item.yolo_class:
            if item.yolo_class not in seen_buy:
                to_buy.append(item)
                seen_buy.add(item.yolo_class)

    extra_items = unmapped_recipe_items(items)
    extra_matched = [
        item for item in extra_items if custom_matches_item(custom_names, item)
    ]

    return ClassifiedIngredients(
        owned=owned,
        to_buy=to_buy,
        pantry=pantry,
        extra=extra_items,
        extra_matched=extra_matched,
    )


def scale_item_quantity(
    item: ParsedIngredient,
    original_servings: str | int | float | None,
    new_servings: int,
) -> tuple[float | None, str | None]:
    """인분 변경 시 재료 1개의 양·단위 계산 (상비·양념은 완만하게 스케일)."""
    from core.scaler import _is_seasoning, _parse_servings

    if item.quantity is None:
        return None, item.unit

    base = _parse_servings(original_servings)
    if base <= 0:
        base = 1
    ratio = new_servings / base
    factor = ratio**0.7 if (_is_seasoning(item) or item.is_staple) else ratio
    return round(item.quantity * factor, 2), item.unit


def format_amount_display(quantity: float | None, unit: str | None) -> str:
    """UI용 재료량 문자열."""
    if quantity is None and not unit:
        return "기호에 따라"
    if quantity is None:
        return unit or "기호에 따라"
    qty_text = str(int(quantity)) if quantity == int(quantity) else str(quantity)
    if unit:
        return f"{qty_text} {unit}"
    return qty_text
