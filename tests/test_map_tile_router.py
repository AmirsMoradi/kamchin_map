from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.map_tile_router import _provider_url, _validate_tile


def test_validate_tile_accepts_valid_coordinate() -> None:
    _validate_tile(z=11, x=1316, y=805)


@pytest.mark.parametrize(
    ("z", "x", "y"),
    [(-1, 0, 0), (20, 0, 0), (2, -1, 0), (2, 0, 4)],
)
def test_validate_tile_rejects_invalid_coordinate(z: int, x: int, y: int) -> None:
    with pytest.raises(HTTPException):
        _validate_tile(z=z, x=x, y=y)


def test_provider_url_builds_mapir_url() -> None:
    assert _provider_url("mapir", 11, 1316, 805).endswith(
        "/shiveh/normal/z11/x1316/y805.png"
    )


def test_provider_url_builds_osm_url() -> None:
    assert _provider_url("osm", 11, 1316, 805) == (
        "https://tile.openstreetmap.org/11/1316/805.png"
    )
