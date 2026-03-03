from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class HackathonAccess(Base):
    """Audit log — records when a participant successfully unlocked a hackathon."""
    __tablename__ = "hackathon_accesses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="accesses")
    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="accesses")
