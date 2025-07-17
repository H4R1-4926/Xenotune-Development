import os
import time
import json
import shutil
import random
import subprocess
import pygame
import atexit
import threading
from datetime import datetime, timedelta
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from json_gen import main  # optional if you auto-refresh config
from pathlib import Path

# === CONFIG ===
STATIC_MUSIC_DIR = "static/music"
CLEANUP_INTERVAL_SECONDS = 600  # 10 minutes
DELETE_OLDER_THAN_MINUTES = 10

# === LOAD CONFIG ===
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# === INSTRUMENT MAP ===
def get_music21_instrument(name):
    mapping = {
        "Charango": instrument.Mandolin(),
        "Reeds": instrument.EnglishHorn(),
        "Harp": instrument.Harp(),
        "Piano": instrument.Piano(),
        "Electric Piano": instrument.ElectricPiano(),
        "Synth Lead": instrument.SopranoSaxophone(),
        "Bass Guitar": instrument.ElectricBass(),
        "Drum Kit": instrument.Woodblock(),
        "Arpeggiator": instrument.Harpsichord(),
        "Acoustic Guitar": instrument.AcousticGuitar(),
        "Soft Strings": instrument.Violin(),
        "Felt Piano": instrument.Piano(),
        "Air Pad": instrument.ElectricOrgan(),
        "Sub Bass": instrument.Contrabass(),
        "Flute": instrument.Flute(),
        "Chill Guitar": instrument.AcousticGuitar(),
        "Electric Guitar": instrument.ElectricGuitar()
    }
    return mapping.get(name, instrument.Instrument(name))

# === MUSIC GENERATOR ===
def generate_music(mode):
    config = load_config()
    mode_data = config.get(mode)
    if not mode_data:
        raise ValueError(f"Invalid mode '{mode}' in config.")

    bpm = mode_data.get("tempo", 80)
    instruments = mode_data.get("instruments", [])
    structure = mode_data.get("structure", ["intro", "loop", "outro"])

    beats_per_bar = 4
    section_lengths = {
        "intro": 4, "groove": 8, "verse": 8, "chorus": 8, "bridge": 8,
        "drop": 8, "build": 8, "solo": 8, "outro": 4, "loop": 16,
        "variation": 8, "layered_loop": 8, "fadeout": 4, "layer1": 8,
        "layer2": 8, "ambient_loop": 16, "dream_flow": 8, "infinite_loop": 16,
        "loop_a": 8, "focus_block": 8, "pause_fill": 4, "soothing_loop": 16,
        "deep_layer": 8, "dream_pad": 8
    }

    Path(STATIC_MUSIC_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    midi_path = f"{STATIC_MUSIC_DIR}/{mode}_{timestamp}.mid"

    score = stream.Score()
    score.append(tempo.MetronomeMark(number=bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

    chord_sets = {
        "focus": [["C4", "E4", "G4"], ["D4", "F4", "A4"], ["G3", "B3", "D4"]],
        "relax": [["C4", "G4", "A4"], ["E4", "G4", "B4"], ["D4", "F4", "A4"]],
        "sleep": [["C3", "E3", "G3"], ["A3", "C4", "E4"], ["F3", "A3", "C4"]]
    }
    progression = chord_sets.get(mode, [["C4", "E4", "G4"]])

    for inst in instruments:
        if "samples" in inst:
            continue
        part = stream.Part()
        part.insert(0, get_music21_instrument(inst.get("name", "Piano")))
        style = inst.get("style", "")
        notes = inst.get("notes", random.choice(progression))

        for section_name in structure:
            bars = section_lengths.get(section_name, 8)
            section_beats = bars * beats_per_bar
            beats = 0
            while beats < section_beats:
                if "slow" in style or "ambient" in style:
                    c = chord.Chord(random.choice(progression), quarterLength=2.0)
                    c.volume.velocity = 30
                    part.append(c)
                    beats += 2
                elif "arp" in style:
                    for n in notes:
                        nt = note.Note(n, quarterLength=0.5)
                        nt.volume.velocity = 40
                        part.append(nt)
                        beats += 0.5
                        if beats >= section_beats:
                            break
                else:
                    c = chord.Chord(random.choice(progression), quarterLength=1.0)
                    c.volume.velocity = 50
                    part.append(c)
                    beats += 1
        score.append(part)

    # Melody
    melody_part = stream.Part()
    melody_part.insert(0, get_music21_instrument("Electric Piano"))
    melody_notes = {
        "focus": ["C5", "D5", "E5", "F5", "G5"],
        "relax": ["C4", "D4", "E4", "G4", "A4"],
        "sleep": ["A3", "B3", "C4", "D4", "E4"]
    }.get(mode, ["C4", "D4", "E4", "G4"])

    def generate_motif():
        return [random.choice(melody_notes) for _ in range(4)]

    for section_name in structure:
        section_beats = section_lengths.get(section_name, 8) * beats_per_bar
        beats = 0
        while beats < section_beats:
            for pitch in generate_motif():
                n = note.Note(pitch, quarterLength=1.0)
                n.volume.velocity = 60
                melody_part.append(n)
                beats += 1
                if beats >= section_beats:
                    break
    score.append(melody_part)

    # Write MIDI
    mf = midi.translate.streamToMidiFile(score)
    mf.open(midi_path, 'wb')
    mf.write()
    mf.close()

    return convert_midi_to_mp3(midi_path)

# === MIDI → MP3 CONVERSION ===
def convert_midi_to_mp3(
    midi_path,
    soundfont_path="FluidR3_GM/FluidR3_GM.sf2",
    fluidsynth_path="fluidsynth/bin/fluidsynth.exe",
    ffmpeg_path="ffmpeg/bin/ffmpeg.exe",
    bgm_path="assets/bgm.mp3",
    music_volume="1.0",
    bgm_volume="0.2"
):
    wav_path = midi_path.replace(".mid", ".wav")
    mp3_path = midi_path.replace(".mid", ".mp3")
    mixed_path = midi_path.replace(".mid", "_mixed.mp3")

    subprocess.run([
        fluidsynth_path, "-ni", "-F", wav_path, "-r", "44100", soundfont_path, midi_path
    ], check=True)

    subprocess.run([ffmpeg_path, "-y", "-i", wav_path, mp3_path], check=True)

    subprocess.run([
        ffmpeg_path, "-y",
        "-i", mp3_path,
        "-i", bgm_path,
        "-filter_complex",
        f"[0:a]volume={music_volume}[a0];[1:a]volume={bgm_volume}[a1];[a0][a1]amix=inputs=2:duration=first",
        "-c:a", "libmp3lame", mixed_path
    ], check=True)

    os.remove(midi_path)
    os.remove(wav_path)
    os.remove(mp3_path)

    return mixed_path

# === CLEANUP OLD FILES ===
def cleanup_old_files(directory=STATIC_MUSIC_DIR, max_age_minutes=10):
    now = datetime.now()
    cutoff = now - timedelta(minutes=max_age_minutes)
    deleted = 0

    for file in Path(directory).glob("*.*"):
        if file.suffix in [".mp3", ".mid", ".wav"] and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
            try:
                file.unlink()
                deleted += 1
            except Exception as e:
                print(f"Failed to delete {file.name}: {e}")
    if deleted:
        print(f"🧹 Cleanup complete: {deleted} old file(s) removed.")

# === LOOP PLAYER ===
stop_thread = False

def generate_and_play_loop(mode="focus"):
    global stop_thread
    pygame.mixer.init()
    print(f"🔁 Starting loop in {mode.upper()} mode")

    try:
        while not stop_thread:
            cleanup_old_files()
            mp3 = generate_music(mode)
            if not mp3 or not os.path.exists(mp3):
                print("⚠️ Skipped empty track")
                time.sleep(2)
                continue
            print(f"🎧 Playing: {mp3}")
            sound = pygame.mixer.Sound(mp3)
            sound.set_volume(0.9)
            sound.play()
            main()
            while pygame.mixer.get_busy() and not stop_thread:
                pygame.time.wait(100)
    finally:
        pygame.mixer.quit()

def cleanup():
    global stop_thread
    stop_thread = True
    print("🛑 Graceful shutdown triggered")

atexit.register(cleanup)

# === ENTRY ===
if __name__ == "__main__":
    threading.Thread(target=generate_and_play_loop, args=("focus",), daemon=True).start()
