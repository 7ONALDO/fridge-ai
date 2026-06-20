#!/usr/bin/env bash
# Docker Buildx는 빌드 경로에 한글이 있으면 gRPC 오류가 납니다.
# COMPOSE_BAKE=false 로 구형 빌드 방식 사용 + 이미지 1번만 빌드
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export COMPOSE_BAKE=false

echo "==> 프로젝트: $ROOT"
echo "==> COMPOSE_BAKE=false (한글 경로 Buildx 우회)"
echo ""

if [[ "$ROOT" == *[^[:ascii:]]* ]]; then
  echo "⚠️  경로에 한글/비ASCII 문자가 있습니다."
  echo "   이 스크립트로도 실패하면 README 'Docker' 절의 영문 경로 방법을 쓰세요."
  echo ""
fi

exec docker compose up --build "$@"
