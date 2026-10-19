from pathlib import Path

from scraper.extraction import extract_product


FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample_kosik_product.html"


def test_extracts_product_fields() -> None:
    product = extract_product(FIXTURE.read_text(encoding="utf-8"), "https://www.kosik.sk/product/milk")
    assert product.raw_title == "K-Classic Mlieko plnotucne 1 l"
    assert product.price == 0.89
    assert product.regular_price == 1.09
    assert product.is_discounted is True
    assert product.unit == "l"


def test_missing_values_are_none() -> None:
    product = extract_product("<html><h1 class='product-title'>Plain item</h1></html>", "https://www.kosik.sk/product/plain")
    assert product.price is None
    assert product.regular_price is None
    assert product.availability is None
