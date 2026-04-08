import os
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.qr_code import QRCode
from app.models.tenant import Tenant
from app.schemas.qr_code import QRGenerateRequest
from app.utils import get_default_branch


def _build_target_url(slug: str, table_number: str | None) -> str:
    base = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/m/{slug}"
    if table_number:
        return f"{base}?table={table_number}"
    return base


def _generate_png(target_url: str, filename: str) -> str:
    """Generates a QR PNG and saves it under MEDIA_DIR/qr/. Returns the relative image path."""
    import qrcode  # imported here to keep startup fast

    img = qrcode.make(target_url)
    qr_dir = os.path.join(settings.MEDIA_DIR, "qr")
    os.makedirs(qr_dir, exist_ok=True)

    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)

    return f"/media/qr/{filename}"


def generate_qr(db: Session, tenant: Tenant, data: QRGenerateRequest) -> QRCode:
    branch = get_default_branch(db, tenant.id)

    target_url = _build_target_url(tenant.slug, data.table_number)
    code_type = "table" if data.table_number else "store"

    # Unique filename: {slug}_{hex8}[_table_{n}].png
    uid = uuid4().hex[:8]
    if data.table_number:
        filename = f"{tenant.slug}_{uid}_table_{data.table_number}.png"
    else:
        filename = f"{tenant.slug}_{uid}.png"

    image_url = _generate_png(target_url, filename)

    qr = QRCode(
        id=str(uuid4()),
        tenant_id=tenant.id,
        branch_id=branch.id,
        code_type=code_type,
        target_url=target_url,
        table_number=data.table_number,
        image_url=image_url,
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)
    return qr


def list_qr_codes(db: Session, tenant_id: str) -> list[QRCode]:
    return (
        db.query(QRCode)
        .filter(QRCode.tenant_id == tenant_id)
        .order_by(QRCode.created_at.desc())
        .all()
    )


def get_qr_code(db: Session, tenant_id: str, qr_id: str) -> QRCode:
    qr = (
        db.query(QRCode)
        .filter(QRCode.id == qr_id, QRCode.tenant_id == tenant_id)
        .first()
    )
    if not qr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR code not found")
    return qr
