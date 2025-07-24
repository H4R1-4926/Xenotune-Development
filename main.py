# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import time

from music_gen import generate_music
from firebase import upload_to_firebase # You need to implement this

app = FastAPI(title="Xenotune")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Constants ---
VALID_MODES = {"focus", "relax", "sleep"}

# --- Request Model ---
class GenerateRequest(BaseModel):
    user_id: str
    mood: str  # focus, relax, sleep

# --- Generate Endpoint ---
@app.post("/generate")
async def generate_and_upload_music(request: GenerateRequest):
    mood = request.mood.lower()

    if mood not in VALID_MODES:
        return JSONResponse({"error": "Invalid mood. Choose focus, relax, or sleep."}, status_code=400)

    try:
        timestamp = int(time.time())
        filename = f"{mood}_{timestamp}.mp3"
        local_path = generate_music(mood, filename)

        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)

        firebase_path = f"users/{request.user_id}/{filename}"
        download_url = upload_to_firebase(local_path, firebase_path)

        return {
            "status": "success",
            "download_url": download_url,
            "message": f"{mood.capitalize()} music generated and uploaded."
        }

    except Exception as e:
        return JSONResponse({"error": f"Unexpected error: {str(e)}"}, status_code=500)

# --- Test Endpoint ---
@app.get("/")
def root():
    return {"message": "Xenotune backend is running and ready to generate music."}
