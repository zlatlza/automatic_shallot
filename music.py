import tkinter as tk
from tkinter import ttk
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
import random
import json

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

def generate_arpeggio(base_freq, intervals, duration_ms, volume_db=-10):
    note_duration = duration_ms // len(intervals)
    arpeggio = AudioSegment.silent(duration=0)
    for interval in intervals:
        freq = base_freq * (2 ** (interval / 12.0))
        tone = generate_sine_wave(freq, note_duration, volume_db)
        arpeggio += tone
    return arpeggio

def generate_atmospheric_noise(duration_ms, volume_db=-30):
    return generate_white_noise(duration_ms, volume_db).low_pass_filter(500).apply_gain(-10)

def generate_drum_beat(duration_ms, bpm, time_signature, volume_db=-10):
    beat_duration_ms = 60000 // bpm
    beats_per_measure = int(time_signature.split('/')[0])
    drum = AudioSegment.silent(duration=duration_ms)
    
    kick = generate_sine_wave(100, beat_duration_ms // 2, volume_db).low_pass_filter(60)
    snare = generate_white_noise(beat_duration_ms // 2, volume_db).high_pass_filter(1000)
    hi_hat = generate_white_noise(beat_duration_ms // 4, volume_db).high_pass_filter(5000)
    
    for beat in range(0, duration_ms, beat_duration_ms):
        measure_position = (beat // beat_duration_ms) % beats_per_measure
        if measure_position == 0 or measure_position == beats_per_measure - 1:
            drum = drum.overlay(kick, position=beat)
        if measure_position == beats_per_measure // 2:
            drum = drum.overlay(snare, position=beat)
        drum = drum.overlay(hi_hat, position=beat)
    
    return drum

def apply_reverb(audio_segment, decay=0.5):
    return audio_segment.overlay(audio_segment - decay)

def apply_echo(audio_segment, delay_ms=300, decay=0.5):
    echo = audio_segment[:delay_ms].overlay(audio_segment, gain_during_overlay=-decay)
    return audio_segment.overlay(echo)

def generate_music():
    global chords
    print("Generating music with chords:", chords)  # Debug print
    try:
        base_freqs = [CHORD_FREQUENCIES[chord[0]] for chord in chords]
        chord_intervals = [CHORD_TYPES[chord[1]] for chord in chords]
        is_arpeggio = [chord[2] for chord in chords]
        has_drums = [chord[3] for chord in chords]
        has_chords = [chord[4] for chord in chords]
        durations = [chord[5] for chord in chords]
        bpms = [chord[6] for chord in chords]
        time_signatures = [chord[7] for chord in chords]
        volumes = [chord[8] for chord in chords]
        reverb_decays = [chord[9] for chord in chords]
        echo_delays = [chord[10] for chord in chords]
        echo_decays = [chord[11] for chord in chords]
    except KeyError as e:
        status_label.config(text=f"Invalid chord name or type: {str(e)}. Please enter valid chords.")
        return
    except Exception as e:
        status_label.config(text=f"Error parsing chords: {str(e)}")
        return

    try:
        duration_ms = sum(durations) * 1000
    except Exception as e:
        status_label.config(text=f"Error calculating duration: {str(e)}")
        return

    try:
        loops = int(loop_entry.get())
    except ValueError:
        loops = 1  # Default to 1 loop if invalid or empty

    try:
        music = AudioSegment.silent(duration=0)
        full_drum_track = AudioSegment.silent(duration=0)
    
        # Generate music and drum sections separately
        for base_freq, intervals, arpeggio, drums, chords, dur, bpm, ts, vol, rvb, edly, edcy in zip(
            base_freqs, chord_intervals, is_arpeggio, has_drums, has_chords, durations, bpms, time_signatures, volumes, reverb_decays, echo_delays, echo_decays):

            duration_ms_per_chord = dur * 1000

            if arpeggio:
                section = generate_arpeggio(base_freq, intervals, duration_ms_per_chord, vol)
            else:
                section = generate_chord(base_freq, intervals, duration_ms_per_chord, vol)

            if chords_var.get() and chords:
                music += section
            else:
                music += AudioSegment.silent(duration=duration_ms_per_chord)

            drum_section = generate_drum_beat(duration_ms_per_chord, bpm, ts, vol) if drums else AudioSegment.silent(duration=duration_ms_per_chord)
            full_drum_track += drum_section

        if noise_var.get():
            atmospheric_noise = generate_atmospheric_noise(len(music), volumes[0])  # Use the first volume value for noise
            music = music.overlay(atmospheric_noise)

        music = music.overlay(full_drum_track)
        music = apply_reverb(music, decay=reverb_decays[0])
        music = apply_echo(music, delay_ms=echo_delays[0], decay=echo_decays[0])

        music = music * loops
        music.export("generated_dungeon_jazz.wav", format="wav")

        status_label.config(text="Music generated and saved as 'generated_dungeon_jazz.wav'")
    except Exception as e:
        status_label.config(text=f"Error generating music: {str(e)}")

def add_chord():
    global chords

    apply_settings = apply_settings_var.get()

    try:
        duration = int(duration_entry.get())
    except ValueError:
        duration = 60  # Default to 60 seconds if invalid or empty

    try:
        bpm = int(bpm_entry.get())
    except ValueError:
        bpm = 120  # Default to 120 BPM if invalid or empty

    time_signature = time_signature_entry.get()
    if not time_signature:
        time_signature = "4/4"  # Default to 4/4 time signature if empty

    try:
        volume_db = int(volume_entry.get())
    except ValueError:
        volume_db = -10  # Default to -10 dB if invalid or empty

    try:
        reverb_decay = float(reverb_entry.get())
    except ValueError:
        reverb_decay = 0.5  # Default to 0.5 if invalid or empty

    try:
        echo_delay_ms = int(echo_delay_entry.get())
    except ValueError:
        echo_delay_ms = 300  # Default to 300 ms if invalid or empty

    try:
        echo_decay = float(echo_decay_entry.get())
    except ValueError:
        echo_decay = 0.5  # Default to 0.5 if invalid or empty

    chord_name = chord_name_var.get().strip().upper()
    chord_type = chord_type_var.get().strip()
    arpeggio = arpeggio_var.get()
    include_drums = drums_var.get()
    include_chords = chords_var.get()
    
    if chord_name in CHORD_FREQUENCIES and chord_type in CHORD_TYPES:
        if apply_settings:
            chords.append((chord_name, chord_type, arpeggio, include_drums, include_chords, duration, bpm, time_signature, volume_db, reverb_decay, echo_delay_ms, echo_decay))
        else:
            # Default values if apply settings is not checked
            chords.append((chord_name, chord_type, arpeggio, include_drums, include_chords, 60, 120, "4/4", -10, 0.5, 300, 0.5))
        
        arpeggio_text = " (Arpeggio)" if arpeggio else ""
        drum_text = " (Drums)" if include_drums else ""
        chord_text = " (Chords)" if include_chords else ""
        chord_listbox.insert(tk.END, f"{chord_name} {chord_type}{arpeggio_text}{drum_text}{chord_text}")
    else:
        status_label.config(text="Invalid chord name or type. Please select valid options.")

def remove_chord():
    global chords
    selected_indices = chord_listbox.curselection()
    for index in selected_indices[::-1]:
        chord_listbox.delete(index)
        del chords[index]

def clear_chords():
    global chords
    chord_listbox.delete(0, tk.END)
    chords.clear()

def save_settings():
    global chords
    settings = {
        "chords": chords,
        "duration": duration_entry.get(),
        "bpm": bpm_entry.get(),
        "time_signature": time_signature_entry.get(),
        "volume": volume_entry.get(),
        "reverb_decay": reverb_entry.get(),
        "echo_delay": echo_delay_entry.get(),
        "echo_decay": echo_decay_entry.get(),
        "loops": loop_entry.get(),
        "include_chords": chords_var.get(),
        "include_drums": drums_var.get(),
        "include_noise": noise_var.get()
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    status_label.config(text="Settings saved to 'settings.json'")

def load_settings():
    global chords
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
        chords = settings["chords"]
        for chord in chords:
            arpeggio_text = " (Arpeggio)" if chord[2] else ""
            drum_text = " (Drums)" if chord[3] else ""
            chord_text = " (Chords)" if chord[4] else ""
            chord_listbox.insert(tk.END, f"{chord[0]} {chord[1]}{arpeggio_text}{drum_text}{chord_text}")
        duration_entry.delete(0, tk.END)
        duration_entry.insert(0, settings["duration"])
        bpm_entry.delete(0, tk.END)
        bpm_entry.insert(0, settings["bpm"])
        time_signature_entry.delete(0, tk.END)
        time_signature_entry.insert(0, settings["time_signature"])
        volume_entry.delete(0, tk.END)
        volume_entry.insert(0, settings["volume"])
        reverb_entry.delete(0, tk.END)
        reverb_entry.insert(0, settings["reverb_decay"])
        echo_delay_entry.delete(0, tk.END)
        echo_delay_entry.insert(0, settings["echo_delay"])
        echo_decay_entry.delete(0, tk.END)
        echo_decay_entry.insert(0, settings["echo_decay"])
        loop_entry.delete(0, tk.END)
        loop_entry.insert(0, settings["loops"])
        chords_var.set(settings["include_chords"])
        drums_var.set(settings["include_drums"])
        noise_var.set(settings["include_noise"])
        status_label.config(text="Settings loaded from 'settings.json'")
    except FileNotFoundError:
        status_label.config(text="No settings file found. Please save settings first.")

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

arpeggio_var = tk.BooleanVar()
arpeggio_checkbox = ttk.Checkbutton(frame, text="Arpeggio", variable=arpeggio_var)
arpeggio_checkbox.grid(column=3, row=0, sticky=(tk.W, tk.E))

apply_settings_var = tk.BooleanVar()
apply_settings_checkbox = ttk.Checkbutton(frame, text="Apply Settings to Chord", variable=apply_settings_var)
apply_settings_checkbox.grid(column=4, row=0, sticky=(tk.W, tk.E))

add_chord_button = ttk.Button(frame, text="Add Chord", command=add_chord)
add_chord_button.grid(column=5, row=0, sticky=(tk.W, tk.E))

chord_listbox = tk.Listbox(frame, height=10)
chord_listbox.grid(column=0, row=1, columnspan=5, sticky=(tk.W, tk.E))
remove_chord_button = ttk.Button(frame, text="Remove Selected Chord", command=remove_chord)
remove_chord_button.grid(column=5, row=1, sticky=(tk.W, tk.E))
clear_chords_button = ttk.Button(frame, text="Clear All Chords", command=clear_chords)
clear_chords_button.grid(column=5, row=2, sticky=(tk.W, tk.E))

# Duration, BPM, Volume, Reverb, Echo Settings, and Checkboxes
ttk.Label(frame, text="Duration (seconds)").grid(column=0, row=3, sticky=tk.W)
duration_entry = ttk.Entry(frame)
duration_entry.grid(column=1, row=3, sticky=(tk.W, tk.E))

ttk.Label(frame, text="BPM").grid(column=0, row=4, sticky=tk.W)
bpm_entry = ttk.Entry(frame)
bpm_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Time Signature (e.g., 4/4)").grid(column=0, row=5, sticky=tk.W)
time_signature_entry = ttk.Entry(frame)
time_signature_entry.grid(column=1, row=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Volume (dB)").grid(column=0, row=6, sticky=tk.W)
volume_entry = ttk.Entry(frame)
volume_entry.grid(column=1, row=6, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Reverb Decay").grid(column=0, row=7, sticky=tk.W)
reverb_entry = ttk.Entry(frame)
reverb_entry.grid(column=1, row=7, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Delay (ms)").grid(column=0, row=8, sticky=tk.W)
echo_delay_entry = ttk.Entry(frame)
echo_delay_entry.grid(column=1, row=8, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Decay").grid(column=0, row=9, sticky=tk.W)
echo_decay_entry = ttk.Entry(frame)
echo_decay_entry.grid(column=1, row=9, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Number of Loops").grid(column=0, row=10, sticky=tk.W)
loop_entry = ttk.Entry(frame)
loop_entry.grid(column=1, row=10, sticky=(tk.W, tk.E))

chords_var = tk.BooleanVar(value=True)
chords_checkbox = ttk.Checkbutton(frame, text="Include Chords", variable=chords_var)
chords_checkbox.grid(column=0, row=11, sticky=tk.W)

drums_var = tk.BooleanVar(value=True)
drums_checkbox = ttk.Checkbutton(frame, text="Include Drums", variable=drums_var)
drums_checkbox.grid(column=1, row=11, sticky=tk.W)

noise_var = tk.BooleanVar(value=True)
noise_checkbox = ttk.Checkbutton(frame, text="Include White Noise", variable=noise_var)
noise_checkbox.grid(column=2, row=11, sticky=tk.W)

# Generate, Save, Load Buttons and Status Label
generate_button = ttk.Button(frame, text="Generate Music", command=generate_music)
generate_button.grid(column=0, row=12, columnspan=6, sticky=(tk.W, tk.E))

save_button = ttk.Button(frame, text="Save Settings", command=save_settings)
save_button.grid(column=0, row=13, columnspan=2, sticky=(tk.W, tk.E))

load_button = ttk.Button(frame, text="Load Settings", command=load_settings)
load_button.grid(column=2, row=13, columnspan=2, sticky=(tk.W, tk.E))

status_label = ttk.Label(frame, text="")
status_label.grid(column=0, row=14, columnspan=6, sticky=(tk.W, tk.E))

root.mainloop()
