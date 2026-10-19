"""Typed scraper data models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictFloat


class ScrapedProduct(BaseModel):
    model_config = ConfigDict(extra="forbid")

    retailer: str = "Kosik"
    url: str
    scraped_at: datetime
    raw_title: str
    brand: str | None = None
    price: StrictFloat | None = None
    regular_price: StrictFloat | None = None
    price_per_unit: StrictFloat | None = None
    unit: Literal["kg", "g", "l", "ml", "ks"] | None = None
    weight_or_volume: str | None = None
    is_discounted: bool = False
    availability: str | None = None
    category: str | None = None
    subcategory: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    needs_review: bool = False
