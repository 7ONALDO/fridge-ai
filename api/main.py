"""냉장고 AI FastAPI 서버."""

import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, List

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import WithJsonSchema

from api.predictor import IngredientPredictor
from api.schemas import (
    ClassifiedIngredientsOut,
    HealthResponse,
    IngredientItemOut,
    PredictResponse,
    RecipeDetailOut,
    RecipeFiltersIn,
    RecipeQuery,
    RecipesResponse,
    RankedRecipeOut,
    ScaleRequest,
    ScaleResponse,
    ScaledIngredientOut,
    DetectionOut,
)
from core.custom_match import custom_matches_item, custom_names_set, normalize_custom_inventory
from core.normalizer import normalize_detections
from core.pantry import classify_ingredients
from core.ranker import RecipeFilters, RecipeStore, count_rankable_recipes, rank_recipes
from core.scaler import scale_ingredients

ROOT = Path(__file__).resolve().parent.parent

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic"}

# FastAPI 0.129+ 는 OAS 3.1 contentMediaType 를 쓰는데,
# Swagger UI 는 format:binary 만 파일 선택 버튼으로 렌더링함.
BinaryUploadFile = Annotated[
    UploadFile,
    WithJsonSchema({"type": "string", "format": "binary"}),
]


def _patch_binary_upload_schema(schema: dict) -> None:
    """Swagger UI 파일 버튼용 — contentMediaType → format:binary."""
    for component in schema.get("components", {}).get("schemas", {}).values():
        for prop in component.get("properties", {}).values():
            if prop.get("contentMediaType") == "application/octet-stream":
                prop.pop("contentMediaType", None)
                prop["format"] = "binary"
            items = prop.get("items")
            if isinstance(items, dict) and items.get("contentMediaType") == "application/octet-stream":
                items.pop("contentMediaType", None)
                items["format"] = "binary"


def _is_image_upload(upload: UploadFile, data: bytes) -> bool:
    if upload.content_type and upload.content_type.startswith("image/"):
        return True
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return True
    # JPEG / PNG magic bytes (Swagger 가 octet-stream 으로 보낼 때)
    if data.startswith(b"\xff\xd8\xff") or data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    return False


def _parse_detected_param(value: str | None) -> dict[str, int]:
    if not value or not value.strip():
        return {}
    items = [x.strip() for x in value.split(",") if x.strip()]
    return normalize_detections(items)


def _parse_custom_param(value: str | None) -> dict[str, int]:
    if not value or not value.strip():
        return {}
    items = [x.strip() for x in value.split(",") if x.strip()]
    return normalize_custom_inventory(items)


def _parsed_item_out(item, *, custom_matched: bool = False) -> IngredientItemOut:
    return IngredientItemOut(
        name=item.name,
        raw_name=item.raw_name,
        quantity=item.quantity,
        unit=item.unit,
        yolo_class=item.yolo_class,
        is_staple=item.is_staple,
        custom_matched=custom_matched,
    )


def _classified_out(
    classified,
    *,
    custom: dict[str, int] | None = None,
) -> ClassifiedIngredientsOut:
    custom_names = custom_names_set(custom)

    def _extra_out(item) -> IngredientItemOut:
        matched = custom_matches_item(custom_names, item)
        return _parsed_item_out(item, custom_matched=matched)

    return ClassifiedIngredientsOut(
        owned=[_parsed_item_out(x) for x in classified.owned],
        to_buy=[_parsed_item_out(x) for x in classified.to_buy],
        pantry=[_parsed_item_out(x) for x in classified.pantry],
        extra=[_extra_out(x) for x in classified.extra],
        extra_matched=[_parsed_item_out(x, custom_matched=True) for x in classified.extra_matched],
    )


def _directions_list(text: str) -> list[str]:
    steps = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        # 식약처 API·수집 스크립트 이중 번호 제거 (예: "1. 1. 돼지고기...")
        line = re.sub(r"^(\d+\.\s*)+", "", line).strip()
        if line:
            steps.append(line)
    return steps


@asynccontextmanager
async def lifespan(app: FastAPI):
    weights = Path(os.environ.get("YOLO_WEIGHTS", str(ROOT / "best.pt")))
    recipes_path = Path(
        os.environ.get("RECIPES_CSV", str(ROOT / "data" / "recipes_merged_ko.csv"))
    )

    predictor = IngredientPredictor(weights_path=weights)
    try:
        predictor.load()
    except FileNotFoundError as exc:
        print(f"[warn] {exc} — /predict 는 가중치 준비 후 사용하세요.")

    app.state.predictor = predictor
    app.state.recipe_store = RecipeStore(recipes_path)
    yield


app = FastAPI(
    title="냉장고 AI API",
    description="YOLOv11 재료 인식 + 레시피 추천",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    _patch_binary_upload_schema(schema)
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


def get_predictor() -> IngredientPredictor:
    return app.state.predictor


def get_store() -> RecipeStore:
    return app.state.recipe_store


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health(
    predictor: IngredientPredictor = Depends(get_predictor),
    store: RecipeStore = Depends(get_store),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=predictor.is_loaded,
        model_path=str(predictor.weights_path),
        recipe_count=len(store.recipes),
    )


@app.post("/predict", response_model=PredictResponse, tags=["vision"])
async def predict(
    files: Annotated[
        List[BinaryUploadFile],
        File(..., description="냉장고 사진 1장 이상"),
    ],
    predictor: IngredientPredictor = Depends(get_predictor),
) -> PredictResponse:
    if not files:
        raise HTTPException(status_code=400, detail="이미지 파일이 필요합니다.")

    images: list[bytes] = []
    for upload in files:
        data = await upload.read()
        if not data:
            continue
        if not _is_image_upload(upload, data):
            raise HTTPException(
                status_code=400,
                detail=f"이미지 파일만 업로드하세요: {upload.filename}",
            )
        images.append(data)

    if not images:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    try:
        ingredients, raw = predictor.predict_bytes(images)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"추론 실패: {exc}") from exc

    detections = [DetectionOut(**item) for item in raw]
    return PredictResponse(
        ingredients=ingredients,
        detections=detections,
        image_count=len(images),
    )


@app.post("/recipes", response_model=RecipesResponse, tags=["recipes"])
def search_recipes(
    query: RecipeQuery,
    store: RecipeStore = Depends(get_store),
) -> RecipesResponse:
    if isinstance(query.ingredients, dict):
        detected = normalize_detections(query.ingredients)
    else:
        detected = normalize_detections(list(query.ingredients))

    custom = normalize_custom_inventory(query.custom_ingredients)

    if not detected and not custom:
        raise HTTPException(status_code=400, detail="ingredients 가 비어 있습니다.")

    filters = None
    if query.filters:
        diets = list(query.filters.diets or [])
        if query.filters.diet and not diets:
            diets = [query.filters.diet]
        filters = RecipeFilters(
            source=query.filters.source,
            category=query.filters.category,
            diets=diets,
            name_query=query.filters.name_query,
        )

    total_rankable = count_rankable_recipes(
        detected,
        filters=filters,
        store=store,
        custom=custom,
        min_detected_used=query.min_detected_used,
    )

    ranked = rank_recipes(
        detected,
        filters=filters,
        top_k=query.top_k,
        offset=query.offset,
        store=store,
        custom=custom,
        min_detected_used=query.min_detected_used,
    )

    results = [
        RankedRecipeOut(
            recipe_id=r.recipe_id,
            recipe_name=r.recipe_name,
            score=r.score,
            coverage=r.coverage,
            shortage=r.shortage,
            missing=r.missing,
            detected_used=r.detected_used,
            rating=r.rating,
            img_src=r.img_src,
            url=r.url,
            cuisine_path=r.cuisine_path,
            source=r.source,
        )
        for r in ranked
    ]
    return RecipesResponse(
        results=results,
        count=len(results),
        total_rankable=total_rankable,
        offset=query.offset,
        page_size=query.top_k,
    )


@app.get("/recipe/{recipe_id}", response_model=RecipeDetailOut, tags=["recipes"])
def get_recipe(
    recipe_id: int,
    detected: str | None = Query(
        default=None,
        description="냉장고 재료 (쉼표 구분). 예: onion,chicken",
    ),
    custom: str | None = Query(
        default=None,
        description="YOLO 30종 밖 직접 입력 재료 (쉼표 구분). 예: 김치,두부",
    ),
    store: RecipeStore = Depends(get_store),
) -> RecipeDetailOut:
    try:
        recipe = store.get(recipe_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.") from exc

    classified = None
    detected_map = _parse_detected_param(detected)
    custom_map = _parse_custom_param(custom)
    if detected_map or custom_map:
        classified = _classified_out(
            classify_ingredients(
                recipe.parsed,
                detected_map,
                source=recipe.parse_source,
                custom=custom_map,
            ),
            custom=custom_map,
        )

    return RecipeDetailOut(
        recipe_id=recipe.recipe_id,
        recipe_name=recipe.recipe_name,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        servings=recipe.servings,
        yield_=recipe.yield_,
        rating=recipe.rating,
        url=recipe.url,
        cuisine_path=recipe.cuisine_path,
        nutrition=recipe.nutrition,
        img_src=recipe.img_src,
        source=recipe.source,
        ingredient_count=len(recipe.parsed),
        directions=_directions_list(recipe.directions),
        classified=classified,
    )


@app.post("/scale", response_model=ScaleResponse, tags=["recipes"])
def scale_recipe(
    body: ScaleRequest,
    store: RecipeStore = Depends(get_store),
) -> ScaleResponse:
    try:
        recipe = store.get(body.recipe_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.") from exc

    from core.scaler import _parse_servings

    scaled = scale_ingredients(
        recipe.parsed,
        recipe.servings,
        body.new_servings,
        source=recipe.parse_source,
    )

    return ScaleResponse(
        recipe_id=recipe.recipe_id,
        original_servings=_parse_servings(recipe.servings),
        new_servings=body.new_servings,
        ingredients=[
            ScaledIngredientOut(
                name=s.name,
                raw_name=s.raw_name,
                quantity=s.quantity,
                unit=s.unit,
                yolo_class=s.yolo_class,
                scale_mode=s.scale_mode,
            )
            for s in scaled
        ],
    )
