from pydantic import BaseModel, model_validator


# ---------------------------------------------------------------------------
# Modifier Option
# ---------------------------------------------------------------------------

class ModifierOptionCreate(BaseModel):
    name: str
    extra_price: float = 0.0
    sort_order: int = 0


class ModifierOptionUpdate(BaseModel):
    name: str
    extra_price: float = 0.0
    sort_order: int = 0
    is_active: bool = True


class ModifierOptionResponse(BaseModel):
    id: str
    name: str
    extra_price: float
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Modifier Group
# ---------------------------------------------------------------------------

class ModifierGroupCreate(BaseModel):
    name: str
    selection_type: str = "single"  # single | multiple
    is_required: bool = False
    min_select: int = 0
    max_select: int = 1
    options: list[ModifierOptionCreate] = []

    @model_validator(mode="after")
    def validate_select_bounds(self) -> "ModifierGroupCreate":
        if self.min_select > self.max_select:
            raise ValueError("min_select cannot be greater than max_select")
        if self.max_select < 1:
            raise ValueError("max_select must be at least 1")
        return self


class ModifierGroupUpdate(BaseModel):
    name: str | None = None
    selection_type: str | None = None
    is_required: bool | None = None
    min_select: int | None = None
    max_select: int | None = None
    is_active: bool | None = None
    # If provided, fully replaces existing options
    options: list[ModifierOptionUpdate] | None = None

    @model_validator(mode="after")
    def validate_select_bounds(self) -> "ModifierGroupUpdate":
        mn = self.min_select
        mx = self.max_select
        if mn is not None and mx is not None and mn > mx:
            raise ValueError("min_select cannot be greater than max_select")
        return self


class ModifierGroupResponse(BaseModel):
    id: str
    tenant_id: str
    branch_id: str
    name: str
    selection_type: str
    is_required: bool
    min_select: int
    max_select: int
    is_active: bool
    options: list[ModifierOptionResponse]

    model_config = {"from_attributes": True}
