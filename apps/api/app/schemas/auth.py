from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    business_name: str
    slug: str
    business_type: str  # waffle | kumpir | midye | other
    currency: str = "TRY"
    name: str
    email: EmailStr
    password: str

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        v = v.strip().lower().replace(" ", "-")
        if not v.replace("-", "").isalnum():
            raise ValueError("Slug must contain only letters, numbers, and hyphens")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    tenant_id: str
    onboarding_completed: bool

    model_config = {"from_attributes": True}


class TenantResponse(BaseModel):
    id: str
    business_name: str
    slug: str
    business_type: str
    currency: str
    onboarding_completed: bool

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    user: UserResponse
    tenant: TenantResponse
