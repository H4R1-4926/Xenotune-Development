from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from music_gen import generate_and_play_loop
import threading
import os

app = FastAPI()

# Serve static music files at /static/music/
STATIC_MUSIC_DIR = "static/music"
os.makedirs(STATIC_MUSIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
