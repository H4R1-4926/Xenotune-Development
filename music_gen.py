import os
import time
import json
import shutil
import random
import subprocess
import pygame
import atexit
import threading
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from json_gen import main

CONFIG_PATH = "config.json"
OUTPUT_PATH = "output"

SECTION_LENGTHS = {
    "intro": 4, "groove": 8, "verse": 8, "chorus": 8, "bridge": 8,
    "drop": 8, "build": 8, "solo": 8, "outro": 4, "loop": 16,
    "variation": 8, "layered_loop": 8, "fadeout": 4, "layer1": 8,
    "layer2": 8, "ambient_loop": 16, "dream_flow": 8, "infinite_loop": 16,
    "loop_a": 8, "focus_block": 8, "pause_fill": 4, "soothing_loop": 16,
    "deep_layer": 8, "dream_pad": 8
}

INSTRUMENT_MAP = {
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

stop_thread = False


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_music21_instrument(name):
    return INSTRUMENT_MAP.get(name, instrument.Instrument(name))


def generate_music(mode):
    try:
        config = load_config()
        mode_data = config.get(mode)
        if not mode_data:
            raise ValueError(f"Invalid mode '{mode}' in config.")

        bpm = mode_data.get("tempo", 80)
        instruments = mode_data.get("instruments", [])
        structure = mode_data.get("structure", ["intro", "loop", "outro"])

        shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
        os.makedirs(OUTPUT_PATH, exist_ok=True)

        score = stream.Score()
        fluctuated_bpm = bpm + random.choice([-2, 0, 1])
        score.append(tempo.MetronomeMark(number=fluctuated_bpm))
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
                beats = 0
                section_beats = SECTION_LENGTHS.get(section_name, 8) * 4
                velocity_range = (20, 50) if "ambient" in style else (30, 70)

                while beats < section_beats:
                    vel = random.randint(*velocity_range)
                    if "slow" in style or "ambient" in style:
                        c = chord.Chord(random.choice(progression), quarterLength=1.5)
                    elif "arp" in style:
                        for n in notes:
                            nt = note.Note(n, quarterLength=0.5)
                            nt.volume.velocity = vel
                            part.append(nt)
                            beats += 0.5
                            if beats >= section_beats:
                                break
                        continue
                    else:
                        c = chord.Chord(random.choice(progression), quarterLength=1.0)

                    c.volume.velocity = vel
                    part.append(c)
                    beats += c.quarterLength

            score.append(part)

        melody_part = create_melody_part(mode, structure, progression)
        score.append(melody_part)

        midi_path = f"{OUTPUT_PATH}/music.mid"
        mf = midi.translate.streamToMidiFile(score)
        mf.open(midi_path, 'wb')
        mf.write()
        mf.close()

        return convert_midi_to_mp3(midi_path)

    except Exception as e:
        print(f"⚠️ Error generating music: {e}")
        return None


def create_melody_part(mode, structure, progression):
    melody_part = stream.Part()
    melody_part.insert(0, {
        "focus": instrument.ElectricPiano(),
        "relax": instrument.Piano(),
        "sleep": instrument.Piano()
    }.get(mode, instrument.Piano()))

    scale_map = {
        "focus": ["C5", "D5", "E5", "F5", "G5", "A5"],
        "relax": ["C4", "D4", "E4", "G4", "A4"],
        "sleep": ["A3", "B3", "C4", "D4", "E4"]
    }
    melody_notes = scale_map.get(mode, ["C4", "D4", "E4", "G4"])

    for section_name in structure:
        beats = 0
        section_beats = SECTION_LENGTHS.get(section_name, 8) * 4
        motif = [random.choice(melody_notes) for _ in range(4)]

        while beats < section_beats:
            phrase = random.choice([motif, motif[::-1], [random.choice(melody_notes) for _ in range(4)]])
            for pitch in phrase:
                dur = random.choice([0.5, 1.0, 1.5]) if mode == "focus" else 1.0
                n = note.Note(pitch, quarterLength=dur)
                n.volume.velocity = random.randint(40, 70)
                melody_part.append(n)
                beats += dur
                if beats >= section_beats:
                    break

    return melody_part


def convert_midi_to_mp3(midi_path):
    soundfont_path = "FluidR3_GM/FluidR3_GM.sf2"
    fluidsynth_path = "fluidsynth/bin/fluidsynth.exe"
    ffmpeg_path = "ffmpeg/bin/ffmpeg.exe"
    bgm_path = "assets/bgm.mp3"

    wav_path = midi_path.replace(".mid", ".wav")
    mp3_path = midi_path.replace(".mid", ".mp3")
    final_mix = midi_path.replace(".mid", "_mixed.mp3")

    try:
        subprocess.run([fluidsynth_path, "-ni", "-F", wav_path, "-r", "44100", soundfont_path, midi_path], check=True)
        subprocess.run([ffmpeg_path, "-y", "-i", wav_path, mp3_path], check=True)
        subprocess.run([
            ffmpeg_path, "-y",
            "-i", mp3_path,
            "-i", bgm_path,
            "-filter_complex",
            "[0:a]volume=1.0[a0];[1:a]volume=0.3[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2",
            "-c:a", "libmp3lame", final_mix
        ], check=True)
    finally:
        for f in [wav_path, mp3_path]:
            if os.path.exists(f):
                os.remove(f)

    return final_mix


def generate_and_play_loop(mode="focus"):
    global stop_thread
    pygame.mixer.init()
    bgm_channel = pygame.mixer.Channel(0)
    music_channel = pygame.mixer.Channel(1)

    print(f"🔁 Starting infinite music loop in {mode.upper()} mode...")

    bgm_path = "assets/bgm.mp3"
    if not os.path.exists(bgm_path):
        print(f"❌ Background music file not found: {bgm_path}")
        return

    bgm_sound = pygame.mixer.Sound(bgm_path)
    bgm_sound.set_volume(0.6)
    bgm_channel.play(bgm_sound, loops=-1)

    try:
        while not stop_thread:
            mp3 = generate_music(mode)
            if not mp3 or not os.path.exists(mp3):
                time.sleep(2)
                continue

            print(f"🎼 Generated and playing: {mp3}")
            music_sound = pygame.mixer.Sound(mp3)
            music_sound.set_volume(2.0)
            music_channel.play(music_sound)
            main()

            while music_channel.get_busy() and not stop_thread:
                pygame.time.wait(100)

    finally:
        music_channel.stop()
        bgm_channel.stop()
        pygame.mixer.quit()


def cleanup():
    global stop_thread
    stop_thread = True
    print("🧹 Cleanup triggered. Music loop will stop.")

atexit.register(cleanup)

if __name__ == "__main__":
    music_thread = threading.Thread(target=generate_and_play_loop, args=("focus",))
    music_thread.start()