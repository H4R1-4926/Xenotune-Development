import os
import time
import json
import shutil
import random
import subprocess
import pygame
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from ai_note_gen import generate_lstm_notes_for_mode

# --- Load Config ---
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# --- Instrument Mapping ---
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
        "Electric Guitar": instrument.ElectricGuitar(),
        "Meditative Flute": instrument.PanFlute(),

    }
    return mapping.get(name, instrument.Instrument(name))

# --- Music Generator ---
def generate_music(mode):
    config = load_config()
    mode_data = config[mode]
    bpm = mode_data["tempo"]
    instruments = mode_data["instruments"]
    structure = mode_data["structure"]

    section_lengths = {
        "intro": 4, "groove": 8, "verse": 8, "chorus": 8, "bridge": 8,
        "drop": 8, "build": 8, "solo": 8, "outro": 4, "loop": 16,
        "variation": 8, "layered_loop": 8, "fadeout": 4, "layer1": 8,
        "layer2": 8, "ambient_loop": 16, "dream_flow": 8, "infinite_loop": 16,
        "loop_a": 8, "focus_block": 8, "pause_fill": 4, "soothing_loop": 16,
        "deep_layer": 8, "dream_pad": 8
    }

    beats_per_bar = 4
    output_path = "output"
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    score = stream.Score()
    score.append(tempo.MetronomeMark(number=bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

    # --- Background Instruments ---
    for inst in instruments:
        if "samples" in inst:
            continue
        part = stream.Part()
        part.insert(0, get_music21_instrument(inst["name"]))
        style = inst.get("style", "")
        notes = inst.get("notes", ["B3", "D4", "F4"])

        for section_name in structure:
            bars = section_lengths.get(section_name, 8)
            section_beats = bars * beats_per_bar
            beats = 0
            while beats < section_beats:
                if "slow" in style or "sustained" in style or "ambient" in style:
                    c = chord.Chord(notes, quarterLength=2.0)
                    c.volume.velocity = 10
                    part.append(c)
                    beats += 2
                elif "arp" in style or "arpeggio" in style:
                    for n in notes:
                        nt = note.Note(n, quarterLength=0.5)
                        nt.volume.velocity = 9
                        part.append(nt)
                        beats += 0.5
                        if beats >= section_beats:
                            break
                else:
                    c = chord.Chord(notes, quarterLength=1.0)
                    c.volume.velocity = 15
                    part.append(c)
                    beats += 1.0
        score.append(part)

    # --- Melody Line ---
    melody_part = stream.Part()
    melody_instrument = {
        "focus": instrument.ElectricPiano(),
        "relax": instrument.Piano(),
        "sleep": instrument.Piano()
    }.get(mode, instrument.Piano())
    melody_part.insert(0, melody_instrument)

    for section_name in structure:
        bars = section_lengths.get(section_name, 8)
        section_beats = bars * beats_per_bar
        melody_beats = 0

        lstm_melody = generate_lstm_notes_for_mode(mode, num_new_notes=int(section_beats))

        for pitch in lstm_melody:
            length = random.choice([0.5, 1.0]) if mode == "focus" else random.choice([1.0, 2.0])
            n = note.Note(pitch, quarterLength=length)
            melody_part.append(n)
            melody_beats += length
            if melody_beats >= section_beats:
                break

    score.append(melody_part)

    # --- Export MIDI File ---
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    midi_file = f"{output_path}/{mode}_composition_{timestamp}.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(midi_file, 'wb')
    mf.write()
    mf.close()

    # --- Convert to MP3 ---
    mp3_file = convert_midi_to_mp3(midi_file)
    return mp3_file

# --- MIDI to MP3 Conversion ---
def convert_midi_to_mp3(
    midi_path,
    soundfont_path="FluidR3_GM/FluidR3_GM.sf2",
    fluidsynth_path="fluidsynth/bin/fluidsynth.exe"
):
    fluidsynth_path="fluidsynth/bin/fluidsynth.exe",
    ffmpeg_path="ffmpeg/bin/ffmpeg.exe",
    bgm_path="assets/bgm.mp3",
    music_volume="2.0",
    bgm_volume="0.6"
    ):
    if not os.path.isfile(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    if not os.path.isfile(soundfont_path):
        raise FileNotFoundError(f"SoundFont not found: {soundfont_path}")
    if not os.path.isfile(fluidsynth_path):
        raise FileNotFoundError(f"FluidSynth not found: {fluidsynth_path}")

    wav_path = midi_path.replace(".mid", ".wav")
    mp3_path = midi_path.replace(".mid", ".mp3")

    try:
        subprocess.run([
            fluidsynth_path, "-ni", soundfont_path, midi_path, "-F", wav_path, "-r", "44100"
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FluidSynth failed: {e}")

    try:
        subprocess.run(["ffmpeg", "-y", "-i", wav_path, mp3_path], check=True)
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

    return mp3_path

# --- Mode Shortcuts ---
def generate_focus_music():
    return generate_music("focus")

def generate_relax_music():
    return generate_music("relax")

def generate_sleep_music():
    return generate_music("sleep")

# --- Infinite Backend Playback Loop ---
def generate_and_play_loop(mode="focus"):
    pygame.mixer.init()
    print(f"🔁 Playing continuous music: {mode.upper()}")
    try:
        while True:
            mp3 = generate_music(mode)
            print(f"🎵 Now playing: {mp3}")
            pygame.mixer.music.load(mp3)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    bgm_channel = pygame.mixer.Channel(0)
    music_channel = pygame.mixer.Channel(1)

    print(f"🔁 Starting infinite music loop in {mode.upper()} mode...")

    bgm_path = "assets/bgm.mp3"
    bgm_sound = pygame.mixer.Sound(bgm_path)
    bgm_sound.set_volume(0.6)
    bgm_channel.play(bgm_sound, loops=-1)

    try:
        while True:
            mp3 = generate_music(mode)
            print(f"🎼 Generated and playing: {mp3}")
            music_sound = pygame.mixer.Sound(mp3)
            music_sound.set_volume(2.0)
            music_channel.play(music_sound)

            while music_channel.get_busy():
                pygame.time.wait(100)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped continuous music loop by user.")
