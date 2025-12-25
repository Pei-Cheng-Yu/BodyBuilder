import uuid
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class MedicalPrescription(Base):
    __tablename__ = "medical_prescriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)

    # JSONB is still used here for our lists
    target_focus_areas: Mapped[list[str]] = mapped_column(JSONB, default=list)
    safety_constraints: Mapped[list[str]] = mapped_column(JSONB, default=list)
    load_recommendation: Mapped[Optional[str]]

    user: Mapped["User"] = relationship(back_populates="prescription")
