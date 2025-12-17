from typing import Literal, Optional

from pydantic import BaseModel, Field, computed_field


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
    left_arm_kg: Optional[float] = Field(None, description="Left Arm Lean Mass (kg)")
    trunk_kg: Optional[float] = Field(None, description="Trunk Lean Mass (kg)")
    right_leg_kg: Optional[float] = Field(None, description="Right Leg Lean Mass (kg)")
    left_leg_kg: Optional[float] = Field(None, description="Left Leg Lean Mass (kg)")


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
    name: Optional[str]
    gender: Literal["Male", "Female"]
    age: int = Field(..., gt=0, lt=120)

    injuries: list[str] = Field(
        default_factory=list, description="傷病史，如 ['knee_pain', 'lower_back']"
    )
    activity_level: Literal[
        "Sedentary", "Lightly Active", "Moderately Active", "Very Active"
    ] = "Sedentary"

    latest_scan: Optional[InbodyMetrics] = None
    # Body composition
