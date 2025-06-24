from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from music_gen import generate_music
import os

app = FastAPI()

# Allow CORS for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set specific Flutter IP/domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema
class ModeRequest(BaseModel):
    mode: str  # "focus", "relax", "sleep"

@app.post("/generate/")
def generate_endpoint(request: ModeRequest):
    mode = request.mode.lower()
    try:
        output_file = generate_music(mode)
        filename = os.path.basename(output_file)
        return {"message": "Music generated", "file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
def download_file(filename: str):
    path = os.path.join("output", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="audio/midi", filename=filename)
