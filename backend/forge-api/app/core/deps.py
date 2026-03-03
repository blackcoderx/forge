from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer = HTTPBearer()


def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_participant(user: User = Depends(_get_current_user)) -> User:
    if user.role != "participant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Participants only")
    return user


def get_current_judge(user: User = Depends(_get_current_user)) -> User:
    if user.role != "judge":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Judges only")
    return user


def get_current_admin(user: User = Depends(_get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user


def get_current_judge_or_admin(user: User = Depends(_get_current_user)) -> User:
    if user.role not in ("judge", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Judges or admins only")
    return user


def get_current_user(user: User = Depends(_get_current_user)) -> User:
    return user
