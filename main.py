from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from music_gen import generate_and_play_loop, generate_music
from firebase import upload_to_firebase
import threading, time

app = FastAPI()

VALID_MODES = {"focus", "relax", "sleep"}
VALID_ACTIONS = {"play_loop", "generate_and_upload"}

class MusicRequest(BaseModel):
    mode: str
    user_id: str | None = None
    action: str = "play_loop"

def start_music_loop(mode: str):
    threading.Thread(target=generate_and_play_loop, args=(mode,), daemon=True).start()

def handle_music_request(mode: str, user_id: str | None, action: str):
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

        local_path = generate_music(mode)
        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)

        filename = f"{mode}_{int(time.time())}.mp3"
        firebase_path = f"users/{user_id}/{filename}"

        try:
            url = upload_to_firebase(local_path, firebase_path)
            return JSONResponse({'download_url': url})
        except Exception as e:
            return JSONResponse({"error": f"Upload failed: {str(e)}"}, status_code=500)

@app.get("/music/{mode}")
async def music_mode_get(
    mode: str,
    user_id: str = Query(None),
    action: str = Query("play_loop")
):
    return handle_music_request(mode, user_id, action)

@app.post("/music")
async def music_mode_post(request: MusicRequest):
    return handle_music_request(request.mode, request.user_id, request.action)
