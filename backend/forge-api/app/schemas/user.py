from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
