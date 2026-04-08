from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.catalog import Category
from app.models.tenant import Tenant
from app.schemas.onboarding import OnboardingSetupRequest
from app.seeds.templates import get_template_categories
from app.utils import get_default_branch


def setup(db: Session, tenant: Tenant, data: OnboardingSetupRequest) -> tuple[Tenant, object]:
    """Update tenant business info and default branch details."""
    if data.business_name is not None:
        tenant.business_name = data.business_name
    if data.business_type is not None:
        tenant.business_type = data.business_type
    if data.currency is not None:
        tenant.currency = data.currency

    branch = get_default_branch(db, tenant.id)

    if data.branch_city is not None:
        branch.city = data.branch_city
    if data.branch_district is not None:
        branch.district = data.branch_district
    if data.branch_address is not None:
        branch.address = data.branch_address

    db.commit()
    db.refresh(tenant)
    db.refresh(branch)
    return tenant, branch


def apply_template(db: Session, tenant: Tenant) -> int:
    """
    Seeds starter categories from the business-type template.
    Idempotent: if categories already exist for this branch, does nothing new
    but still marks onboarding complete.
    Returns count of categories created.
    """
    branch = get_default_branch(db, tenant.id)

    existing_count = (
        db.query(Category)
        .filter(Category.tenant_id == tenant.id, Category.branch_id == branch.id)
        .count()
    )

    created = 0
    if existing_count == 0:
        category_names = get_template_categories(tenant.business_type)
        for i, name in enumerate(category_names):
            cat = Category(
                id=str(uuid4()),
                tenant_id=tenant.id,
                branch_id=branch.id,
                name=name,
                sort_order=i,
            )
            db.add(cat)
            created += 1

    tenant.onboarding_completed = True
    db.commit()
    return created
