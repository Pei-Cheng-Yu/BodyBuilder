import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.db.base import Base
from sqlalchemy import ForeignKey, event, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)

    # stores the output of 'plan_compiler_node'
    # It will contain the 7-day schedule with all exercises
    plan_data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB), nullable=False
    )
    # Track which plan is currently active
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationship back to the owner
    user: Mapped["User"] = relationship(back_populates="weekly_plans")


def _inject_ids_recursive(data: dict[str, Any]) -> None:
    """
    Traverses the plan_data dictionary and injects 'id' fields
    for DailyWorkout blocks and Exercise items if they are missing.
    This supports the Frontend's Drag-and-Drop requirements (JIRA-like).
    """
    if not data or "schedule" not in data:
        return

    schedule = data["schedule"]
    if not isinstance(schedule, list):
        return

    for day_block in schedule:
        if isinstance(day_block, dict):
            # 1. Block ID (for the column/day container)
            if "id" not in day_block:
                day_block["id"] = str(uuid.uuid4())

            # 2. Exercise Instance IDs (for the draggable cards)
            exercises = day_block.get("exercises", [])
            if isinstance(exercises, list):
                for ex in exercises:
                    if isinstance(ex, dict) and "id" not in ex:
                        ex["id"] = str(uuid.uuid4())


def before_save_plan_listener(mapper, connection, target):
    if target.plan_data:
        _inject_ids_recursive(target.plan_data)


# Register the event listeners to ensure IDs are always present in DB
event.listen(WeeklyPlan, "before_insert", before_save_plan_listener)
event.listen(WeeklyPlan, "before_update", before_save_plan_listener)
