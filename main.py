from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from music_gen import generate_and_play_loop, generate_music
from firebase import upload_to_firebase
import threading, time
 
app = FastAPI()
 
def start_music_loop(mode: str):
    threading.Thread(target=generate_and_play_loop, args=(mode,), daemon=True).start()
 
@app.get("/play/{mode}")
async def play_mode(mode: str):
    if mode not in ["focus", "relax", "sleep"]:
        return JSONResponse({"error": "Invalid mode. Choose from focus, relax, or sleep."}, status_code=400)
   
    start_music_loop(mode)
    return JSONResponse({"status": f"{mode.capitalize()} music started playing on backend."})
 
 
@app.post("/generate-music")
async def generate_music_api(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    mood = data.get("mood", "relax")
 
    filename = f"{mood}_{int(time.time())}.mp3"
    local_path = generate_music(mood)
 
    if not local_path:
        return JSONResponse({"error": "Music generation failed."}, status_code=500)
 
    firebase_path = f"users/{user_id}/{filename}"  # Optional: organize uploads by user
    url = upload_to_firebase(local_path, firebase_path)
 
    return JSONResponse({'download_url': url})