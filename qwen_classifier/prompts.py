from __future__ import annotations

from typing import Sequence

ALLOWED_CATEGORIES = [
    "masove_vyrobky",
    "mliecne_vyrobky",
    "pekaren",
    "ovocie_zelenina",
    "napoje",
    "mrazene",
    "sladkosti",
    "ine",
]


def build_classification_prompt(products: Sequence[str]) -> str:
    numbered_products = "\n".join(f"{index}. {name}" for index, name in enumerate(products, start=1))
    categories = "\n".join(f"- {category}" for category in ALLOWED_CATEGORIES)
    return (
        "You are a food product classifier.\n"
        "Classify each input product into exactly one category.\n\n"
        "Allowed categories:\n"
        f"{categories}\n\n"
        "Rules:\n"
        "- Return only a JSON array of objects.\n"
        "- No markdown, no comments, no explanations.\n"
        "- Return exactly one object per input product.\n"
        "- Preserve product order from input.\n"
        "- Copy the exact original product name into `name`.\n"
        "- `category` must be exactly one value from the allowed list.\n"
        "- If uncertain, use `category` = `ine`.\n"
        "- `confidence` must be a number from 0 to 1.\n"
        "- Do not add extra fields except optional `subcategory` when useful.\n"
        "- Confidence interpretation:\n"
        "  - 0.90 to 1.00: clear category\n"
        "  - 0.70 to 0.89: probable category\n"
        "  - 0.50 to 0.69: uncertain category\n"
        "  - 0.00 to 0.49: cannot be reliably categorized\n\n"
        "Input products:\n"
        f"{numbered_products}"
    )
