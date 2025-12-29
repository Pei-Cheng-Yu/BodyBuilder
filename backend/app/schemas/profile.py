from typing import List, Literal, Optional

from pydantic import BaseModel, Field, conint


class UserProfileRead(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    workout_frequency: int = 3
    user_goal: Optional[str] = None
    injuries: List[str] = Field(default_factory=list)
    load: Optional[int] = None
    training_location: Literal["gym", "home", "both"] = "gym"
    available_equipment: List[str] = Field(default_factory=list)
    avoid_equipment: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    # full replace (PUT) - keep defaults aligned with DB defaults
    gender: Optional[str] = None
    age: Optional[int] = None
    workout_frequency: conint(ge=0, le=14) = 3  # example range; adjust if you want
    user_goal: Optional[str] = None
    injuries: List[str] = Field(default_factory=list)
    load: Optional[int] = None
    training_location: Literal["gym", "home", "both"] = "gym"
    available_equipment: List[str] = Field(default_factory=list)
    avoid_equipment: List[str] = Field(default_factory=list)


class UserProfilePatch(BaseModel):
    # partial update (PATCH)
    gender: Optional[str] = None
    age: Optional[int] = None
    workout_frequency: Optional[conint(ge=0, le=14)] = None
    user_goal: Optional[str] = None
    injuries: Optional[List[str]] = None
    load: Optional[int] = None
    training_location: Optional[Literal["gym", "home", "both"]] = None
    available_equipment: Optional[List[str]] = None
    avoid_equipment: Optional[List[str]] = None
