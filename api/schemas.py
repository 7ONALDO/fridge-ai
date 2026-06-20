"""FastAPI 요청/응답 Pydantic 모델."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DetectionOut(BaseModel):
    class_name: str
    confidence: float
    count: int = 1


class PredictResponse(BaseModel):
    ingredients: dict[str, int] = Field(
        description="표준 YOLO 클래스별 개수 (normalizer 결과)"
    )
    detections: list[DetectionOut] = Field(
        default_factory=list,
        description="이미지별 탐지 상세 (디버그/시각화용)",
    )
    image_count: int = 0


class RecipeFiltersIn(BaseModel):
    source: str | None = Field(
        default=None,
        description="레시피 DB: foodsafety(식약처 한식) | allrecipes",
    )
    category: str | None = Field(
        default=None,
        description="Allrecipes cuisine_path L1 또는 식약처 /한식/{유형}",
    )
    diet: str | None = Field(
        default=None,
        description="단일 식단 필터 (하위 호환). diets 와 함께 쓰지 마세요.",
    )
    diets: list[str] | None = Field(
        default=None,
        description="복수 식단 필터 — 모두 만족(AND)하는 레시피만",
    )


class RecipeQuery(BaseModel):
    ingredients: dict[str, int] | list[str] = Field(
        description="냉장고 재료 — dict(개수) 또는 클래스명 리스트"
    )
    custom_ingredients: dict[str, int] | list[str] = Field(
        default_factory=dict,
        description="YOLO 30종 밖 직접 입력 재료 (예: {'김치': 1})",
    )
    filters: RecipeFiltersIn | None = None
    top_k: int = Field(default=20, ge=1, le=100, description="페이지당 결과 수")
    offset: int = Field(default=0, ge=0, description="건너뛸 결과 수 (페이지네이션)")
    min_detected_used: int = Field(default=1, ge=1)


class RankedRecipeOut(BaseModel):
    recipe_id: int
    recipe_name: str
    score: float
    coverage: float
    shortage: int
    missing: list[str]
    detected_used: int
    rating: float
    img_src: str
    url: str
    cuisine_path: str
    source: str


class RecipesResponse(BaseModel):
    results: list[RankedRecipeOut]
    count: int = Field(description="이번 페이지 결과 수")
    total_rankable: int = Field(
        description="동일 필터·재료 조건으로 추천 가능한 전체 레시피 수"
    )
    offset: int = Field(default=0, description="이번 페이지 시작 위치")
    page_size: int = Field(description="요청한 페이지당 결과 수")


class IngredientItemOut(BaseModel):
    name: str
    raw_name: str
    quantity: float | None = None
    unit: str | None = None
    yolo_class: str | None = None
    is_staple: bool = False
    custom_matched: bool = False


class ClassifiedIngredientsOut(BaseModel):
    owned: list[IngredientItemOut]
    to_buy: list[IngredientItemOut]
    pantry: list[IngredientItemOut]
    extra: list[IngredientItemOut] = Field(default_factory=list)
    extra_matched: list[IngredientItemOut] = Field(default_factory=list)


class RecipeDetailOut(BaseModel):
    recipe_id: int
    recipe_name: str
    prep_time: str
    cook_time: str
    total_time: str
    servings: str
    yield_: str = Field(alias="yield")
    rating: float
    url: str
    cuisine_path: str
    nutrition: str
    img_src: str
    source: str
    ingredient_count: int
    directions: list[str]
    classified: ClassifiedIngredientsOut | None = None

    model_config = {"populate_by_name": True}


class ScaleRequest(BaseModel):
    recipe_id: int = Field(ge=0)
    new_servings: int = Field(ge=1, le=100)


class ScaledIngredientOut(BaseModel):
    name: str
    raw_name: str
    quantity: float | None = None
    unit: str | None = None
    yolo_class: str | None = None
    scale_mode: str


class ScaleResponse(BaseModel):
    recipe_id: int
    original_servings: int
    new_servings: int
    ingredients: list[ScaledIngredientOut]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    recipe_count: int
