import uvicorn
from app.auth import routes as auth
from app.routers import exercise_detail, stream, plan
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BodyBuilder AI Backend")

# --- CORS Configuration ---
# Allow requests from the frontend (React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---

app.include_router(auth.router, prefix="/api/auth")
app.include_router(exercise_detail.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(plan.router, prefix="/api", tags=["Plans"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "BodyBuilder API is running"}


if __name__ == "__main__":
    # Run with: python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
