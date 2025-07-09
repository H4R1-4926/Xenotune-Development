from fastapi import FastAPI
from fastapi.responses import JSONResponse
from music_gen import generate_music
import threading

app = FastAPI()

music_paths = {
    "focus": "",
    "relax": "",
    "sleep": ""
}
generation_status = {
    "focus": "not_started",
    "relax": "not_started",
    "sleep": "not_started"
}

@app.get("/generate/{mode}")
async def generate(mode: str):
    mode = mode.lower()
    if mode not in music_paths:
        return JSONResponse({"error": "Invalid mode"}, status_code=400)

    def generate_task():
        generation_status[mode] = "generating"
        path = generate_music(mode)
        music_paths[mode] = path
        generation_status[mode] = "done"

    threading.Thread(target=generate_task, daemon=True).start()
    return JSONResponse({"status": f"{mode.capitalize()} music generation started."})

@app.get("/status/{mode}")
async def status(mode: str):
    mode = mode.lower()
    if mode not in generation_status:
        return JSONResponse({"error": "Invalid mode"}, status_code=400)

    return JSONResponse({"status": generation_status[mode]})
