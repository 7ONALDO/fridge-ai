"""재료 문자열 파싱 — 영문 recipes.csv / 한식 식약처 CSV 공통."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PANTRY = ROOT / "data" / "pantry.json"
DEFAULT_MAPPING_KO = ROOT / "data" / "mapping_ko.json"
DEFAULT_MAPPING_EN = ROOT / "data" / "mapping.json"

FRACTIONS = {
    "½": 0.5,
    "¼": 0.25,
    "¾": 0.75,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "⅛": 0.125,
}

ENGLISH_UNITS = (
    r"cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|"
    r"pound|pounds|lb|lbs|ounce|ounces|oz|gram|grams|g|kilogram|kilograms|kg|"
    r"milliliter|milliliters|ml|liter|liters|l|clove|cloves|pinch|pinches|"
    r"can|cans|package|packages|pkg|head|heads|stalk|stalks|bunch|bunches|"
    r"slice|slices|sheet|sheets|stick|sticks|dash|dashes|sprig|sprigs|"
    r"medium|small|large|whole|piece|pieces"
)

KOREAN_UNITS = (
    r"g|kg|mg|ml|l|L|개|마리|줄기|쪽|큰술|작은술|컵|모|장|봉|팩|포기|송이|꼬지|인분|"
    r"온스|파운드|테이블스푼|티스푼|알|가닥|봉지|뿌리|ts|Ts|TS"
)

SECTION_SKIP = re.compile(
    r"^(●|·|\[|\]|고명|드레싱|곁들임|토핑|장식)$",
    re.IGNORECASE,
)

# 양념장/소스/식약처 섹션 — 접두어만 제거하고 뒤 재료는 파싱
SECTION_HEADER = re.compile(
    r"^(?:"
    r"필수\s*재료|"
    r"육수\s*재료|"
    r"양념장|양념|"
    r"소스|드레싱|고명|곁들임|토핑|장식|"
    r"육수"
    r")\s*[:：]\s*",
    re.IGNORECASE,
)

# 조리 설명 패턴 (재료명 아닌 경우) — "껍질을 벗기고 씨를 제거한" 등
_PREP_NOTE = re.compile(
    r"(고$|어서$|아서$|하여$|해서$|한다$|하고$|거나$|게$|도록$|며$|면서$|어$|아$|한$|는$|된$|게\s*썬$|게\s*다진$)",
    re.IGNORECASE,
)

KO_QTY = r"[\d½¼¾⅓⅔⅛]+(?:\.\d+)?(?:\s*/\s*\d+)?"

_QTY_PAREN_INNER = re.compile(
    rf"^\d+\.?\d*\s*({KOREAN_UNITS})$",
    re.IGNORECASE,
)


def _strip_trailing_paren_note(s: str) -> str:
    """끝 괄호 중 (40g) 같은 분량은 유지, (선택 사항) 등 메모만 제거."""
    while True:
        m = re.search(r"\s*\(([^)]*)\)\s*$", s)
        if not m:
            break
        inner = m.group(1).strip()
        if _QTY_PAREN_INNER.match(inner):
            break
        if re.match(r"^[\d½¼¾⅓⅔⅛]", inner):
            break
        if re.search(rf"{KO_QTY}\s*{KOREAN_UNITS}", inner, re.IGNORECASE):
            break
        s = s[: m.start()].strip()
    return s

KO_PREP_ONLY = re.compile(
    r"^(?:다진\s*것|썬\s*것|잘게\s*썬\s*것|갈은\s*것|즙을\s*짠\s*것|"
    r".*,\s*다진\s*것|.*,\s*썬\s*것)$",
    re.IGNORECASE,
)

KO_META_NOTE = re.compile(
    r"^(?:"
    r"나누(?:어|)\s*(?:사용|쓸|기)|"
    r"또는\s*(?:기호|필요)(?:에|시)?\s*따라(?:\s*더)?(?:\s*추가)?(?:\s*가능)?|"
    r"(?:기호|필요)(?:에|시)?\s*따라(?:\s*더)?(?:\s*추가)?(?:\s*가능)?|"
    r"더\s*추가(?:\s*가능)?|"
    r"필요시\s*더\s*추가|"
    r"선택\s*사항|"
    r"장식(?:용|을\s*위한)(?:\s*추가)?|"
    r"요리용\s*스프레이|"
    r"질감을\s*조절하기\s*위한"
    r")$",
    re.IGNORECASE,
)

_KO_CUT_INSTRUCTION = re.compile(
    r"^(?:"
    r"한\s*입\s*크기(?:로)?\s*(?:잘(?:라|)|썰(?:어|)|찢(?:어|은)?|다져|부숴|갈아)(?:서|\s*것)?|"
    r"(?:얇|잘|굵|곱|대충|작)?게\s*(?:잘(?:라|)|썰(?:어|)|찢(?:어|은)?)(?:서|것)?|"
    r".*크기(?:로)?\s*(?:잘(?:라|)|썰(?:어|)|찢(?:어|은)?)(?:서|것|기)?|"
    r"심\s*제거(?:하고|한)?\s*작은\s*크기(?:로)?\s*잘(?:라|)기|"
    r"조각(?:으로)?\s*나누(?:기|)|"
    r"잘라낸|"
    r"나누(?:기|)"
    r")$",
    re.IGNORECASE,
)


def _is_ko_meta_note(raw: str) -> bool:
    text = raw.strip()
    if not text:
        return True
    if text in (
        "또는 기호에 따라",
        "기호에 따라",
        "또는 기호에 따라 더 추가",
        "기호에 따라 더 추가",
        "또는 기호에 따라 더",
        "더 추가 가능",
        "필요시 더 추가",
        "나누어 사용",
        "나누기",
        "주스",
    ):
        return True
    return bool(KO_META_NOTE.match(text))


_KO_PREP_STANDALONE = re.compile(
    r"^(?:"
    r"물기를\s*제거한\s*것|"
    r"물기를\s*뺀\s*것|"
    r"깍둑\s*썰기한\s*것|"
    r"깍둑썰기한\s*것|"
    r"부드럽게\s*한\s*것|"
    r"가볍게\s*휘(?:저|진)(?:은)?\s*것|"
    r"해동(?:한|된)\s*것|"
    r"녹인\s*것|"
    r"슬라이스한\s*것|"
    r"4등분한\s*것|"
    r"다진\s*것|"
    r"썬\s*것|"
    r"갈은\s*것|"
    r"간\s*것|"
    r"즙을\s*짠\s*것|"
    r"나누어\s*쓸\s*것|"
    r"물기를\s*뺀|"
    r"물기\s*제거|"
    r"깍둑\s*썰기|"
    r"깍둑썰기"
    r")(?:\s*\([^)]*\))?$",
    re.IGNORECASE,
)


def _normalize_ko_item_text(raw: str) -> str:
    """번역 재료 끝의 '또는 기호에 따라'·'(선택 사항)' 등 분량·메모 제거."""
    s = raw.strip().rstrip(".")
    s = _strip_trailing_paren_note(s)
    s = re.sub(r"^기호에\s*따라\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^필요(?:에|시)?\s*따라\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^또는\s+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*,?\s*(?:또는\s*)?기호에\s*따라\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(
        r"\s*,?\s*(?:또는\s*)?(?:기호|필요)(?:에|시)?\s*따라(?:\s*더)?(?:\s*추가)?(?:\s*가능)?\s*$",
        "",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r"\s*,?\s*맛에\s*따라\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*,?\s*필요(?:에)?\s*따라\s*$", "", s, flags=re.IGNORECASE)
    if " - " in s:
        head, tail = [p.strip() for p in s.split(" - ", 1)]
        if re.match(
            r"^(?:한\s*입|껍질|씨(?:를)?|심|잘게|얇게|굵게|곱게|작게|물기|"
            r"다진|썬|갈|깍둑|4등분|반으로|부드|간)",
            tail,
            re.IGNORECASE,
        ):
            s = head
    if ", " in s:
        head, tail = [p.strip() for p in s.rsplit(", ", 1)]
        if _is_ko_prep_fragment(tail) or _is_ko_meta_note(tail):
            s = head
    return s.strip()


_KO_PREP_ADV = r"(?:잘게|굵게|곱게|대충|얇게|작게|가볍게)"
_KO_PREP_VERB = (
    r"(?:다진|썬|갈|푼|부순|으깬|구운|찢(?:은)?|풀어놓(?:은)?|헹군|"
    r"깍둑(?:썰기)?|슬라이스(?:한)?|채\s*썬|4등분(?:한)?|"
    r"반으로\s*자른?|조각으로\s*자른?|즙을\s*(?:낸|짠)|"
    r"부드럽게\s*한|가볍게\s*휘(?:저|진)(?:은)?|녹(?:인)?|벗긴|제거(?:한)?|부서진|간)"
)
_KO_PREP_TAIL = (
    rf"(?:(?:{_KO_PREP_ADV}\s+)?{_KO_PREP_VERB})"
    rf"(?:\s+(?:(?:{_KO_PREP_ADV}\s+)?{_KO_PREP_VERB}))*"
    rf"(?:\s*것)?"
)

_KO_PREP_CLAUSE = re.compile(
    rf"^(?:"
    rf"씨(?:를)?\s*제거(?:하고|한)?(?:\s*후)?(?:\s+{_KO_PREP_TAIL})?|"
    rf"껍질을\s*벗기(?!지\s*않)(?:고|한)?"
    rf"(?:\s*[,，]?\s*(?:씨(?:를)?\s*제거(?:하고|한)?(?:\s*후)?|"
    rf"심을\s*제거(?:하고|한)?(?:\s*후)?))?"
    rf"(?:\s+{_KO_PREP_TAIL})?|"
    rf"심을\s*제거(?:하고|한)?(?:\s*후)?(?:\s+{_KO_PREP_TAIL})?|"
    rf"물기(?:를)?\s*(?:제거(?:하고|한)?|뺀(?:\s*헹군)?)(?:\s+{_KO_PREP_TAIL})?|"
    rf"줄기(?:를)?\s*제거(?:하고\s*4등분)?|"
    rf"물기(?:를)?\s*제거(?:하고|한)?\s*주스(?:는)?\s*따로\s*보관|"
    rf"해동(?:했지만\s*여전히\s*차가운\s*상태)?(?:\s*후\s*물기\s*제거)?|"
    rf"강판에\s*간\s*것|"
    rf"나누어\s*(?:쓸|사용)|"
    rf"{_KO_PREP_TAIL}|"
    rf"다진|"
    rf"깍둑\s*썰기|"
    rf"깍둑썰기|"
    rf"씨\s*제거(?:\s*후\s*다진\s*것)?|"
    rf"반으로\s*자르고\s*씨\s*제거|"
    rf"조각으로\s*자른?"
    rf")$",
    re.IGNORECASE,
)


def _is_ko_prep_fragment(text: str) -> bool:
    """쉼표로 잘린 전처리·손질 구절 (재료명 없음)."""
    t = re.sub(r"\s*\([^)]*\)\s*$", "", text.strip()).strip()
    if not t:
        return True
    if _KO_PREP_CLAUSE.match(t):
        return True
    if re.search(r"\s것$", t) and len(t) <= 55:
        if re.match(r"^씨(?:를)?\s*제거", t):
            return True
        if re.match(
            r"^(?:물기|깍둑|껍질|줄기|해동|심|가볍|얇|잘|굵|곱|대충|작|"
            r"4등분|반으로|푼|부순|으깬|구운|찢|풀|헹|녹|부드|슬라이|"
            r"다진|썬|갈|채|즙|조각|나누|웨지|강판|대충)",
            t,
        ):
            return True
    if len(t) <= 50 and re.match(
        r"^(?:씨(?:를)?\s*제거|껍질을\s*벗기(?!지\s*않)|물기|줄기\s*제거|"
        r"해동|심을\s*제거|녹(?:인)?|나누어|주스(?:는)?\s*따로|"
        r"반으로\s*자르고\s*씨\s*제거|조각으로\s*자른?|씻어서)",
        t,
    ):
        return True
    if re.match(
        r"^(?:스트립|큐브|웨지|슬라이스|조각)(?:으로|로)?(?:\s+(?:모양|크기))?"
        r"(?:으로|로)?\s+(?:썬|자른)(?:\s*것)?$",
        t,
        re.IGNORECASE,
    ):
        return True
    return False

# 재료명 뒤 수량+단위 붙임: "으깬 붉은 고추 조각 ¼작은술", "버터15g"
KO_ITEM_NAME_QTYGLUE = re.compile(
    rf"^(.+?)\s*({KO_QTY})({KOREAN_UNITS})$",
    re.IGNORECASE,
)

# 식약처 API: 밥 180, 배추김치(줄기부분) 30 — 단위 g 생략
KO_ITEM_QTY_BARE = re.compile(
    rf"^(.+?)\s+({KO_QTY})$",
    re.IGNORECASE,
)


def is_recipe_noise_item(raw: str) -> bool:
    """재료가 아닌 조리 메모·분량 안내 (파서·기타 재료 필터 공통)."""
    text = _normalize_ko_item_text(raw or "")
    if not text:
        return True
    if _is_ko_meta_note(text):
        return True
    if re.match(r"^.+나누(?:어|)\s*(?:사용|쓸)$", text) and len(text) <= 45:
        return True
    if KO_PREP_ONLY.match(text):
        return True
    if _KO_PREP_STANDALONE.match(text):
        return True
    if _KO_PREP_CLAUSE.match(text):
        return True
    if _is_ko_prep_fragment(text):
        return True
    if _KO_CUT_INSTRUCTION.match(text):
        return True
    if text in ("다진", "깍둑썰기", "깍둑 썰기", "슬라이스", "썬", "갈은", "푼", "간 것"):
        return True
    if (
        text.endswith("로 자른 것")
        or text.endswith("로 썬")
        or re.match(r"^\d+인치\s", text)
    ):
        return True
    # "껍질을 벗기고 …", "물기를 제거하고 …" 등 짧은 전처리 구절
    if len(text) <= 40 and not re.match(r"^[\d½¼]", text):
        if re.search(r"(?:한|된|진|간)\s*것(?:\s*\(|$)", text):
            if re.match(
                r"^(?:물기|깍둑|껍질|씨를|해동|녹|부드|가볍|슬라이|4등분|반으로|"
                r"조각으로|얇게|잘게|다진|썬|갈|즙|나누|웨지|강판|간)",
                text,
            ):
                return True
    if not re.search(r"\d", text) and _PREP_NOTE.search(text):
        return True
    return False


KO_ITEM = re.compile(
    rf"^(.+?)\s+({KO_QTY})\s*({KOREAN_UNITS})(?:\([^)]*\))?$",
    re.IGNORECASE,
)

# 번역된 재료 형식: "2컵 시금치", "1개 감자"
KO_ITEM_NUM_FIRST = re.compile(
    rf"^({KO_QTY})\s*({KOREAN_UNITS})\s+(.+)$",
    re.IGNORECASE,
)

# 번역 재료: "2개의 구운 빨간 피망"
KO_ITEM_NUM_FIRST_POSSESSIVE = re.compile(
    rf"^({KO_QTY})개(?:의)?\s+(.+)$",
    re.IGNORECASE,
)

# 번역된 재료 (단위 없음): "1 후유 감"
KO_ITEM_NUM_FIRST_NO_UNIT = re.compile(
    r"^(\d+\.?\d*)\s+([가-힣].+)$",
)

# 식약처 API: 돼지고기(70g), 대추(3알) — 이름에 숫자·괄호 없음
KO_ITEM_NAME_PARENS = re.compile(
    rf"^([^(\d]+?)\s*\(({KO_QTY})\s*({KOREAN_UNITS})\)\s*$",
    re.IGNORECASE,
)

# 식약처 API: 닭고기(가슴살, 120g) — 괄호 안 부위·분량
KO_ITEM_PARENS_COMPLEX = re.compile(
    rf"^(.+?)\s*\([^)]*?({KO_QTY})\s*({KOREAN_UNITS})\)\s*$",
    re.IGNORECASE,
)

# 식약처 API: 식초 약간, 통깨 약간
KO_ITEM_TO_TASTE = re.compile(
    r"^(.+?)\s+(약간|조금|적당(?:량|히)?)$",
    re.IGNORECASE,
)

# 식약처 API: 연두부 75g(3/4모) — 괄호 안은 집기량, 앞 숫자·단위 사용
KO_ITEM_WEIGHT_EXTRA = re.compile(
    rf"^(.+?)\s+(\d+\.?\d*)\s*({KOREAN_UNITS})\([^)]+\)\s*$",
    re.IGNORECASE,
)

EN_ITEM = re.compile(
    rf"^(?P<qty>[\d½¼¾⅓⅔⅛]+(?:\s+\d+/\d+)?(?:\s*-\s*[\d½¼¾]+)?)\s+"
    rf"(?P<unit>(?:\(\s*[^)]+\s*\))|(?:{ENGLISH_UNITS}))\s+"
    rf"(?P<name>.+)$",
    re.IGNORECASE,
)

EN_ITEM_PARENS = re.compile(
    r"^(?P<outer>[\d½¼¾⅓⅔⅛]+(?:\s+\d+/\d+)?)\s+"
    r"\(\s*(?P<inner_qty>[\d.]+\s*[\w-]+)\s*\)\s+"
    r"(?P<name>.+)$",
    re.IGNORECASE,
)

EN_ITEM_QTY_ONLY = re.compile(
    rf"^(?P<qty>[\d½¼¾⅓⅔⅛]+(?:\s+\d+/\d+)?)\s+(?P<name>.+)$",
    re.IGNORECASE,
)


@dataclass
class ParsedIngredient:
    name: str
    raw_name: str
    quantity: float | None = None
    unit: str | None = None
    is_staple: bool = False
    yolo_class: str | None = None
    canonical: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.canonical is None:
            self.canonical = self.yolo_class or self.name


def load_pantry_aliases(path: Path | None = None) -> dict[str, list[str]]:
    """pantry.json → {canonical_id: [aliases]}"""
    path = path or DEFAULT_PANTRY
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {item: [item] for item in data}
    return {str(k): [str(a) for a in v] for k, v in data.items()}


def load_mapping_ko(path: Path | None = None) -> dict[str, list[str]]:
    path = path or DEFAULT_MAPPING_KO
    return json.loads(path.read_text(encoding="utf-8"))


def load_mapping_en(path: Path | None = None) -> dict[str, list[str]]:
    path = path or DEFAULT_MAPPING_EN
    return json.loads(path.read_text(encoding="utf-8"))


def _build_alias_index(mapping: dict[str, list[str]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for yolo_class, aliases in mapping.items():
        index[yolo_class.lower()] = yolo_class
        for alias in aliases:
            index[alias.lower().strip()] = yolo_class
    return index


def _build_pantry_index(pantry: dict[str, list[str]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for canonical, aliases in pantry.items():
        index[canonical.lower()] = canonical
        for alias in aliases:
            index[alias.lower().strip()] = canonical
    return index


def _parse_quantity(text: str) -> float | None:
    text = text.strip()
    if not text:
        return None
    total = 0.0
    rest = text
    for frac, val in FRACTIONS.items():
        if frac in rest:
            total += val
            rest = rest.replace(frac, " ")
    rest = rest.strip()
    if rest:
        if "/" in rest:
            parts = rest.split()
            for part in parts:
                if "/" in part:
                    num, den = part.split("/", 1)
                    try:
                        total += float(num) / float(den)
                    except ValueError:
                        return None
                else:
                    try:
                        total += float(part)
                    except ValueError:
                        return None
        else:
            try:
                total += float(rest)
            except ValueError:
                return None if total == 0 else total
    return total if total else None


def _normalize_token(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\bs\b$", "", text).strip()
    return text


_EN_NEW_INGREDIENT = re.compile(
    r"^[\d½¼¾⅓⅔⅛]|"
    r"^\d+\s*\(|"
    r"^salt\b",
    re.IGNORECASE,
)


def _matches_korean_ingredient_pattern(part: str) -> bool:
    """한 줄 재료 조각이 독립 항목으로 파싱 가능한 형식인지."""
    return bool(
        KO_ITEM.match(part)
        or KO_ITEM_NAME_PARENS.match(part)
        or KO_ITEM_PARENS_COMPLEX.match(part)
        or KO_ITEM_WEIGHT_EXTRA.match(part)
        or KO_ITEM_NAME_QTYGLUE.match(part)
        or KO_ITEM_QTY_BARE.match(part)
        or KO_ITEM_NUM_FIRST.match(part)
        or KO_ITEM_NUM_FIRST_POSSESSIVE.match(part)
        or KO_ITEM_TO_TASTE.match(part)
    )


def _looks_like_new_korean_ingredient(part: str) -> bool:
    """쉼표로 잘린 조각이 새 재료 항목의 시작인지."""
    part = part.strip().rstrip(".")
    if not part:
        return False
    if _is_ko_meta_note(part) or _is_ko_prep_fragment(part):
        return False
    if is_recipe_noise_item(part):
        return False
    if re.match(rf"^{KO_QTY}", part):
        return True
    if _matches_korean_ingredient_pattern(part):
        return True
    # 괄호·분량이 포함된 미매칭 조각 (인삼(1뿌리) 등)
    if re.search(rf"\([^)]*{KO_QTY}", part):
        return True
    if re.search(rf"(?:^|\s){KO_QTY}\s*{KOREAN_UNITS}", part, re.IGNORECASE):
        return True
    if re.search(rf"{KO_QTY}\s*{KOREAN_UNITS}\s*$", part, re.IGNORECASE):
        return True
    # 분량 없는 짧은 재료명 (고명·채소 등)
    if not re.search(r"\d", part) and len(part) <= 30 and not _PREP_NOTE.search(part):
        return True
    return False


def _split_korean_ingredients(text: str) -> list[str]:
    """한 줄 한국어 재료 목록 — 손질·분량 메모는 앞 재료에 병합."""
    text = text.strip()
    if not text:
        return []
    raw_parts = _split_outside_parens(text, ",")
    merged: list[str] = []
    buf = ""
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if buf and not _looks_like_new_korean_ingredient(part):
            buf = f"{buf}, {part}"
        elif buf:
            merged.append(buf)
            buf = part
        else:
            buf = part
    if buf:
        merged.append(buf)
    return merged


def _looks_like_new_english_ingredient(part: str) -> bool:
    """쉼표로 잘린 조각이 새 재료 항목의 시작인지 (Allrecipes 한 줄 목록용)."""
    part = part.strip()
    if not part:
        return False
    if _EN_NEW_INGREDIENT.match(part):
        return True
    return bool(EN_ITEM.match(part) or EN_ITEM_PARENS.match(part) or EN_ITEM_QTY_ONLY.match(part))


def _split_english_ingredients(text: str) -> list[str]:
    """
    영문 레시피 재료 문자열 분리.

    Allrecipes 등은 한 줄에 쉼표로 이어진 경우가 많아,
    모든 쉼표가 아니라 **새 재료가 시작하는 쉼표**에서만 나눈다.
    """
    text = text.strip()
    if not text:
        return []
    raw_parts = _split_outside_parens(text, ",")
    merged: list[str] = []
    buf = ""
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if buf and _looks_like_new_english_ingredient(part):
            merged.append(buf)
            buf = part
        else:
            buf = f"{buf}, {part}" if buf else part
    if buf:
        merged.append(buf)
    return merged


def _split_outside_parens(text: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
        if ch == sep and depth == 0:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _strip_section_prefix(text: str) -> str:
    text = SECTION_HEADER.sub("", text.strip()).strip()
    text = re.sub(r"^재료\s+", "", text, flags=re.IGNORECASE)
    # 식약처 소분류: "그린매쉬드포테이토 :", "멸치육수 :"
    text = re.sub(r"^[^:：\d]{2,40}[:：]\s*", "", text)
    return text.strip()


def _clean_korean_line(line: str) -> str | None:
    line = line.strip()
    if not line:
        return None
    line = re.sub(r"^[●·•\u2022\[]+", "", line).strip()
    line = re.sub(r"^(?:\[\s*)?\d+인분\s*\]?\s*", "", line)
    line = re.sub(r"^\d+\.\s*", "", line)
    line = _strip_section_prefix(line)
    if not line:
        return None
    if line.endswith(":"):
        return None
    if SECTION_SKIP.match(line) and not re.search(r"\d", line):
        return None
    return line or None


def _parse_korean_item(raw: str) -> ParsedIngredient | None:
    raw = _normalize_ko_item_text(raw)
    if not raw:
        return None

    if is_recipe_noise_item(raw):
        return None

    m = KO_ITEM_NAME_PARENS.match(raw)
    if m:
        name, qty, unit = m.group(1).strip(), m.group(2), m.group(3)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    m = KO_ITEM_WEIGHT_EXTRA.match(raw)
    if m:
        name, qty, unit = m.group(1).strip(), m.group(2), m.group(3)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    m = KO_ITEM_PARENS_COMPLEX.match(raw)
    if m:
        name, qty, unit = m.group(1).strip(), m.group(2), m.group(3)
        inner = re.search(r"\(([^)]*)\)\s*$", raw)
        raw_name = f"{name}({inner.group(1)})" if inner else name
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=raw_name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    m = KO_ITEM.match(raw)
    if m:
        name, qty, unit = m.group(1).strip(), m.group(2), m.group(3)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    # 번역된 재료 형식: "2컵 대충 썬 시금치", "3큰술 석류 씨"
    m = KO_ITEM_NUM_FIRST.match(raw)
    if m:
        qty, unit, name = m.group(1), m.group(2), m.group(3).strip()
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    m = KO_ITEM_NUM_FIRST_POSSESSIVE.match(raw)
    if m:
        qty, name = m.group(1), m.group(2).strip()
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit="개",
        )

    # "재료명 ¼작은술" / "버터15g" (수량·단위 사이 공백 없음)
    m = KO_ITEM_NAME_QTYGLUE.match(raw)
    if m:
        name, qty, unit = m.group(1).strip(), m.group(2), m.group(3)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=unit,
        )

    # 식약처 API: 밥 180 — g 생략
    m = KO_ITEM_QTY_BARE.match(raw)
    if m:
        name, qty = m.group(1).strip(), m.group(2)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit="g",
        )

    # 번역된 재료 (단위 없음): "1 후유 감"
    m = KO_ITEM_NUM_FIRST_NO_UNIT.match(raw)
    if m:
        qty, name = m.group(1), m.group(2).strip()
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(qty),
            unit=None,
        )

    m = KO_ITEM_TO_TASTE.match(raw)
    if m:
        name, unit = m.group(1).strip(), m.group(2)
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=None,
            unit=unit,
        )

    # "재료명" only (고명 등) — 조리 메모·분량 안내는 제외
    name = re.sub(r"\([^)]*\)", "", raw).strip()
    if is_recipe_noise_item(name):
        return None
    if len(name) < 2:
        return None
    return ParsedIngredient(name=_normalize_token(name), raw_name=name)


def _parse_english_item(raw: str) -> ParsedIngredient | None:
    raw = raw.strip()
    if not raw or raw.lower().startswith("optional"):
        return None

    m = EN_ITEM_PARENS.match(raw)
    if m:
        inner = m.group("inner_qty").strip()
        inner_parts = inner.split(None, 1)
        inner_qty = _parse_quantity(inner_parts[0])
        inner_unit = inner_parts[1] if len(inner_parts) > 1 else None
        name = m.group("name").strip()
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=inner_qty or _parse_quantity(m.group("outer")),
            unit=inner_unit,
        )

    m = EN_ITEM.match(raw)
    if m:
        unit = m.group("unit").strip("() ")
        name = m.group("name").strip()
        return ParsedIngredient(
            name=_normalize_token(name),
            raw_name=name,
            quantity=_parse_quantity(m.group("qty")),
            unit=unit,
        )

    m = EN_ITEM_QTY_ONLY.match(raw)
    if m:
        return ParsedIngredient(
            name=_normalize_token(m.group("name")),
            raw_name=m.group("name").strip(),
            quantity=_parse_quantity(m.group("qty")),
            unit=None,
        )

    return ParsedIngredient(name=_normalize_token(raw), raw_name=raw)


def _parse_structured_list(text: str) -> list[ParsedIngredient] | None:
    text = text.strip()
    if not text.startswith("["):
        return None
    try:
        items = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None
    if not isinstance(items, list):
        return None

    parsed: list[ParsedIngredient] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        qty_raw = str(item.get("quantity", "")).strip()
        qty = _parse_quantity(qty_raw) if qty_raw else None
        unit = str(item.get("unit", "")).strip() or None
        parsed.append(
            ParsedIngredient(
                name=_normalize_token(name),
                raw_name=name,
                quantity=qty,
                unit=unit,
            )
        )
    return parsed


def resolve_parse_source(
    db_source: str,
    ingredients: str,
    directions: str = "",
) -> str:
    """CSV ``source`` + 본문 언어로 재료 파서 모드 결정."""
    if db_source == "foodsafety":
        return "korean"
    blob = f"{ingredients}\n{directions}"
    if re.search(r"[가-힣]", blob):
        return "korean"
    return "english"


def _detect_source(text: str, source: str) -> str:
    if source != "auto":
        return source
    if re.search(r"[가-힣]", text):
        return "korean"
    if text.strip().startswith("["):
        return "structured"
    return "english"


def parse_ingredients(
    text: str,
    *,
    source: str = "auto",
    pantry: dict[str, list[str]] | None = None,
    mapping_en: dict[str, list[str]] | None = None,
    mapping_ko: dict[str, list[str]] | None = None,
) -> list[ParsedIngredient]:
    """재료 문자열 → ParsedIngredient 리스트."""
    if not text or not str(text).strip():
        return []

    pantry = pantry if pantry is not None else load_pantry_aliases()
    mapping_en = mapping_en if mapping_en is not None else load_mapping_en()
    mapping_ko = mapping_ko if mapping_ko is not None else load_mapping_ko()

    pantry_idx = _build_pantry_index(pantry)
    yolo_idx = _build_alias_index({**mapping_en, **mapping_ko})

    src = _detect_source(text, source)
    structured = _parse_structured_list(text)
    if structured is not None:
        items = structured
    elif src == "korean":
        items = []
        for line in text.splitlines():
            cleaned = _clean_korean_line(line)
            if not cleaned:
                continue
            for part in _split_korean_ingredients(cleaned):
                for sub in _split_outside_parens(part, "·"):
                    sub = _strip_section_prefix(sub.strip())
                    if not sub:
                        continue
                    if SECTION_SKIP.match(sub) and not re.search(r"\d", sub):
                        continue
                    parsed = _parse_korean_item(sub)
                    if parsed:
                        items.append(parsed)
    else:
        items = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for part in _split_english_ingredients(line):
                parsed = _parse_english_item(part)
                if parsed:
                    items.append(parsed)

    return _finalize_parsed_items(
        items,
        pantry=pantry,
        pantry_idx=pantry_idx,
        yolo_idx=yolo_idx,
    )


def _finalize_parsed_items(
    items: list[ParsedIngredient],
    *,
    pantry: dict[str, list[str]] | None = None,
    pantry_idx: dict[str, str] | None = None,
    yolo_idx: dict[str, str] | None = None,
) -> list[ParsedIngredient]:
    pantry = pantry if pantry is not None else load_pantry_aliases()
    pantry_idx = pantry_idx or _build_pantry_index(pantry)
    if yolo_idx is None:
        yolo_idx = _build_alias_index(
            {**load_mapping_en(), **load_mapping_ko()}
        )
    for item in items:
        token = item.raw_name or item.name
        embedded = _find_embedded_pantry(token, pantry_idx)
        if len(embedded) >= 2:
            item.yolo_class = None
            item.is_staple = False
        else:
            item.yolo_class = match_yolo_class(item.name, yolo_idx)
            pantry_key = match_pantry(item.name, pantry_idx) or match_pantry(
                item.raw_name, pantry_idx
            )
            item.is_staple = pantry_key is not None
            if pantry_key and not item.yolo_class:
                item.canonical = pantry_key
    return _expand_embedded_staples(items, pantry, pantry_idx)


YOLO_FAMILY: dict[str, frozenset[str]] = {
    "beef": frozenset({"beef", "ground_beef"}),
    "ground_beef": frozenset({"beef", "ground_beef"}),
    "chicken": frozenset({"chicken", "chicken_breast"}),
    "chicken_breast": frozenset({"chicken", "chicken_breast"}),
    "cheese": frozenset({"cheese", "goat_cheese"}),
    "goat_cheese": frozenset({"cheese", "goat_cheese"}),
    "potato": frozenset({"potato", "sweet_potato"}),
    "sweet_potato": frozenset({"potato", "sweet_potato"}),
}


def _yolo_family(yolo_class: str) -> frozenset[str]:
    return YOLO_FAMILY.get(yolo_class, frozenset({yolo_class}))


def _alias_in_directions(alias: str, text: str) -> bool:
    alias = alias.strip()
    if len(alias) < 2:
        return False
    if re.search(r"[가-힣]", alias):
        return alias in text
    return bool(
        re.search(
            rf"(?<![a-z]){re.escape(alias.lower())}(?![a-z])",
            text.lower(),
        )
    )


def _collect_parsed_coverage(
    items: list[ParsedIngredient],
    pantry_idx: dict[str, str],
) -> tuple[set[str], set[str], set[str]]:
    yolo_seen: set[str] = set()
    pantry_seen: set[str] = set()
    name_tokens: set[str] = set()
    for item in items:
        if item.yolo_class:
            yolo_seen |= _yolo_family(item.yolo_class)
        pk = match_pantry(item.name, pantry_idx) or match_pantry(
            item.raw_name, pantry_idx
        )
        if pk:
            pantry_seen.add(pk)
        if item.canonical and item.is_staple:
            pantry_seen.add(item.canonical)
        for field in (item.raw_name, item.name):
            if not field:
                continue
            clean = re.sub(r"\s*\(조리법\)\s*", "", field)
            name_tokens.add(_normalize_token(clean))
    return yolo_seen, pantry_seen, name_tokens


def _build_direction_scan_terms(
    mapping_en: dict[str, list[str]],
    mapping_ko: dict[str, list[str]],
    pantry: dict[str, list[str]],
) -> list[tuple[str, str, str]]:
    """(별칭, kind=yolo|pantry, target) — 긴 별칭 우선."""
    terms: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for cls, aliases in {**mapping_en, **mapping_ko}.items():
        for alias in aliases:
            key = alias.strip().lower()
            if len(key) < 2 or key in seen:
                continue
            seen.add(key)
            terms.append((alias.strip(), "yolo", cls))
    for canonical, aliases in pantry.items():
        for alias in aliases:
            key = alias.strip().lower()
            if len(key) < 2 or key in seen:
                continue
            seen.add(key)
            terms.append((alias.strip(), "pantry", canonical))
    terms.sort(key=lambda x: -len(x[0]))
    return terms


def supplement_from_directions(
    parsed: list[ParsedIngredient],
    directions: str,
    *,
    source: str = "auto",
    pantry: dict[str, list[str]] | None = None,
    mapping_en: dict[str, list[str]] | None = None,
    mapping_ko: dict[str, list[str]] | None = None,
) -> list[ParsedIngredient]:
    """재료 필드에 없고 조리법에만 등장하는 항목을 사전 기반으로 보강 (ML 없음)."""
    if not directions or not str(directions).strip():
        return parsed

    pantry = pantry if pantry is not None else load_pantry_aliases()
    mapping_en = mapping_en if mapping_en is not None else load_mapping_en()
    mapping_ko = mapping_ko if mapping_ko is not None else load_mapping_ko()
    pantry_idx = _build_pantry_index(pantry)
    yolo_idx = _build_alias_index({**mapping_en, **mapping_ko})

    text = re.sub(r"\s+", " ", str(directions).replace("\n", " "))
    text = re.sub(r"\d+\.\s*", " ", text)

    yolo_seen, pantry_seen, name_tokens = _collect_parsed_coverage(
        parsed, pantry_idx
    )
    terms = _build_direction_scan_terms(mapping_en, mapping_ko, pantry)
    extras: list[ParsedIngredient] = []

    for alias, kind, target in terms:
        if not _alias_in_directions(alias, text):
            continue
        alias_norm = _normalize_token(alias)
        if alias_norm in name_tokens:
            continue
        if kind == "yolo":
            if target in yolo_seen or _yolo_family(target) & yolo_seen:
                continue
            yolo_seen |= _yolo_family(target)
        else:
            if target in pantry_seen:
                continue
            pantry_seen.add(target)

        extras.append(
            ParsedIngredient(
                name=alias_norm or alias,
                raw_name=f"{alias} (조리법)",
            )
        )

    if not extras:
        return parsed

    combined = list(parsed) + extras
    return _finalize_parsed_items(
        combined,
        pantry=pantry,
        pantry_idx=pantry_idx,
        yolo_idx=yolo_idx,
    )


def match_yolo_class(name: str, alias_index: dict[str, str] | None = None) -> str | None:
    """정규화된 재료명 → YOLO 클래스 (없으면 None)."""
    if alias_index is None:
        alias_index = _build_alias_index(
            {**load_mapping_en(), **load_mapping_ko()}
        )
    token = _normalize_token(name)
    if not token:
        return None

    if token in alias_index:
        return alias_index[token]

    for alias, yolo_class in sorted(alias_index.items(), key=lambda x: -len(x[0])):
        if len(alias) < 2:
            continue
        if alias in token or token in alias:
            return yolo_class
    return None


_FALSE_PEPPER = re.compile(
    r"red pepper|bell pepper|chili pepper|pepper flake|crushed red|gochugaru",
    re.IGNORECASE,
)


def _pantry_alias_matches(alias: str, canonical: str, token: str) -> bool:
    if token == alias or token == canonical:
        return True
    if alias in token or token in alias:
        if canonical == "pepper" and _FALSE_PEPPER.search(token):
            return False
        if re.search(r"[가-힣]", alias) or re.search(r"[가-힣]", token):
            return len(alias) >= 2
        if len(alias) <= 5:
            return bool(re.search(rf"\b{re.escape(alias)}\b", token))
        return True
    return False


def _pantry_display_label(canonical: str, pantry: dict[str, list[str]]) -> str:
    aliases = pantry.get(canonical, [canonical])
    for alias in aliases:
        if re.search(r"[가-힣]", alias):
            return alias
    return aliases[0]


def _find_embedded_pantry(
    text: str,
    pantry_index: dict[str, str],
) -> set[str]:
    token = _normalize_token(text)
    if not token:
        return set()
    found: set[str] = set()
    for alias, canonical in sorted(pantry_index.items(), key=lambda x: -len(x[0])):
        if len(alias) < 2:
            continue
        if _pantry_alias_matches(alias, canonical, token):
            found.add(canonical)
    return found


def _expand_embedded_staples(
    items: list[ParsedIngredient],
    pantry: dict[str, list[str]],
    pantry_index: dict[str, str],
) -> list[ParsedIngredient]:
    """복합 양념명(버섯마늘소금 등)에서 누락된 상비 재료를 추출."""
    pantry_keys = set(pantry.keys())
    covered: set[str] = set()
    for item in items:
        if not item.is_staple:
            continue
        if item.canonical and item.canonical in pantry_keys:
            covered.add(item.canonical)
        pk = match_pantry(item.name, pantry_index) or match_pantry(
            item.raw_name, pantry_index
        )
        if pk:
            covered.add(pk)

    out = list(items)
    for item in items:
        embedded = _find_embedded_pantry(item.raw_name or item.name, pantry_index)
        if len(embedded) < 2:
            continue
        for canonical in embedded:
            if canonical in covered:
                continue
            label = _pantry_display_label(canonical, pantry)
            out.append(
                ParsedIngredient(
                    name=label,
                    raw_name=f"{label} ({item.raw_name})",
                    quantity=None,
                    unit=None,
                    is_staple=True,
                    canonical=canonical,
                )
            )
            covered.add(canonical)
    return out


def match_pantry(name: str, pantry_index: dict[str, str] | None = None) -> str | None:
    if pantry_index is None:
        pantry_index = _build_pantry_index(load_pantry_aliases())
    token = _normalize_token(name)
    if not token:
        return None
    if token in pantry_index:
        return pantry_index[token]
    for alias, canonical in sorted(pantry_index.items(), key=lambda x: -len(x[0])):
        if len(alias) < 2:
            continue
        if _pantry_alias_matches(alias, canonical, token):
            return canonical
    return None


def ingredient_names(text: str, **kwargs) -> list[str]:
    """매칭용 정규화 이름 목록 (YOLO 클래스 또는 pantry canonical)."""
    names: list[str] = []
    for item in parse_ingredients(text, **kwargs):
        key = item.yolo_class or item.canonical or item.name
        if key and key not in names:
            names.append(key)
    return names


def _demo() -> None:
    import csv

    samples = [
        (
            "english",
            "3 tablespoons butter, 2 pounds Granny Smith apples, 1 teaspoon salt",
        ),
        (
            "korean",
            "연두부 75g(3/4모), 칵테일새우 20g(5마리), 설탕 5g(1작은술), 소금 0.3g",
        ),
    ]
    print("=== 샘플 파싱 ===")
    for label, text in samples:
        print(f"\n[{label}]")
        for p in parse_ingredients(text, source=label):
            flags = []
            if p.yolo_class:
                flags.append(f"yolo={p.yolo_class}")
            if p.is_staple:
                flags.append("pantry")
            extra = f" ({', '.join(flags)})" if flags else ""
            qty = f"{p.quantity} {p.unit}" if p.quantity else "-"
            print(f"  - {p.raw_name!r} → {p.name!r} [{qty}]{extra}")

    ko_path = ROOT / "data" / "recipes_korean.csv"
    en_path = ROOT / "Recipes Dataset" / "recipes.csv"
    stats = {"korean": {"total": 0, "parsed": 0, "yolo": 0}, "english": {"total": 0, "parsed": 0, "yolo": 0}}

    with ko_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stats["korean"]["total"] += 1
            items = parse_ingredients(row["ingredients"], source="korean")
            if items:
                stats["korean"]["parsed"] += 1
            if any(i.yolo_class for i in items):
                stats["korean"]["yolo"] += 1

    with en_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stats["english"]["total"] += 1
            items = parse_ingredients(row["ingredients"], source="english")
            if items:
                stats["english"]["parsed"] += 1
            if any(i.yolo_class for i in items):
                stats["english"]["yolo"] += 1

    print("\n=== CSV 검증 ===")
    for key, s in stats.items():
        rate = 100 * s["parsed"] / s["total"] if s["total"] else 0
        yolo_rate = 100 * s["yolo"] / s["total"] if s["total"] else 0
        print(
            f"{key}: {s['parsed']}/{s['total']} 레시피 파싱 성공 ({rate:.1f}%), "
            f"YOLO 매칭 {s['yolo']} ({yolo_rate:.1f}%)"
        )


if __name__ == "__main__":
    _demo()
