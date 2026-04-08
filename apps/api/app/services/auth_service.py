from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.settings import BusinessSettings
from app.models.tenant import Branch, Tenant
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register(db: Session, data: RegisterRequest) -> tuple[User, Tenant]:
    if db.query(User).filter(User.email == data.email).first():
        raise ValueError("Email already registered")

    if db.query(Tenant).filter(Tenant.slug == data.slug).first():
        raise ValueError("Slug already taken")

    tenant = Tenant(
        id=str(uuid4()),
        business_name=data.business_name,
        slug=data.slug,
        business_type=data.business_type,
        currency=data.currency,
    )
    db.add(tenant)
    db.flush()

    branch = Branch(
        id=str(uuid4()),
        tenant_id=tenant.id,
        name="Ana Şube",
    )
    db.add(branch)
    db.flush()

    # Default business settings for the branch
    biz_settings = BusinessSettings(
        id=str(uuid4()),
        tenant_id=tenant.id,
        branch_id=branch.id,
    )
    db.add(biz_settings)

    user = User(
        id=str(uuid4()),
        tenant_id=tenant.id,
        name=data.name,
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(tenant)

    return user, tenant


def login(db: Session, data: LoginRequest) -> User:
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise ValueError("Invalid email or password")
    return user


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
