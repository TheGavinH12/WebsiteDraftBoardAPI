from datetime import datetime
from pydantic import BaseModel, Field


class ProspectIn(BaseModel):
    rank: int = Field(..., ge=1)
    name: str
    position: str
    school: str
    note: str = ""


class ProspectOut(ProspectIn):
    id: int

    class Config:
        from_attributes = True


class BoardMeta(BaseModel):
    label: str
    updated: str | None
    count: int
