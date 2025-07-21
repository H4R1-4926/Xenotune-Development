from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional
from music_gen import generate_and_play_loop, generate_music
from firebase import upload_to_firebase
import threading, time
 
app = FastAPI()
 
VALID_MODES = {"focus", "relax", "sleep"}
VALID_ACTIONS = {"play_loop", "generate_and_upload"}
 
 
# Start loop in background thread
def start_music_loop(mode: str):
    threading.Thread(target=generate_and_play_loop, args=(mode,), daemon=True).start()
 
 
# Shared logic for /music and /gmusic
def handle_music_logic(mode: str, user_id: Optional[str], action: str):
    if mode not in VALID_MODES:
        return JSONResponse({"error": "Invalid mode. Choose from focus, relax, or sleep."}, status_code=400)
   
    if action not in VALID_ACTIONS:
        return JSONResponse({"error": "Invalid action. Choose from play_loop or generate_and_upload."}, status_code=400)
 
    if action == "play_loop":
        start_music_loop(mode)
        return JSONResponse({"status": f"{mode.capitalize()} music loop started playing on backend."})
 
    if action == "generate_and_upload":
        if not user_id:
            return JSONResponse({"error": "user_id is required for uploading."}, status_code=400)
       
        filename = f"{mode}_{int(time.time())}.mp3"
        local_path = generate_music(mode)
 
        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)
 
        try:
            firebase_path = f"users/{user_id}/{filename}"
            url = upload_to_firebase(local_path, firebase_path)
            return JSONResponse({'download_url': url})
        except Exception as e:
            return JSONResponse({"error": f"Upload failed: {str(e)}"}, status_code=500)
 
 
# GET endpoint with query parameters
@app.get("/music/{mode}")
async def music_mode_get(
    mode: str,
    user_id: Optional[str] = Query(None),
    action: str = Query("play_loop")
):
    return handle_music_logic(mode, user_id, action)
 
 
 
 
# POST endpoint that accepts JSON and uploads music
@app.post("/generate-music")
async def generate_music_api(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        mood = data.get("mood", "sleep")
 
        if not user_id:
            return JSONResponse({"error": "user_id is required."}, status_code=400)
 
        filename = f"output/{mood}_{int(time.time())}.mp3"
        local_path = generate_music(mood)
 
        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)
 
        firebase_path = f"users/{user_id}/{filename}"
        url = upload_to_firebase(local_path, firebase_path)
 
        # ✅ Start background loop after upload
        start_music_loop(mood)
 
        return JSONResponse({'download_url': url})
 
    except Exception as e:
        return JSONResponse({"error": f"Unexpected error: {str(e)}"}, status_code=500)
 
 