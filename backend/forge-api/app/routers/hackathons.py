from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_participant, get_current_admin, get_current_user
from app.core.security import encrypt_secret
from app.models.hackathon import Hackathon
from app.models.user import User
from app.schemas.hackathon import HackathonOut, HackathonAdminOut, HackathonCreate, HackathonUpdate

router = APIRouter(prefix="/api/hackathons", tags=["hackathons"])


def _get_hackathon_or_404(hackathon_id: int, db: Session) -> Hackathon:
    h = db.query(Hackathon).filter(Hackathon.id == hackathon_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return h


# ── Participant endpoints ──────────────────────────────────────────────────────

@router.get("", response_model=list[HackathonOut])
def list_hackathons(
    status_filter: str = Query("current", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    hackathons = db.query(Hackathon).all()
    if status_filter in ("current", "upcoming", "ended"):
        hackathons = [h for h in hackathons if h.status == status_filter]
    return hackathons


@router.get("/{hackathon_id}", response_model=HackathonOut)
def get_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_hackathon_or_404(hackathon_id, db)


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/all", response_model=list[HackathonAdminOut])
def admin_list_hackathons(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.query(Hackathon).all()


@router.post("", response_model=HackathonAdminOut, status_code=status.HTTP_201_CREATED)
def create_hackathon(
    body: HackathonCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    hackathon = Hackathon(
        name=body.name,
        description=body.description,
        rules=body.rules,
        theme=body.theme,
        start_at=body.start_at,
        end_at=body.end_at,
        event_code=body.event_code,
        langflow_url=body.langflow_url,
        langflow_admin_username=body.langflow_admin_username,
        langflow_admin_password=encrypt_secret(body.langflow_admin_password),
    )
    db.add(hackathon)
    db.commit()
    db.refresh(hackathon)
    return hackathon


@router.put("/{hackathon_id}", response_model=HackathonAdminOut)
def update_hackathon(
    hackathon_id: int,
    body: HackathonUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    hackathon = _get_hackathon_or_404(hackathon_id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        if field == "langflow_admin_password":
            value = encrypt_secret(value)
        setattr(hackathon, field, value)
    db.commit()
    db.refresh(hackathon)
    return hackathon


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    hackathon = _get_hackathon_or_404(hackathon_id, db)
    db.delete(hackathon)
    db.commit()
