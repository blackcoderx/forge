from pydantic import BaseModel
from typing import Literal


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal["participant", "judge", "admin"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
