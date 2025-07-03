from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from music_gen import generate_focus_music, generate_relax_music, generate_sleep_music

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + Templates
app.mount("/output", StaticFiles(directory="output"), name="output")
templates = Jinja2Templates(directory="templates")

# Global paths for last generated files
last_files = {
    "focus": None,
    "relax": None,
    "sleep": None
}

# HTML Home
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Music Endpoints ---
@app.get("/generate/focus")
async def generate_focus():
    path = generate_focus_music()
    last_files["focus"] = os.path.basename(path)
    return {"filename": last_files["focus"]}

@app.get("/generate/relax")
async def generate_relax():
    path = generate_relax_music()
    last_files["relax"] = os.path.basename(path)
    return {"filename": last_files["relax"]}

@app.get("/generate/sleep")
async def generate_sleep():
    path = generate_sleep_music()
    last_files["sleep"] = os.path.basename(path)
    return {"filename": last_files["sleep"]}

@app.get("/play/{mode}")
async def play_music(mode: str):
    filename = last_files.get(mode)
    if filename:
        path = os.path.join("output", filename)
        return FileResponse(path, media_type="audio/midi", filename=filename)
    return {"error": "No file generated yet. Click generate first."}
