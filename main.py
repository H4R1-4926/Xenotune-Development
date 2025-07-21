from fastapi import FastAPI
from fastapi.responses import JSONResponse
from music_gen import generate_and_play_loop, generate_music
from firebase import upload_to_firebase
import threading, time

app = FastAPI()

def start_music_loop(mode: str):
    threading.Thread(target=generate_and_play_loop, args=(mode,), daemon=True).start()

@app.get("/music/{mode}")
async def music_mode_handler(mode: str, user_id: str = None, action: str = "play_loop"):
    if mode not in ["focus", "relax", "sleep"]:
        return JSONResponse({"error": "Invalid mode. Choose from focus, relax, or sleep."}, status_code=400)
    
    if action == "play_loop":
        start_music_loop(mode)
        return JSONResponse({"status": f"{mode.capitalize()} music loop started playing on backend."})

    elif action == "generate_and_upload":
        filename = f"{mode}_{int(time.time())}.mp3"
        local_path = generate_music(mode)

        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)

        if not user_id:
            return JSONResponse({"error": "user_id is required for uploading."}, status_code=400)

        firebase_path = f"users/{user_id}/{filename}"
        url = upload_to_firebase(local_path, firebase_path)
        return JSONResponse({'download_url': url})

    else:
        return JSONResponse({"error": "Invalid action. Choose from play_loop or generate_and_upload."}, status_code=400)
    

@app.post("/gmusic")
async def music_mode_handler(mode: str, user_id: str = None, action: str = "play_loop"):
    if mode not in ["focus", "relax", "sleep"]:
        return JSONResponse({"error": "Invalid mode. Choose from focus, relax, or sleep."}, status_code=400)
    
    if action == "play_loop":
        start_music_loop(mode)
        return JSONResponse({"status": f"{mode.capitalize()} music loop started playing on backend."})

    elif action == "generate_and_upload":
        filename = f"{mode}_{int(time.time())}.mp3"
        local_path = generate_music(mode)

        if not local_path:
            return JSONResponse({"error": "Music generation failed."}, status_code=500)

        if not user_id:
            return JSONResponse({"error": "user_id is required for uploading."}, status_code=400)

        firebase_path = f"users/{user_id}/{filename}"
        url = upload_to_firebase(local_path, firebase_path)
        return JSONResponse({'download_url': url})

    else:
        return JSONResponse({"error": "Invalid action. Choose from play_loop or generate_and_upload."}, status_code=400)