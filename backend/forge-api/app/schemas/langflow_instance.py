from datetime import datetime

from pydantic import BaseModel


class LangflowInstanceCreate(BaseModel):
    url: str
    limit: int = 30


class LangflowInstanceUpdate(BaseModel):
    url: str | None = None
    limit: int | None = None


class LangflowInstanceOut(BaseModel):
    id: int
    url: str
    limit: int
    usage: int
    created_at: datetime

    model_config = {"from_attributes": True}
