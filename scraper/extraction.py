"""Deterministic extraction of product fields from rendered HTML."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser

from .models import ScrapedProduct


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.current: list[str] = []
        self.classes: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            return
        self.classes.append(
            " ".join(
                [
                    tag,
                    attrs_dict.get("class", "") or "",
                    attrs_dict.get("id", "") or "",
                    attrs_dict.get("data-tid", "") or "",
                    attrs_dict.get("data-testid", "") or "",
                    attrs_dict.get("aria-label", "") or "",
                ]
            ).lower()
        )

    def handle_endtag(self, tag: str) -> None:
        if self.classes:
            self.classes.pop()

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        self.parts.append(text)
        self.current.append(" ".join(self.classes) + "\t" + text)


def _fields(html: str) -> list[tuple[str, str]]:
    parser = _TextParser()
    parser.feed(html)
    return [tuple(item.split("\t", 1)) for item in parser.current if "\t" in item]


def _meta(html: str, key: str) -> str | None:
    pattern = re.compile(
        rf"<meta[^>]+(?:property|name)=[\"'][^\"']*{re.escape(key)}[^\"']*[\"'][^>]+content=[\"']([^\"']+)",
        re.IGNORECASE,
    )
    match = pattern.search(html)
    return " ".join(match.group(1).split()) if match else None


def _first_text(fields: list[tuple[str, str]], patterns: tuple[str, ...]) -> str | None:
    for context, text in fields:
        if any(pattern in context for pattern in patterns):
            return text
    return None


def _combined_text(fields: list[tuple[str, str]], patterns: tuple[str, ...]) -> str | None:
    values = [text for context, text in fields if any(pattern in context for pattern in patterns)]
    return " ".join(values) if values else None


def _price(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"\d+(?:[,.]\d{1,2})?", value.replace("\xa0", " "))
    return float(match.group(0).replace(",", ".")) if match else None


def _unit(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"\b(kg|g|l|ml|ks)\b", value.lower())
    return match.group(1) if match else None


def extract_product(page_content: str, url: str) -> ScrapedProduct:
    fields = _fields(page_content)
    title = _first_text(
        fields,
        (
            "product-title",
            "product_name",
            "product-name",
            "producttitle",
            "product-detail__product-name",
        ),
    )
    title = title or _meta(page_content, "og:title")
    title = title or next((text for context, text in fields if context.startswith("h1 ")), "Unknown product")
    current = _first_text(fields, ("pbox-price", "price", "sale-price", "current-price"))
    regular = _first_text(
        fields,
        ("product-box__crossed-price", "regular-price", "old-price", "original-price"),
    )
    unit_price = _combined_text(
        fields,
        ("pbox-price-per-unit", "price-per-unit", "unit-price", "priceperunit"),
    )
    weight = _first_text(
        fields,
        ("product-detail__product-weight", "weight", "volume", "quantity", "size"),
    )
    availability = _first_text(
        fields,
        ("availability", "stock", "in-stock", "product-to-cart__to-cart"),
    )
    brand = _first_text(fields, ("product-detail__main-info__info_brand",))
    price_value = _price(current)
    regular_value = _price(regular)
    unit_value = _unit(unit_price) or _unit(weight)
    discounted = regular_value is not None and price_value is not None and regular_value > price_value
    return ScrapedProduct(
        url=url,
        scraped_at=datetime.now(timezone.utc),
        raw_title=title,
        brand=brand,
        price=price_value,
        regular_price=regular_value,
        price_per_unit=_price(unit_price),
        unit=unit_value,
        weight_or_volume=weight,
        is_discounted=discounted,
        availability=availability,
    )
