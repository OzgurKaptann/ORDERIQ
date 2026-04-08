from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, get_current_tenant
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TenantResponse,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service, event_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user, tenant = auth_service.register(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    event_service.log(db, "merchant_registered", tenant_id=tenant.id, payload={"slug": tenant.slug})
    db.commit()

    token = auth_service.create_access_token(user)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.login(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = auth_service.create_access_token(user)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return MeResponse(
        user=UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=current_user.role,
            tenant_id=current_user.tenant_id,
            onboarding_completed=current_tenant.onboarding_completed,
        ),
        tenant=TenantResponse(
            id=current_tenant.id,
            business_name=current_tenant.business_name,
            slug=current_tenant.slug,
            business_type=current_tenant.business_type,
            currency=current_tenant.currency,
            onboarding_completed=current_tenant.onboarding_completed,
        ),
    )
