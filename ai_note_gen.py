# ai_note_gen.py

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings

import json
import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras import Input
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# --------------------- Load Configuration ---------------------
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

# --------------------- Note Extractor ---------------------
def get_mode_notes(mode):
    config = load_config()
    instruments = config[mode]["instruments"]
    all_notes = []
    for inst in instruments:
        all_notes.extend(inst.get("notes", []))
    return list(set(all_notes))

# --------------------- Sequence Preparer ---------------------
def prepare_sequences(notes, seq_length=4):
    le = LabelEncoder()
    encoded = le.fit_transform(notes)
    num_notes = len(set(notes))

    inputs, targets = [], []
    for i in range(len(encoded) - seq_length):
        inputs.append(encoded[i:i + seq_length])
        targets.append(encoded[i + seq_length])

    X = np.reshape(inputs, (len(inputs), seq_length, 1)) / float(num_notes)
    y = to_categorical(targets, num_classes=num_notes)

    return X, y, le

# --------------------- LSTM Model Builder ---------------------
def build_model(input_shape, output_dim):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64),
        Dense(output_dim, activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

# --------------------- Note Generator ---------------------
def generate_notes(model, seed_sequence, length, le):
    reverse_map = dict(enumerate(le.classes_))
    encoded_seed = le.transform(seed_sequence)
    input_seq = encoded_seed[-4:]
    output = list(seed_sequence)

    for _ in range(length):
        input_arr = np.reshape(input_seq, (1, 4, 1)) / len(le.classes_)
        prediction = model.predict(input_arr, verbose=0)[0]
        next_index = np.random.choice(len(prediction), p=prediction)
        next_note = reverse_map[next_index]
        output.append(next_note)
        input_seq = np.append(input_seq[1:], [next_index])

    return output

# --------------------- Main Note Generation Entry ---------------------
def generate_lstm_notes_for_mode(mode="focus", num_new_notes=16):
    print(f"\n🎵 Generating AI melody for: {mode}")
    notes = get_mode_notes(mode)

    if len(notes) < 5:
        raise ValueError("Not enough unique notes to train LSTM.")

    # Create diverse training data (multiply original notes)
    training_data = notes * 15
    random.shuffle(training_data)

    X, y, le = prepare_sequences(training_data, seq_length=4)
    model = build_model((X.shape[1], X.shape[2]), y.shape[1])
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)  # Fast & stable

    seed = random.sample(notes, 4)
    generated = generate_notes(model, seed, num_new_notes, le)
    return generated
