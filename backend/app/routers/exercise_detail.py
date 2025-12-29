import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/exercises/{exercise_id}")
async def get_exercise_detail(
    exercise_id: str,
):
    url = f"https://exercisedb-api1.p.rapidapi.com/api/v1/exercises/{exercise_id}"

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "exercisedb-api1.p.rapidapi.com",
    }

    async with httpx.AsyncClient(
        headers=headers, timeout=httpx.Timeout(10.0)
    ) as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Exercise not found")

    data = resp.json()
    exercise = data["data"]
    image_urls = exercise["imageUrls"]
    return {
        "name": exercise["name"],
        "overview": exercise["overview"],
        "bodyParts": exercise["bodyParts"],
        "imageUrl": image_urls["1080p"],
        "videoUrl": exercise["videoUrl"],
        "instructions": exercise["instructions"],
        "exerciseTips": exercise["exerciseTips"],
    }
