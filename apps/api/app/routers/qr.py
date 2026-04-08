from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.qr_code import QRCodeResponse, QRGenerateRequest
from app.services import event_service, qr_service

router = APIRouter(prefix="/qr", tags=["qr"])


@router.post("/generate", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
def generate_qr(
    data: QRGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    qr = qr_service.generate_qr(db, current_tenant, data)

    event_service.log(
        db,
        "qr_generated",
        tenant_id=current_tenant.id,
        payload={
            "qr_id": qr.id,
            "code_type": qr.code_type,
            "table_number": qr.table_number,
        },
    )
    db.commit()

    return qr


@router.get("", response_model=list[QRCodeResponse])
def list_qr_codes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return qr_service.list_qr_codes(db, current_tenant.id)


@router.get("/{qr_id}", response_model=QRCodeResponse)
def get_qr_code(
    qr_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return qr_service.get_qr_code(db, current_tenant.id, qr_id)
