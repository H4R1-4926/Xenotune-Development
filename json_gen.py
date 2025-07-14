import json
import numpy as np
import tensorflow as tf
import random

# 🎵 Notes used across your config (based on your file)
NOTE_VOCAB = sorted(list(set([
    "C2", "D2", "E2", "F2", "G2", "A2", "B2",
    "C3", "D3", "E3", "F#3", "G3", "A3", "B3",
    "C4", "D4", "E4", "F#4", "G4", "A4",
    "C5", "D5", "E5", "F#5", "G5", "A5", "B5"
])))

note_to_int = {n: i for i, n in enumerate(NOTE_VOCAB)}
int_to_note = {i: n for n, i in note_to_int.items()}

# 📥 Load your config.json
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# 💾 Save updated config
def save_config(config, path="config.json"):
    with open(path, "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Updated config saved.")

# 🧠 Generate training data
def generate_training_data(seq_len=4, num_seq=500):
    X, y = [], []
    for _ in range(num_seq):
        seq = np.random.choice(NOTE_VOCAB, size=seq_len + 1)
        X.append([note_to_int[n] for n in seq[:-1]])
        y.append(note_to_int[seq[-1]])
    return np.array(X), np.array(y)

# 🧠 Build and train LSTM model
def build_and_train_model(X, y):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(input_dim=len(NOTE_VOCAB), output_dim=32, input_length=X.shape[1]),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dense(len(NOTE_VOCAB), activation='softmax')
    ])
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    model.fit(X, y, epochs=20, verbose=0)
    return model

# 🎼 Generate sequence from model
def generate_notes(model, start_seq=None, length=6):
    if start_seq is None:
        start_seq = [random.randint(0, len(NOTE_VOCAB)-1) for _ in range(4)]
    seq = start_seq[:]
    for _ in range(length):
        input_seq = np.array(seq[-4:]).reshape(1, -1)
        pred = model.predict(input_seq, verbose=0)
        next_note = np.argmax(pred)
        seq.append(next_note)
    notes = [int_to_note[i] for i in seq]
    chords = [notes[i:i+3] for i in range(len(notes) - 2)]
    return notes, chords

# 🔁 Update the config with generated notes/chords
def update_config(config, model):
    for mode in config:
        for instrument in config[mode].get("instruments", []):
            existing_notes = instrument.get("notes", [])
            start = [note_to_int[n] for n in existing_notes[:4] if n in note_to_int]
            if len(start) < 4:
                start += [random.randint(0, len(NOTE_VOCAB)-1) for _ in range(4 - len(start))]
            notes, chords = generate_notes(model, start_seq=start)
            instrument["notes"] = notes
            instrument["chords"] = chords
    return config

# 🔁 Full lifecycle
def main():
    config_path = "config.json"
    
    print("📥 Loading config...")
    config = load_config(config_path)

    print("🧠 Generating training data...")
    X, y = generate_training_data()

    print("🔁 Training LSTM model...")
    model = build_and_train_model(X, y)

    print("🎶 Generating notes/chords...")
    updated_config = update_config(config, model)

    print("💾 Saving updated config...")
    save_config(updated_config, config_path)

if __name__ == "__main__":
    main()
