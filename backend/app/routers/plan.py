from app.db.models.plan import WeeklyPlan
from app.db.session import AsyncSessionLocal
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, text

router = APIRouter()


class PlanDateUpdate(BaseModel):
    day: str


@router.patch("/{daily_plan_id}")
async def update_daily_plan_date(daily_plan_id: str, body: PlanDateUpdate):
    """
    Updates the 'day' of a specific DailyWorkout block within a WeeklyPlan.
    """
    async with AsyncSessionLocal() as session:
        # 1. Find the WeeklyPlan that contains the daily_plan_id in its schedule
        # We use a JSONB query to find the row where the schedule array contains an object with this id
        # Note: This assumes plan_data['schedule'] is a list of objects with an 'id' field.

        # Construct a JSON fragment to search for
        search_json = f'[{{"id": "{daily_plan_id}"}}]'

        stmt = (
            select(WeeklyPlan)
            .where(text("plan_data->'schedule' @> :search_json"))
            .params(search_json=search_json)
        )

        result = await session.execute(stmt)
        plan = result.scalar_one_or_none()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily plan with ID {daily_plan_id} not found.",
            )

        # 2. Update the specific block in Python
        # Since updating a specific array element in JSONB via SQL is complex,
        # we modify the dict and save it back.
        current_data = dict(plan.plan_data)
        schedule = current_data.get("schedule", [])

        updated = False
        for day_block in schedule:
            if day_block.get("id") == daily_plan_id:
                day_block["day"] = body.day
                updated = True
                break

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ID found in query but not in loop (unexpected concurrency issue).",
            )

        # 3. Save changes
        # We must re-assign to trigger SQLAlchemy's change tracking for JSON types
        plan.plan_data = current_data
        # Mark the field as modified explicitly if needed, but re-assignment usually works

        await session.commit()

        return {
            "status": "success",
            "updated_to": body.day,
            "daily_plan_id": daily_plan_id,
        }
