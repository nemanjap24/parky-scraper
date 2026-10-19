from qwen_classifier.prompts import build_classification_prompt


def test_build_classification_prompt_contains_numbered_products_and_rules() -> None:
    prompt = build_classification_prompt(["A", "B"])

    assert "1. A" in prompt
    assert "2. B" in prompt
    assert "- masove_vyrobky" in prompt
    assert "- ine" in prompt
    assert "0.90 to 1.00" in prompt
    assert "0.70 to 0.89" in prompt
    assert "0.50 to 0.69" in prompt
    assert "0.00 to 0.49" in prompt
