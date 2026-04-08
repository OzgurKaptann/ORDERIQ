from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    HourlyOrdersResponse,
    TopProductsResponse,
)
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return analytics_service.get_summary(db, current_tenant.id)


@router.get("/top-products", response_model=TopProductsResponse)
def get_top_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return analytics_service.get_top_products(db, current_tenant.id)


@router.get("/hourly-orders", response_model=HourlyOrdersResponse)
def get_hourly_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return analytics_service.get_hourly_orders(db, current_tenant.id)
