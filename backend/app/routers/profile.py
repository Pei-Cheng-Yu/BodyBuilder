from app.auth.protected import get_current_user
from app.db.models.profile import UserProfile
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.profile import UserProfilePatch, UserProfileRead, UserProfileUpdate
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/profile", tags=["profile"])


def _normalize_list(items: list[str]) -> list[str]:
    # remove empties + trim + de-dup while keeping order
    seen = set()
    out: list[str] = []
    for x in items:
        x = (x or "").strip()
        if not x:
            continue
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


# Ensure that the db session is an AsyncSession
@router.get("/me", response_model=UserProfileRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        # return default shape even if not created yet
        return UserProfile(
            user_id=current_user.id,
            workout_frequency=3,
            training_location="gym",
            injuries=[],
            available_equipment=[],
            avoid_equipment=[],
        )
    return profile


@router.put("/me", response_model=UserProfileRead)
async def put_my_profile(
    body: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.gender = body.gender
    profile.age = body.age
    profile.workout_frequency = body.workout_frequency
    profile.user_goal = body.user_goal
    profile.injuries = _normalize_list(body.injuries)
    profile.load = body.load
    profile.training_location = body.training_location
    profile.available_equipment = _normalize_list(body.available_equipment)
    profile.avoid_equipment = _normalize_list(body.avoid_equipment)

    await db.commit()
    await db.refresh(profile)

    return profile


@router.patch("/me", response_model=UserProfileRead)
async def patch_my_profile(
    body: UserProfilePatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    data = body.model_dump(exclude_unset=True)

    if "gender" in data:
        profile.gender = data["gender"]
    if "age" in data:
        profile.age = data["age"]
    if "workout_frequency" in data:
        profile.workout_frequency = data["workout_frequency"]
    if "user_goal" in data:
        profile.user_goal = data["user_goal"]
    if "injuries" in data:
        profile.injuries = _normalize_list(data["injuries"] or [])
    if "load" in data:
        profile.load = data["load"]
    if "training_location" in data:
        profile.training_location = data["training_location"]
    if "available_equipment" in data:
        profile.available_equipment = _normalize_list(data["available_equipment"] or [])
    if "avoid_equipment" in data:
        profile.avoid_equipment = _normalize_list(data["avoid_equipment"] or [])

    await db.commit()
    await db.refresh(profile)

    return profile
