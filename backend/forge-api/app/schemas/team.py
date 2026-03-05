from datetime import datetime
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    portal_username: str
    portal_password: str
    langflow_username: str
    langflow_password: str
    instance_id: int | None = None
    judge_id: int | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    portal_password: str | None = None
    langflow_username: str | None = None
    langflow_password: str | None = None


class TeamOut(BaseModel):
    id: int
    name: str
    hackathon_id: int
    langflow_username: str
    instance_id: int | None
    judge_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnlockRequest(BaseModel):
    event_code: str


class UnlockResponse(BaseModel):
    langflow_username: str
    langflow_password: str
    langflow_url: str
