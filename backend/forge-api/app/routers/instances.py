from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin
from app.models.langflow_instance import LangflowInstance
from app.models.team import Team
from app.models.user import User
from app.schemas.langflow_instance import LangflowInstanceCreate, LangflowInstanceUpdate, LangflowInstanceOut

router = APIRouter(prefix="/api/admin/instances", tags=["instances"])


def _to_out(inst: LangflowInstance, db: Session) -> LangflowInstanceOut:
    usage = db.query(Team).filter(Team.instance_id == inst.id).count()
    return LangflowInstanceOut(
        id=inst.id,
        url=inst.url,
        limit=inst.limit,
        usage=usage,
        created_at=inst.created_at,
    )


@router.get("", response_model=list[LangflowInstanceOut])
def list_instances(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    instances = db.query(LangflowInstance).all()
    return [_to_out(inst, db) for inst in instances]


@router.get("/available", response_model=list[LangflowInstanceOut])
def list_available_instances(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    instances = db.query(LangflowInstance).all()
    result = []
    for inst in instances:
        usage = db.query(Team).filter(Team.instance_id == inst.id).count()
        if usage < inst.limit:
            result.append(LangflowInstanceOut(
                id=inst.id,
                url=inst.url,
                limit=inst.limit,
                usage=usage,
                created_at=inst.created_at,
            ))
    return result


@router.post("", response_model=LangflowInstanceOut, status_code=status.HTTP_201_CREATED)
def create_instance(
    body: LangflowInstanceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    if db.query(LangflowInstance).filter(LangflowInstance.url == body.url).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Instance URL already exists")
    inst = LangflowInstance(url=body.url, limit=body.limit)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return _to_out(inst, db)


@router.put("/{instance_id}", response_model=LangflowInstanceOut)
def update_instance(
    instance_id: int,
    body: LangflowInstanceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    inst = db.query(LangflowInstance).filter(LangflowInstance.id == instance_id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    if body.url is not None:
        inst.url = body.url
    if body.limit is not None:
        inst.limit = body.limit
    db.commit()
    db.refresh(inst)
    return _to_out(inst, db)


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    inst = db.query(LangflowInstance).filter(LangflowInstance.id == instance_id).first()
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    usage = db.query(Team).filter(Team.instance_id == instance_id).count()
    if usage > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete instance with {usage} team(s) assigned",
        )
    db.delete(inst)
    db.commit()
