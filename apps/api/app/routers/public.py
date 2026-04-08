from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.public_menu import PublicMenuResponse
from app.services import catalog_service, event_service

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/menu/{slug}", response_model=PublicMenuResponse)
def get_public_menu(slug: str, db: Session = Depends(get_db)):
    menu = catalog_service.get_public_menu(db, slug)

    event_service.log(
        db,
        "public_menu_viewed",
        tenant_id=menu.tenant_id,
        payload={"slug": slug},
    )
    db.commit()

    return menu
