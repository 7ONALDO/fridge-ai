#!/usr/bin/env python3
"""
식약처 Open API (COOKRCP01) → 한식 레시피 CSV 수집 + 기존 recipes.csv 병합

사용법:
  1) 프로젝트 루트 .env 파일에 FOODSAFETY_API_KEY=인증키 저장 (권장)
  2) python scripts/fetch_foodsafety_recipes.py

  또는: export FOODSAFETY_API_KEY="발급받은_인증키"

산출물:
  data/recipes_korean.csv      — 식약처 레시피만 (~1146건)
  data/recipes_merged.csv      — Allrecipes + 식약처 병합본
  data/korean_recipes_raw.json — API 원본 JSON (디버그/재현용)

환경변수:
  FOODSAFETY_API_KEY  (필수) 식품안전나라 Open API 인증키
  RECIPES_ENGLISH     (선택) 영문 recipes.csv 경로
                        기본: Recipes Dataset/recipes.csv
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load_dotenv(path: Path | None = None) -> None:
    """프로젝트 루트 .env 를 읽어 환경변수에 반영 (이미 설정된 값은 덮어쓰지 않음)."""
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv()
DEFAULT_ENGLISH = ROOT / "Recipes Dataset" / "recipes.csv"
KOREAN_CSV = DATA / "recipes_korean.csv"
MERGED_CSV = DATA / "recipes_merged.csv"
RAW_JSON = DATA / "korean_recipes_raw.json"

API_BASE = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_ID = "COOKRCP01"
BATCH_SIZE = 1000

# recipes.csv 호환 컬럼 + 출처 메타
CSV_FIELDS = [
    "recipe_name",
    "prep_time",
    "cook_time",
    "total_time",
    "servings",
    "yield",
    "ingredients",
    "directions",
    "rating",
    "url",
    "cuisine_path",
    "nutrition",
    "timing",
    "img_src",
    "source",
    "rcp_seq",
]


def get_api_key() -> str:
    key = os.environ.get("FOODSAFETY_API_KEY", "").strip()
    if not key:
        print(
            "[오류] FOODSAFETY_API_KEY 환경변수가 없습니다.\n"
            "  export FOODSAFETY_API_KEY='발급받은_인증키'\n"
            "  python scripts/fetch_foodsafety_recipes.py",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def fetch_range(api_key: str, start: int, end: int) -> tuple[list[dict], dict]:
    """COOKRCP01 JSON 구간 조회. (rows, result_meta) 반환."""
    url = f"{API_BASE}/{api_key}/{SERVICE_ID}/json/{start}/{end}"
    print(f"[fetch] {start}~{end}  {url[:80]}...")

    req = urllib.request.Request(url, headers={"User-Agent": "fridge-recipe-bot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"[오류] HTTP {e.code}: {url}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"[오류] 네트워크 실패: {e.reason}") from e

    body = payload.get("COOKRCP01") or payload.get(SERVICE_ID) or {}
    result = body.get("RESULT") or {}
    code = result.get("CODE", "")
    if code != "INFO-000":
        msg = result.get("MSG", "unknown")
        raise SystemExit(f"[오류] API 응답 CODE={code} MSG={msg}")

    rows = body.get("row") or []
    if isinstance(rows, dict):
        rows = [rows]

    meta = {
        "total_count": int(body.get("total_count") or 0),
        "count": len(rows),
        "start": start,
        "end": end,
    }
    return rows, meta


def fetch_all(api_key: str) -> list[dict]:
    """전체 레시피 수집 (1000건 단위, 2회 호출)."""
    rows1, meta1 = fetch_range(api_key, 1, BATCH_SIZE)
    total = meta1["total_count"] or (len(rows1) if len(rows1) < BATCH_SIZE else BATCH_SIZE)

    all_rows = list(rows1)
    if total > BATCH_SIZE:
        time.sleep(0.3)
        rows2, meta2 = fetch_range(api_key, BATCH_SIZE + 1, total)
        all_rows.extend(rows2)
        print(f"[fetch] 2차 수집: {meta2['count']}건 (누적 {len(all_rows)}/{total})")
    else:
        print(f"[fetch] 전체 {len(all_rows)}건 (1회 호출로 완료)")

    if len(all_rows) != total:
        print(f"[경고] 수집 {len(all_rows)}건 ≠ API total_count {total}")

    return all_rows


def build_directions(item: dict) -> str:
    steps: list[str] = []
    for i in range(1, 21):
        text = (item.get(f"MANUAL{i:02d}") or "").strip()
        if text:
            steps.append(f"{len(steps) + 1}. {text}")
    return "\n".join(steps)


def build_nutrition(item: dict) -> str:
    parts = []
    mapping = [
        ("열량", "INFO_ENG", "kcal"),
        ("탄수화물", "INFO_CAR", "g"),
        ("단백질", "INFO_PRO", "g"),
        ("지방", "INFO_FAT", "g"),
        ("나트륨", "INFO_NA", "mg"),
    ]
    for label, key, unit in mapping:
        val = (item.get(key) or "").strip()
        if val:
            parts.append(f"{label} {val}{unit}")
    tip = (item.get("RCP_NA_TIP") or "").strip()
    if tip:
        parts.append(f"TIP: {tip}")
    return ", ".join(parts)


def to_csv_row(item: dict) -> dict:
    """API row → recipes.csv 호환 dict."""
    rcp_seq = str(item.get("RCP_SEQ") or "").strip()
    pat2 = (item.get("RCP_PAT2") or "").strip()
    way = (item.get("RCP_WAY2") or "").strip()
    wgt = (item.get("INFO_WGT") or "").strip()

    return {
        "recipe_name": (item.get("RCP_NM") or "").strip(),
        "prep_time": "",
        "cook_time": way,
        "total_time": "",
        "servings": "1",
        "yield": f"1인분 {wgt}g" if wgt else "1인분",
        "ingredients": (item.get("RCP_PARTS_DTLS") or "").strip(),
        "directions": build_directions(item),
        "rating": "",
        "url": (
            f"https://www.foodsafetykorea.go.kr/recipe/{rcp_seq}"
            if rcp_seq
            else "https://www.foodsafetykorea.go.kr"
        ),
        "cuisine_path": f"/한식/{pat2}" if pat2 else "/한식",
        "nutrition": build_nutrition(item),
        "timing": f"조리방법: {way}" if way else "",
        "img_src": (item.get("ATT_FILE_NO_MK") or item.get("ATT_FILE_NO_MAIN") or "").strip(),
        "source": "foodsafety",
        "rcp_seq": rcp_seq,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[save] {len(rows)}건 → {path}")


def load_english_recipes(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"[오류] 영문 recipes.csv 없음: {path}")

    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = {k: (raw.get(k) or "").strip() for k in CSV_FIELDS if k not in ("source", "rcp_seq")}
            row["source"] = "allrecipes"
            row["rcp_seq"] = ""
            rows.append(row)
    print(f"[load] 영문 레시피 {len(rows)}건 ← {path}")
    return rows


def merge_recipes(english: list[dict], korean: list[dict]) -> list[dict]:
    merged = english + korean
    print(f"[merge] allrecipes {len(english)} + foodsafety {len(korean)} = {len(merged)}")
    return merged


def main() -> None:
    api_key = get_api_key()
    english_path = Path(os.environ.get("RECIPES_ENGLISH", str(DEFAULT_ENGLISH)))

    print("=" * 60)
    print("  식약처 COOKRCP01 수집 + recipes.csv 병합")
    print("=" * 60)

    raw_rows = fetch_all(api_key)
    DATA.mkdir(parents=True, exist_ok=True)
    RAW_JSON.write_text(json.dumps(raw_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[save] 원본 JSON → {RAW_JSON}")

    korean_rows = [to_csv_row(item) for item in raw_rows]
    write_csv(KOREAN_CSV, korean_rows)

    english_rows = load_english_recipes(english_path)
    merged_rows = merge_recipes(english_rows, korean_rows)
    write_csv(MERGED_CSV, merged_rows)

    print("\n" + "=" * 60)
    print("  ✅ 완료")
    print(f"  한식만     : {KOREAN_CSV}")
    print(f"  병합본     : {MERGED_CSV}")
    print("  FastAPI/랭커에서 data/recipes_merged.csv 를 사용하세요.")
    print("=" * 60)


if __name__ == "__main__":
    main()
