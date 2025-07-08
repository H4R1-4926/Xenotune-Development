import json
import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# --- Load Configuration ---
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# --- Get Notes from Selected Mode ---
def get_mode_notes(mode):
    config = load_config()
    instruments = config[mode]["instruments"]
    all_notes = []
    for inst in instruments:
        all_notes.extend(inst.get("notes", []))
    return list(set(all_notes))

# --- Prepare Sequences for LSTM ---
def prepare_sequences(notes, seq_length=4):
    le = LabelEncoder()
    encoded = le.fit_transform(notes)
    num_notes = len(set(notes))

    inputs = []
    targets = []
    for i in range(len(encoded) - seq_length):
        inputs.append(encoded[i:i + seq_length])
        targets.append(encoded[i + seq_length])

    X = np.reshape(inputs, (len(inputs), seq_length, 1)) / float(num_notes)
    y = to_categorical(targets, num_classes=num_notes)

    return X, y, le

# --- Build the LSTM Model ---
def build_model(input_shape, output_dim):
    model = Sequential()
    model.add(LSTM(128, input_shape=input_shape))
    model.add(Dense(output_dim, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

# --- Generate Notes using the Trained Model ---
def generate_notes(model, seed_sequence, length, le):
    reverse_map = dict(enumerate(le.classes_))
    encoded_seed = le.transform(seed_sequence)
    output = list(seed_sequence)
    input_seq = encoded_seed[-4:]

    for _ in range(length):
        input_arr = np.reshape(input_seq, (1, 4, 1)) / len(le.classes_)
        prediction = model.predict(input_arr, verbose=0)[0]
        next_index = np.argmax(prediction)
        next_note = reverse_map[next_index]
        output.append(next_note)
        input_seq = np.append(input_seq[1:], [next_index])

    return output

# --- Main Generation Function ---
def generate_lstm_notes_for_mode(mode="focus", num_new_notes=16):
    print(f"\n🎶 Generating LSTM notes for mode: {mode}")
    notes = get_mode_notes(mode)

    if len(notes) < 5:
        raise ValueError("Not enough unique notes to train LSTM.")

    # Mock data expansion for training stability
    X, y, le = prepare_sequences(notes * 10, seq_length=4)
    model = build_model((X.shape[1], X.shape[2]), y.shape[1])
    model.fit(X, y, epochs=100, batch_size=8, verbose=0)

    seed = random.sample(notes, 4)
    generated = generate_notes(model, seed, num_new_notes, le)
    return generated
