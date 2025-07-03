from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from music_gen import generate_focus_music, generate_relax_music, generate_sleep_music

app = FastAPI()

# CORS middleware for API + Flutter compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to your frontend origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates setup
app.mount("/output", StaticFiles(directory="output"), name="output")
templates = Jinja2Templates(directory="templates")

# HTML Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Generate Focus MIDI
@app.get("/generate/focus")
async def generate_focus():
    midi_path = generate_focus_music()
    return FileResponse(midi_path, media_type="audio/midi", filename=os.path.basename(midi_path))

# Generate Relax MIDI
@app.get("/generate/relax")
async def generate_relax():
    midi_path = generate_relax_music()
    return FileResponse(midi_path, media_type="audio/midi", filename=os.path.basename(midi_path))

# Generate Sleep MIDI
@app.get("/generate/sleep")
async def generate_sleep():
    midi_path = generate_sleep_music()
    return FileResponse(midi_path, media_type="audio/midi", filename=os.path.basename(midi_path))
