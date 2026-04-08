from datetime import datetime, timezone

from sqlalchemy import cast, Date, desc, extract, func
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    HourlyOrderEntry,
    HourlyOrdersResponse,
    TopProductEntry,
    TopProductsResponse,
)

# Statuses that count as active/placed orders (excludes cancelled)
_ACTIVE_STATUSES = ("pending", "preparing", "ready", "delivered")


def _today():
    """Server UTC date for V1. Replace with tenant timezone in V2."""
    return datetime.now(timezone.utc).date()


def _base_filter(tenant_id: str):
    """Shared filter: today's non-cancelled orders for this tenant."""
    today = _today()
    return [
        Order.tenant_id == tenant_id,
        cast(Order.placed_at, Date) == today,
        Order.status.in_(_ACTIVE_STATUSES),
    ]


def get_summary(db: Session, tenant_id: str) -> AnalyticsSummaryResponse:
    filters = _base_filter(tenant_id)

    today_order_count: int = (
        db.query(func.count(Order.id)).filter(*filters).scalar() or 0
    )

    today_revenue: float = float(
        db.query(func.sum(Order.total_amount)).filter(*filters).scalar() or 0
    )

    average_basket_value: float = float(
        db.query(func.avg(Order.total_amount)).filter(*filters).scalar() or 0
    )

    return AnalyticsSummaryResponse(
        today_order_count=today_order_count,
        today_revenue=round(today_revenue, 2),
        average_basket_value=round(average_basket_value, 2),
    )


def get_top_products(db: Session, tenant_id: str) -> TopProductsResponse:
    filters = _base_filter(tenant_id)

    rows = (
        db.query(
            OrderItem.product_name_snapshot,
            func.sum(OrderItem.quantity).label("total_quantity"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(*filters)
        .group_by(OrderItem.product_name_snapshot)
        .order_by(desc("total_quantity"))
        .limit(5)
        .all()
    )

    return TopProductsResponse(
        products=[
            TopProductEntry(product_name=row.product_name_snapshot, total_quantity=int(row.total_quantity))
            for row in rows
        ]
    )


def get_hourly_orders(db: Session, tenant_id: str) -> HourlyOrdersResponse:
    filters = _base_filter(tenant_id)

    rows = (
        db.query(
            extract("hour", Order.placed_at).label("hour"),
            func.count(Order.id).label("order_count"),
        )
        .filter(*filters)
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    return HourlyOrdersResponse(
        distribution=[
            HourlyOrderEntry(hour=int(row.hour), order_count=int(row.order_count))
            for row in rows
        ]
    )
