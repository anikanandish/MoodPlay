"""
app.py — MoodPlay Localhost Web Application.
Serves the vinyl-inspired, private local AI music discovery interface.
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from mood_engine import get_music_recommendations, check_ollama_status
from spotify_service import is_spotify_configured

app = FastAPI(title="MoodPlay — Private AI Music Companion")

# In-memory mood history (stores recent sessions)
mood_history = [
    "Late night jazz with warm rain",
    "Deep focus ambient coding",
    "Golden hour sunset drive"
]


class MoodRequest(BaseModel):
    mood: str
    count: Optional[int] = 5


# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "MoodPlay Web UI is loading..."}


@app.get("/api/status")
def get_system_status():
    ollama_info = check_ollama_status()
    spotify_ready = is_spotify_configured()
    return {
        "ollama": ollama_info,
        "spotify": {
            "configured": spotify_ready,
            "mode": "API Live" if spotify_ready else "Direct Search Link (Offline Friendly)"
        }
    }


@app.get("/api/history")
def get_history():
    return {"history": mood_history}


@app.post("/api/recommend")
def recommend_music(payload: MoodRequest):
    mood = payload.mood.strip()
    if not mood:
        raise HTTPException(status_code=400, detail="Mood description cannot be empty.")

    # Update history (keep last 8 unique)
    if mood in mood_history:
        mood_history.remove(mood)
    mood_history.insert(0, mood)
    if len(mood_history) > 8:
        mood_history.pop()

    try:
        recommendations = get_music_recommendations(mood, count=payload.count or 5)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating playlist: {str(e)}"
        )


# Mount static assets (CSS, JS, images, icons)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🎵 MoodPlay Local Web Server Starting...")
    print("✨ Open your browser to: http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
