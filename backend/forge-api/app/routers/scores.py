from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_judge, get_current_judge_or_admin
from app.models.score import Score
from app.models.team import Team
from app.models.user import User
from app.schemas.score import ScoreCreate, ScoreUpdate, ScoreOut, LeaderboardEntry

router = APIRouter(prefix="/api", tags=["scores"])


@router.get("/scores/{team_id}", response_model=ScoreOut | None)
def get_score(
    team_id: int,
    hackathon_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_judge_or_admin),
):
    """Get this judge's score for a specific team. Returns null if not yet scored."""
    score = db.query(Score).filter(
        Score.team_id == team_id,
        Score.hackathon_id == hackathon_id,
        Score.judge_id == current_user.id,
    ).first()
    return score


@router.post("/scores/{team_id}", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
def submit_score(
    team_id: int,
    body: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_judge),
):
    # Ensure team exists
    team = db.query(Team).filter(Team.id == team_id, Team.hackathon_id == body.hackathon_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    # Prevent duplicate scores from same judge
    existing = db.query(Score).filter(
        Score.team_id == team_id,
        Score.hackathon_id == body.hackathon_id,
        Score.judge_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already scored this team. Use PUT to update.",
        )

    score = Score(
        hackathon_id=body.hackathon_id,
        team_id=team_id,
        judge_id=current_user.id,
        innovation=body.innovation,
        execution=body.execution,
        impact=body.impact,
        presentation=body.presentation,
        comments=body.comments,
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.put("/scores/{team_id}", response_model=ScoreOut)
def update_score(
    team_id: int,
    body: ScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_judge),
):
    score = db.query(Score).filter(
        Score.team_id == team_id,
        Score.hackathon_id == body.hackathon_id,
        Score.judge_id == current_user.id,
    ).first()
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found. Submit first.")

    score.innovation = body.innovation
    score.execution = body.execution
    score.impact = body.impact
    score.presentation = body.presentation
    score.comments = body.comments
    db.commit()
    db.refresh(score)
    return score


@router.get("/hackathons/{hackathon_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    hackathon_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_judge_or_admin),
):
    results = (
        db.query(
            Score.team_id,
            Team.name.label("team_name"),
            func.avg(Score.innovation + Score.execution + Score.impact + Score.presentation).label("avg_total"),
            func.count(Score.id).label("count"),
        )
        .join(Team, Team.id == Score.team_id)
        .filter(Score.hackathon_id == hackathon_id)
        .group_by(Score.team_id, Team.name)
        .order_by(func.avg(Score.innovation + Score.execution + Score.impact + Score.presentation).desc())
        .all()
    )

    return [
        LeaderboardEntry(
            team_id=r.team_id,
            team_name=r.team_name,
            average_score=round(r.avg_total, 2),
            scores_submitted=r.count,
        )
        for r in results
    ]
