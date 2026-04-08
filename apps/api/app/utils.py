from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tenant import Branch


def get_default_branch(db: Session, tenant_id: str) -> Branch:
    """Returns the first active branch for a tenant. V1 is single-branch."""
    branch = (
        db.query(Branch)
        .filter(Branch.tenant_id == tenant_id, Branch.is_active == True)
        .first()
    )
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active branch found for this tenant",
        )
    return branch
