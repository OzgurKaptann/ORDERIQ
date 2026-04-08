from pydantic import BaseModel


class PublicModifierOption(BaseModel):
    id: str
    name: str
    extra_price: float
    sort_order: int


class PublicModifierGroup(BaseModel):
    id: str
    name: str
    selection_type: str
    is_required: bool
    min_select: int
    max_select: int
    options: list[PublicModifierOption]


class PublicProduct(BaseModel):
    id: str
    name: str
    description: str | None
    image_url: str | None
    base_price: float
    is_in_stock: bool
    prep_time_minutes: int | None
    modifier_groups: list[PublicModifierGroup]


class PublicCategory(BaseModel):
    id: str
    name: str
    sort_order: int
    products: list[PublicProduct]


class PublicMenuResponse(BaseModel):
    tenant_id: str
    business_name: str
    slug: str
    currency: str
    service_mode: str
    accepts_orders: bool
    categories: list[PublicCategory]
