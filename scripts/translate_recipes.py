#!/usr/bin/env python3
"""
allrecipes 영어 레시피 → 한국어 번역 스크립트 (OpenAI GPT)

사용법:
  export OPENAI_API_KEY="sk-..."
  cd "/Users/k2/Documents/프로젝트"
  source .venv/bin/activate
  python3 scripts/translate_recipes.py

중단 후 재실행하면 체크포인트에서 이어서 진행합니다.
결과: data/recipes_merged_ko.csv
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INPUT_CSV   = ROOT / "data" / "recipes_merged.csv"
OUTPUT_CSV  = ROOT / "data" / "recipes_merged_ko.csv"
CHECKPOINT  = ROOT / "data" / "translate_checkpoint.json"
MODEL       = "gpt-4o-mini"

TRANSLATE_FIELDS = ["recipe_name", "ingredients", "directions", "cuisine_path"]


def _check_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("[오류] OPENAI_API_KEY 환경변수가 없습니다.")
        print("  → export OPENAI_API_KEY='sk-...' 실행 후 다시 시도하세요.")
        sys.exit(1)


def translate_recipe(client, row: dict) -> dict:
    payload = {k: row.get(k, "") for k in TRANSLATE_FIELDS}

    prompt = (
        "아래 영어 레시피를 자연스러운 한국어로 번역해 주세요.\n"
        "반드시 JSON 형식만 반환하고 다른 텍스트는 포함하지 마세요.\n\n"
        f"입력:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
        "규칙:\n"
        "- recipe_name: 한국어 레시피명 (예: '닭고기 카레')\n"
        "- ingredients: 재료 목록 한국어 변환 (단위도 한국식으로, 원래 형식 유지)\n"
        "- directions: 조리 방법 한국어 번역\n"
        "- cuisine_path: 카테고리 경로를 한국어로 (/ 구분자 유지, 예: /메인요리/닭고기요리/)\n\n"
        '출력 형식: {"recipe_name":"...","ingredients":"...","directions":"...","cuisine_path":"..."}'
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    text = response.choices[0].message.content.strip()
    return json.loads(text)


def main() -> None:
    _check_api_key()

    try:
        from openai import OpenAI
    except ImportError:
        print("[오류] openai 패키지가 없습니다. pip install openai")
        sys.exit(1)

    client = OpenAI()

    # 체크포인트 로드
    checkpoint: dict[str, dict] = {}
    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        print(f"체크포인트 로드: {len(checkpoint)}개 이미 번역됨")

    # CSV 읽기
    with open(INPUT_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        all_rows = list(reader)

    allrecipes = [(i, r) for i, r in enumerate(all_rows) if r.get("source", "").strip() == "allrecipes"]
    remaining  = [(i, r) for i, r in allrecipes if f"idx_{i}" not in checkpoint]
    total      = len(allrecipes)

    print(f"총 allrecipes: {total}개 | 남은 번역: {len(remaining)}개")
    if not remaining:
        print("이미 모두 번역되었습니다. CSV 생성 단계로 넘어갑니다.")

    # 번역 루프
    done = 0
    errors = 0
    for i, row in remaining:
        key = f"idx_{i}"
        name_preview = row.get("recipe_name", "")[:45]

        try:
            translated = translate_recipe(client, row)
            checkpoint[key] = translated
            done += 1

            print(f"[{len(checkpoint)}/{total}] {name_preview} → {translated.get('recipe_name','?')[:45]}")

            # 10개마다 체크포인트 저장
            if done % 10 == 0:
                CHECKPOINT.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")

            time.sleep(0.2)

        except Exception as exc:
            errors += 1
            print(f"  [오류] {name_preview}: {exc}")
            time.sleep(1)
            continue

    # 최종 체크포인트 저장
    CHECKPOINT.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n번역 완료: {done}개 | 오류: {errors}개")

    # 번역 반영 후 CSV 저장
    output_rows = []
    translated_apply = 0
    for i, row in enumerate(all_rows):
        key = f"idx_{i}"
        if row.get("source", "").strip() == "allrecipes" and key in checkpoint:
            row = row.copy()
            t = checkpoint[key]
            for field in TRANSLATE_FIELDS:
                if t.get(field):
                    row[field] = t[field]
            translated_apply += 1
        output_rows.append(row)

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"번역 반영: {translated_apply}개 / 전체: {len(output_rows)}개")
    print(f"\n저장 완료 → {OUTPUT_CSV}")
    print("\n다음 단계: API 서버를 아래 환경변수로 재시작하세요:")
    print(f'  RECIPES_CSV="{OUTPUT_CSV}" python3 scripts/run_api.py')


if __name__ == "__main__":
    main()
