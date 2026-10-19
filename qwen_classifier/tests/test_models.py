import pytest
from pydantic import ValidationError

from qwen_classifier.models import ClassificationResponse, ProductClassification


def test_valid_classification_response() -> None:
    response = ClassificationResponse(
        products=[
            ProductClassification(
                name="K-Classic Dušená šunka výberová 100 g",
                category="masove_vyrobky",
                subcategory="sunka",
                confidence=0.98,
            )
        ]
    )

    assert response.products[0].category == "masove_vyrobky"


def test_invalid_category() -> None:
    with pytest.raises(ValidationError):
        ProductClassification(name="Test", category="zle", confidence=0.8)


def test_confidence_out_of_range() -> None:
    with pytest.raises(ValidationError):
        ProductClassification(name="Test", category="ine", confidence=1.2)
