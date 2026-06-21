"""30 YOLO 클래스 밖 사용자 재료 ↔ 레시피 비매핑 재료 매칭."""

from __future__ import annotations

import re

from core.ingredient_parser import ParsedIngredient, is_recipe_noise_item

EXCLUDE_UNMAPPED = re.compile(
    r"(broth|stock|bouillon|consomme|육수|멸치육수|다시마|"
    r"나누어\s*사용|기호에\s*따라|필요에\s*따라|선택\s*사항)",
    re.IGNORECASE,
)

# 부분 일치만으로는 안 잡히거나 한 글자 입력(쌀)이 건너뛰어지는 재료
RICE_EQUIV = frozenset(
    {
        "쌀",
        "멥쌀",
        "밥",
        "쌀밥",
        "현미",
        "보리",
        "찹쌀",
        "잡곡",
        "곡물",
        "현미밥",
        "보리밥",
        "백미",
        "통곡물",
    }
)
CUSTOM_EQUIV_GROUPS: tuple[frozenset[str], ...] = (RICE_EQUIV,)


def normalize_custom_name(name: str) -> str:
    s = (name or "").strip()
    if not s:
        return ""
    s = re.sub(r"\s+", "", s)
    return s.lower() if s.isascii() else s


def normalize_custom_inventory(
    custom: dict[str, int] | list[str] | None,
) -> dict[str, int]:
    if not custom:
        return {}
    if isinstance(custom, list):
        out: dict[str, int] = {}
        for raw in custom:
            key = normalize_custom_name(raw)
            if key:
                out[key] = out.get(key, 0) + 1
        return out
    out = {}
    for raw, qty in custom.items():
        key = normalize_custom_name(str(raw))
        if key:
            out[key] = out.get(key, 0) + max(1, int(qty))
    return out


def custom_names_set(custom: dict[str, int] | list[str] | None) -> set[str]:
    return set(normalize_custom_inventory(custom).keys())


def is_unmapped_requirement(item: ParsedIngredient) -> bool:
    if item.is_staple or item.yolo_class:
        return False
    if EXCLUDE_UNMAPPED.search(item.raw_name or ""):
        return False
    name = (item.name or item.raw_name or "").strip()
    if is_recipe_noise_item(name):
        return False
    return bool(name)


def unmapped_recipe_items(parsed: list[ParsedIngredient]) -> list[ParsedIngredient]:
    """레시피에서 YOLO·상비 제외 재료 (중복 raw_name 기준 1건)."""
    seen: set[str] = set()
    items: list[ParsedIngredient] = []
    for item in parsed:
        if not is_unmapped_requirement(item):
            continue
        key = normalize_custom_name(item.raw_name or item.name)
        if not key or key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def _item_tokens(item: ParsedIngredient) -> list[str]:
    tokens: list[str] = []
    for field in (item.name, item.raw_name, item.canonical):
        if not field:
            continue
        norm = normalize_custom_name(field)
        if norm and norm not in tokens:
            tokens.append(norm)
    return tokens


def _expand_custom_names(names: set[str]) -> set[str]:
    out = set(names)
    for group in CUSTOM_EQUIV_GROUPS:
        if names & group:
            out |= group
    return out


def _is_valid_custom_key(name: str) -> bool:
    if len(name) >= 2:
        return True
    if len(name) == 1 and not name.isascii():
        return any(name in group for group in CUSTOM_EQUIV_GROUPS)
    return False


def custom_matches_item(
    custom_names: set[str],
    item: ParsedIngredient,
) -> bool:
    """사용자 입력 재료명 ↔ 레시피 항목 (동의어·부분 일치 허용)."""
    if not custom_names:
        return False
    effective = _expand_custom_names(custom_names)
    item_tokens = _item_tokens(item)
    for custom in effective:
        if not _is_valid_custom_key(custom):
            continue
        for token in item_tokens:
            if custom == token:
                return True
            if custom in token or token in custom:
                return True
    return False


def count_unmapped_matched(
    items: list[ParsedIngredient],
    custom: dict[str, int] | list[str] | None,
) -> int:
    names = custom_names_set(custom)
    if not names:
        return 0
    return sum(1 for item in items if custom_matches_item(names, item))
