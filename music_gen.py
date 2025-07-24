import os, time, json, shutil, random, subprocess, atexit, threading, signal
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from json_gen import main

CONFIG_PATH = "config.json"
OUTPUT_PATH = "output"
FFPLAY_PATH = "ffmpeg/bin/ffplay.exe"
FLUIDSYNTH_PATH = "fluidsynth/bin/fluidsynth.exe"
SOUNDFONT_PATH = "FluidR3_GM/FluidR3_GM.sf2"
FFMPEG_PATH = "ffmpeg/bin/ffmpeg.exe"
BGM_PATH = "assets/bgm.mp3"

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

music_state = {
    "stop": False,
    "pause": False,
    "volume": 1.0,
    "mode": "focus"
}


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_instrument(name):
    return INSTRUMENT_MAP.get(name, instrument.Instrument(name))

import subprocess
import os

def convert_midi_to_mp3(midi_path):
    wav = midi_path.replace(".mid", ".wav")
    mp3 = midi_path.replace(".mid", ".mp3")
    mixed = midi_path.replace(".mid", "_mixed.mp3")

    try:
        # Convert MIDI to WAV
        subprocess.run([FLUIDSYNTH_PATH, "-ni", "-F", wav, "-r", "44100", SOUNDFONT_PATH, midi_path], check=True)
        
        # Convert WAV to MP3
        subprocess.run([FFMPEG_PATH, "-y", "-i", wav, mp3], check=True)

        # Get the duration of the generated music (mp3)
        result = subprocess.run(
            [FFMPEG_PATH, "-i", mp3, "-f", "null", "-"],
            stderr=subprocess.PIPE,
            text=True
        )
        duration_line = [line for line in result.stderr.splitlines() if "Duration" in line]
        duration = None
        if duration_line:
            time_str = duration_line[0].split("Duration:")[1].split(",")[0].strip()
            h, m, s = map(float, time_str.replace(":", " ").split())
            duration = h * 3600 + m * 60 + s

        if not duration:
            raise Exception("Could not extract MP3 duration.")

        # Mix and trim both generated music and BGM to same duration
        subprocess.run([
            FFMPEG_PATH, "-y",
            "-t", str(duration),
            "-i", mp3,
            "-t", str(duration),
            "-i", BGM_PATH,
            "-filter_complex", "[0:a]volume=0.3[a0];[1:a]volume=0.5[a1];[a0][a1]amix=inputs=2:duration=shortest",
            "-c:a", "libmp3lame",
            mixed
        ], check=True)

    finally:
        for f in [wav, mp3]:
            if os.path.exists(f):
                os.remove(f)

    return mixed

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

def generate_music(mode):
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

def music_loop():
    while not music_state["stop"]:
        if music_state["pause"]:
            time.sleep(0.5)
            continue

        music_path = generate_music(music_state["mode"])
        if not music_path:
            continue
        print(f"🎶 Playing: {music_path}")
        main()
        p = subprocess.Popen([FFPLAY_PATH, "-nodisp", "-autoexit", "-volume", str(int(music_state["volume"] * 100)), music_path])
        while p.poll() is None:
            if music_state["stop"]:
                p.terminate()
                break
            if music_state["pause"]:
                p.send_signal(signal.SIGSTOP)
                while music_state["pause"] and not music_state["stop"]:
                    time.sleep(0.5)
                if not music_state["stop"]:
                    p.send_signal(signal.SIGCONT)
            time.sleep(0.5)

def start_music(mode):
    music_state.update({"stop": False, "pause": False, "mode": mode})
    threading.Thread(target=music_loop, daemon=True).start()

def stop_music():
    music_state["stop"] = True

def pause_music():
    music_state["pause"] = True

def resume_music():
    music_state["pause"] = False

def set_volume(vol):
    music_state["volume"] = max(0.0, min(vol, 1.0))

atexit.register(stop_music)
