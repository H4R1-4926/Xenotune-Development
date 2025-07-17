from fastapi import FastAPI
from fastapi.responses import JSONResponse
from music_gen import generate_and_play_loop, generate_music
import threading, time, jsonify
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

@app.route('/generate-music', methods=['POST'])
def generate_music(request):
    user_id = request.json['user_id']
    filename = f"song_{int(time.time())}.mp3"
    local_path = generate_music(filename)  # Your music generation logic
    url = upload_to_firebase(local_path, user_id, filename)
    return jsonify({'download_url': url})