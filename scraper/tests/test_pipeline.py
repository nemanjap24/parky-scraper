import asyncio
import pytest

from qwen_classifier.models import ProductClassification
from scraper.config import ScraperSettings
from scraper.pipeline import ScrapingPipeline


class FakeCrawler:
    async def crawl(self, url: str) -> str:
        return "<h1 class='product-title'>Milk</h1><span class='sale-price'>1,00 €</span>"


class FakeClassifier:
    def classify(self, products: list[str], mark_needs_review: bool = False) -> list[ProductClassification]:
        return [ProductClassification(name=products[0], category="mliecne_vyrobky", subcategory="mlieko", confidence=0.9, needs_review=False)]


def test_classification_is_merged() -> None:
    pipeline = ScrapingPipeline(FakeCrawler(), FakeClassifier(), ScraperSettings(classification_enabled=True))
    product = asyncio.run(pipeline.scrape("https://www.kosik.sk/product/milk"))
    assert product.category == "mliecne_vyrobky"
    assert product.subcategory == "mlieko"


def test_classification_can_be_disabled() -> None:
    pipeline = ScrapingPipeline(FakeCrawler(), FakeClassifier(), ScraperSettings(classification_enabled=False))
    product = asyncio.run(pipeline.scrape("https://www.kosik.sk/product/milk"))
    assert product.category is None


def test_classifier_failure_is_clear() -> None:
    class BrokenClassifier(FakeClassifier):
        def classify(self, products: list[str], mark_needs_review: bool = False) -> list[ProductClassification]:
            raise RuntimeError("service unavailable")

    pipeline = ScrapingPipeline(FakeCrawler(), BrokenClassifier(), ScraperSettings(classification_enabled=True))
    with pytest.raises(RuntimeError, match="Product classification failed"):
        asyncio.run(pipeline.scrape("https://www.kosik.sk/product/milk"))
