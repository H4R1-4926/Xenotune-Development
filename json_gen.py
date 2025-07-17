import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random

# 🎵 Notes Vocabulary
NOTE_VOCAB = sorted(list(set([
    "C2", "D2", "E2", "F2", "G2", "A2", "B2",
    "C3", "D3", "E3", "F#3", "G3", "A3", "B3",
    "C4", "D4", "E4", "F#4", "G4", "A4",
    "C5", "D5", "E5", "F#5", "G5", "A5", "B5"
])))
note_to_int = {n: i for i, n in enumerate(NOTE_VOCAB)}
int_to_note = {i: n for n, i in note_to_int.items()}

# 🧠 LSTM Model
class NoteLSTM(nn.Module):
    def __init__(self, input_dim, embed_dim, hidden_dim, output_dim):
        super(NoteLSTM, self).__init__()
        self.embedding = nn.Embedding(input_dim, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.embedding(x)
        _, (hidden, _) = self.lstm(x)
        out = self.fc(hidden[-1])
        return out

# 📥 Load config
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# 💾 Save config
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
    return torch.tensor(X), torch.tensor(y)

# 🧠 Build & train the model
def build_and_train_model(X, y, epochs=20):
    input_dim = len(NOTE_VOCAB)
    model = NoteLSTM(input_dim, embed_dim=32, hidden_dim=64, output_dim=input_dim)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X)
        loss = loss_fn(outputs, y)
        loss.backward()
        optimizer.step()
    return model

# 🎼 Generate sequence
def generate_notes(model, start_seq=None, length=6):
    model.eval()
    if start_seq is None:
        start_seq = [random.randint(0, len(NOTE_VOCAB)-1) for _ in range(4)]

    seq = start_seq[:]
    for _ in range(length):
        input_seq = torch.tensor(seq[-4:]).unsqueeze(0)
        with torch.no_grad():
            pred = model(input_seq)
            next_idx = torch.argmax(pred, dim=1).item()
        seq.append(next_idx)

    notes = [int_to_note[i] for i in seq]
    chords = [notes[i:i+3] for i in range(len(notes) - 2)]
    return notes, chords

# 🔁 Update config
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

# 🧠 Main
def main():
    print("📥 Loading config...")
    config = load_config()

    print("🧠 Generating training data...")
    X, y = generate_training_data()

    print("🎶 Training PyTorch LSTM model...")
    model = build_and_train_model(X, y)

    print("🎼 Generating notes/chords...")
    updated_config = update_config(config, model)

    print("💾 Saving updated config...")
    save_config(updated_config)

if __name__ == "__main__":
    main()
