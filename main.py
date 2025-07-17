from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from music_gen import generate_and_play_loop, generate_music
import threading, time
from firebase import upload_to_firebase

app = FastAPI()

@app.get("/play/focus")

async def play_focus():
    threading.Thread(target=generate_and_play_loop, args=("focus",), daemon=True).start()
    return JSONResponse({"status": "Focus music started playing on backend."})
@app.get("/play/relax")

async def play_relax():
    threading.Thread(target=generate_and_play_loop, args=("relax",), daemon=True).start()
    return JSONResponse({"status": "Relax music started playing on backend."})

@app.get("/play/sleep")
async def play_sleep():
    threading.Thread(target=generate_and_play_loop, args=("sleep",), daemon=True).start()
    return JSONResponse({"status": "Sleep music started playing on backend."})

@app.post("/generate-music")
async def generate_music_api(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    mood = data.get("mood", "relax")  # default mood is 'relax'
    filename = f"{mood}_{int(time.time())}.mp3"
    local_path = generate_music(filename, mood)  # Make sure this accepts mood
    url = upload_to_firebase(local_path, user_id, filename)
    return JSONResponse({'download_url': url})