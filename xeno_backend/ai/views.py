import os, json, time, shutil, random, subprocess
from music21 import stream, chord, note, instrument, tempo, metadata, midi
from pydub import AudioSegment

def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

def cleanup_output():
    output_path = "output"
    if os.path.exists(output_path):
        try:
            shutil.rmtree(output_path)
        except PermissionError as e:
            print(f"⚠️ Could not remove output folder: {e}")
    os.makedirs(output_path, exist_ok=True)

def get_music21_instrument(name):
    mapping = {
        "Grand Piano": instrument.Piano(),
        "Electric Bass": instrument.ElectricBass(),
        "String Ensemble": instrument.Violin(),
        "Electric Guitar": instrument.ElectricGuitar(),
        "Nylon Guitar": instrument.AcousticGuitar(),
        "Flute": instrument.Flute(),
        "Pan Flute": instrument.PanFlute(),
        "Ambient Pad": instrument.ElectricOrgan(),
        "Ambient Synth Pad": instrument.ElectricPiano(),
        "Soft Felt Piano": instrument.Piano(),
        "Synth Pad": instrument.ElectricPiano(),
        "Nature FX": instrument.ElectricOrgan(),
        "Poly Synth": instrument.ElectricPiano()
    }
    return mapping.get(name, instrument.Instrument(name))

def generate_chord_notes(root, quality):
    intervals = {
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "sus2": [0, 2, 7],
        "add9": [0, 4, 7, 14],
        "maj9": [0, 4, 7, 11, 14],
        "min9": [0, 3, 7, 10, 14],
        "quartal": [0, 5, 10],
        "power": [0, 7],
        "drone": [0, 5, 12]
    }.get(quality, [0, 4, 7])
    root_midi = note.Note(root).pitch.midi
    return [note.Note(midi=root_midi + i).nameWithOctave for i in intervals]

def generate_composition(mode, config):
    mode_data = config[mode]
    bpm = mode_data["tempo"]
    instruments = mode_data["instruments"]
    structure = mode_data.get("structure", ["loop"])
    section_lengths = {
        "intro": 8, "build": 12, "loop": 16, "variation": 16,
        "bridge": 12, "fadeout": 8, "outro": 8, "layered loop": 24, "drone": 16
    }
    beats_per_bar = 4

    score = stream.Score()
    score.append(tempo.MetronomeMark(number=bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

    # Prepare a chord pool across all instruments that have chords
    global_chord_pool = []
    for inst in instruments:
        chords = inst.get("chords", [])
        if chords:
            global_chord_pool.extend(chords)

    if not global_chord_pool:
        print(f"⚠️ No chords found in any instrument for mode '{mode}'. Aborting composition.")
        return score  # Return empty score to avoid crash

    for inst in instruments:
        part = stream.Part()
        part.insert(0, get_music21_instrument(inst["name"]))
        style = inst.get("style", "")
        chord_pool = inst.get("chords", [])
        print(f"🎻 Instrument: {inst['name']} | Style: {style} | Chords: {len(chord_pool)}")
        has_notes = False

        # Skip instrument if no chords
        if not chord_pool:
            print(f"⚠️ Skipping instrument '{inst['name']}' - no chords defined.")
            continue

        for section in structure:
            bars = section_lengths.get(section, 16)
            section_beats = bars * beats_per_bar
            beats = 0
            while beats < section_beats:
                chord_def = random.choice(chord_pool)
                notes = chord_def.get("notes", [])
                if not notes or "fx" in chord_def.get("type", "").lower():
                    continue
                has_notes = True
                if "slow" in style or "sustained" in style or "harmony" in style:
                    c = chord.Chord(notes, quarterLength=4.0)
                    beats += 4
                elif "arpeggiated" in style or "plucked" in style or "fingerpicked" in style:
                    for n in notes:
                        part.append(note.Note(n, quarterLength=0.5))
                        beats += 0.5
                        if beats >= section_beats:
                            break
                    continue
                else:
                    c = chord.Chord(notes, quarterLength=2.0)
                    beats += 2
                part.append(c)

        if has_notes:
            print(f"✅ Added part: {inst['name']} with notes")
            score.append(part)
        else:
            print(f"⚠️ Skipped empty part: {inst['name']}")

    # Melody Section (unchanged)
    melody_part = stream.Part()
    melody_instrument = {
        "focus": instrument.Flute(),
        "relax": instrument.Oboe(),
        "sleep": instrument.Clarinet()
    }.get(mode, instrument.Flute())
    melody_part.insert(0, melody_instrument)

    scale_map = {
        "focus": ["C5", "D5", "E5", "F5", "G5", "A5", "B4"],
        "relax": ["C5", "D5", "E5", "G5", "A5"],
        "sleep": ["C5", "D5", "F5", "G5"]
    }
    melody_notes = scale_map.get(mode, ["C5", "D5", "E5"])
    return score

def write_midi(score, mode):
    os.makedirs("output", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"output/{mode}_composition_{timestamp}.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(path, 'wb')
    mf.write()
    mf.close()
    return path

def convert_midi_to_wav(midi_path):
    soundfont = r"C:\\Path\\To\\Your\\FluidR3_GM.sf2"
    fluidsynth_path = r"C:\\Path\\To\\fluidsynth.exe"
    wav_path = midi_path.replace(".mid", ".wav")
    subprocess.run([fluidsynth_path, "-ni", soundfont, midi_path, "-F", wav_path, "-r", "44100"], check=True)
    return wav_path

def mix_ambient_layers(wav_path, mode):
    ambient_map = {
        "focus": "assets/forest.wav",
        "relax": "assets/birds.wav",
        "sleep": "assets/rain.wav"
    }
    ambient_path = ambient_map.get(mode)
    if not ambient_path:
        return wav_path
    base = AudioSegment.from_wav(wav_path)
    ambient = AudioSegment.from_wav(ambient_path).low_pass_filter(3000).apply_gain(-10)
    ambient = ambient * (len(base) // len(ambient) + 1)
    ambient = ambient[:len(base)]
    mixed = base.overlay(ambient)
    final_path = wav_path.replace(".wav", "_with_ambient.wav")
    mixed.export(final_path, format="wav")
    return final_path

def generate_music(mode):
    config = load_config()
    cleanup_output()
    score = generate_composition(mode, config)
    midi_path = write_midi(score, mode)
    wav_path = convert_midi_to_wav(midi_path)
    final_path = mix_ambient_layers(wav_path, mode)
    return final_path
