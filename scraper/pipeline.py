"""Scraping and optional classification orchestration."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from qwen_classifier.models import ProductClassification

from .config import ScraperSettings, get_scraper_settings
from .crawler import KosikCrawler
from .extraction import extract_product
from .models import ScrapedProduct


class Classifier(Protocol):
    def classify(self, products: list[str], mark_needs_review: bool = False) -> list[ProductClassification]: ...


class ScrapingPipeline:
    def __init__(
        self,
        crawler: KosikCrawler | None = None,
        classifier: Classifier | None = None,
        settings: ScraperSettings | None = None,
    ) -> None:
        self.settings = settings or get_scraper_settings()
        self.crawler = crawler or KosikCrawler(self.settings)
        self.classifier = classifier

    async def scrape(self, url: str, classify: bool | None = None) -> ScrapedProduct:
        product = extract_product(await self.crawler.crawl(url), url)
        enabled = self.settings.classification_enabled if classify is None else classify
        if not enabled:
            return product
        return self.classify_product(product)

    def classify_product(self, product: ScrapedProduct) -> ScrapedProduct:
        if self.classifier is None:
            raise RuntimeError("Classification is enabled but no classifier was provided")
        try:
            result = self.classifier.classify(
                [product.raw_title],
                mark_needs_review=True,
            )
        except Exception as exc:
            raise RuntimeError(f"Product classification failed: {exc}") from exc
        if len(result) != 1:
            raise RuntimeError("Classifier returned an unexpected number of results")
        classification = result[0]
        return product.model_copy(
            update={
                "category": classification.category,
                "subcategory": classification.subcategory,
                "confidence": classification.confidence,
                "needs_review": bool(classification.needs_review),
            }
        )

    async def scrape_many(self, urls: Sequence[str], classify: bool | None = None) -> list[ScrapedProduct]:
        return [await self.scrape(url, classify=classify) for url in urls]
