# 냉장고 AI — 재료 인식 + 레시피 추천

냉장고 사진에서 **YOLOv11**으로 재료를 인식하고, 보유 재료·필터 조건에 맞는 레시피를 **규칙 기반**으로 추천하는 End-to-End 시스템입니다.

## 기능 요약

1. **사진 업로드** (여러 장) → YOLO 재료 탐지
2. **재료 확인** — 통합 재료 표, **−/+·삭제**, 이름 **단일 입력** 추가 (YOLO/custom 자동 분기)
3. **레시피 종류** — 전체 / 한식(식약처) / 양식(Allrecipes) — **괄호 = 추천 가능 건수**
4. **세부 카테고리** — 출처별 분류 (아래 표) — **괄호 = 추천 가능 건수**
5. **식단 필터** — 7종 **토글 버튼 복수 선택(AND)** — 단독 괄호 + **선택 조합 N건**
6. **레시피 추천** — **페이지당 20건**, 이전/다음으로 전체 목록 탐색
7. **상세** — 재료 **4열**(보유·추가구매·상비·**기타**), 인분 자동 스케일, 조리법

## 레시피 데이터

| 출처 | 파일 | 건수 | 분류 필드 |
|---|---|---:|---|
| **Allrecipes** | `Recipes Dataset/recipes.csv` | 1,090 | `cuisine_path` **1단계** (예: `/Desserts/...`) |
| **식약처** | API → `data/recipes_merged.csv` | 1,146 | `/한식/{유형}` (반찬, 일품, …) |
| **병합 DB** | `data/recipes_merged.csv` | ~2,107 | `source` = `allrecipes` \| `foodsafety` |

### 카테고리 (필터) — 총 19개 (출처별 택1)

**양식** (`filters.source=allrecipes`) — L1 **13개**:

- 디저트·베이킹, 샐러드, 수프·스튜, 아침·브런치, … (`core/recipe_categories.py`)

**한식** (`filters.source=foodsafety`) — 유형 **6개**:

| 유형 | 설명 |
|---|---|
| 반찬 | 밑반찬·나물 등 |
| **일품** | 면·국수·만두·덮밥 등 **한 그릇 요리** (~171건) |
| 후식 | 식후 디저트 |
| 밥 | 밥·죽 |
| 국·찌개 | 국·찌개 |
| 기타 | 위 분류 외 |

> 구버전 **식사(아침/점심/…)** · **5개국 요리** 필터는 폐기. Allrecipes는 path L1로 대체.

### 출처별 메타 (UI 표시)

| | 양식 | 한식 |
|---|---|---|
| **별점** | Allrecipes 사용자 평점 표시 | **표시 안 함** (API에 없음; 랭킹만 중립 3.0) |
| **시간** | 준비 · 조리 · 총 | **`조리방법: 볶기`** 등 (분 단위 없음) |
| **이미지** | allrecipes.com | 식품안전나라 `foodsafetykorea.go.kr/uploadimg/...` |
| **재료량** | `3 tbsp butter` 등 | `돼지고기(70g)` 형식 파싱 |

### 필터 옵션 괄호 숫자 (3~5단계)

- **의미**: 지금 2단계 재료 기준 rankable 수. **카테고리**는 상호 배타(합 일치). **식단**은 **겹칠 수 있음**(옵션 합 ≠ 전체).
- **5단계 복수 선택**: **「현재 선택 조합: N건」** = 6단계 `total_rankable` 과 동일.
- **6단계**: 한 화면 **20건**씩, **← 이전 / 다음 →** 로 전체 탐색.
- **구현**: `ui/filter_counts.py` → `core/ranker.py` `count_rankable_recipes()`.

### 2단계 재료 확인 (통합 UI)

- **하나의 표**에 인식·직접 추가 재료 통합 (구분 열 없음).
- 표에서 **− / +** 수량 변경, **삭제** 즉시 반영.
- **재료 추가**: 이름 입력 → `mapping_ko.json` 매칭 시 YOLO `ingredients`, 아니면 `custom_ingredients` (예: 김치, 두부).
- 백엔드·API는 **`ingredients` + `custom_ingredients`** 분리 유지.

## 실행

터미널 **2개** 필요 (API + UI).

```bash
cd "/Users/k2/Documents/프로젝트"
source .venv/bin/activate
pip install -r requirements.txt   # 최초 1회

# 터미널 1
python3 scripts/run_api.py    # http://127.0.0.1:8000  Swagger /docs

# 터미널 2
python3 scripts/run_ui.py     # http://127.0.0.1:8501
```

코드 수정 후에는 두 서버를 **Ctrl+C로 종료 후 재실행**하고, 브라우저 **강력 새로고침** (`Cmd+Shift+R`).

## Docker로 실행 (한 번에 API + UI)

> **Docker Desktop**이 Mac에 설치되어 있어야 합니다.  
> [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) 에서 설치 후 실행하세요.

**Docker란?** 앱(API·UI)을 “상자(컨테이너)”에 넣어, 터미널 명령 **한 번**으로 같은 환경에서 실행하는 도구입니다.

```bash
cd "/Users/k2/Documents/프로젝트"

# 권장 (한글 경로 Buildx 오류 우회)
chmod +x scripts/docker-up.sh   # 최초 1회
./scripts/docker-up.sh

# 또는
COMPOSE_BAKE=false docker compose up --build

# 백그라운드
COMPOSE_BAKE=false docker compose up --build -d

# 종료
docker compose down
```

**한글 폴더 `프로젝트`에서 자주 나는 오류**

| 증상 | 해결 |
|------|------|
| `project name must not be empty` | `name: fridge-ai` (compose에 적용됨) |
| **0.3초 만에 끝** + `non-printable ASCII characters` | **`COMPOSE_BAKE=false`** 또는 **`./scripts/docker-up.sh`** |

`COMPOSE_BAKE=false`로도 안 되면 **영문 경로**로 복사 후 빌드 (Docker Buildx 한글 경로 버그):

```bash
cp -R "/Users/k2/Documents/프로젝트" ~/fridge-ai
cd ~/fridge-ai
COMPOSE_BAKE=false docker compose up --build
```

정상 빌드는 PyTorch 다운로드로 **5~15분** 걸립니다. **0.3초에 끝나면 아직 실패**입니다.

브라우저:

| 주소 | 내용 |
|------|------|
| http://127.0.0.1:8501 | Streamlit UI (평소와 동일) |
| http://127.0.0.1:8000/docs | API Swagger |

**주의**

- 프로젝트 루트에 **`best.pt`** 가 있어야 합니다 (YOLO 가중치).
- UI는 컨테이너 안에서 API를 `http://api:8000` 으로 부릅니다 (`docker-compose.yml`의 `API_URL`).
- 로그 확인: `docker compose logs -f`

환경 변수 (선택):

- `YOLO_MODEL_PATH` / `YOLO_WEIGHTS` — 기본 `best.pt`
- `API_URL` — UI에서 API 주소 (기본 `http://127.0.0.1:8000`)

## API 예시 (`POST /recipes`)

```json
{
  "ingredients": {"onion": 2, "chicken": 1},
  "custom_ingredients": {"김치": 1},
  "filters": {
    "source": "foodsafety",
    "category": "국&찌개",
    "diets": ["low-carb", "sugar-free"]
  },
  "top_k": 20,
  "offset": 0
}
```

응답: `results`, `count`, `total_rankable`, `offset`, `page_size`

## CLI 데모

```bash
python3 scripts/rank_demo.py --ingredients onion,chicken --source foodsafety --category 반찬 --top 5
python3 scripts/rank_demo.py --ingredients apple,butter --source allrecipes --category Desserts --top 5
```

## 문서

- 계획서: `fridge-recipe-plan-v3.md` (§4.2.3~4.2.4 · v3.16 · 부록 O)
- 요약: `project-final-summary.md`
- PPT: `ppt-slides-v3.md`
- 학습: `train_yolo_byclaude.py` · Ablation: `ablation_yolo.py`
