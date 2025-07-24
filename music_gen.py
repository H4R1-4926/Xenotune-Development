import os, time, json, shutil, random, subprocess, atexit, threading, signal
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from json_gen import main

# --- Paths ---
CONFIG_PATH = "config.json"
OUTPUT_PATH = "output"
FFPLAY_PATH = "ffmpeg/bin/ffplay.exe"
FLUIDSYNTH_PATH = "fluidsynth/bin/fluidsynth.exe"
SOUNDFONT_PATH = "FluidR3_GM/FluidR3_GM.sf2"
FFMPEG_PATH = "ffmpeg/bin/ffmpeg.exe"
BGM_PATH = "assets/bgm.mp3"

# --- Globals ---
stop_flag = False
music_proc = None
bgm_proc = None
is_paused = False
volume = 1.0  # Default volume (1.0 = 100%)

SECTION_LENGTHS = {
    "intro": 4, "groove": 8, "verse": 8, "chorus": 8, "bridge": 8, "drop": 8,
    "build": 8, "solo": 8, "outro": 4, "loop": 16, "variation": 8, "layered_loop": 8,
    "fadeout": 4, "layer1": 8, "layer2": 8, "ambient_loop": 16, "dream_flow": 8,
    "infinite_loop": 16, "loop_a": 8, "focus_block": 8, "pause_fill": 4,
    "soothing_loop": 16, "deep_layer": 8, "dream_pad": 8
}

INSTRUMENT_MAP = {
    "Charango": instrument.Mandolin(), "Reeds": instrument.EnglishHorn(),
    "Harp": instrument.Harp(), "Piano": instrument.Piano(),
    "Electric Piano": instrument.ElectricPiano(), "Synth Lead": instrument.SopranoSaxophone(),
    "Bass Guitar": instrument.ElectricBass(), "Drum Kit": instrument.Woodblock(),
    "Arpeggiator": instrument.Harpsichord(), "Acoustic Guitar": instrument.AcousticGuitar(),
    "Soft Strings": instrument.Violin(), "Felt Piano": instrument.Piano(),
    "Air Pad": instrument.ElectricOrgan(), "Sub Bass": instrument.Contrabass(),
    "Flute": instrument.Flute(), "Chill Guitar": instrument.AcousticGuitar(),
    "Electric Guitar": instrument.ElectricGuitar()
}

# --- Config Loader ---
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_instrument(name):
    return INSTRUMENT_MAP.get(name, instrument.Instrument(name))

# --- Convert MIDI to MP3 + Mix with BGM ---
def convert_midi_to_mp3(midi_path):
    wav = midi_path.replace(".mid", ".wav")
    mp3 = midi_path.replace(".mid", ".mp3")
    mixed = midi_path.replace(".mid", "_mixed.mp3")
    try:
        subprocess.run([FLUIDSYNTH_PATH, "-ni", "-F", wav, "-r", "44100", SOUNDFONT_PATH, midi_path], check=True)
        subprocess.run([FFMPEG_PATH, "-y", "-i", wav, mp3], check=True)
        subprocess.run([
            FFMPEG_PATH, "-y", "-i", mp3, "-i", BGM_PATH,
            "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.3[a1];[a0][a1]amix=inputs=2",
            "-c:a", "libmp3lame", mixed
        ], check=True)
    finally:
        for f in [wav, mp3]:
            if os.path.exists(f):
                os.remove(f)
    return mixed

# --- Melody Generator ---
def create_melody_part(mode, structure, progression):
    melody = stream.Part()
    melody.insert(0, {
        "focus": instrument.ElectricPiano(),
        "relax": instrument.Piano(),
        "sleep": instrument.Piano()
    }.get(mode, instrument.Piano()))

    scale = {
        "focus": ["C5", "D5", "E5", "F5", "G5", "A5"],
        "relax": ["C4", "D4", "E4", "G4", "A4"],
        "sleep": ["A3", "B3", "C4", "D4", "E4"]
    }.get(mode, ["C4", "D4", "E4", "G4"])

    for section in structure:
        beats = 0
        total_beats = SECTION_LENGTHS.get(section, 8) * 4
        motif = [random.choice(scale) for _ in range(4)]
        while beats < total_beats:
            phrase = random.choice([motif, motif[::-1], [random.choice(scale) for _ in range(4)]])
            for pitch in phrase:
                dur = random.choice([0.5, 1.0]) if mode == "focus" else 1.0
                n = note.Note(pitch, quarterLength=dur)
                n.volume.velocity = random.randint(40, 70)
                melody.append(n)
                beats += dur
                if beats >= total_beats:
                    break
    return melody

# --- Music Generator ---
def generate_music(mode):
    try:
        config = load_config()
        data = config.get(mode)
        if not data:
            raise ValueError(f"Invalid mode: {mode}")
        bpm = data.get("tempo", 80)
        instruments = data.get("instruments", [])
        structure = data.get("structure", ["intro", "loop", "outro"])

        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.makedirs(OUTPUT_PATH, exist_ok=True)

        score = stream.Score()
        score.append(tempo.MetronomeMark(number=bpm + random.choice([-2, 0, 1])))
        score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()}"))

        progression_map = {
            "focus": [["C4", "E4", "G4"], ["D4", "F4", "A4"], ["G3", "B3", "D4"]],
            "relax": [["C4", "G4", "A4"], ["E4", "G4", "B4"], ["D4", "F4", "A4"]],
            "sleep": [["C3", "E3", "G3"], ["A3", "C4", "E4"], ["F3", "A3", "C4"]]
        }
        progression = progression_map.get(mode, [["C4", "E4", "G4"]])

        for inst in instruments:
            if "samples" in inst:
                continue
            part = stream.Part()
            part.insert(0, get_instrument(inst.get("name", "Piano")))
            style = inst.get("style", "")
            notes = inst.get("notes", random.choice(progression))
            vel_range = (20, 50) if "ambient" in style else (30, 70)

            for section in structure:
                beats = 0
                total_beats = SECTION_LENGTHS.get(section, 8) * 4
                while beats < total_beats:
                    vel = random.randint(*vel_range)
                    if "arp" in style:
                        for n in notes:
                            nt = note.Note(n, quarterLength=0.5)
                            nt.volume.velocity = vel
                            part.append(nt)
                            beats += 0.5
                            if beats >= total_beats:
                                break
                        continue
                    length = 1.5 if "slow" in style else 1.0
                    c = chord.Chord(random.choice(progression), quarterLength=length)
                    c.volume.velocity = vel
                    part.append(c)
                    beats += c.quarterLength
            score.append(part)

        score.append(create_melody_part(mode, structure, progression))

        midi_path = os.path.join(OUTPUT_PATH, f"{mode}.mid")
        mf = midi.translate.streamToMidiFile(score)
        mf.open(midi_path, 'wb'); mf.write(); mf.close()
        return convert_midi_to_mp3(midi_path)

    except Exception as e:
        print(f"⚠️ Error generating music: {e}")
        return None

# --- Loop & Control ---
def start_music_loop(mode="focus"):
    global stop_flag, music_proc, bgm_proc
    stop_flag = False
    print(f"🎧 Starting music loop in {mode.upper()} mode...")

    bgm_proc = subprocess.Popen([FFPLAY_PATH, "-nodisp", "-autoexit", "-loop", "0", BGM_PATH],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    while not stop_flag:
        music_path = generate_music(mode)
        if not music_path or not os.path.exists(music_path):
            time.sleep(2)
            continue
        print(f"🎶 Playing: {music_path}")
        main()  # optional: update metadata
        music_proc = subprocess.Popen([FFPLAY_PATH, "-nodisp", "-autoexit", "-volume", str(int(volume * 100)), music_path])
        music_proc.wait()

    stop_music()

def pause_playback():
    global is_paused, music_proc
    if music_proc and not is_paused:
        music_proc.send_signal(signal.SIGSTOP)
        is_paused = True
        print("⏸ Paused")

def resume_playback():
    global is_paused, music_proc
    if music_proc and is_paused:
        music_proc.send_signal(signal.SIGCONT)
        is_paused = False
        print("▶️ Resumed")

def stop_music():
    global stop_flag, music_proc, bgm_proc
    stop_flag = True
    if music_proc: music_proc.terminate()
    if bgm_proc: bgm_proc.terminate()
    print("🛑 Music & BGM stopped")

def set_volume(vol: float):
    global volume
    volume = max(0.0, min(vol, 1.0))
    print(f"🔊 Volume set to {int(volume * 100)}%")

# --- Cleanup ---
def cleanup():
    stop_music()
    print("✅ Cleanup complete")

atexit.register(cleanup)

# --- Local Test ---
if __name__ == "__main__":
    threading.Thread(target=start_music_loop, args=("focus",)).start()
