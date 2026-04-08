from datetime import datetime

from pydantic import BaseModel


class QRGenerateRequest(BaseModel):
    # If provided, generates a table-specific QR; otherwise generates a store-level QR
    table_number: str | None = None


class QRCodeResponse(BaseModel):
    id: str
    tenant_id: str
    branch_id: str
    code_type: str        # store | table
    target_url: str
    table_number: str | None
    image_url: str | None
    created_at: datetime
