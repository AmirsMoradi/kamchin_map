from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SupermarketBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    status: str
    lat: float
    lng: float


class SupermarketCreate(SupermarketBase):
    pass


class SupermarketUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class SupermarketResponse(SupermarketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
