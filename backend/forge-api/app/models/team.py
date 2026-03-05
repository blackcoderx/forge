from datetime import datetime, timezone

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    instance_id: Mapped[int | None] = mapped_column(ForeignKey("langflow_instances.id"), nullable=True)

    # Langflow credentials for this team (password encrypted via Fernet)
    langflow_username: Mapped[str] = mapped_column(String(128), nullable=False)
    langflow_password: Mapped[str] = mapped_column(String(512), nullable=False)  # encrypted

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="teams")
    user: Mapped["User"] = relationship("User", back_populates="team")
    scores: Mapped[list["Score"]] = relationship("Score", back_populates="team", cascade="all, delete-orphan")
    instance: Mapped["LangflowInstance | None"] = relationship("LangflowInstance", back_populates="teams")
