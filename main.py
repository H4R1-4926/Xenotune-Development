from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from music_gen import generate_music
import os

app = FastAPI()

# Enable CORS for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output folder
app.mount("/output", StaticFiles(directory="output"), name="output")

# ---- API: JSON endpoint ----
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

# ---- UI: HTML interface ----
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>Xenotune Generator</title></head>
        <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
            <h1>🎶 Xenotune AI Music Generator</h1>
            <form action="/generate" method="post">
                <label>Select Mode:</label><br><br>
                <select name="mode">
                    <option value="focus">Focus</option>
                    <option value="relax">Relax</option>
                    <option value="sleep">Sleep</option>
                </select><br><br>
                <button type="submit">Generate Music</button>
            </form>
        </body>
    </html>
    """

@app.post("/generate", response_class=FileResponse)
async def generate_ui(mode: str = Form(...)):
    try:
        path = generate_music(mode)
        filename = os.path.basename(path)
        return FileResponse(path, media_type="audio/midi", filename=filename)
    except Exception as e:
        return HTMLResponse(f"<h2>Error: {str(e)}</h2>", status_code=500)
