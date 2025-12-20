# Mapped based on ExerciseDB taxonomy and standard anatomy
MUSCLE_GROUPS = {
    "back": [
        "back",  # General
        "lats",  # Slang/Common
        "latissimus dorsi",  # Medical
        "traps",
        "trapezius",
        "upper back",
        "lower back",
        "rhomboids",
        "spine",
        "levator scapulae",
    ],
    "cardio": ["cardiovascular system", "cardio"],
    "chest": [
        "chest",  # General
        "pectorals",  # Medical
        "upper chest",
        "serratus anterior",
    ],
    "lower arms": [
        "forearms",
        "brachialis",
        "wrist extensors",
        "wrist flexors",
        "wrists",
        "hands",
        "grip muscles",
    ],
    "upper arms": ["biceps", "triceps"],
    "lower legs": ["calves", "soleus", "shins", "ankles", "ankle stabilizers", "feet"],
    "upper legs": [
        "quads",
        "quadriceps",
        "hamstrings",
        "glutes",
        "abductors",
        "adductors",
        "inner thighs",
        "groin",
        "hip flexors",
    ],
    "neck": [
        "neck",
        "sternocleidomastoid",
        "levator scapulae",  # Can function in both back/neck logic
    ],
    "shoulders": ["shoulders", "delts", "deltoids", "rear deltoids", "rotator cuff"],
    "waist": ["abs", "abdominals", "lower abs", "obliques", "core"],
}
STANDARD_EQUIPMENT = [
    "stepmill machine",
    "elliptical machine",
    "trap bar",
    "stationary bike",
    "wheel roller",
    "smith machine",
    "skierg machine",
    "roller",
    "resistance band",
    "bosu ball",
    "weighted",
    "olympic barbell",
    "kettlebell",
    "upper body ergometer",
    "sled machine",
    "ez barbell",
    "dumbbell",
    "rope",
    "barbell",
    "band",
    "stability ball",
    "medicine ball",
    "assisted",
    "leverage machine",
    "cable",
    "body weight",
]
# Helper: Flattened list if you need to check valid muscles quickly
VALID_TARGET_MUSCLES = [m for muscles in MUSCLE_GROUPS.values() for m in muscles]
VALID_BODY_PARTS = list(MUSCLE_GROUPS.keys())
