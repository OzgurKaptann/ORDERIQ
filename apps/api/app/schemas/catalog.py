from datetime import datetime

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryCreate(BaseModel):
    name: str
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: str
    tenant_id: str
    branch_id: str
    name: str
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    category_id: str
    name: str
    description: str | None = None
    image_url: str | None = None
    base_price: float
    is_in_stock: bool = True
    prep_time_minutes: int | None = None
    tags: list[str] = []
    modifier_group_ids: list[str] = []

    @field_validator("base_price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("base_price must be >= 0")
        return v


class ProductUpdate(BaseModel):
    category_id: str | None = None
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    base_price: float | None = None
    is_active: bool | None = None
    is_in_stock: bool | None = None
    prep_time_minutes: int | None = None
    # If provided, replaces existing tags entirely
    tags: list[str] | None = None
    # If provided, replaces modifier group links entirely
    modifier_group_ids: list[str] | None = None

    @field_validator("base_price")
    @classmethod
    def price_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("base_price must be >= 0")
        return v


class ProductResponse(BaseModel):
    id: str
    tenant_id: str
    branch_id: str
    category_id: str
    name: str
    description: str | None
    image_url: str | None
    base_price: float
    is_active: bool
    is_in_stock: bool
    prep_time_minutes: int | None
    tags: list[str]
    modifier_group_ids: list[str]
    created_at: datetime
