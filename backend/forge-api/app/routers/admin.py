from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin
from app.core.security import hash_password
from app.models.hackathon import Hackathon
from app.models.score import Score
from app.models.team import Team
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    total_teams = db.query(Team).count()
    all_hackathons = db.query(Hackathon).all()
    active = sum(1 for h in all_hackathons if h.status == "current")
    total_scores = db.query(Score).count()

    # Count teams that have at least one score
    scored_team_ids = db.query(Score.team_id).distinct().all()
    scored_teams = len(scored_team_ids)
    unscored_teams = total_teams - scored_teams

    return {
        "total_teams": total_teams,
        "active_hackathons": active,
        "total_hackathons": len(all_hackathons),
        "scored_teams": scored_teams,
        "unscored_teams": unscored_teams,
        "total_scores": total_scores,
    }


@router.get("/judges", response_model=list[UserOut])
def list_judges(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.query(User).filter(User.role == "judge").all()


@router.post("/judges", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_judge(
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.username}' already exists",
        )
    judge = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role="judge",
    )
    db.add(judge)
    db.commit()
    db.refresh(judge)
    return judge


@router.put("/judges/{judge_id}", response_model=UserOut)
def update_judge(
    judge_id: int,
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    judge = db.query(User).filter(User.id == judge_id, User.role == "judge").first()
    if not judge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Judge not found")
    judge.username = body.username
    judge.hashed_password = hash_password(body.password)
    db.commit()
    db.refresh(judge)
    return judge


@router.delete("/judges/{judge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_judge(
    judge_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    judge = db.query(User).filter(User.id == judge_id, User.role == "judge").first()
    if not judge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Judge not found")
    db.delete(judge)
    db.commit()
