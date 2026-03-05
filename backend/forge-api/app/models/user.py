from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # participant | judge | admin
    hackathon_id: Mapped[int | None] = mapped_column(ForeignKey("hackathons.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # A user can be linked to one team (as a participant)
    team: Mapped["Team | None"] = relationship("Team", back_populates="user", foreign_keys="Team.user_id", uselist=False)
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="judge")
    accesses: Mapped[list["HackathonAccess"]] = relationship("HackathonAccess", back_populates="user")
