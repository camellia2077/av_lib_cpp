from __future__ import annotations

from typing import Any

import requests

from .config import Config
from .models import MovieInfo

_COVER_KEYS = ("cover", "poster", "image", "img", "thumb", "thumbnail")


def _collect_actor_names(raw: Any) -> list[str]:
    names: list[str] = []
    if raw is None:
        return names
    if isinstance(raw, str):
        value = raw.strip()
        return [value] if value else []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                value = item.strip()
                if value:
                    names.append(value)
                continue
            if isinstance(item, dict):
                for key in ("name", "title", "actor", "actress"):
                    value = item.get(key)
                    if isinstance(value, str) and value.strip():
                        names.append(value.strip())
                        break
        return names
    if isinstance(raw, dict):
        for key in ("name", "title", "actor", "actress"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                names.append(value.strip())
                break
    return names


def extract_actor_names(data: dict[str, Any]) -> list[str]:
    # Different javbus-api builds expose cast fields with different key names.
    # Merge all known variants and deduplicate to keep downstream logic stable.
    actor_keys = ("stars", "star", "actresses", "actress", "actors", "actor")
    merged: list[str] = []
    seen: set[str] = set()
    for key in actor_keys:
        for name in _collect_actor_names(data.get(key)):
            normalized = name.strip()
            if not normalized:
                continue
            lowered = normalized.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            merged.append(normalized)
    return merged


def _collect_tag_names(raw: Any) -> list[str]:
    names: list[str] = []
    if raw is None:
        return names
    if isinstance(raw, str):
        value = raw.strip()
        return [value] if value else []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                value = item.strip()
                if value:
                    names.append(value)
                continue
            if isinstance(item, dict):
                for key in ("name", "title", "tag", "label", "genre"):
                    value = item.get(key)
                    if isinstance(value, str) and value.strip():
                        names.append(value.strip())
                        break
        return names
    if isinstance(raw, dict):
        for key in ("name", "title", "tag", "label", "genre"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                names.append(value.strip())
                break
    return names


def extract_tag_names(data: dict[str, Any]) -> list[str]:
    tag_keys = (
        "genres",
        "genre",
        "tags",
        "tag",
        "labels",
        "label",
        "categories",
        "category",
    )
    merged: list[str] = []
    seen: set[str] = set()
    for key in tag_keys:
        for name in _collect_tag_names(data.get(key)):
            normalized = name.strip()
            if not normalized:
                continue
            lowered = normalized.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            merged.append(normalized)
    return merged


def _extract_url_from_raw(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        value = raw.strip()
        return value
    if isinstance(raw, dict):
        for key in ("url", "src", "href", "large", "small", "value"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if isinstance(raw, list):
        for item in raw:
            extracted = _extract_url_from_raw(item)
            if extracted:
                return extracted
    return ""


def extract_cover_url(data: dict[str, Any]) -> str:
    for key in _COVER_KEYS:
        extracted = _extract_url_from_raw(data.get(key))
        if extracted:
            return extracted

    for key in ("images", "covers", "posters", "gallery"):
        extracted = _extract_url_from_raw(data.get(key))
        if extracted:
            return extracted
    return ""


def get_movie_info(movie_code: str, cfg: Config) -> MovieInfo:
    movie_id = movie_code.strip().upper()
    url = f"{cfg.api_base}/movies/{movie_id}"

    with requests.Session() as session:
        # Allow callers to bypass global proxy env for localhost API stability.
        session.trust_env = cfg.use_env_proxy
        response = session.get(url, timeout=cfg.timeout)

    if response.status_code != 200:
        raise RuntimeError(f"API查询失败: {response.status_code} {response.text}")

    data = response.json()
    return MovieInfo(
        movie_id=str(data.get("id") or movie_id),
        title=str(data.get("title") or ""),
        actors=extract_actor_names(data),
        tags=extract_tag_names(data),
        cover_url=extract_cover_url(data),
    )
