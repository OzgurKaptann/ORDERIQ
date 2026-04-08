from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import Product
from app.models.modifier import ModifierGroup, ModifierOption, ProductModifierGroup
from app.models.order import Order, OrderItem, OrderItemModifier
from app.models.tenant import Tenant
from app.schemas.order import (
    OrderItemInput,
    OrderResponse,
    PublicOrderCreateRequest,
    PublicOrderCreateResponse,
)
from app.utils import get_default_branch

# ---------------------------------------------------------------------------
# Allowed status transitions
# ---------------------------------------------------------------------------

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["preparing", "cancelled"],
    "preparing": ["ready", "cancelled"],
    "ready": ["delivered"],
    "delivered": [],
    "cancelled": [],
}


# ---------------------------------------------------------------------------
# Internal serializer (handles Decimal → float explicitly)
# ---------------------------------------------------------------------------

def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "tenant_id": order.tenant_id,
        "branch_id": order.branch_id,
        "order_number": order.order_number,
        "order_type": order.order_type,
        "status": order.status,
        "table_number": order.table_number,
        "customer_note": order.customer_note,
        "subtotal": float(order.subtotal),
        "total_amount": float(order.total_amount),
        "currency": order.currency,
        "placed_at": order.placed_at,
        "completed_at": order.completed_at,
        "cancelled_at": order.cancelled_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name_snapshot": item.product_name_snapshot,
                "unit_price": float(item.unit_price),
                "quantity": item.quantity,
                "line_total": float(item.line_total),
                "modifiers": [
                    {
                        "id": mod.id,
                        "modifier_option_id": mod.modifier_option_id,
                        "modifier_name_snapshot": mod.modifier_name_snapshot,
                        "extra_price": float(mod.extra_price),
                    }
                    for mod in item.modifiers
                ],
            }
            for item in order.items
        ],
    }


# ---------------------------------------------------------------------------
# Item validation + price calculation
# ---------------------------------------------------------------------------

def _validate_and_price_item(
    db: Session,
    tenant_id: str,
    branch_id: str,
    item_input: OrderItemInput,
) -> tuple[dict, list[dict]]:
    """
    Validates a single order item against DB state.
    Returns (item_fields_dict, list_of_modifier_fields_dicts).
    Raises ValueError with a clear message on any validation failure.
    All prices are calculated server-side from DB values — client prices are ignored.
    """
    product = (
        db.query(Product)
        .filter(
            Product.id == item_input.product_id,
            Product.tenant_id == tenant_id,
            Product.branch_id == branch_id,
            Product.is_active == True,
            Product.is_in_stock == True,
        )
        .first()
    )
    if not product:
        raise ValueError(
            f"Product '{item_input.product_id}' is not available "
            "(not found, inactive, or out of stock)"
        )

    # --- Resolve submitted modifier options ---
    submitted_option_ids = [m.modifier_option_id for m in item_input.modifiers]
    submitted_options: dict[str, ModifierOption] = {}

    if submitted_option_ids:
        found_options = (
            db.query(ModifierOption)
            .filter(
                ModifierOption.id.in_(submitted_option_ids),
                ModifierOption.is_active == True,
            )
            .all()
        )
        submitted_options = {o.id: o for o in found_options}

        missing = set(submitted_option_ids) - set(submitted_options.keys())
        if missing:
            raise ValueError(f"Modifier options not found or inactive: {missing}")

    # --- Get all modifier groups linked to this product ---
    product_mg_ids: set[str] = {
        pmg.modifier_group_id for pmg in product.modifier_groups
    }

    # --- Verify no submitted option belongs to an unlinked group ---
    for opt in submitted_options.values():
        if opt.modifier_group_id not in product_mg_ids:
            raise ValueError(
                f"Modifier option '{opt.id}' does not belong to any group "
                f"linked to product '{product.id}'"
            )

    # --- Per-group validation (required, min/max) ---
    if product_mg_ids:
        active_groups = (
            db.query(ModifierGroup)
            .filter(
                ModifierGroup.id.in_(product_mg_ids),
                ModifierGroup.is_active == True,
            )
            .all()
        )

        # Group submitted options by modifier_group_id
        selected_by_group: dict[str, list[ModifierOption]] = {g.id: [] for g in active_groups}
        for opt in submitted_options.values():
            if opt.modifier_group_id in selected_by_group:
                selected_by_group[opt.modifier_group_id].append(opt)

        for group in active_groups:
            count = len(selected_by_group[group.id])

            if group.is_required and count < group.min_select:
                raise ValueError(
                    f"Modifier group '{group.name}' is required and needs "
                    f"at least {group.min_select} selection(s), but got {count}"
                )

            if count > group.max_select:
                raise ValueError(
                    f"Modifier group '{group.name}' allows at most "
                    f"{group.max_select} selection(s), but got {count}"
                )

    # --- Calculate prices from DB values only ---
    modifier_extra = sum(float(o.extra_price) for o in submitted_options.values())
    unit_price = round(float(product.base_price) + modifier_extra, 2)
    line_total = round(unit_price * item_input.quantity, 2)

    item_fields = {
        "product": product,
        "unit_price": unit_price,
        "quantity": item_input.quantity,
        "line_total": line_total,
    }

    modifier_fields = [
        {
            "option_id": opt_id,
            "modifier_name_snapshot": submitted_options[opt_id].name,
            "extra_price": float(submitted_options[opt_id].extra_price),
        }
        for opt_id in submitted_option_ids  # preserve submission order
    ]

    return item_fields, modifier_fields


# ---------------------------------------------------------------------------
# Public: create order (no auth)
# ---------------------------------------------------------------------------

def create_public_order(db: Session, data: PublicOrderCreateRequest) -> dict:
    tenant = (
        db.query(Tenant)
        .filter(Tenant.slug == data.slug, Tenant.is_active == True)
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    branch = get_default_branch(db, tenant.id)

    # --- Validate all items and price them before writing anything ---
    validated_items: list[tuple[dict, list[dict]]] = []
    for item_input in data.items:
        item_fields, modifier_fields = _validate_and_price_item(
            db, tenant.id, branch.id, item_input
        )
        validated_items.append((item_fields, modifier_fields))

    # --- Calculate totals ---
    subtotal = round(sum(item["line_total"] for item, _ in validated_items), 2)
    total_amount = subtotal  # no tax, no discounts in V1

    # --- Assign order_number (MAX + 1 per tenant) ---
    max_num = (
        db.query(func.max(Order.order_number))
        .filter(Order.tenant_id == tenant.id)
        .scalar()
    )
    order_number = (max_num or 0) + 1

    # --- Create order ---
    order = Order(
        id=str(uuid4()),
        tenant_id=tenant.id,
        branch_id=branch.id,
        order_number=order_number,
        order_type=data.order_type,
        status="pending",
        table_number=data.table_number,
        customer_note=data.customer_note,
        subtotal=subtotal,
        total_amount=total_amount,
        currency=tenant.currency,
    )
    db.add(order)
    db.flush()

    for item_fields, modifier_fields in validated_items:
        product = item_fields["product"]
        order_item = OrderItem(
            id=str(uuid4()),
            order_id=order.id,
            product_id=product.id,
            product_name_snapshot=product.name,
            unit_price=item_fields["unit_price"],
            quantity=item_fields["quantity"],
            line_total=item_fields["line_total"],
        )
        db.add(order_item)
        db.flush()

        for mod in modifier_fields:
            db.add(
                OrderItemModifier(
                    id=str(uuid4()),
                    order_item_id=order_item.id,
                    modifier_option_id=mod["option_id"],
                    modifier_name_snapshot=mod["modifier_name_snapshot"],
                    extra_price=mod["extra_price"],
                )
            )

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        # tenant_id included so the router can log events; not exposed in PublicOrderCreateResponse
        "_tenant_id": tenant.id,
        "order_number": order.order_number,
        "status": order.status,
        "order_type": order.order_type,
        "table_number": order.table_number,
        "customer_note": order.customer_note,
        "total_amount": float(order.total_amount),
        "currency": order.currency,
        "placed_at": order.placed_at,
    }


# ---------------------------------------------------------------------------
# Admin: list orders (with kitchen-ready detail)
# ---------------------------------------------------------------------------

def list_orders(
    db: Session,
    tenant_id: str,
    status_filter: str | None = None,
) -> list[dict]:
    q = (
        db.query(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.modifiers))
        .filter(Order.tenant_id == tenant_id)
    )

    if status_filter:
        statuses = [s.strip() for s in status_filter.split(",") if s.strip()]
        q = q.filter(Order.status.in_(statuses))

    orders = q.order_by(Order.placed_at.desc()).all()
    return [_serialize_order(o) for o in orders]


# ---------------------------------------------------------------------------
# Admin: get single order
# ---------------------------------------------------------------------------

def get_order(db: Session, tenant_id: str, order_id: str) -> dict:
    order = (
        db.query(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.modifiers))
        .filter(Order.id == order_id, Order.tenant_id == tenant_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _serialize_order(order)


# ---------------------------------------------------------------------------
# Admin/kitchen: update order status
# ---------------------------------------------------------------------------

def update_order_status(
    db: Session,
    tenant_id: str,
    order_id: str,
    new_status: str,
) -> dict:
    order = (
        db.query(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.modifiers))
        .filter(Order.id == order_id, Order.tenant_id == tenant_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    allowed = ALLOWED_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Cannot transition order from '{order.status}' to '{new_status}'. "
                f"Allowed transitions from '{order.status}': {allowed or ['none']}"
            ),
        )

    order.status = new_status

    now = datetime.now(timezone.utc)
    if new_status == "delivered":
        order.completed_at = now
    elif new_status == "cancelled":
        order.cancelled_at = now

    db.commit()
    db.refresh(order)
    return _serialize_order(order)
