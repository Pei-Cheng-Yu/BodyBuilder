from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


class BasicScanMetrics(BaseModel):
    height_cm: float = Field(..., gt=50, lt=300, description="Height in cm")
    weight_kg: float = Field(..., description="Total Weight in kg")
    skeletal_muscle_mass_kg: float = Field(description="SMM 骨骼肌重 (kg)")
    body_fat_percent: float = Field(description="PBF 體脂率 (%)")

    basal_metabolic_rate: float = Field(description="BMR 基礎代謝率")
    visceral_fat_level: Optional[int] = Field(
        None, description="Visceral Fat Level 內臟脂肪等級 (Level 1-20)"
    )
    inbody_score: Optional[int] = Field(None, description="InBody Score 總分")
    curve_type: str = Field(
        ...,
        description="The shape formed by Weight/Muscle/Fat bars. Options: 'C-Shape', 'I-Shape', 'D-Shape'",
    )


class SegmentalAnalysis(BaseModel):
    """部位肌肉量 (用於偵測不平衡)"""

    right_arm_kg: Optional[float] = Field(None, description="Right Arm Lean Mass (kg)")
    right_arm_percent: Optional[float] = Field(
        None, description="Right Arm Lean Mass (%) - The number usually below the kg"
    )
    left_arm_kg: Optional[float] = Field(None, description="Left Arm Lean Mass (kg)")
    left_arm_percent: Optional[float] = Field(
        None, description="Left Arm Lean Mass (%)"
    )
    trunk_kg: Optional[float] = Field(None, description="Trunk Lean Mass (kg)")
    trunk_percent: Optional[float] = Field(None, description="Trunk Lean Mass (%)")
    right_leg_kg: Optional[float] = Field(None, description="Right Leg Lean Mass (kg)")
    right_leg_percent: Optional[float] = Field(
        None, description="Right Leg Lean Mass (%)"
    )
    left_leg_kg: Optional[float] = Field(None, description="Left Leg Lean Mass (kg)")
    left_leg_percent: Optional[float] = Field(
        None, description="Left Leg Lean Mass (%)"
    )


class InbodyMetrics(BaseModel):
    height_cm: float = Field(..., gt=50, lt=300, description="Height in cm")
    weight_kg: float = Field(..., description="Total Weight in kg")
    skeletal_muscle_mass_kg: float = Field(description="SMM 骨骼肌重 (kg)")
    body_fat_percent: float = Field(description="PBF 體脂率 (%)")

    basal_metabolic_rate: float = Field(description="BMR 基礎代謝率")
    visceral_fat_level: Optional[int] = Field(
        None, description="Visceral Fat Level 內臟脂肪等級 (Level 1-20)"
    )
    inbody_score: Optional[int] = Field(None, description="InBody Score 總分")
    curve_type: str = Field(
        ...,
        description="The shape formed by Weight/Muscle/Fat bars. Options: 'C-Shape', 'I-Shape', 'D-Shape'",
    )
    activity_level: Literal[
        "Sedentary", "Lightly Active", "Moderately Active", "Very Active"
    ] = "Sedentary"
    segmental_muscle: Optional[SegmentalAnalysis] = Field(
        None,
        description="Muscle mass for specific body parts (Right/Left Arm, Trunk, Right/Left Leg)",
    )

    # --- 6. 衍生指標 (Derived Metrics - 自動計算) ---
    @computed_field
    def ffmi(self) -> float:
        """
        計算 FFMI (Fat-Free Mass Index)
        公式: 瘦體重(kg) / 身高(m)^2
        瘦體重 = 體重 * (1 - 體脂率)
        """
        lean_mass = self.weight_kg * (1 - (self.body_fat_percent / 100))
        height_m = self.height_cm / 100
        return round(lean_mass / (height_m**2), 2)

    @computed_field
    def tdee(self) -> float:
        """
        計算 TDEE (每日總熱量消耗)
        BMR * 活動係數
        """
        multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
        }
        return round(
            self.basal_metabolic_rate * multipliers.get(self.activity_level, 1.2), 0
        )


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gender: Optional[str] = None
    age: Optional[int] = Field(default=18, gt=0, lt=120)
    user_goal: Optional[str] = None
    workout_frequency: int = Field(
        default=3, ge=1, le=7, description="Number of days per week the user can train."
    )
    injuries: list[str] = Field(
        default_factory=list, description="傷病史，如 ['knee_pain', 'lower_back']"
    )
    load: Optional[int] = None
    training_location: Optional[Literal["gym", "home", "both"]] = "gym"

    available_equipment: list[str] = Field(
        default_factory=list,
        description="Equipment the user can use, e.g. ['barbell','dumbbell','cable','machines']",
    )
    avoid_equipment: list[str] = Field(
        default_factory=list, description="Equipment to avoid, e.g. ['barbell']"
    )
    latest_scan: Optional[InbodyMetrics] = None


class DoctorSuggestion(BaseModel):
    """
    The medical prescription passed to the Strategy Planner.
    """

    model_config = ConfigDict(from_attributes=True)
    target_focus_areas: list[str] = Field(
        ...,
        description="List of body parts to prioritize this week (e.g., 'Glutes', 'Triceps').",
    )

    safety_constraints: list[str] = Field(
        ...,
        description="Specific movements to AVOID based on injuries (e.g., 'Avoid deep squats due to knee pain').",
    )

    load_recommendation: str = Field(
        ...,
        description="Guidance on weight/RPE (e.g., 'Use 70% 1RM', 'Focus on time-under-tension', or specific weights if provided).",
    )


class ExerciseDetail(BaseModel):
    exercise_id: str = Field(
        ..., description="The ID of the excercise response from the API"
    )
    name: str = Field(..., description="Name of the exercise (e.g., 'Barbell Squat')")
    sets: int = Field(..., description="Number of sets")
    reps: str = Field(..., description="Rep range (e.g., '8-12' or 'AMRAP')")


class DailyWorkout(BaseModel):
    day: str = Field(..., description="Day of the week (e.g., 'Monday' or 'Day 1')")

    # --- The Coach (Strategy Planner) Fills These ---
    is_rest_day: bool = Field(False, description="True if this is a recovery day")
    focus_area: str = Field(
        ..., description="Target muscles (e.g., 'Legs - Quads focus')"
    )
    coach_instructions: str = Field(
        ...,
        description="Specific directive for this day (e.g., 'Keep intensity high, use drop sets').",
    )

    # --- The Curator (Worker) Fills This Later ---
    need_exercise_generate: bool = Field(False)
    exercises: list[ExerciseDetail] = Field(
        default_factory=list, description="List of specific exercises"
    )
    user_instruction: Optional[str] = Field(
        None, description="User requested adjustment for this day only"
    )


class WeeklyPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    plan_name: str = Field(
        ..., description="Name of the split (e.g., 'PPL Hypertrophy Phase')"
    )
    goal_summary: str = Field(
        ..., description="Brief explanation of why this plan fits the user."
    )

    # This list allows us to easily map-reduce later
    schedule: list[DailyWorkout] = Field(..., description="List of 7 daily plans.")
