from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_participant, get_current_admin
from app.core.security import encrypt_secret, decrypt_secret, hash_password
from app.models.hackathon import Hackathon
from app.models.hackathon_access import HackathonAccess
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamOut, UnlockRequest, UnlockResponse

router = APIRouter(prefix="/api/hackathons", tags=["teams"])


def _get_hackathon_or_404(hackathon_id: int, db: Session) -> Hackathon:
    h = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return h


def _get_team_or_404(hackathon_id: int, team_id: int, db: Session) -> Team:
    t = db.query(Team).filter(Team.id == team_id, Team.hackathon_id == hackathon_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return t


# ── Participant: unlock hackathon → receive Langflow creds ────────────────────

@router.post("/{hackathon_id}/unlock", response_model=UnlockResponse)
def unlock_hackathon(
    hackathon_id: int,
    body: UnlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_participant),
):
    hackathon = _get_hackathon_or_404(hackathon_id, db)

    if body.event_code.strip().upper() != hackathon.event_code.strip().upper():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event code")

    # Find this user's team for this hackathon
    team = db.query(Team).filter(
        Team.hackathon_id == hackathon_id,
        Team.user_id == current_user.id,
    ).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No team found for your account in this hackathon",
        )

    # Log the access
    access = HackathonAccess(user_id=current_user.id, hackathon_id=hackathon_id)
    db.add(access)
    db.commit()

    return UnlockResponse(
        langflow_username=team.langflow_username,
        langflow_password=decrypt_secret(team.langflow_password),
        langflow_url=hackathon.langflow_url,
    )


# ── Admin: team CRUD ──────────────────────────────────────────────────────────

@router.get("/{hackathon_id}/teams", response_model=list[TeamOut])
def list_teams(
    hackathon_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    _get_hackathon_or_404(hackathon_id, db)
    return db.query(Team).filter(Team.hackathon_id == hackathon_id).all()


@router.post("/{hackathon_id}/teams", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(
    hackathon_id: int,
    body: TeamCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    _get_hackathon_or_404(hackathon_id, db)

    # Check portal username is unique
    if db.query(User).filter(User.username == body.portal_username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.portal_username}' already exists",
        )

    # Create portal user account
    user = User(
        username=body.portal_username,
        hashed_password=hash_password(body.portal_password),
        role="participant",
    )
    db.add(user)
    db.flush()  # get user.id before committing

    team = Team(
        name=body.name,
        hackathon_id=hackathon_id,
        user_id=user.id,
        langflow_username=body.langflow_username,
        langflow_password=encrypt_secret(body.langflow_password),
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/{hackathon_id}/teams/{team_id}", response_model=TeamOut)
def get_team(
    hackathon_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return _get_team_or_404(hackathon_id, team_id, db)


@router.put("/{hackathon_id}/teams/{team_id}", response_model=TeamOut)
def update_team(
    hackathon_id: int,
    team_id: int,
    body: TeamUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    team = _get_team_or_404(hackathon_id, team_id, db)

    if body.name is not None:
        team.name = body.name
    if body.langflow_username is not None:
        team.langflow_username = body.langflow_username
    if body.langflow_password is not None:
        team.langflow_password = encrypt_secret(body.langflow_password)
    if body.portal_password is not None:
        team.user.hashed_password = hash_password(body.portal_password)

    db.commit()
    db.refresh(team)
    return team


@router.delete("/{hackathon_id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    hackathon_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    team = _get_team_or_404(hackathon_id, team_id, db)
    db.delete(team)
    db.commit()
