from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
from music_gen import generate_music
from firebase import upload_to_firebase

app = FastAPI(title="Xenotune AI Music Generator")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Valid Modes ---
VALID_MODES = {"focus", "relax", "sleep"}

# --- Request Model ---
class GenerateMusicRequest(BaseModel):
    user_id: str
    mode: str

# --- Generate Music Endpoint ---
@app.post("/generate")
async def handle_music_generation(request: GenerateMusicRequest):
    mode = request.mode.lower().strip()
    user_id = request.user_id.strip()

    if mode not in VALID_MODES:
        return JSONResponse(
            content={"error": "Invalid mode. Choose from focus, relax, or sleep."},
            status_code=400
        )
    if not user_id:
        return JSONResponse(content={"error": "User ID is required."}, status_code=400)

    try:
        timestamp = int(time.time())
        filename = f"{mode}_{timestamp}.mp3"

        # Generate music
        local_path = generate_music(mode)
        if not local_path:
            return JSONResponse(content={"error": "Music generation failed."}, status_code=500)

        # Upload to Firebase
        firebase_path = f"users/{user_id}/{filename}"
        download_url = upload_to_firebase(local_path, firebase_path)

        return {
            "status": "success",
            "mode": mode,
            "filename": filename,
            "download_url": download_url,
            "message": f"{mode.capitalize()} music generated and uploaded."
        }

    except Exception as e:
        return JSONResponse(
            content={"error": f"Server error: {str(e)}"},
            status_code=500
        )

# --- Health Check ---
@app.get("/", summary="Xenotune API Health")
def health_check():
    return {"message": "🎶 Xenotune backend is alive and ready to generate music!"}
