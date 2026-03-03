from datetime import datetime, timezone

from sqlalchemy import Integer, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        CheckConstraint("innovation BETWEEN 1 AND 10", name="ck_innovation"),
        CheckConstraint("execution BETWEEN 1 AND 10", name="ck_execution"),
        CheckConstraint("impact BETWEEN 1 AND 10", name="ck_impact"),
        CheckConstraint("presentation BETWEEN 1 AND 10", name="ck_presentation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    judge_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    innovation: Mapped[int] = mapped_column(Integer, nullable=False)
    execution: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    presentation: Mapped[int] = mapped_column(Integer, nullable=False)

    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="scores")
    team: Mapped["Team"] = relationship("Team", back_populates="scores")
    judge: Mapped["User"] = relationship("User", back_populates="scores")

    @property
    def total(self) -> int:
        return self.innovation + self.execution + self.impact + self.presentation
