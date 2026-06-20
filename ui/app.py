"""냉장고 AI — Streamlit UI (7단계)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import streamlit as st

from core.recipe_categories import (
    ALLRECIPES_CATEGORY_COUNT,
    FOODSAFETY_CATEGORY_COUNT,
    FOODSAFETY_CATEGORY_HELP,
    RECIPE_SOURCE_OPTIONS,
    UI_NONE,
    allrecipes_category_options,
    foodsafety_category_options,
)
from core.ingredient_parser import ParsedIngredient
from core.pantry import format_amount_display, scale_item_quantity
from ui.api_client import ApiError, DEFAULT_API_URL, get_recipe, health, predict, scale_recipe, search_recipes
from ui.filter_counts import category_counts, diet_combo_count, diet_counts, source_counts
from ui.labels import load_ko_labels

st.set_page_config(
    page_title="냉장고 AI",
    page_icon="🧊",
    layout="wide",
)

KO = load_ko_labels()

DIET_OPTIONS = [
    "vegetarian",
    "vegan",
    "dairy-free",
    "high-protein",
    "low-carb",
    "low-fat",
    "sugar-free",
]
DIET_KO = {
    "vegetarian": "채식",
    "vegan": "비건",
    "dairy-free": "유제품 없음",
    "high-protein": "고단백",
    "low-carb": "저탄수화물",
    "low-fat": "저지방",
    "sugar-free": "무설탕",
}

SOURCE_UI_VALUES = [UI_NONE] + [v for v, _ in RECIPE_SOURCE_OPTIONS if v]
SOURCE_LABELS = {UI_NONE: "전체 (한식 + 양식)"}
SOURCE_LABELS.update({v: label for v, label in RECIPE_SOURCE_OPTIONS if v})

STEP_TITLES = [
    "1. 사진 업로드",
    "2. 재료 확인",
    "3. 레시피 종류",
    "4. 세부 카테고리",
    "5. 식단 선호",
    "6. 추천 레시피",
    "7. 레시피 상세",
]

RECIPES_PAGE_SIZE = 20


def _init_state() -> None:
    defaults = {
        "step": 1,
        "ingredients": {},
        "manual_ingredients": [],
        "custom_ingredients": {},
        "recipe_source": UI_NONE,
        "category": UI_NONE,
        "diets": [],
        "recipes": [],
        "recipe_total": 0,
        "recipe_page": 0,
        "selected_recipe": None,
        "detail": None,
        "scaled": None,
        "servings": 2,
        "api_url": os.environ.get("API_URL", DEFAULT_API_URL),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    legacy_diet = st.session_state.get("diet")
    if legacy_diet and legacy_diet != UI_NONE and not st.session_state.get("diets"):
        st.session_state.diets = [legacy_diet]


def _label(cls: str) -> str:
    return KO.get(cls, cls.replace("_", " "))


@st.cache_data
def _load_yolo_alias_index() -> dict[str, str]:
    path = Path(__file__).resolve().parent.parent / "data" / "mapping_ko.json"
    mapping = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, str] = {}
    for yolo_class, aliases in mapping.items():
        index[_normalize_ingredient_name(yolo_class)] = yolo_class
        for alias in aliases:
            index[_normalize_ingredient_name(alias)] = yolo_class
    return index


def _normalize_ingredient_name(name: str) -> str:
    return re.sub(r"\s+", "", name.strip().lower())


def _resolve_yolo_class(name: str) -> str | None:
    norm = _normalize_ingredient_name(name)
    if not norm:
        return None
    return _load_yolo_alias_index().get(norm)


def _unified_ingredient_rows(
    ing: dict[str, int],
    custom: dict[str, int],
) -> list[tuple[str, str, str, int]]:
    """(kind, key, display_name, qty) — kind: yolo | custom"""
    rows: list[tuple[str, str, str, int]] = []
    for cls, qty in sorted(ing.items(), key=lambda x: _label(x[0])):
        rows.append(("yolo", cls, _label(cls), qty))
    for name, qty in sorted(custom.items()):
        rows.append(("custom", name, name, qty))
    return rows


def _add_unified_ingredient(name: str, qty: int) -> None:
    label = name.strip()
    if not label or qty <= 0:
        return
    yolo_class = _resolve_yolo_class(label)
    if yolo_class:
        _add_ingredient(yolo_class, qty)
    else:
        _add_custom_ingredient(label, qty)


def _change_unified_qty(kind: str, key: str, delta: int) -> None:
    if kind == "yolo":
        current = int(st.session_state.ingredients.get(key, 0))
        _set_ingredient_qty(key, current + delta)
    else:
        current = int(st.session_state.custom_ingredients.get(key, 0))
        _set_custom_qty(key, current + delta)


def _remove_unified(kind: str, key: str) -> None:
    if kind == "yolo":
        _remove_ingredient(key)
    else:
        _remove_custom_ingredient(key)


def _mark_manual(cls: str) -> None:
    manual = list(st.session_state.get("manual_ingredients") or [])
    if cls not in manual:
        manual.append(cls)
    st.session_state.manual_ingredients = manual


def _add_ingredient(cls: str, qty: int) -> None:
    ing = dict(st.session_state.ingredients)
    was_new = cls not in ing
    ing[cls] = ing.get(cls, 0) + qty
    st.session_state.ingredients = ing
    if was_new:
        _mark_manual(cls)


def _remove_ingredient(cls: str) -> None:
    ing = dict(st.session_state.ingredients)
    ing.pop(cls, None)
    st.session_state.ingredients = ing
    manual = [c for c in (st.session_state.get("manual_ingredients") or []) if c != cls]
    st.session_state.manual_ingredients = manual


def _set_ingredient_qty(cls: str, qty: int) -> None:
    ing = dict(st.session_state.ingredients)
    if qty <= 0:
        ing.pop(cls, None)
        manual = [c for c in (st.session_state.get("manual_ingredients") or []) if c != cls]
        st.session_state.manual_ingredients = manual
    else:
        ing[cls] = qty
    st.session_state.ingredients = ing


def _add_custom_ingredient(name: str, qty: int) -> None:
    label = name.strip()
    if not label:
        return
    custom = dict(st.session_state.get("custom_ingredients") or {})
    custom[label] = custom.get(label, 0) + qty
    st.session_state.custom_ingredients = custom


def _remove_custom_ingredient(name: str) -> None:
    custom = dict(st.session_state.get("custom_ingredients") or {})
    custom.pop(name, None)
    st.session_state.custom_ingredients = custom


def _set_custom_qty(name: str, qty: int) -> None:
    custom = dict(st.session_state.get("custom_ingredients") or {})
    if qty <= 0:
        custom.pop(name, None)
    else:
        custom[name] = qty
    st.session_state.custom_ingredients = custom


def _has_any_ingredients() -> bool:
    return bool(st.session_state.ingredients) or bool(st.session_state.custom_ingredients)


def _custom_for_api() -> dict[str, int]:
    return dict(st.session_state.get("custom_ingredients") or {})


def _recipe_filter_params() -> tuple[str | None, str | None, list[str]]:
    source = (
        st.session_state.recipe_source
        if st.session_state.recipe_source != UI_NONE
        else None
    )
    category = (
        st.session_state.category
        if st.session_state.category != UI_NONE
        else None
    )
    diets = list(st.session_state.get("diets") or [])
    return source, category, diets


def _fetch_recipes_page(page: int) -> None:
    source, category, diets = _recipe_filter_params()
    data = search_recipes(
        st.session_state.ingredients,
        custom_ingredients=_custom_for_api(),
        source=source,
        category=category,
        diets=diets or None,
        top_k=RECIPES_PAGE_SIZE,
        offset=page * RECIPES_PAGE_SIZE,
        base=st.session_state.api_url,
    )
    st.session_state.recipes = data.get("results") or []
    st.session_state.recipe_total = int(
        data.get("total_rankable") or len(st.session_state.recipes)
    )
    st.session_state.recipe_page = page


def _recipe_page_count(total: int) -> int:
    if total <= 0:
        return 1
    return (total + RECIPES_PAGE_SIZE - 1) // RECIPES_PAGE_SIZE


def _render_recipe_pagination(page: int, total: int, key_prefix: str) -> None:
    total_pages = _recipe_page_count(total)
    if total_pages <= 1:
        return

    nav_prev, nav_info, nav_next = st.columns([1, 2, 1])
    with nav_prev:
        if st.button("← 이전", disabled=page <= 0, key=f"{key_prefix}_prev"):
            with st.spinner("레시피 불러오는 중..."):
                _fetch_recipes_page(page - 1)
                st.rerun()
    with nav_info:
        st.markdown(
            f"<div style='text-align:center;padding-top:0.4rem'>"
            f"{page + 1} / {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with nav_next:
        if st.button("다음 →", disabled=page >= total_pages - 1, key=f"{key_prefix}_next"):
            with st.spinner("레시피 불러오는 중..."):
                _fetch_recipes_page(page + 1)
                st.rerun()


def _with_count(label: str, count: int) -> str:
    return f"{label} ({count})"


def _source_radio_label(value: str | None, counts: dict[str | None, int]) -> str:
    base = SOURCE_LABELS.get(value, str(value))
    return _with_count(base, counts.get(value, 0))


def _category_radio_label(value: str, labels: dict[str, str], counts: dict[str, int]) -> str:
    base = labels.get(value, value)
    return _with_count(base, counts.get(value, 0))


def _diet_option_label(value: str, counts: dict[str, int]) -> str:
    base = DIET_KO.get(value, value)
    return _with_count(base, counts.get(value, 0))


def _toggle_diet(diet_key: str) -> None:
    diets = list(st.session_state.get("diets") or [])
    if diet_key in diets:
        st.session_state.diets = [d for d in diets if d != diet_key]
    else:
        st.session_state.diets = diets + [diet_key]


def _render_diet_toggle_buttons(dcounts: dict[str, int]) -> list[str]:
    selected = set(st.session_state.get("diets") or [])
    st.markdown("**식단 필터 (버튼으로 복수 선택)**")
    left, right = st.columns(2)
    for idx, diet_key in enumerate(DIET_OPTIONS):
        col = left if idx % 2 == 0 else right
        with col:
            label = _diet_option_label(diet_key, dcounts)
            btn_type = "primary" if diet_key in selected else "secondary"
            if st.button(
                label,
                key=f"diet_btn_{diet_key}",
                type=btn_type,
                use_container_width=True,
            ):
                _toggle_diet(diet_key)
                st.rerun()
    return list(st.session_state.get("diets") or [])


def _is_korean_recipe(source: str | None) -> bool:
    return source == "foodsafety"


def _recipe_stats_caption(r: dict) -> str:
    src_tag = "한식" if _is_korean_recipe(r.get("source")) else "양식"
    parts = [
        f"[{src_tag}]",
        f"점수 {r['score']:.3f}",
        f"재료 일치 {r['coverage']:.0%}",
        f"부족 {r['shortage']}개",
    ]
    if not _is_korean_recipe(r.get("source")):
        parts.append(f"별점 {r['rating']}")
    return " · ".join(parts)


def _recipe_subtitle(detail: dict) -> str:
    path = detail.get("cuisine_path") or ""
    if _is_korean_recipe(detail.get("source")):
        return path
    return f"별점 {detail.get('rating')} · {path}"


def _recipe_time_line(detail: dict) -> str:
    if _is_korean_recipe(detail.get("source")):
        method = (detail.get("cook_time") or "").strip()
        return f"조리방법: {method or '-'}"
    return (
        f"⏱ 준비 {detail.get('prep_time') or '-'} · "
        f"조리 {detail.get('cook_time') or '-'} · "
        f"총 {detail.get('total_time') or '-'}"
    )


def _sidebar() -> None:
    with st.sidebar:
        st.header("냉장고 AI")
        st.caption("냉장고 AI · Streamlit 데모")
        st.session_state.api_url = st.text_input(
            "API 주소",
            value=st.session_state.api_url,
        )
        if st.button("API 연결 확인"):
            try:
                info = health(st.session_state.api_url)
                st.success(
                    f"연결됨 · 레시피 {info['recipe_count']}건 · "
                    f"모델 {'로드됨' if info['model_loaded'] else '없음'}"
                )
            except Exception as exc:
                st.error(f"연결 실패: {exc}")

        st.divider()
        for i, title in enumerate(STEP_TITLES, start=1):
            mark = "▶" if st.session_state.step == i else " "
            st.text(f"{mark} {title}")
        if st.button("처음부터"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def _step_upload() -> None:
    st.title("1. 냉장고 사진 업로드")
    st.write("냉장고 안 식재료 사진을 1장 이상 올려주세요.")
    uploads = st.file_uploader(
        "이미지 선택 (jpg, png)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )
    if st.button("재료 인식하기", type="primary", disabled=not uploads):
        files = []
        for f in uploads:
            mime = f.type or "image/jpeg"
            files.append((f.name, f.getvalue(), mime))
        with st.spinner("YOLO 추론 중..."):
            try:
                result = predict(files, base=st.session_state.api_url)
                st.session_state.ingredients = result.get("ingredients") or {}
                st.session_state.manual_ingredients = []
                st.session_state.custom_ingredients = {}
                st.session_state.step = 2
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"API 오류: {exc}")


def _step_ingredients() -> None:
    st.title("2. 재료 확인")
    st.caption(
        "인식된 재료와 직접 추가한 재료를 한곳에서 관리합니다. "
        "표에서 **− / +** 로 수량을 바꾸고, **삭제**로 빼세요."
    )
    ing: dict[str, int] = dict(st.session_state.ingredients or {})
    custom: dict[str, int] = dict(st.session_state.custom_ingredients or {})

    if not _has_any_ingredients():
        st.warning("재료가 없습니다. 아래에서 추가하거나 다른 사진을 시도해 보세요.")

    rows = _unified_ingredient_rows(ing, custom)
    if rows:
        kind_count = len(rows)
        total_qty = sum(ing.values()) + sum(custom.values())
        m1, m2 = st.columns(2)
        m1.metric("재료 종류", kind_count)
        m2.metric("총 개수", total_qty)

        search = st.text_input("재료 검색", placeholder="예: 양파, 김치, 감자...")
        if search.strip():
            q = _normalize_ingredient_name(search)
            rows = [
                row
                for row in rows
                if q in _normalize_ingredient_name(row[2])
                or q in _normalize_ingredient_name(row[1])
            ]

        h1, h2, h3 = st.columns([4, 2, 1])
        h1.markdown("**재료**")
        h2.markdown("**수량**")
        h3.markdown("**삭제**")

        if not rows:
            st.info("검색 결과가 없습니다.")
        for idx, (kind, key, display, qty) in enumerate(rows):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                st.write(display)
            with c2:
                q1, q2, q3 = st.columns([1, 1, 1])
                with q1:
                    if st.button("−", key=f"ing_dec_{kind}_{idx}", use_container_width=True):
                        _change_unified_qty(kind, key, -1)
                        st.rerun()
                with q2:
                    st.markdown(
                        f"<div style='text-align:center;padding-top:0.35rem'>{qty}</div>",
                        unsafe_allow_html=True,
                    )
                with q3:
                    if st.button("+", key=f"ing_inc_{kind}_{idx}", use_container_width=True):
                        _change_unified_qty(kind, key, 1)
                        st.rerun()
            with c3:
                if st.button("삭제", key=f"ing_del_{kind}_{idx}", use_container_width=True):
                    _remove_unified(kind, key)
                    st.rerun()

    st.divider()
    st.subheader("재료 추가")
    st.caption(
        "재료 이름만 입력하세요. 양파·감자 등 **인식 목록**에 있으면 자동 연결되고, "
        "김치·두부 등 **그 외 이름**은 자유 입력으로 추가됩니다."
    )
    a1, a2, a3 = st.columns([3, 1, 1])
    with a1:
        add_name = st.text_input(
            "재료 이름",
            placeholder="예: 양파, 김치, 두부, onion",
            key="unified_add_name",
            label_visibility="collapsed",
        )
    with a2:
        add_qty = st.number_input(
            "개수",
            min_value=1,
            max_value=99,
            value=1,
            key="unified_add_qty",
            label_visibility="collapsed",
        )
    with a3:
        st.write("")
        if st.button("추가", type="primary", key="unified_add_btn", use_container_width=True):
            if not add_name.strip():
                st.warning("재료 이름을 입력해 주세요.")
            else:
                _add_unified_ingredient(add_name, int(add_qty))
                st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← 다시 업로드"):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.button(
            "다음: 레시피 종류 →",
            type="primary",
            disabled=not _has_any_ingredients(),
        ):
            st.session_state.step = 3
            st.rerun()


def _step_source() -> None:
    st.title("3. 레시피 종류")
    st.caption(
        "한식(식약처)과 양식(해외 레시피)은 **분류 방식이 다릅니다**. "
        "괄호 안 숫자는 **지금 재료로 6단계에 나올 수 있는** 레시피 수입니다."
    )
    scounts = source_counts(st.session_state.ingredients or {}, _custom_for_api())
    choice = st.radio(
        "레시피 출처",
        SOURCE_UI_VALUES,
        index=(
            SOURCE_UI_VALUES.index(st.session_state.recipe_source)
            if st.session_state.recipe_source in SOURCE_UI_VALUES
            else 0
        ),
        format_func=lambda x: _source_radio_label(x, scounts),
    )
    if choice != st.session_state.recipe_source:
        st.session_state.category = UI_NONE
    st.session_state.recipe_source = choice
    _nav(2, 4)


def _category_options() -> list[tuple[str, str]]:
    src = st.session_state.recipe_source
    if src == "foodsafety":
        return foodsafety_category_options()
    if src == "allrecipes":
        return allrecipes_category_options()
    return [(UI_NONE, "출처를 먼저 선택하세요 (또는 전체 검색)")]


def _step_category() -> None:
    st.title("4. 세부 카테고리")
    src = st.session_state.recipe_source
    if src == "foodsafety":
        st.caption(
            f"식약처 한식 — **{FOODSAFETY_CATEGORY_COUNT}개** 유형. "
            "괄호 = **현재 재료·선택 출처** 기준 추천 가능 건수."
        )
    elif src == "allrecipes":
        st.caption(
            f"해외 레시피 — **{ALLRECIPES_CATEGORY_COUNT}개** 유형. "
            "괄호 = **현재 재료·선택 출처** 기준 추천 가능 건수."
        )
    else:
        st.caption("「전체」를 고르면 카테고리 없이 모든 레시피에서 검색합니다.")

    options = _category_options()
    values = [v for v, _ in options]
    labels = {v: lbl for v, lbl in options}
    cat_counts = category_counts(
        st.session_state.ingredients or {},
        src if src != UI_NONE else None,
        _custom_for_api(),
    )
    current = st.session_state.category
    if current not in values:
        current = values[0]

    choice = st.radio(
        "세부 카테고리",
        values,
        index=values.index(current),
        format_func=lambda x: _category_radio_label(x, labels, cat_counts),
        disabled=(src == UI_NONE),
    )
    st.session_state.category = choice
    if src == "foodsafety" and choice == "일품":
        st.info(FOODSAFETY_CATEGORY_HELP["일품"])
    _nav(3, 5)


def _step_diet() -> None:
    st.title("5. 식단 · 선호")
    st.caption(
        "괄호 = 해당 옵션 **단독** 적용 시 추천 가능 건수(겹칠 수 있음). "
        "여러 개를 고르면 **모두 만족(AND)** 하는 레시피만 추천됩니다. "
        f"6단계에서는 **페이지당 {RECIPES_PAGE_SIZE}개**씩 전체 목록을 볼 수 있습니다."
    )
    dcounts = diet_counts(
        st.session_state.ingredients or {},
        st.session_state.recipe_source,
        st.session_state.category,
        _custom_for_api(),
    )
    none_count = dcounts.get(UI_NONE, 0)
    selected = _render_diet_toggle_buttons(dcounts)
    if selected:
        combo = diet_combo_count(
            st.session_state.ingredients or {},
            st.session_state.recipe_source,
            st.session_state.category,
            selected,
            _custom_for_api(),
        )
        st.info(f"현재 선택 조합: **{combo}건** 추천 가능")
    else:
        st.info(f"식단 필터 없음: **{none_count}건** 추천 가능")
    if st.button("레시피 추천 받기 →", type="primary"):
        with st.spinner("레시피 검색 중..."):
            try:
                _fetch_recipes_page(0)
                st.session_state.step = 6
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"서버 연결 오류: {exc}")
    _nav(4, None)


def _step_recipes() -> None:
    st.title("6. 추천 레시피")
    recipes = st.session_state.recipes
    total = int(st.session_state.get("recipe_total") or len(recipes))
    page = int(st.session_state.get("recipe_page") or 0)
    if not recipes:
        st.info("조건에 맞는 레시피가 없습니다. 필터를 완화해 보세요.")
        if st.button("← 필터 다시"):
            st.session_state.step = 5
            st.rerun()
        return

    start_idx = page * RECIPES_PAGE_SIZE + 1
    end_idx = min((page + 1) * RECIPES_PAGE_SIZE, total)
    st.caption(
        f"총 **{total}건** · **{start_idx}–{end_idx}**번째 표시 "
        f"(페이지당 {RECIPES_PAGE_SIZE}개)"
    )
    _render_recipe_pagination(page, total, "recipe_top")

    for r in recipes:
        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                if r.get("img_src"):
                    st.image(r["img_src"], use_container_width=True)
            with cols[1]:
                st.subheader(r["recipe_name"])
                st.caption(_recipe_stats_caption(r))
                st.caption(r.get("cuisine_path") or "")
                if r.get("missing"):
                    st.write("부족:", ", ".join(r["missing"]))
                if st.button("상세 보기", key=f"pick_{r['recipe_id']}"):
                    st.session_state.selected_recipe = r
                    st.session_state.step = 7
                    st.rerun()

    _render_recipe_pagination(page, total, "recipe_bottom")

    if st.button("← 필터 다시"):
        st.session_state.step = 5
        st.rerun()


def _step_detail() -> None:
    st.title("7. 레시피 상세")
    sel = st.session_state.selected_recipe
    if not sel:
        st.session_state.step = 6
        st.rerun()
        return

    recipe_id = sel["recipe_id"]
    try:
        detail = get_recipe(
            recipe_id,
            st.session_state.ingredients,
            custom_ingredients=_custom_for_api(),
            base=st.session_state.api_url,
        )
    except ApiError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"서버 연결 오류: {exc}")
        return

    st.session_state.detail = detail
    cols = st.columns([1, 2])
    with cols[0]:
        if detail.get("img_src"):
            st.image(detail["img_src"], use_container_width=True)
    with cols[1]:
        st.header(detail["recipe_name"])
        st.write(_recipe_time_line(detail))
        st.write(_recipe_subtitle(detail))

    orig = detail.get("servings") or "1"
    try:
        import re

        m = re.search(r"\d+", str(orig))
        default_serv = int(m.group()) if m else 2
    except (TypeError, ValueError):
        default_serv = 2

    servings = st.number_input(
        "서빙 인원",
        min_value=1,
        max_value=20,
        value=st.session_state.get("servings") or default_serv,
    )
    st.session_state.servings = servings

    orig_servings = detail.get("servings") or default_serv

    try:
        scaled = scale_recipe(recipe_id, servings, base=st.session_state.api_url)
        st.session_state.scaled = scaled
    except ApiError as exc:
        st.warning(f"인분 계산 실패: {exc}")
        scaled = st.session_state.scaled

    classified = detail.get("classified")
    if classified:
        st.subheader("재료 구분")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**🧊 냉장고 보유**")
            _classified_table(
                classified.get("owned") or [],
                orig_servings,
                servings,
            )
        with col2:
            shortage = sel.get("shortage", 0)
            missing_ids = set(sel.get("missing") or [])
            to_buy_all = classified.get("to_buy") or []
            if shortage == 0:
                to_buy = []
            elif 1 <= shortage <= 2:
                to_buy = [
                    x
                    for x in to_buy_all
                    if x.get("yolo_class") in missing_ids
                ]
                if not to_buy:
                    to_buy = to_buy_all[:shortage]
            else:
                to_buy = []
            st.markdown("**🛒 추가 구매**")
            st.caption("YOLO 30종 · 부족 1~2개")
            if to_buy:
                _classified_table(to_buy, orig_servings, servings)
            else:
                st.caption("없음")
        with col3:
            st.markdown("**🏠 상비 재료**")
            _classified_table(
                classified.get("pantry") or [],
                orig_servings,
                servings,
            )
        with col4:
            st.markdown("**📋 기타 재료**")
            st.caption("YOLO 30종 밖 · 레시피 필요")
            _extra_classified_table(
                classified.get("extra") or [],
                orig_servings,
                servings,
            )

    scaled = st.session_state.scaled
    if scaled:
        st.subheader(f"인분 {scaled['new_servings']}인 기준 전체 재료")
        st.dataframe(
            [
                {
                    "재료": row["raw_name"],
                    "양": row["quantity"] if row["quantity"] is not None else "기호에 따라",
                    "단위": row["unit"] or "",
                    "비고": "양념" if row["scale_mode"] == "seasoning" else "주재료",
                }
                for row in scaled.get("ingredients") or []
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("조리 방법")
    for i, line in enumerate(detail.get("directions") or [], start=1):
        st.write(f"{i}. {line}")

    if st.button("← 추천 목록"):
        st.session_state.step = 6
        st.rerun()


def _classified_table(
    items: list[dict],
    original_servings: str | int,
    new_servings: int,
) -> None:
    if not items:
        st.caption("없음")
        return
    rows = []
    for row in items:
        parsed = ParsedIngredient(
            name=row.get("name") or row.get("raw_name") or "",
            raw_name=row.get("raw_name") or row.get("name") or "",
            quantity=row.get("quantity"),
            unit=row.get("unit"),
            is_staple=bool(row.get("is_staple")),
        )
        qty, unit = scale_item_quantity(parsed, original_servings, new_servings)
        rows.append(
            {
                "재료": parsed.raw_name,
                "필요량": format_amount_display(qty, unit),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _extra_classified_table(
    items: list[dict],
    original_servings: str | int,
    new_servings: int,
) -> None:
    if not items:
        st.caption("없음")
        return
    rows = []
    for row in items:
        parsed = ParsedIngredient(
            name=row.get("name") or row.get("raw_name") or "",
            raw_name=row.get("raw_name") or row.get("name") or "",
            quantity=row.get("quantity"),
            unit=row.get("unit"),
            is_staple=bool(row.get("is_staple")),
        )
        qty, unit = scale_item_quantity(parsed, original_servings, new_servings)
        status = "보유(직접입력)" if row.get("custom_matched") else "필요"
        rows.append(
            {
                "재료": parsed.raw_name,
                "필요량": format_amount_display(qty, unit),
                "상태": status,
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _nav(back: int | None, forward: int | None) -> None:
    c1, c2 = st.columns(2)
    with c1:
        if back and st.button("← 이전"):
            st.session_state.step = back
            st.rerun()
    with c2:
        if forward and st.button("다음 →"):
            st.session_state.step = forward
            st.rerun()


def main() -> None:
    _init_state()
    _sidebar()
    step = st.session_state.step
    if step == 1:
        _step_upload()
    elif step == 2:
        _step_ingredients()
    elif step == 3:
        _step_source()
    elif step == 4:
        _step_category()
    elif step == 5:
        _step_diet()
    elif step == 6:
        _step_recipes()
    elif step == 7:
        _step_detail()
    else:
        st.session_state.step = 1
        st.rerun()


if __name__ == "__main__":
    main()
