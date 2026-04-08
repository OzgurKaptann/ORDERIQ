from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.catalog import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services import catalog_service, event_service

router = APIRouter(tags=["catalog"])


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return catalog_service.list_categories(db, current_tenant.id)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    cat = catalog_service.create_category(db, current_tenant.id, data)
    event_service.log(db, "category_created", tenant_id=current_tenant.id, payload={"name": data.name})
    db.commit()
    return cat


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        return catalog_service.update_category(db, current_tenant.id, category_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        catalog_service.delete_category(db, current_tenant.id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@router.get("/products", response_model=list[ProductResponse])
def list_products(
    category_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return catalog_service.list_products(db, current_tenant.id, category_id)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        product = catalog_service.create_product(db, current_tenant.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    event_service.log(db, "product_created", tenant_id=current_tenant.id, payload={"name": data.name})
    db.commit()
    return product


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        product = catalog_service.update_product(db, current_tenant.id, product_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    event_service.log(db, "product_updated", tenant_id=current_tenant.id, payload={"product_id": product_id})
    db.commit()
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        catalog_service.delete_product(db, current_tenant.id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
