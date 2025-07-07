import os
import time
import json
import shutil
import random
import subprocess
import pygame
from music21 import stream, chord, note, instrument, tempo, metadata, midi

# Load configuration
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# Map instrument name to music21 instrument
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

# Music Generator
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
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path, exist_ok=True)

    score = stream.Score()
    base_tempo = bpm
    fluctuated_bpm = base_tempo + random.choice([-1, 0, 1])
    score.append(tempo.MetronomeMark(number=fluctuated_bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

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
                if "slow" in style or "ambient" in style:
                    c = chord.Chord(notes, quarterLength=1.0)
                    c.volume.velocity = 20
                    part.append(c)
                    beats += 2
                elif "arp" in style:
                    for n in notes:
                        nt = note.Note(n, quarterLength=0.5)
                        nt.volume.velocity = 15
                        part.append(nt)
                        beats += 0.5
                        if beats >= section_beats:
                            break
                else:
                    c = chord.Chord(notes, quarterLength=0.5)
                    c.volume.velocity = 25
                    part.append(c)
                    beats += 1.0
        score.append(part)

    melody_part = stream.Part()
    melody_instrument = {
        "focus": instrument.ElectricPiano(),
        "relax": instrument.Piano(),
        "sleep": instrument.Piano()
    }.get(mode, instrument.Piano())
    melody_part.insert(0, melody_instrument)

    scale_map = {
        "focus": ["C5", "D5", "E5", "F5", "G5", "A5", "B5"],
        "relax": ["C4", "D4", "E4", "G4", "A4"],
        "sleep": ["B3", "C4", "D4", "F4", "G4"]
    }
    melody_notes = scale_map.get(mode, ["C4", "D4", "E4", "G4"])

    def generate_motif():
        return [random.choice(melody_notes) for _ in range(3)]

    def vary_motif(motif):
        return [random.choice([n, random.choice(melody_notes)]) for n in motif]

    def retrograde(motif):
        return motif[::-1]

    for section_name in structure:
        motif = generate_motif()
        bars = section_lengths.get(section_name, 8)
        section_beats = bars * beats_per_bar
        melody_beats = 0
        while melody_beats < section_beats:
            phrase = random.choice([motif, vary_motif(motif), retrograde(motif)])
            for pitch in phrase:
                length = random.choice([0.5, 1.0]) if mode == "focus" else random.choice([1.0, 2.0])
                n = note.Note(pitch, quarterLength=length)
                melody_part.append(n)
                melody_beats += length
                if melody_beats >= section_beats:
                    break
    score.append(melody_part)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    midi_file = f"{output_path}/{mode}_composition_{timestamp}.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(midi_file, 'wb')
    mf.write()
    mf.close()

    return convert_midi_to_mp3(midi_file)

# Convert MIDI to MP3 with BGM mixing
def convert_midi_to_mp3(
    midi_path,
    soundfont_path="FluidR3_GM/FluidR3_GM.sf2",
    fluidsynth_path="fluidsynth/bin/fluidsynth.exe",
    ffmpeg_path="ffmpeg/bin/ffmpeg.exe",
    bgm_path="assets/bgm.mp3",
    music_volume="0.4",
    bgm_volume="0.1"
):
    if not os.path.isfile(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    wav_path = midi_path.replace(".mid", ".wav")
    mp3_path = midi_path.replace(".mid", ".mp3")
    final_mix = midi_path.replace(".mid", "_mixed.mp3")

    subprocess.run([
        fluidsynth_path, "-ni", "-F", wav_path, "-r", "44100", soundfont_path, midi_path
    ], check=True, capture_output=True, text=True)

    subprocess.run([ffmpeg_path, "-y", "-i", wav_path, mp3_path],
                    check=True, capture_output=True, text=True)

    subprocess.run([
        ffmpeg_path, "-y",
        "-i", mp3_path,
        "-i", bgm_path,
        "-filter_complex",
        f"[0:a]volume={music_volume}[a0];[1:a]volume={bgm_volume}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:a", "libmp3lame", final_mix
    ], check=True, capture_output=True, text=True)

    os.remove(wav_path) if os.path.exists(wav_path) else None
    os.remove(mp3_path) if os.path.exists(mp3_path) else None

    return final_mix

# Mode Shortcuts
def generate_focus_music():
    return generate_music("focus")

def generate_relax_music():
    return generate_music("relax")

def generate_sleep_music():
    return generate_music("sleep")

# Infinite loop player
def generate_and_play_loop(mode="focus"):
    pygame.mixer.init()
    bgm_channel = pygame.mixer.Channel(0)
    music_channel = pygame.mixer.Channel(1)

    print(f"🔁 Starting infinite music loop in {mode.upper()} mode...")

    bgm_path = "assets/bgm.mp3"
    bgm_sound = pygame.mixer.Sound(bgm_path)
    bgm_sound.set_volume(0.01)
    bgm_channel.play(bgm_sound, loops=-1)

    try:
        while True:
            mp3 = generate_music(mode)
            print(f"🎼 Generated and playing: {mp3}")
            music_sound = pygame.mixer.Sound(mp3)
            music_sound.set_volume(0.3)
            music_channel.play(music_sound)

            while music_channel.get_busy():
                pygame.time.wait(100)
    except KeyboardInterrupt:
        print("🛑 Music loop stopped by user.")
        music_channel.stop()
        bgm_channel.stop()
        pygame.mixer.quit()

