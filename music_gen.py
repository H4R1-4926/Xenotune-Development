import os, time, json, shutil, random
from music21 import stream, chord, note, instrument, tempo, metadata, midi

# --- Load Config ---
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# --- Instrument Mapping ---
def get_music21_instrument(name):
    mapping = {
        "Guzheng": instrument.AcousticGuitar(),
        "Charango": instrument.Mandolin(),
        "Reeds": instrument.Clarinet(),
        "Harp": instrument.Harp(),
        "Piano": instrument.ElectricPiano(),
    }
    return mapping.get(name, instrument.Instrument(name))

# --- Section Generator ---
def generate_section(name, bars):
    s = stream.Stream()
    for _ in range(bars):
        m = stream.Measure()
        m.append(note.Rest(quarterLength=4.0))
        s.append(m)
    return s

# --- Main Generator ---
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
        "layer2": 8, "ambient_loop": 16, "dream_flow": 8, "infinite_loop": 16
    }

    beats_per_bar = 1
    output_path = "output"
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    score = stream.Score()
    score.append(tempo.MetronomeMark(number=bpm))
    score.insert(0, metadata.Metadata(title=f"Xenotune - {mode.title()} Mode"))

    # --- Instrumental Parts ---
    for inst in instruments:
        part = stream.Part()
        part.insert(0, get_music21_instrument(inst["name"]))
        style = inst.get("style", "")
        notes = inst.get("notes", ["C4", "E4", "G4"])

        for section_name in structure:
            bars = section_lengths.get(section_name, 8)
            section_beats = bars * beats_per_bar
            beats = 0
            while beats < section_beats:
                if "slow" in style or "sustained" in style or "ambient" in style:
                    c = chord.Chord(notes, quarterLength=2.0)
                    c.volume.velocity = 20
                    part.append(c)
                    beats += 2
                elif "arp" in style or "plucked" in style or "fingerpicking" in style:
                    for n in notes:
                        nt = note.Note(n, quarterLength=0.5)
                        nt.volume.velocity = 15
                        part.append(nt)
                        beats += 0.5
                        if beats >= section_beats:
                            break
                else:
                    c = chord.Chord(notes, quarterLength=1.0)
                    c.volume.velocity = 20
                    part.append(c)
                    beats += 1.0

        score.append(part)

    # --- Melody Part ---
    melody_part = stream.Part()

    melody_instrument = {
        "focus": instrument.ElectricPiano(),
        "relax": instrument.Flute(),
        "sleep": instrument.Clarinet()
    }.get(mode, instrument.Piano())
    melody_part.insert(0, melody_instrument)

    # Mode-specific scales
    scale_map = {
        "focus": ["C4", "D4", "E4", "G4", "A4", "C5", "D5", "E5", "G5", "A5"],
        "relax": ["A3", "B3", "C4", "D4", "E4", "G4", "A4", "B4", "C5", "D5"],
        "sleep": ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]
    }

    melody_notes = scale_map.get(mode, ["C4", "E4", "G4"])

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
                length = random.choice([1.0, 2.0]) if mode == "focus" else random.choice([2.0, 4.0])
                n = note.Note(pitch, quarterLength=length)
                n.volume.velocity = 30
                melody_part.append(n)
                melody_beats += length
                if melody_beats >= section_beats:
                    break

    score.append(melody_part)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_path}/{mode}_composition_{timestamp}.mid"
    mf = midi.translate.streamToMidiFile(score)
    mf.open(output_file, 'wb')
    mf.write()
    mf.close()
    return output_file

# --- Mode Functions ---
def generate_focus_music():
    return generate_music("focus")

def generate_relax_music():
    return generate_music("relax")

def generate_sleep_music():
    return generate_music("sleep")
