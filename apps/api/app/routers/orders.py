from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.order import (
    OrderResponse,
    OrderStatusUpdateRequest,
    PublicOrderCreateRequest,
    PublicOrderCreateResponse,
)
from app.services import event_service, order_service

router = APIRouter(tags=["orders"])


# ---------------------------------------------------------------------------
# Public — guest checkout, no auth
# ---------------------------------------------------------------------------

@router.post(
    "/public/orders",
    response_model=PublicOrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(data: PublicOrderCreateRequest, db: Session = Depends(get_db)):
    """
    Guest order submission. Tenant is resolved from slug in the request body.
    All prices are calculated server-side. Client-supplied prices are ignored.
    """
    try:
        result = order_service.create_public_order(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    tenant_id = result.pop("_tenant_id")
    event_service.log(
        db,
        "order_placed",
        tenant_id=tenant_id,
        payload={
            "order_id": result["id"],
            "order_number": result["order_number"],
            "total_amount": result["total_amount"],
        },
    )
    db.commit()

    return result


# ---------------------------------------------------------------------------
# Admin / kitchen — JWT required
# ---------------------------------------------------------------------------

@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Comma-separated statuses: pending,preparing",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return order_service.list_orders(db, current_tenant.id, status_filter)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return order_service.get_order(db, current_tenant.id, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    data: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    result = order_service.update_order_status(db, current_tenant.id, order_id, data.status)

    event_service.log(
        db,
        "order_status_changed",
        tenant_id=current_tenant.id,
        payload={"order_id": order_id, "new_status": data.status},
    )
    db.commit()

    return result
