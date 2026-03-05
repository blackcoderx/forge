from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    hackathon_id: int | None = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    hackathon_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
