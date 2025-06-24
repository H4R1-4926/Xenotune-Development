import os, time, json, shutil, random
from music21 import stream, chord, note, instrument, tempo, metadata, midi

# --- Load Config ---
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# --- Instrument Mapping ---
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

# --- Chord Generator ---
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

# --- Music Generator Core ---
def generate_music(mode):
    config = load_config()
    mode_data = config[mode]
    bpm = mode_data["tempo"]
    instruments = mode_data["instruments"]
    structure = mode_data.get("structure", ["loop"])
    section_lengths = {
        "intro": 8, "build": 12, "loop": 16, "variation": 16,
        "bridge": 12, "fadeout": 8, "outro": 8, "layered loop": 24, "drone": 16
    }
    beats_per_bar = 4

    # Cleanup output directory
    output_path = "output"
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    score = stream.Score()
    score.append(tempo.MetronomeMark(number=bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

    global_chord_pool = []
    for inst in instruments:
        global_chord_pool.extend(inst.get("chords", []))

    for inst in instruments:
        part = stream.Part()
        part.insert(0, get_music21_instrument(inst["name"]))
        chord_pool = inst.get("chords", [])
        style = inst.get("style", "")
        has_notes = False

        if not chord_pool:
            continue

        for section in structure:
            bars = section_lengths.get(section, 16)
            section_beats = bars * beats_per_bar
            beats = 0
            while beats < section_beats:
                chord_def = random.choice(chord_pool)
                notes = chord_def.get("notes", [])
                if not notes:
                    continue
                has_notes = True
                if "slow" in style or "sustained" in style:
                    c = chord.Chord(notes, quarterLength=4.0)
                    beats += 4
                elif "arpeggiated" in style:
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
            score.append(part)

    # Melody Generator
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

    def generate_motif():
        return [random.choice(melody_notes) for _ in range(3)]

    def vary_motif(motif):
        return [random.choice([n, random.choice(melody_notes)]) for n in motif]

    def retrograde(motif):
        return motif[::-1]

    for section in structure:
        motif = generate_motif()
        bars = section_lengths.get(section, 16)
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

    # --- Export MIDI ---
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"output/{mode}_composition_{timestamp}.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(output_file, 'wb')
    mf.write()
    mf.close()
    return output_file
