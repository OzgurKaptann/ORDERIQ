from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.catalog import Category, Product, ProductTag
from app.models.modifier import ModifierGroup, ModifierOption, ProductModifierGroup
from app.models.settings import BusinessSettings
from app.models.tenant import Tenant
from app.schemas.catalog import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate
from app.schemas.public_menu import (
    PublicCategory,
    PublicMenuResponse,
    PublicModifierGroup,
    PublicModifierOption,
    PublicProduct,
)
from app.utils import get_default_branch


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_product_response(product: Product) -> dict:
    return {
        "id": product.id,
        "tenant_id": product.tenant_id,
        "branch_id": product.branch_id,
        "category_id": product.category_id,
        "name": product.name,
        "description": product.description,
        "image_url": product.image_url,
        "base_price": float(product.base_price),
        "is_active": product.is_active,
        "is_in_stock": product.is_in_stock,
        "prep_time_minutes": product.prep_time_minutes,
        "tags": [t.tag for t in product.tags],
        "modifier_group_ids": [pmg.modifier_group_id for pmg in product.modifier_groups],
        "created_at": product.created_at,
    }


def _assert_category_belongs_to_tenant(db: Session, category_id: str, tenant_id: str) -> Category:
    cat = db.query(Category).filter(
        Category.id == category_id, Category.tenant_id == tenant_id
    ).first()
    if not cat:
        raise ValueError("Category not found")
    return cat


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def list_categories(db: Session, tenant_id: str) -> list[Category]:
    branch = get_default_branch(db, tenant_id)
    return (
        db.query(Category)
        .filter(Category.tenant_id == tenant_id, Category.branch_id == branch.id)
        .order_by(Category.sort_order)
        .all()
    )


def create_category(db: Session, tenant_id: str, data: CategoryCreate) -> Category:
    branch = get_default_branch(db, tenant_id)
    cat = Category(
        id=str(uuid4()),
        tenant_id=tenant_id,
        branch_id=branch.id,
        name=data.name,
        sort_order=data.sort_order,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, tenant_id: str, category_id: str, data: CategoryUpdate) -> Category:
    cat = db.query(Category).filter(
        Category.id == category_id, Category.tenant_id == tenant_id
    ).first()
    if not cat:
        raise ValueError("Category not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)

    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, tenant_id: str, category_id: str) -> None:
    cat = db.query(Category).filter(
        Category.id == category_id, Category.tenant_id == tenant_id
    ).first()
    if not cat:
        raise ValueError("Category not found")
    cat.is_active = False
    db.commit()


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def list_products(db: Session, tenant_id: str, category_id: str | None = None) -> list[dict]:
    branch = get_default_branch(db, tenant_id)
    q = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.branch_id == branch.id,
    )
    if category_id:
        q = q.filter(Product.category_id == category_id)
    products = q.order_by(Product.created_at).all()
    return [_build_product_response(p) for p in products]


def create_product(db: Session, tenant_id: str, data: ProductCreate) -> dict:
    branch = get_default_branch(db, tenant_id)
    _assert_category_belongs_to_tenant(db, data.category_id, tenant_id)

    # Validate modifier group IDs belong to this tenant
    if data.modifier_group_ids:
        valid_ids = {
            r.id
            for r in db.query(ModifierGroup.id).filter(
                ModifierGroup.id.in_(data.modifier_group_ids),
                ModifierGroup.tenant_id == tenant_id,
            ).all()
        }
        invalid = set(data.modifier_group_ids) - valid_ids
        if invalid:
            raise ValueError(f"Modifier group IDs not found: {invalid}")

    product = Product(
        id=str(uuid4()),
        tenant_id=tenant_id,
        branch_id=branch.id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        image_url=data.image_url,
        base_price=data.base_price,
        is_in_stock=data.is_in_stock,
        prep_time_minutes=data.prep_time_minutes,
    )
    db.add(product)
    db.flush()

    for tag in data.tags:
        db.add(ProductTag(id=str(uuid4()), product_id=product.id, tag=tag))

    for mg_id in data.modifier_group_ids:
        db.add(ProductModifierGroup(id=str(uuid4()), product_id=product.id, modifier_group_id=mg_id))

    db.commit()
    db.refresh(product)
    return _build_product_response(product)


def update_product(db: Session, tenant_id: str, product_id: str, data: ProductUpdate) -> dict:
    product = db.query(Product).filter(
        Product.id == product_id, Product.tenant_id == tenant_id
    ).first()
    if not product:
        raise ValueError("Product not found")

    updates = data.model_dump(exclude_unset=True)

    # Handle tags replacement separately
    new_tags = updates.pop("tags", None)
    new_modifier_group_ids = updates.pop("modifier_group_ids", None)

    if "category_id" in updates:
        _assert_category_belongs_to_tenant(db, updates["category_id"], tenant_id)

    for field, value in updates.items():
        setattr(product, field, value)

    if new_tags is not None:
        for existing_tag in product.tags:
            db.delete(existing_tag)
        db.flush()
        for tag in new_tags:
            db.add(ProductTag(id=str(uuid4()), product_id=product.id, tag=tag))

    if new_modifier_group_ids is not None:
        if new_modifier_group_ids:
            valid_ids = {
                r.id
                for r in db.query(ModifierGroup.id).filter(
                    ModifierGroup.id.in_(new_modifier_group_ids),
                    ModifierGroup.tenant_id == tenant_id,
                ).all()
            }
            invalid = set(new_modifier_group_ids) - valid_ids
            if invalid:
                raise ValueError(f"Modifier group IDs not found: {invalid}")

        for existing_link in product.modifier_groups:
            db.delete(existing_link)
        db.flush()
        for mg_id in new_modifier_group_ids:
            db.add(ProductModifierGroup(id=str(uuid4()), product_id=product.id, modifier_group_id=mg_id))

    db.commit()
    db.refresh(product)
    return _build_product_response(product)


def delete_product(db: Session, tenant_id: str, product_id: str) -> None:
    product = db.query(Product).filter(
        Product.id == product_id, Product.tenant_id == tenant_id
    ).first()
    if not product:
        raise ValueError("Product not found")
    product.is_active = False
    db.commit()


# ---------------------------------------------------------------------------
# Public menu (no auth — called by customer-facing endpoints)
# ---------------------------------------------------------------------------

def get_public_menu(db: Session, slug: str) -> PublicMenuResponse:
    tenant = db.query(Tenant).filter(Tenant.slug == slug, Tenant.is_active == True).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    branch = get_default_branch(db, tenant.id)

    biz_settings = (
        db.query(BusinessSettings)
        .filter(
            BusinessSettings.tenant_id == tenant.id,
            BusinessSettings.branch_id == branch.id,
        )
        .first()
    )
    service_mode = biz_settings.service_mode if biz_settings else "both"
    accepts_orders = biz_settings.accepts_orders if biz_settings else True

    categories = (
        db.query(Category)
        .filter(
            Category.tenant_id == tenant.id,
            Category.branch_id == branch.id,
            Category.is_active == True,
        )
        .order_by(Category.sort_order)
        .all()
    )

    result_categories: list[PublicCategory] = []

    for cat in categories:
        products = (
            db.query(Product)
            .filter(
                Product.category_id == cat.id,
                Product.tenant_id == tenant.id,
                Product.is_active == True,
            )
            .all()
        )

        result_products: list[PublicProduct] = []
        for product in products:
            # Fetch linked modifier groups with active options only
            mg_ids = [pmg.modifier_group_id for pmg in product.modifier_groups]
            result_groups: list[PublicModifierGroup] = []

            if mg_ids:
                groups = (
                    db.query(ModifierGroup)
                    .filter(
                        ModifierGroup.id.in_(mg_ids),
                        ModifierGroup.is_active == True,
                    )
                    .all()
                )
                for grp in groups:
                    active_options = [o for o in grp.options if o.is_active]
                    result_groups.append(
                        PublicModifierGroup(
                            id=grp.id,
                            name=grp.name,
                            selection_type=grp.selection_type,
                            is_required=grp.is_required,
                            min_select=grp.min_select,
                            max_select=grp.max_select,
                            options=[
                                PublicModifierOption(
                                    id=o.id,
                                    name=o.name,
                                    extra_price=float(o.extra_price),
                                    sort_order=o.sort_order,
                                )
                                for o in sorted(active_options, key=lambda x: x.sort_order)
                            ],
                        )
                    )

            result_products.append(
                PublicProduct(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    image_url=product.image_url,
                    base_price=float(product.base_price),
                    is_in_stock=product.is_in_stock,
                    prep_time_minutes=product.prep_time_minutes,
                    modifier_groups=result_groups,
                )
            )

        result_categories.append(
            PublicCategory(
                id=cat.id,
                name=cat.name,
                sort_order=cat.sort_order,
                products=result_products,
            )
        )

    return PublicMenuResponse(
        tenant_id=tenant.id,
        business_name=tenant.business_name,
        slug=tenant.slug,
        currency=tenant.currency,
        service_mode=service_mode,
        accepts_orders=accepts_orders,
        categories=result_categories,
    )
