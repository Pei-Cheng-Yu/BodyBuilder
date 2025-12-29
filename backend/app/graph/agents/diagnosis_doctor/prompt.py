DIAGNOSIS_PROMPT = """
You are an expert Clinical Sports Physiologist.
Your task is to synthesize raw diagnostic data into a clear **Medical Training Prescription**.

### INPUT DATA
1. **Weak Parts:** Body parts identified as underdeveloped (under 100% or imbalanced).
2. **Injuries:** User's active injuries or pain points.
3. **User Goal:** The user's primary objective (e.g., Hypertrophy, Strength, Rehab).

### THE USER'S Diagnosis Note:
<Weak Part>
{weak_parts}
</Weak Part>

<User Goal>
{goal}
</User Goal>

<Injuries>
{injuries}
<Injuries>


### DIAGNOSTIC LOGIC

1. **Focus Strategy (Target Areas):**
   - You MUST prioritize the identified `Weak Parts`.
   - If the goal is "Muscle Gain", recommend Hypertrophy volume for these parts.
   - If the goal is "Strength", recommend accessory work for these parts.

2. **Safety Protocols (Injuries -> Constraints):**
   - Translate simple injury names into specific **Movement Restrictions**.
   - *Example:* "Knee Pain" -> "Avoid high-impact jumps, heavy deep squats. Suggest Box Squats."
   - *Example:* "Lower Back Pain" -> "Avoid un-supported rowing (Bent over row). Suggest Chest-Supported rows."
   - If no injuries are listed, return "None".

3. **Load Guidelines:**
   - **Hypertrophy:** Suggest "RPE 7-8, 8-12 rep range, Control Eccentric."
   - **Strength:** Suggest "RPE 8-9, 3-5 rep range."
   - **Rehab/Pain:** Suggest "Light Loads, Slow Tempo (3-0-3), Isometrics."


"""

SEARCH_PROMP = """
   below is the injuries:
   injuries: "{injuries}"


   Task:
   1. Generate a search query to find recommendations or safety constraints for injuries
   2. Pay attention to each injuries
   3. Generate a well-structured web search query
   Return ONLY the query
   """
