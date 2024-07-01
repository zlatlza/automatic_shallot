import tkinter as tk
from tkinter import ttk
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
import random

# Dictionary to map chord names to base frequencies
CHORD_FREQUENCIES = {
    "C": 261.63,
    "C#": 277.18,
    "D": 293.66,
    "D#": 311.13,
    "E": 329.63,
    "F": 349.23,
    "F#": 369.99,
    "G": 392.00,
    "G#": 415.30,
    "A": 440.00,
    "A#": 466.16,
    "B": 493.88
}

# Dictionary to map chord types to intervals
CHORD_TYPES = {
    "Major": [0, 4, 7],
    "Minor": [0, 3, 7],
    "Diminished": [0, 3, 6],
    "Augmented": [0, 4, 8],
    "Dominant 7th": [0, 4, 7, 10],
    "Major 7th": [0, 4, 7, 11],
    "Minor 7th": [0, 3, 7, 10],
    "Diminished 7th": [0, 3, 6, 9],
    "Half-Diminished 7th": [0, 3, 6, 10],
    "Minor-Major 7th": [0, 3, 7, 11]
}

def generate_sine_wave(frequency, duration_ms, volume_db=-10):
    return Sine(frequency).to_audio_segment(duration=duration_ms).apply_gain(volume_db)

def generate_white_noise(duration_ms, volume_db=-20):
    return WhiteNoise().to_audio_segment(duration=duration_ms).apply_gain(volume_db)

def generate_chord(base_freq, intervals, duration_ms, volume_db=-10):
    chord = AudioSegment.silent(duration=duration_ms)
    for interval in intervals:
        freq = base_freq * (2 ** (interval / 12.0))
        tone = generate_sine_wave(freq, duration_ms, volume_db)
        chord = chord.overlay(tone)
    return chord

def generate_atmospheric_noise(duration_ms, volume_db=-30):
    return generate_white_noise(duration_ms, volume_db).low_pass_filter(500).apply_gain(-10)

def generate_drum_beat(duration_ms, bpm, volume_db=-10):
    beat_duration_ms = 60000 // bpm
    drum = AudioSegment.silent(duration=duration_ms)
    
    kick = generate_sine_wave(100, beat_duration_ms // 2, volume_db).low_pass_filter(60)
    snare = generate_white_noise(beat_duration_ms // 2, volume_db).high_pass_filter(1000)
    hi_hat = generate_white_noise(beat_duration_ms // 4, volume_db).high_pass_filter(5000)
    
    for beat in range(0, duration_ms, beat_duration_ms):
        if (beat // beat_duration_ms) % 5 in [0, 2, 3, 4]:
            drum = drum.overlay(kick, position=beat)
        if (beat // beat_duration_ms) % 5 == 2:
            drum = drum.overlay(snare, position=beat)
        drum = drum.overlay(hi_hat, position=beat)
    
    return drum

def generate_walking_bass(chord_order, duration_ms_per_chord, bpm, volume_db=-10):
    beat_duration_ms = 60000 // bpm
    bass = AudioSegment.silent(duration=0)
    for base_freq in chord_order:
        for _ in range(duration_ms_per_chord // beat_duration_ms):
            for interval in [0, 2, 4, 5]:
                freq = base_freq * (2 ** (interval / 12.0))
                note = generate_sine_wave(freq, beat_duration_ms, volume_db).low_pass_filter(200)
                bass += note
    return bass

def apply_reverb(audio_segment, decay=0.5):
    return audio_segment.overlay(audio_segment - decay)

def apply_echo(audio_segment, delay_ms=300, decay=0.5):
    echo = audio_segment[:delay_ms].overlay(audio_segment, gain_during_overlay=-decay)
    return audio_segment.overlay(echo)

def generate_music():
    try:
        base_freqs = [CHORD_FREQUENCIES[chord[0]] for chord in chords]
        chord_intervals = [CHORD_TYPES[chord[1]] for chord in chords]
    except KeyError as e:
        status_label.config(text=f"Invalid chord name or type: {str(e)}. Please enter valid chords.")
        return

    duration_ms = int(duration_entry.get()) * 1000
    bpm = int(bpm_entry.get())
    volume_db = int(volume_entry.get())
    reverb_decay = float(reverb_entry.get())
    echo_delay_ms = int(echo_delay_entry.get())
    echo_decay = float(echo_decay_entry.get())

    duration_ms_per_chord = duration_ms // len(base_freqs)

    music = AudioSegment.silent(duration=0)
    for base_freq, intervals in zip(base_freqs, chord_intervals):
        chord = generate_chord(base_freq, intervals, duration_ms_per_chord, volume_db)
        bass = generate_walking_bass([base_freq], duration_ms_per_chord, bpm, volume_db)
        section = chord.overlay(bass)
        music += section

    drum_beat = generate_drum_beat(len(music), bpm, volume_db)
    music = music.overlay(drum_beat)

    atmospheric_noise = generate_atmospheric_noise(len(music), volume_db)
    music = music.overlay(atmospheric_noise)
    music = apply_reverb(music, decay=reverb_decay)
    music = apply_echo(music, delay_ms=echo_delay_ms, decay=echo_decay)

    music = music * int(loop_entry.get())
    music.export("generated_dungeon_jazz.wav", format="wav")

    status_label.config(text="Music generated and saved as 'generated_dungeon_jazz.wav'")

def add_chord():
    chord_name = chord_name_var.get().strip().upper()
    chord_type = chord_type_var.get().strip()
    if chord_name in CHORD_FREQUENCIES and chord_type in CHORD_TYPES:
        chords.append((chord_name, chord_type))
        chord_listbox.insert(tk.END, f"{chord_name} {chord_type}")
    else:
        status_label.config(text="Invalid chord name or type. Please select valid options.")

def remove_chord():
    selected_indices = chord_listbox.curselection()
    for index in selected_indices[::-1]:
        chord_listbox.delete(index)
        del chords[index]

def clear_chords():
    chord_listbox.delete(0, tk.END)
    chords.clear()

# Initialize GUI
root = tk.Tk()
root.title("Dungeon Jazz Music Generator")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Chord Management
chords = []

ttk.Label(frame, text="Add Chord").grid(column=0, row=0, sticky=tk.W)

chord_name_var = tk.StringVar()
chord_name_menu = ttk.OptionMenu(frame, chord_name_var, "C", *CHORD_FREQUENCIES.keys())
chord_name_menu.grid(column=1, row=0, sticky=(tk.W, tk.E))

chord_type_var = tk.StringVar()
chord_type_menu = ttk.OptionMenu(frame, chord_type_var, "Major", *CHORD_TYPES.keys())
chord_type_menu.grid(column=2, row=0, sticky=(tk.W, tk.E))

add_chord_button = ttk.Button(frame, text="Add Chord", command=add_chord)
add_chord_button.grid(column=3, row=0, sticky=(tk.W, tk.E))

chord_listbox = tk.Listbox(frame, height=10)
chord_listbox.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))
remove_chord_button = ttk.Button(frame, text="Remove Selected Chord", command=remove_chord)
remove_chord_button.grid(column=3, row=1, sticky=(tk.W, tk.E))
clear_chords_button = ttk.Button(frame, text="Clear All Chords", command=clear_chords)
clear_chords_button.grid(column=3, row=2, sticky=(tk.W, tk.E))

# Duration, BPM, Volume, Reverb, and Echo Settings
ttk.Label(frame, text="Duration (seconds)").grid(column=0, row=3, sticky=tk.W)
duration_entry = ttk.Entry(frame)
duration_entry.grid(column=1, row=3, sticky=(tk.W, tk.E))

ttk.Label(frame, text="BPM").grid(column=0, row=4, sticky=tk.W)
bpm_entry = ttk.Entry(frame)
bpm_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Volume (dB)").grid(column=0, row=5, sticky=tk.W)
volume_entry = ttk.Entry(frame)
volume_entry.grid(column=1, row=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Reverb Decay").grid(column=0, row=6, sticky=tk.W)
reverb_entry = ttk.Entry(frame)
reverb_entry.grid(column=1, row=6, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Delay (ms)").grid(column=0, row=7, sticky=tk.W)
echo_delay_entry = ttk.Entry(frame)
echo_delay_entry.grid(column=1, row=7, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Decay").grid(column=0, row=8, sticky=tk.W)
echo_decay_entry = ttk.Entry(frame)
echo_decay_entry.grid(column=1, row=8, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Number of Loops").grid(column=0, row=9, sticky=tk.W)
loop_entry = ttk.Entry(frame)
loop_entry.grid(column=1, row=9, sticky=(tk.W, tk.E))

# Generate Button and Status Label
generate_button = ttk.Button(frame, text="Generate Music", command=generate_music)
generate_button.grid(column=0, row=10, columnspan=4, sticky=(tk.W, tk.E))

status_label = ttk.Label(frame, text="")
status_label.grid(column=0, row=11, columnspan=4, sticky=(tk.W, tk.E))

root.mainloop()
