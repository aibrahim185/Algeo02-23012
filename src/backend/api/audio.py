import os
import math
from mido import MidiFile
import time

# Fungsi untuk memproses file MIDI dan membagi melodi menjadi window
def process_midi(midi_path):
    window_size_beats=40
    stride_beats=8
    try:
        midi = MidiFile(midi_path)
        ticks_per_beat = midi.ticks_per_beat

        notes = []
        for track in midi.tracks:
            time_elapsed = 0
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append((msg.note, time_elapsed / ticks_per_beat))
                time_elapsed += msg.time

        if not notes:
            print(f"File: {midi_path} - No notes found.")
            return []

        # Normalisasi pitch
        pitches = [note[0] for note in notes]
        beat_durations = [notes[i + 1][1] - notes[i][1] for i in range(len(notes) - 1)]
        beat_durations.append(0)  # Tambahkan durasi nol untuk nada terakhir

        pitch_mean = sum(pitches) / len(pitches) if pitches else 0
        pitch_std = math.sqrt(sum((p - pitch_mean) ** 2 for p in pitches) / len(pitches)) if pitches else 0
        normalized_pitches = [(p - pitch_mean) / pitch_std if pitch_std > 0 else 0 for p in pitches]

        note_representation = list(zip(normalized_pitches, beat_durations))

        # Sliding window processing
        windows = []
        start_beat = 0
        total_beats = sum(beat_durations)
        while start_beat < total_beats:
            current_window = []
            accumulated_beats = 0
            for note, beat_duration in note_representation:
                if start_beat <= accumulated_beats < start_beat + window_size_beats:
                    current_window.append((note, beat_duration))
                accumulated_beats += beat_duration
                if accumulated_beats >= start_beat + window_size_beats:
                    break
            if current_window:
                windows.append(current_window)
            start_beat += stride_beats

        return windows
    except Exception as e:
        print(f"Error processing file {midi_path}: {e}")
        return []

# Fungsi untuk mengekstrak fitur dari not MIDI
def extract_features(pitches):
    hist_atb = [0] * 128
    hist_rtb = [0] * 512
    hist_ftb = [0] * 512

    for p in pitches:
        pi = int(p)
        if 0 <= pi < 128:
            hist_atb[pi] += 1

    for i in range(1, len(pitches)):
        diff = pitches[i] - pitches[i - 1]
        index = int(diff + 256)
        if 0 <= index < 512:
            hist_rtb[index] += 1

    if pitches:
        first_note = pitches[0]
        for p in pitches:
            diff = p - first_note
            index = int(diff + 256)
            if 0 <= index < 512:
                hist_ftb[index] += 1

    def normalize(h):
        s = sum(h)
        return [x / s if s > 0 else 0 for x in h]

    hist_atb = normalize(hist_atb)
    hist_rtb = normalize(hist_rtb)
    hist_ftb = normalize(hist_ftb)

    return hist_atb, hist_rtb, hist_ftb

# Fungsi untuk menghitung kesamaan
def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a ** 2 for a in v1))
    norm2 = math.sqrt(sum(b ** 2 for b in v2))
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

def compute_similarity(query_features, db_features):
    query_atb, query_rtb, query_ftb = query_features
    db_atb, db_rtb, db_ftb = db_features

    similarity = (
        0.2 * cosine_similarity(query_atb, db_atb) +
        0.4 * cosine_similarity(query_rtb, db_rtb) +
        0.4 * cosine_similarity(query_ftb, db_ftb)
    )
    return similarity

# Fungsi utama untuk mencari lagu yang mirip
def get_similar_audio(target_midi_path, search_directory="public", threshold=0):
    start_time = time.time()

    target_windows = process_midi(target_midi_path)
    if not target_windows:
        print(f"File target {target_midi_path} tidak memiliki data nada.")
        return []

    target_features = [extract_features([note[0] for note in window]) for window in target_windows]

    public_files = [
        os.path.join(search_directory, f)
        for f in os.listdir(search_directory)
        if f.endswith('.mid')
    ]

    similar_songs = []
    for midi_file in public_files:
        print(f"Processing file: {midi_file}")
        db_windows = process_midi(midi_file)
        if not db_windows:
            continue

        min_windows = min(len(target_windows), len(db_windows))
        trimmed_target_features = target_features[:min_windows]
        trimmed_db_windows = db_windows[:min_windows]
        db_features = [extract_features([note[0] for note in window]) for window in trimmed_db_windows]

        total_similarity = sum(
            compute_similarity(t_feature, db_feature)
            for t_feature, db_feature in zip(trimmed_target_features, db_features)
        )
        average_similarity = (total_similarity / len(trimmed_target_features)) * 100

        print(f"File: {os.path.basename(midi_file)} - Similarity: {average_similarity:.2f}%")

        if average_similarity >= threshold:
            similar_songs.append((os.path.basename(midi_file), average_similarity))

    similar_songs.sort(key=lambda x: x[1], reverse=True)

    end_time = time.time()
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    return similar_songs

# Test
get_similar_audio("Caught Up In You.mid", search_directory="public", threshold=0)
