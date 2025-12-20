from typing import List

from app.graph.schema import SegmentalAnalysis


def identify_weak_parts(seg: SegmentalAnalysis) -> List[str]:
    weak_parts = []
    parts = {
        "Right Arm": seg.right_arm_percent,
        "Left Arm": seg.left_arm_percent,
        "Trunk": seg.trunk_percent,
        "Right Leg": seg.right_leg_percent,
        "Left Leg": seg.left_leg_percent,
    }

    # Check weakness (<100%)
    for name, percent in parts.items():
        if percent is not None and percent < 100.0:
            weak_parts.append(name)

    # Check Imbalance
    if seg.right_arm_percent and seg.left_arm_percent:
        diff = abs(seg.right_arm_percent - seg.left_arm_percent)
        if diff > 6.0:
            # Add the weaker side
            if seg.right_arm_percent < seg.left_arm_percent:
                weak_parts.append("Right Arm")
            else:
                weak_parts.append("Left Arm")

    if seg.right_leg_percent and seg.left_leg_percent:
        diff = abs(seg.right_leg_percent - seg.left_leg_percent)
        if diff > 6.0:
            if seg.right_leg_percent < seg.left_leg_percent:
                weak_parts.append("Right Leg")
            else:
                weak_parts.append("Left Leg")

    weak_parts = list(set(weak_parts))

    # Fallback: choose the lowest
    if not weak_parts:
        valid_parts = {k: v for k, v in parts.items() if v is not None}
        if valid_parts:
            weakest_link = min(valid_parts, key=valid_parts.get)
            weak_parts.append(weakest_link)

    return weak_parts
