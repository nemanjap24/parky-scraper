from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProductClassification(BaseModel):
    name: str
    category: Literal[
        "masove_vyrobky",
        "mliecne_vyrobky",
        "pekaren",
        "ovocie_zelenina",
        "napoje",
        "mrazene",
        "sladkosti",
        "ine",
    ]
    subcategory: str | None = None
    confidence: float = Field(ge=0, le=1)
    needs_review: bool | None = None


class ClassificationResponse(BaseModel):
    products: list[ProductClassification]
