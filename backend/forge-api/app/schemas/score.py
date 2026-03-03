from datetime import datetime
from pydantic import BaseModel, field_validator


class ScoreCreate(BaseModel):
    hackathon_id: int
    innovation: int
    execution: int
    impact: int
    presentation: int
    comments: str = ""

    @field_validator("innovation", "execution", "impact", "presentation")
    @classmethod
    def validate_range(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError("Score must be between 1 and 10")
        return v


class ScoreUpdate(ScoreCreate):
    pass


class ScoreOut(BaseModel):
    id: int
    hackathon_id: int
    team_id: int
    judge_id: int
    innovation: int
    execution: int
    impact: int
    presentation: int
    total: int
    comments: str
    scored_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    team_id: int
    team_name: str
    average_score: float
    scores_submitted: int
