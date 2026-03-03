from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    rules: Mapped[str] = mapped_column(Text, nullable=False, default="")
    theme: Mapped[str | None] = mapped_column(String(128), nullable=True)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Event code participants enter at the event to unlock their creds
    event_code: Mapped[str] = mapped_column(String(64), nullable=False)

    # Langflow instance for this hackathon
    langflow_url: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    langflow_admin_username: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    langflow_admin_password: Mapped[str] = mapped_column(String(512), nullable=False, default="")  # encrypted

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    teams: Mapped[list["Team"]] = relationship("Team", back_populates="hackathon", cascade="all, delete-orphan")
    accesses: Mapped[list["HackathonAccess"]] = relationship("HackathonAccess", back_populates="hackathon", cascade="all, delete-orphan")
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="hackathon", cascade="all, delete-orphan")

    @property
    def status(self) -> str:
        now = datetime.now(timezone.utc)
        # SQLite stores datetimes as naive — make them UTC-aware for comparison
        start = self.start_at.replace(tzinfo=timezone.utc) if self.start_at.tzinfo is None else self.start_at
        end = self.end_at.replace(tzinfo=timezone.utc) if self.end_at.tzinfo is None else self.end_at
        if now < start:
            return "upcoming"
        if now > end:
            return "ended"
        return "current"
