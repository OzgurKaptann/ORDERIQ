from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class ModifierGroup(Base):
    __tablename__ = "modifier_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    branch_id: Mapped[str] = mapped_column(String(36), ForeignKey("branches.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # single | multiple
    selection_type: Mapped[str] = mapped_column(String(20), default="single")
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    min_select: Mapped[int] = mapped_column(Integer, default=0)
    max_select: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    options: Mapped[list["ModifierOption"]] = relationship(
        "ModifierOption", back_populates="group", cascade="all, delete-orphan"
    )
    product_links: Mapped[list["ProductModifierGroup"]] = relationship(
        "ProductModifierGroup", back_populates="modifier_group"
    )


class ModifierOption(Base):
    __tablename__ = "modifier_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    modifier_group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modifier_groups.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extra_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    group: Mapped["ModifierGroup"] = relationship("ModifierGroup", back_populates="options")


class ProductModifierGroup(Base):
    __tablename__ = "product_modifier_groups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    modifier_group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modifier_groups.id"), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="modifier_groups")
    modifier_group: Mapped["ModifierGroup"] = relationship(
        "ModifierGroup", back_populates="product_links"
    )
