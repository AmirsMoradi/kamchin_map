from __future__ import annotations

from pathlib import Path
from typing import Final

import requests
from fastapi import APIRouter, HTTPException, Response, status
from requests import RequestException

from app.core.config import settings

router = APIRouter(prefix="/map", tags=["map"])

MAPIR_TILE_URL: Final[str] = "https://map.ir/shiveh/normal/z{z}/x{x}/y{y}.png"
OSM_TILE_URL: Final[str] = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
USER_AGENT: Final[str] = "kamchin-map/1.0"
PNG_MEDIA_TYPE: Final[str] = "image/png"
CACHE_CONTROL: Final[str] = "public, max-age=604800, immutable"


def _validate_tile(z: int, x: int, y: int) -> None:
    if z < 0 or z > settings.map_max_zoom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid zoom level.",
        )

    max_index = (2**z) - 1
    if x < 0 or y < 0 or x > max_index or y > max_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tile coordinate.",
        )


def _tile_cache_path(provider: str, z: int, x: int, y: int) -> Path:
    return (
        settings.resolved_map_tile_cache_dir
        / provider
        / str(z)
        / str(x)
        / f"{y}.png"
    )


def _read_cached_tile(provider: str, z: int, x: int, y: int) -> bytes | None:
    path = _tile_cache_path(provider, z, x, y)
    if not path.is_file():
        return None
    return path.read_bytes()


def _write_cached_tile(provider: str, z: int, x: int, y: int, content: bytes) -> None:
    if not settings.map_tile_cache_enabled:
        return

    path = _tile_cache_path(provider, z, x, y)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _request_tile(url: str, provider: str) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    params: dict[str, str] = {}

    if provider == "mapir":
        if not settings.mapir_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MAPIR_API_KEY is not configured.",
            )
        params["x-api-key"] = settings.mapir_api_key

    proxies = settings.map_proxy_config

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            proxies=proxies,
            timeout=settings.map_tile_timeout_seconds,
        )
    except RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Tile provider is unreachable: {exc}",
        ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Tile provider returned HTTP {response.status_code}.",
        )

    content_type = response.headers.get("content-type", "")
    if "image" not in content_type and not response.content.startswith(b"\x89PNG"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Tile provider did not return an image.",
        )

    return response.content


def _provider_url(provider: str, z: int, x: int, y: int) -> str:
    if provider == "mapir":
        return MAPIR_TILE_URL.format(z=z, x=x, y=y)
    if provider == "osm":
        return OSM_TILE_URL.format(z=z, x=x, y=y)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unknown map tile provider.",
    )


def _tile_response(content: bytes) -> Response:
    return Response(
        content=content,
        media_type=PNG_MEDIA_TYPE,
        headers={"Cache-Control": CACHE_CONTROL},
    )


@router.get("/tiles/{z}/{x}/{y}.png")
def get_default_tile(z: int, x: int, y: int) -> Response:
    return get_provider_tile(settings.map_default_provider, z, x, y)


@router.get("/tiles/{provider}/{z}/{x}/{y}.png")
def get_provider_tile(provider: str, z: int, x: int, y: int) -> Response:
    provider = provider.lower().strip()
    _validate_tile(z, x, y)

    if settings.map_tile_cache_enabled:
        cached = _read_cached_tile(provider, z, x, y)
        if cached is not None:
            return _tile_response(cached)

    content = _request_tile(_provider_url(provider, z, x, y), provider)
    _write_cached_tile(provider, z, x, y, content)
    return _tile_response(content)


@router.get("/health")
def get_map_health() -> dict[str, object]:
    return {
        "default_provider": settings.map_default_provider,
        "cache_enabled": settings.map_tile_cache_enabled,
        "cache_dir": str(settings.resolved_map_tile_cache_dir),
        "mapir_configured": bool(settings.mapir_api_key),
        "http_proxy_configured": bool(settings.map_http_proxy),
        "https_proxy_configured": bool(settings.map_https_proxy),
    }
