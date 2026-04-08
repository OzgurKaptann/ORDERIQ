from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.modifier import ModifierGroup, ModifierOption
from app.schemas.modifier import ModifierGroupCreate, ModifierGroupUpdate
from app.utils import get_default_branch


def list_modifier_groups(db: Session, tenant_id: str) -> list[ModifierGroup]:
    branch = get_default_branch(db, tenant_id)
    return (
        db.query(ModifierGroup)
        .filter(ModifierGroup.tenant_id == tenant_id, ModifierGroup.branch_id == branch.id)
        .all()
    )


def create_modifier_group(db: Session, tenant_id: str, data: ModifierGroupCreate) -> ModifierGroup:
    branch = get_default_branch(db, tenant_id)

    group = ModifierGroup(
        id=str(uuid4()),
        tenant_id=tenant_id,
        branch_id=branch.id,
        name=data.name,
        selection_type=data.selection_type,
        is_required=data.is_required,
        min_select=data.min_select,
        max_select=data.max_select,
    )
    db.add(group)
    db.flush()

    for opt_data in data.options:
        db.add(
            ModifierOption(
                id=str(uuid4()),
                modifier_group_id=group.id,
                name=opt_data.name,
                extra_price=opt_data.extra_price,
                sort_order=opt_data.sort_order,
            )
        )

    db.commit()
    db.refresh(group)
    return group


def update_modifier_group(
    db: Session, tenant_id: str, group_id: str, data: ModifierGroupUpdate
) -> ModifierGroup:
    group = db.query(ModifierGroup).filter(
        ModifierGroup.id == group_id, ModifierGroup.tenant_id == tenant_id
    ).first()
    if not group:
        raise ValueError("Modifier group not found")

    updates = data.model_dump(exclude_unset=True)
    new_options = updates.pop("options", None)

    # Validate combined min/max after merge
    final_min = updates.get("min_select", group.min_select)
    final_max = updates.get("max_select", group.max_select)
    if final_min > final_max:
        raise ValueError("min_select cannot be greater than max_select")

    for field, value in updates.items():
        setattr(group, field, value)

    if new_options is not None:
        # Soft-deactivate all existing options (preserves FK refs from historical orders)
        for existing_opt in group.options:
            existing_opt.is_active = False
        db.flush()

        for opt_data in new_options:
            db.add(
                ModifierOption(
                    id=str(uuid4()),
                    modifier_group_id=group.id,
                    name=opt_data.name,
                    extra_price=opt_data.extra_price,
                    sort_order=opt_data.sort_order,
                    is_active=opt_data.is_active,
                )
            )

    db.commit()
    db.refresh(group)
    return group


def delete_modifier_group(db: Session, tenant_id: str, group_id: str) -> None:
    group = db.query(ModifierGroup).filter(
        ModifierGroup.id == group_id, ModifierGroup.tenant_id == tenant_id
    ).first()
    if not group:
        raise ValueError("Modifier group not found")
    group.is_active = False
    db.commit()
