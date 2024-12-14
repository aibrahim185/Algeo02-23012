import os
import time
import math
import numpy as np
from mido import MidiFile, MidiTrack, Message
from multiprocessing import Pool

# Process MIDI to extract note data
def process_midi(midi_path):
    window_size_beats = 40
    stride_beats = 8

    try:
        # Attempt to load the MIDI file
        midi = MidiFile(midi_path)
        ticks_per_beat = midi.ticks_per_beat

        notes = []
        for track in midi.tracks:
            time_elapsed = 0
            for msg in track:
                try:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        notes.append((msg.note, time_elapsed / ticks_per_beat))
                    time_elapsed += msg.time
                except ValueError as e:
                    # Skip invalid messages
                    print(f"Skipping invalid message in {midi_path}: {e}")
                    continue

        if not notes:
            print(f"File {midi_path} has no valid notes.")
            return []

        # Convert to numpy arrays for efficient processing
        pitches = np.array([note[0] for note in notes])
        beat_durations = np.diff([note[1] for note in notes], prepend=0)
        note_representation = np.column_stack((pitches, beat_durations))

        # Sliding window
        windows = []
        start_beat = 0
        total_beats = np.sum(beat_durations)
        while start_beat < total_beats:
            mask = (note_representation[:, 1].cumsum() > start_beat) & \
                   (note_representation[:, 1].cumsum() <= start_beat + window_size_beats)
            current_window = note_representation[mask]
            if current_window.size > 0:
                windows.append(current_window)
            start_beat += stride_beats

        return windows

    except ValueError as e:
        print(f"File {midi_path} is corrupt or malformed: {e}")
    except Exception as e:
        print(f"Unexpected error processing file {midi_path}: {e}")
    return []

# Feature extraction
def extract_features(pitches):
    pitches = np.array(pitches, dtype=int)
    
    hist_atb = np.bincount(pitches, minlength=128)[:128]
    hist_rtb = np.zeros(512, dtype=int)
    hist_ftb = np.zeros(512, dtype=int)

    if len(pitches) > 1:
        pitch_diffs = pitches[1:] - pitches[:-1]
        hist_rtb = np.bincount(pitch_diffs + 256, minlength=512)
    
    if len(pitches) > 0:
        first_note = pitches[0]
        pitch_from_first = pitches - first_note
        hist_ftb = np.bincount(pitch_from_first + 256, minlength=512)

    def normalize(hist):
        total = hist.sum()
        return hist / total if total > 0 else hist

    return normalize(hist_atb), normalize(hist_rtb), normalize(hist_ftb)

# Compute cosine similarity
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

# Batch compute similarity
def compute_similarity_batch(query_features, db_features):
    similarity = []
    for qf, dbf in zip(query_features, db_features):
        sim = (
            0.2 * cosine_similarity(qf[0], dbf[0]) +
            0.4 * cosine_similarity(qf[1], dbf[1]) +
            0.4 * cosine_similarity(qf[2], dbf[2])
        )
        similarity.append(sim)
    return np.mean(similarity) if similarity else 0

# Process a single MIDI file for parallel processing
def process_single_midi(file_data):
    midi_file, midi_path = file_data
    windows = process_midi(midi_path)
    if not windows:
        return midi_file, []

    features = [extract_features(window[:, 0]) for window in windows]
    return midi_file, features

# Main function
def get_similar_audio(target_midi_path, threshold=0):
    search_directory="uploads/audio"
    start_time = time.time()

    # Process target MIDI file
    target_windows = process_midi(target_midi_path)
    if not target_windows:
        print(f"File target {target_midi_path} tidak memiliki data nada.")
        return []

    target_features = [extract_features(window[:, 0]) for window in target_windows]

    # Get all MIDI files in the directory
    midi_files = [
        (os.path.basename(f), os.path.join(search_directory, f))
        for f in os.listdir(search_directory) if f.endswith('.mid')
    ]

    # Process all database MIDI files in parallel
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(process_single_midi, midi_files)

    # Compute similarity for all files
    similar_songs = []
    for midi_file, db_features in results:
        if not db_features:
            continue

        min_windows = min(len(target_features), len(db_features))
        trimmed_target_features = target_features[:min_windows]
        trimmed_db_features = db_features[:min_windows]

        similarity = compute_similarity_batch(trimmed_target_features, trimmed_db_features) * 100
        print(f"File: {midi_file} - Similarity: {similarity:.2f}%")

        if similarity >= threshold:
            similar_songs.append((midi_file, similarity))

    similar_songs.sort(key=lambda x: x[1], reverse=True)

    end_time = time.time()
    print(f"Execution Time: {(end_time - start_time)*1000:.2f} ms")
    return similar_songs


# Example usage
# if __name__ == "__main__":
#     similar_files = get_similar_audio("Caught Up In You.mid", threshold=50)
#     print("Similar Files:")
#     for file, similarity in similar_files:
#         print(f"{file}: {similarity:.2f}%")