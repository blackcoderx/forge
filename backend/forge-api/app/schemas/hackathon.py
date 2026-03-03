from datetime import datetime
from pydantic import BaseModel


class HackathonBase(BaseModel):
    name: str
    description: str = ""
    rules: str = ""
    theme: str | None = None
    start_at: datetime
    end_at: datetime
    event_code: str
    langflow_url: str = ""
    langflow_admin_username: str = ""
    langflow_admin_password: str = ""


class HackathonCreate(HackathonBase):
    pass


class HackathonUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    rules: str | None = None
    theme: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    event_code: str | None = None
    langflow_url: str | None = None
    langflow_admin_username: str | None = None
    langflow_admin_password: str | None = None


class HackathonOut(BaseModel):
    id: int
    name: str
    description: str
    rules: str
    theme: str | None
    start_at: datetime
    end_at: datetime
    status: str
    langflow_url: str

    model_config = {"from_attributes": True}


class HackathonAdminOut(HackathonOut):
    """Extended view for admin — includes event code and Langflow admin creds."""
    event_code: str
    langflow_admin_username: str
