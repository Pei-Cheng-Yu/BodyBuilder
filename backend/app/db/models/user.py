import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .medical import MedicalPrescription
    from .plan import WeeklyPlan
    from .profile import UserProfile


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user")
    prescription: Mapped[Optional["MedicalPrescription"]] = relationship(
        back_populates="user"
    )
    weekly_plans: Mapped[list["WeeklyPlan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",  # If user is deleted, delete their plans too
    )
