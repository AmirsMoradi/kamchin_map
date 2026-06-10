from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="kamchin_map", alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")

    map_default_provider: Literal["mapir", "osm"] = Field(
        default="mapir",
        alias="MAP_DEFAULT_PROVIDER",
    )
    mapir_api_key: str | None = Field(default=None, alias="MAPIR_API_KEY")
    map_tile_cache_enabled: bool = Field(default=True, alias="MAP_TILE_CACHE_ENABLED")
    map_tile_cache_dir: Path = Field(
        default=BASE_DIR / "data" / "tile_cache",
        alias="MAP_TILE_CACHE_DIR",
    )
    map_tile_timeout_seconds: float = Field(
        default=6.0,
        alias="MAP_TILE_TIMEOUT_SECONDS",
    )
    map_max_zoom: int = Field(default=19, alias="MAP_MAX_ZOOM")
    map_http_proxy: str | None = Field(default=None, alias="MAP_HTTP_PROXY")
    map_https_proxy: str | None = Field(default=None, alias="MAP_HTTPS_PROXY")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def map_proxy_config(self) -> dict[str, str] | None:
        proxies: dict[str, str] = {}
        if self.map_http_proxy:
            proxies["http"] = self.map_http_proxy
        if self.map_https_proxy:
            proxies["https"] = self.map_https_proxy
        return proxies or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
