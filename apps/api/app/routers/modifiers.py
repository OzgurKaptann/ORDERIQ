from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_tenant, get_current_user, get_db
from app.schemas.modifier import ModifierGroupCreate, ModifierGroupResponse, ModifierGroupUpdate
from app.services import modifier_service

router = APIRouter(prefix="/modifier-groups", tags=["modifiers"])


@router.get("", response_model=list[ModifierGroupResponse])
def list_modifier_groups(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return modifier_service.list_modifier_groups(db, current_tenant.id)


@router.post("", response_model=ModifierGroupResponse, status_code=status.HTTP_201_CREATED)
def create_modifier_group(
    data: ModifierGroupCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    return modifier_service.create_modifier_group(db, current_tenant.id, data)


@router.patch("/{group_id}", response_model=ModifierGroupResponse)
def update_modifier_group(
    group_id: str,
    data: ModifierGroupUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        return modifier_service.update_modifier_group(db, current_tenant.id, group_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_modifier_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_tenant=Depends(get_current_tenant),
):
    try:
        modifier_service.delete_modifier_group(db, current_tenant.id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
