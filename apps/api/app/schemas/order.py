from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Input — public order creation (no auth)
# ---------------------------------------------------------------------------

class OrderItemModifierInput(BaseModel):
    modifier_option_id: str


class OrderItemInput(BaseModel):
    product_id: str
    quantity: int
    modifiers: list[OrderItemModifierInput] = []

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("quantity must be at least 1")
        return v

    @model_validator(mode="after")
    def no_duplicate_modifiers(self) -> "OrderItemInput":
        ids = [m.modifier_option_id for m in self.modifiers]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate modifier_option_id entries are not allowed within a single item")
        return self


class PublicOrderCreateRequest(BaseModel):
    slug: str
    order_type: str  # dine_in | pickup
    table_number: str | None = None
    customer_note: str | None = None
    items: list[OrderItemInput]

    @field_validator("order_type")
    @classmethod
    def valid_order_type(cls, v: str) -> str:
        if v not in ("dine_in", "pickup"):
            raise ValueError("order_type must be 'dine_in' or 'pickup'")
        return v

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


# ---------------------------------------------------------------------------
# Output — public order creation response (minimal, shown on success screen)
# ---------------------------------------------------------------------------

class PublicOrderCreateResponse(BaseModel):
    id: str
    order_number: int
    status: str
    order_type: str
    table_number: str | None
    customer_note: str | None
    total_amount: float
    currency: str
    placed_at: datetime


# ---------------------------------------------------------------------------
# Output — admin / kitchen order responses (full item detail)
# ---------------------------------------------------------------------------

class OrderItemModifierResponse(BaseModel):
    id: str
    modifier_option_id: str
    modifier_name_snapshot: str
    extra_price: float


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name_snapshot: str
    unit_price: float
    quantity: int
    line_total: float
    modifiers: list[OrderItemModifierResponse]


class OrderResponse(BaseModel):
    id: str
    tenant_id: str
    branch_id: str
    order_number: int
    order_type: str
    status: str
    table_number: str | None
    customer_note: str | None
    subtotal: float
    total_amount: float
    currency: str
    placed_at: datetime
    completed_at: datetime | None
    cancelled_at: datetime | None
    items: list[OrderItemResponse]


# ---------------------------------------------------------------------------
# Input — status update (admin/kitchen)
# ---------------------------------------------------------------------------

VALID_STATUSES = {"pending", "preparing", "ready", "delivered", "cancelled"}


class OrderStatusUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {sorted(VALID_STATUSES)}")
        return v
