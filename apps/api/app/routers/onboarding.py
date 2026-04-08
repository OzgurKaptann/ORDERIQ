from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.onboarding import ApplyTemplateResponse, OnboardingSetupRequest, OnboardingSetupResponse
from app.services import event_service, onboarding_service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/setup", response_model=OnboardingSetupResponse)
def setup(
    data: OnboardingSetupRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    tenant, branch = onboarding_service.setup(db, current_tenant, data)
    return OnboardingSetupResponse(
        tenant_id=tenant.id,
        business_name=tenant.business_name,
        slug=tenant.slug,
        business_type=tenant.business_type,
        currency=tenant.currency,
        branch_id=branch.id,
        onboarding_completed=tenant.onboarding_completed,
    )


@router.post("/apply-template", response_model=ApplyTemplateResponse)
def apply_template(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    created = onboarding_service.apply_template(db, current_tenant)

    event_service.log(
        db,
        "template_applied",
        tenant_id=current_tenant.id,
        payload={"business_type": current_tenant.business_type, "categories_created": created},
    )
    event_service.log(db, "onboarding_completed", tenant_id=current_tenant.id)
    db.commit()

    msg = (
        f"{created} categories created from '{current_tenant.business_type}' template."
        if created > 0
        else "Template already applied. Onboarding marked complete."
    )
    return ApplyTemplateResponse(
        applied=created > 0,
        categories_created=created,
        message=msg,
    )
