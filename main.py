from fastapi import FastAPI
from fastapi.responses import JSONResponse
from music_gen import generate_and_play_loop
import threading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (safe for mobile apps)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
