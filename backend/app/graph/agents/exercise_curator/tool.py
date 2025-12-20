from typing import Optional

import requests
from langchain_core.tools import tool

BASE_URL = "https://www.exercisedb.dev/api/v1"


def is_url_valid(url: str) -> bool:
    """Helper to check if a GIF URL actually exists and is accessible."""
    if not url:
        return False
    try:
        # Use a HEAD request to be fast (doesn't download the image body)
        # Use a timeout so the agent doesn't hang
        response = requests.head(url, allow_redirects=True, timeout=2.0)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        # Specifically catch network errors (timeouts, DNS issues, etc.)
        # We return False because the image is essentially unreachable for the user
        print(f"📡 GIF Validation failed for {url}: {e}")
        return False


@tool
def search_exercise_tool(
    target_muscle: Optional[str] = None,
    equipment: Optional[str] = None,
    body_part: Optional[str] = None,
    offset: int = 0,
):
    """
    Search for fitness exercises based on muscle, equipment, or body part.

    Args:
        target_muscle: The specific muscle (e.g., 'biceps', 'pectoralis', 'latissimus').
        equipment: Equipment available (e.g., 'dumbbell', 'body weight', 'cable').
        body_part: General area (e.g., 'waist', 'upper arms', 'chest').
        offset: Skip this many results. Use 0 for most popular, gentally plus 10 for variations.
    """
    if target_muscle or equipment or body_part:
        endpoint = f"{BASE_URL}/exercises/filter"
        params = {
            "muscles": target_muscle,
            "equipment": equipment,
            "bodyParts": body_part,
            "limit": 10,  # Don't overwhelm the context window
            "offset": offset,
        }
    else:
        return "Error: You must provide at least one search parameter."

    try:
        print(f"🛠️ Content Curator searching: {endpoint} with {params}")
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            return f"API Error: {response.status_code}"

        data = response.json().get("data", [])
        valid_results = []

        for ex in data:
            gif_url = ex.get("gifUrl")

            # --- VALIDATION STEP ---
            if is_url_valid(gif_url):
                valid_results.append(
                    {
                        "name": ex.get("name"),
                        "id": ex.get("exerciseId"),
                        "instructions": " ".join(ex.get("instructions", [])),
                        "gifUrl": gif_url,  # Now we include it because we know it works
                    }
                )

            # Stop once we have 5-6 solid, working exercises to save context
            if len(valid_results) >= 6:
                break

        return (
            valid_results
            if valid_results
            else "No exercises found with working video links."
        )

    except Exception as e:
        return f"Request Failed: {e}"
