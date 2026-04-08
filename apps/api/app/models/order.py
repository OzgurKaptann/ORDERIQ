from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    branch_id: Mapped[str] = mapped_column(String(36), ForeignKey("branches.id"), nullable=False)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # dine_in | pickup
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # pending | preparing | ready | delivered | cancelled
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    table_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="TRY")
    placed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    product_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    modifiers: Mapped[list["OrderItemModifier"]] = relationship(
        "OrderItemModifier", back_populates="order_item", cascade="all, delete-orphan"
    )


class OrderItemModifier(Base):
    __tablename__ = "order_item_modifiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("order_items.id"), nullable=False)
    modifier_option_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modifier_options.id"), nullable=False
    )
    modifier_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    extra_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)

    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="modifiers")
