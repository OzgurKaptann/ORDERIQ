from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid4())


class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    branch_id: Mapped[str] = mapped_column(String(36), ForeignKey("branches.id"), nullable=False)
    # dine_in | pickup | both
    service_mode: Mapped[str] = mapped_column(String(20), default="both")
    accepts_orders: Mapped[bool] = mapped_column(Boolean, default=True)
    opening_hours_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme_json: Mapped[str | None] = mapped_column(Text, nullable=True)
