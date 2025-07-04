from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from music_gen import generate_focus_music, generate_relax_music, generate_sleep_music

app = FastAPI()

# Root Route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("index.html", {"request": request})

# Generate Focus Music
@app.get("/generate/focus")
async def generate_focus():
    file_path = generate_focus_music()
    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")

# Generate Relax Music
@app.get("/generate/relax")
async def generate_relax():
    file_path = generate_relax_music()
    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")

# Generate Sleep Music
@app.get("/generate/sleep")
async def generate_sleep():
    file_path = generate_sleep_music()
    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")
