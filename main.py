from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

from music_gen import generate_music  # Must return local MP3 path
from firebase import upload_to_firebase  # Must upload and return URL

app = FastAPI(title="Xenotune AI Music Generator")

# Enable CORS (open for frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Valid Modes ---
VALID_MOODS = {"focus", "relax", "sleep"}

# --- Request Model ---
class GenerateMusicRequest(BaseModel):
    user_id: str
    mood: str

# --- Music Generation Endpoint ---
@app.post("/generate", summary="Generate and Upload Music")
async def handle_music_generation(request: GenerateMusicRequest):
    mood = request.mood.lower().strip()
    user_id = request.user_id.strip()

    if mood not in VALID_MOODS:
        return JSONResponse(
            content={"error": "Invalid mood. Choose from focus, relax, or sleep."},
            status_code=400
        )

    if not user_id:
        return JSONResponse(content={"error": "User ID is required."}, status_code=400)

    try:
        timestamp = int(time.time())
        filename = f"{mood}_{timestamp}.mp3"

        # Generate music based on mood and save locally
        local_mp3_path = generate_music(mood, filename)
        if not local_mp3_path:
            return JSONResponse(content={"error": "Music generation failed."}, status_code=500)

        # Upload generated music to Firebase
        firebase_path = f"users/{user_id}/{filename}"
        download_url = upload_to_firebase(local_mp3_path, firebase_path)

        return {
            "status": "success",
            "mood": mood,
            "filename": filename,
            "download_url": download_url,
            "message": f"{mood.capitalize()} music successfully generated and uploaded."
        }

    except Exception as e:
        return JSONResponse(
            content={"error": f"Unexpected server error: {str(e)}"},
            status_code=500
        )

# --- Health Check Endpoint ---
@app.get("/", summary="Check API Status")
def health_check():
    return {"message": "🎵 Xenotune backend is up and ready to generate your music!"}
