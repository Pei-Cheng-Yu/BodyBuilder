import copy
from typing import List, Optional

from app.auth.protected import get_current_user
from app.db.models.plan import WeeklyPlan
from app.db.models.user import User
from app.db.session import AsyncSessionLocal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter()


# --- Request/Response Schemas ---


class BlockUpdate(BaseModel):
    day: str


class ExerciseMove(BaseModel):
    block_id: str = Field(..., alias="blockId")  # Target Block ID
    order: int  # Target Index


class ExerciseSearchResponse(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    target_muscle: str


# --- Helpers ---


def format_sets(sets: int, reps: str) -> str:
    """Formats sets and reps into a string like '4x12'."""
    return f"{sets}x{reps}"


def transform_plan_to_frontend(plan_data: dict) -> List[dict]:
    """
    Adapts the Backend WeeklyPlan structure to the Frontend Data Model.
    """
    schedule = plan_data.get("schedule", [])
    result = []
    for day in schedule:
        # Map Backend 'DailyWorkout' -> Frontend 'Block'
        exercises_formatted = []
        for ex in day.get("exercises", []):
            exercises_formatted.append(
                {
                    "id": ex.get("id"),  # Unique Instance ID (for Drag & Drop)
                    "title": ex.get("name"),
                    "sets": format_sets(ex.get("sets", 0), ex.get("reps", "")),
                    "exercise_id": ex.get("exercise_id"),  # DB Reference ID
                }
            )

        result.append(
            {
                "id": day.get("id"),
                "day": day.get("day"),
                "title": day.get("focus_area", "Rest"),  # Map focus_area to title
                "exercises": exercises_formatted,
                "is_rest_day": day.get("is_rest_day", False),
            }
        )
    return result


# --- Endpoints ---


@router.get("/plans")
async def get_active_plan(current_user: User = Depends(get_current_user)):
    """獲取全週計畫 (Get Full Weekly Plan)"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(WeeklyPlan)
            .where(
                WeeklyPlan.user_id == current_user.id, WeeklyPlan.is_active.is_(True)
            )
            .order_by(WeeklyPlan.created_at.desc())
        )

        result = await session.execute(stmt)
        plan = result.scalars().first()

        if not plan:
            return []

        return transform_plan_to_frontend(plan.plan_data)


@router.patch("/blocks/{block_id}")
async def update_block_day(
    block_id: str, body: BlockUpdate, current_user: User = Depends(get_current_user)
):
    """更新模組位置 (Update Block Day)"""
    async with AsyncSessionLocal() as session:
        stmt = select(WeeklyPlan).where(
            WeeklyPlan.user_id == current_user.id, WeeklyPlan.is_active.is_(True)
        )
        result = await session.execute(stmt)
        plan = result.scalars().first()

        if not plan:
            raise HTTPException(404, "Active plan not found")

        current_data = copy.deepcopy(plan.plan_data)
        schedule = current_data.get("schedule", [])

        found = False
        for day in schedule:
            if day.get("id") == block_id:
                day["day"] = body.day
                found = True
                break

        if not found:
            raise HTTPException(404, "Block not found")

        plan.plan_data = current_data
        flag_modified(plan, "plan_data")
        await session.commit()
        return {"status": "success", "block_id": block_id, "new_day": body.day}


@router.patch("/exercises/move/{exercise_id}")
async def move_exercise(
    exercise_id: str, body: ExerciseMove, current_user: User = Depends(get_current_user)
):
    """更新動作排序 (Move Exercise between blocks or reorder)"""
    async with AsyncSessionLocal() as session:
        stmt = select(WeeklyPlan).where(
            WeeklyPlan.user_id == current_user.id, WeeklyPlan.is_active.is_(True)
        )
        result = await session.execute(stmt)
        plan = result.scalars().first()

        if not plan:
            raise HTTPException(404, "Active plan not found")

        current_data = copy.deepcopy(plan.plan_data)
        schedule = current_data.get("schedule", [])

        # 1. Find and remove exercise from source
        target_ex = None
        for day in schedule:
            exercises = day.get("exercises", [])
            for i, ex in enumerate(exercises):
                if ex.get("id") == exercise_id:
                    target_ex = exercises.pop(i)
                    break
            if target_ex:
                break

        if not target_ex:
            raise HTTPException(404, "Exercise not found")

        # 2. Find target block and insert
        target_block = None
        for day in schedule:
            if day.get("id") == body.block_id:
                target_block = day
                break

        if not target_block:
            raise HTTPException(404, "Target block not found")

        # Ensure exercises list exists
        if "exercises" not in target_block:
            target_block["exercises"] = []

        # Insert at order (clamped to bounds)
        insert_idx = max(0, min(body.order, len(target_block["exercises"])))
        target_block["exercises"].insert(insert_idx, target_ex)

        plan.plan_data = current_data
        flag_modified(plan, "plan_data")
        await session.commit()
        return {"status": "success"}
