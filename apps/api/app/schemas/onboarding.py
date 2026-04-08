from pydantic import BaseModel


class OnboardingSetupRequest(BaseModel):
    """Updates tenant + default branch business details. All fields optional."""
    business_name: str | None = None
    business_type: str | None = None
    currency: str | None = None
    branch_city: str | None = None
    branch_district: str | None = None
    branch_address: str | None = None


class OnboardingSetupResponse(BaseModel):
    tenant_id: str
    business_name: str
    slug: str
    business_type: str
    currency: str
    branch_id: str
    onboarding_completed: bool


class ApplyTemplateResponse(BaseModel):
    applied: bool
    categories_created: int
    message: str
