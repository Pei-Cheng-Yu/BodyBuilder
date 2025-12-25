import uuid
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    # Only for the IDE and Ruff! Ignored at runtime.
    from .user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    gender: Mapped[Optional[str]]
    age: Mapped[Optional[int]]
    weight: Mapped[Optional[float]]
    height: Mapped[Optional[float]]
    body_fat: Mapped[Optional[float]]
    workout_frequency: Mapped[int] = mapped_column(default=3)
    user_goal: Mapped[Optional[str]]

    user: Mapped["User"] = relationship(back_populates="profile")
