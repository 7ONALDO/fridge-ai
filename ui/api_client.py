"""FastAPI HTTP 클라이언트."""

from __future__ import annotations

import os
from typing import Any

import requests

DEFAULT_API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}{path}"


def health(base: str = DEFAULT_API_URL) -> dict[str, Any]:
    r = requests.get(_url(base, "/health"), timeout=10)
    r.raise_for_status()
    return r.json()


def _error_detail(r: requests.Response) -> str:
    try:
        return r.json().get("detail", r.text)
    except Exception:
        return r.text


def predict(files: list[tuple[str, bytes, str]], base: str = DEFAULT_API_URL) -> dict[str, Any]:
    multipart = [("files", (name, data, mime)) for name, data, mime in files]
    r = requests.post(_url(base, "/predict"), files=multipart, timeout=120)
    if not r.ok:
        raise ApiError(_error_detail(r), r.status_code)
    return r.json()


def search_recipes(
    ingredients: dict[str, int],
    *,
    custom_ingredients: dict[str, int] | None = None,
    source: str | None = None,
    category: str | None = None,
    diet: str | None = None,
    diets: list[str] | None = None,
    name_query: str | None = None,
    top_k: int = 20,
    offset: int = 0,
    min_detected_used: int = 1,
    base: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "ingredients": ingredients,
        "custom_ingredients": custom_ingredients or {},
        "top_k": top_k,
        "offset": offset,
        "min_detected_used": min_detected_used,
    }
    filter_body: dict[str, Any] = {}
    if source:
        filter_body["source"] = source
    if category:
        filter_body["category"] = category
    if diets:
        filter_body["diets"] = diets
    elif diet:
        filter_body["diet"] = diet
    if name_query and name_query.strip():
        filter_body["name_query"] = name_query.strip()
    if filter_body:
        body["filters"] = filter_body
    r = requests.post(_url(base, "/recipes"), json=body, timeout=60)
    if not r.ok:
        raise ApiError(_error_detail(r), r.status_code)
    return r.json()


def get_recipe(
    recipe_id: int,
    detected: dict[str, int],
    *,
    custom_ingredients: dict[str, int] | None = None,
    base: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    params: dict[str, str] = {}
    if detected:
        params["detected"] = ",".join(detected.keys())
    custom = custom_ingredients or {}
    if custom:
        params["custom"] = ",".join(custom.keys())
    r = requests.get(
        _url(base, f"/recipe/{recipe_id}"),
        params=params,
        timeout=30,
    )
    if not r.ok:
        raise ApiError(_error_detail(r), r.status_code)
    return r.json()


def scale_recipe(
    recipe_id: int,
    new_servings: int,
    base: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    r = requests.post(
        _url(base, "/scale"),
        json={"recipe_id": recipe_id, "new_servings": new_servings},
        timeout=30,
    )
    if not r.ok:
        raise ApiError(_error_detail(r), r.status_code)
    return r.json()
