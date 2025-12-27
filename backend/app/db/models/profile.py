import uuid
from typing import TYPE_CHECKING, Literal, Optional

from app.db.base import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    # Only for the IDE and Ruff! Ignored at runtime.
    from .user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    gender: Mapped[Optional[str]]
    age: Mapped[Optional[int]]
    workout_frequency: Mapped[int] = mapped_column(default=3)
    user_goal: Mapped[Optional[str]]
    injuries: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default="{}",
    )

    load: Mapped[Optional[int]] = mapped_column(nullable=True)

    # store as plain string column
    training_location: Mapped[Literal["gym", "home", "both"]] = mapped_column(
        String,
        nullable=False,
        default="gym",
        server_default="gym",
    )

    available_equipment: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default="{}",
    )

    avoid_equipment: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        server_default="{}",
    )

    latest_scan: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
