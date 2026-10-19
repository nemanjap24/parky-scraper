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


def test_uses_rendered_data_testid_and_meta_title() -> None:
    html = """
    <meta property="og:title" content="Fallback title">
    <div data-testid="product-title">Rendered title</div>
    <span data-testid="product-price">2,49 €</span>
    """
    product = extract_product(html, "https://www.kosik.sk/product/rendered")
    assert product.raw_title == "Rendered title"
    assert product.price == 2.49


def test_unit_comes_from_price_per_unit_before_product_size() -> None:
    html = """
    <h1 data-tid="product-detail__product-name">Frozen fries</h1>
    <p data-tid="product-detail__product-weight">750 g</p>
    <section data-tid="pbox-price"><span>1,59</span></section>
    <s data-tid="product-box__crossed-price">2,89</s>
    <div data-tid="pbox-price-per-unit"><span>2,12</span><span>€/kg</span></div>
    """
    product = extract_product(html, "https://www.kosik.sk/product/fries")
    assert product.unit == "kg"
