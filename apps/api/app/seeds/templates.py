"""
Deterministic business-type template seeds.
These are category name lists only — no products.
The merchant populates products after onboarding.
"""

TEMPLATES: dict[str, list[str]] = {
    "waffle": ["Wafflelar", "Soslar", "Meyveler", "Süslemeler", "İçecekler"],
    "kumpir": ["Kumpirler", "Ek Malzemeler", "Soslar", "İçecekler"],
    "midye": ["Midyeler", "Ek Ürünler", "İçecekler"],
    "other": ["Ürünler", "İçecekler"],
}


def get_template_categories(business_type: str) -> list[str]:
    return TEMPLATES.get(business_type, TEMPLATES["other"])
