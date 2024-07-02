import tkinter as tk
from tkinter import ttk
from chord_management import add_chord, remove_chord, clear_chords, chords, CHORD_FREQUENCIES, CHORD_TYPES
from music_generation import generate_music, generate_chord, generate_arpeggio, generate_drum_beat, generate_atmospheric_noise, apply_reverb, apply_echo
from settings_management import save_settings, load_settings
from pydub import AudioSegment
import numpy as np
import pygame

pygame.mixer.init()

copied_chord = None

def calculate_duration():
    try:
        bpm = int(bpm_entry.get())
        time_signature = time_signature_entry.get()
        measures = int(measures_entry.get())

        # Calculate duration for a clean loop
        beats_per_measure = int(time_signature.split('/')[0])
        duration_in_beats = beats_per_measure * measures
        duration_in_seconds = (duration_in_beats * 60) / bpm
        duration_entry.delete(0, tk.END)
        duration_entry.insert(0, str(int(duration_in_seconds)))
    except ValueError:
        status_label.config(text="Invalid BPM, Time Signature, or Measures. Please enter valid values.")

def save_chord_settings():
    selected_index = chord_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        chord_name = chord_name_var.get().strip().upper()
        chord_type = chord_type_var.get().strip()
        octave = int(octave_var.get())
        arpeggio = arpeggio_var.get()
        include_chords = chords_var.get()
        include_drums = drums_var.get()

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
            volume = int(volume_entry.get())
        except ValueError:
            volume = -10  # Default to -10 dB if invalid or empty

        try:
            reverb_decay = float(reverb_entry.get())
        except ValueError:
            reverb_decay = 0.5  # Default to 0.5 if invalid or empty

        try:
            echo_delay = int(echo_delay_entry.get())
        except ValueError:
            echo_delay = 300  # Default to 300 ms if invalid or empty

        try:
            echo_decay = float(echo_decay_entry.get())
        except ValueError:
            echo_decay = 0.5  # Default to 0.5 if invalid or empty

        if chord_name in CHORD_FREQUENCIES and chord_type in CHORD_TYPES:
            chords[index] = (chord_name, chord_type, arpeggio, include_drums, include_chords, duration, bpm, time_signature, volume, reverb_decay, echo_delay, echo_decay, octave)
            arpeggio_text = " (Arpeggio)" if arpeggio else ""
            drum_text = " (Drums)" if include_drums else ""
            chord_text = " (Chords)" if include_chords else ""
            chord_listbox.delete(index)
            chord_listbox.insert(index, f"{chord_name}{octave} {chord_type}{arpeggio_text}{drum_text}{chord_text}")
            chord_listbox.select_set(index)
        else:
            status_label.config(text="Invalid chord name or type. Please select valid options.")

def on_double_click(event):
    selected_index = chord_listbox.curselection()
    if selected_index:
        chord = chords[selected_index[0]]
        chord_name_var.set(chord[0])
        chord_type_var.set(chord[1])
        octave_var.set(str(chord[12]))
        arpeggio_var.set(chord[2])
        duration_entry.delete(0, tk.END)
        duration_entry.insert(0, chord[5])
        bpm_entry.delete(0, tk.END)
        bpm_entry.insert(0, chord[6])
        time_signature_entry.delete(0, tk.END)
        time_signature_entry.insert(0, chord[7])
        volume_entry.delete(0, tk.END)
        volume_entry.insert(0, chord[8])
        reverb_entry.delete(0, tk.END)
        reverb_entry.insert(0, chord[9])
        echo_delay_entry.delete(0, tk.END)
        echo_delay_entry.insert(0, chord[10])
        echo_decay_entry.delete(0, tk.END)
        echo_decay_entry.insert(0, chord[11])
        chords_var.set(chord[4])
        drums_var.set(chord[3])

def copy_chord():
    global copied_chord
    selected_index = chord_listbox.curselection()
    if selected_index:
        copied_chord = chords[selected_index[0]]

def paste_chord():
    global copied_chord
    if copied_chord:
        chords.append(copied_chord)
        arpeggio_text = " (Arpeggio)" if copied_chord[2] else ""
        drum_text = " (Drums)" if copied_chord[3] else ""
        chord_text = " (Chords)" if copied_chord[4] else ""
        chord_listbox.insert(tk.END, f"{copied_chord[0]}{copied_chord[12]} {copied_chord[1]}{arpeggio_text}{drum_text}{chord_text}")

def move_up():
    selected_index = chord_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        if index > 0:
            # Swap chords in the list
            chords[index], chords[index-1] = chords[index-1], chords[index]
            # Update the listbox
            chord_text = chord_listbox.get(index)
            chord_listbox.delete(index)
            chord_listbox.insert(index-1, chord_text)
            chord_listbox.select_set(index-1)
            chord_listbox.activate(index-1)

def move_down():
    selected_index = chord_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        if index < len(chords) - 1:
            # Swap chords in the list
            chords[index], chords[index+1] = chords[index+1], chords[index]
            # Update the listbox
            chord_text = chord_listbox.get(index)
            chord_listbox.delete(index)
            chord_listbox.insert(index+1, chord_text)
            chord_listbox.select_set(index+1)
            chord_listbox.activate(index+1)

def preview_chord(chords, chord_listbox):
    selected_index = chord_listbox.curselection()
    if selected_index:
        chord = chords[selected_index[0]]
        base_freq = CHORD_FREQUENCIES[chord[0]] * (2 ** (chord[12] - 4))
        intervals = CHORD_TYPES[chord[1]]
        if chord[2]:  # If arpeggio
            chord_audio = generate_arpeggio(base_freq, intervals, chord[5] * 1000, chord[8])
        else:
            chord_audio = generate_chord(base_freq, intervals, chord[5] * 1000, chord[8])
        
        if chord[3]:  # If drums
            drum_audio = generate_drum_beat(chord[5] * 1000, chord[6], chord[7], chord[8])
            chord_audio = chord_audio.overlay(drum_audio)

        play_audio(chord_audio)

def play_audio(audio_segment):
    # Convert AudioSegment to numpy array
    audio_data = np.array(audio_segment.get_array_of_samples())

    # Make sure audio data is contiguous
    if not audio_data.flags['C_CONTIGUOUS']:
        audio_data = np.ascontiguousarray(audio_data)

    # Convert to a format pygame can use
    audio_data = audio_data.reshape(-1, audio_segment.channels)

    sound = pygame.sndarray.make_sound(audio_data)
    sound.play()

def preview_song(chords, chords_var, drums_var, noise_var):
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

        play_audio(music)

    except Exception as e:
        status_label.config(text=f"Error previewing song: {str(e)}")

# Initialize GUI
root = tk.Tk()
root.title("automatic shallot v0.3")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Chord Management
ttk.Label(frame, text="Add Chord").grid(column=0, row=0, sticky=tk.W)

chord_name_var = tk.StringVar()
chord_name_menu = ttk.OptionMenu(frame, chord_name_var, "C", *CHORD_FREQUENCIES.keys())
chord_name_menu.grid(column=1, row=0, sticky=(tk.W, tk.E))

chord_type_var = tk.StringVar()
chord_type_menu = ttk.OptionMenu(frame, chord_type_var, "Major", *CHORD_TYPES.keys())
chord_type_menu.grid(column=2, row=0, sticky=(tk.W, tk.E))

octave_var = tk.StringVar(value="4")
octave_menu = ttk.OptionMenu(frame, octave_var, "4", "0", "1", "2", "3", "4", "5", "6", "7", "8")
octave_menu.grid(column=3, row=0, sticky=(tk.W, tk.E))

arpeggio_var = tk.BooleanVar()
arpeggio_checkbox = ttk.Checkbutton(frame, text="Arpeggio", variable=arpeggio_var)
arpeggio_checkbox.grid(column=4, row=0, sticky=(tk.W, tk.E))

apply_settings_var = tk.BooleanVar()
apply_settings_checkbox = ttk.Checkbutton(frame, text="Apply Settings to Chord", variable=apply_settings_var)
apply_settings_checkbox.grid(column=5, row=0, sticky=(tk.W, tk.E))

add_chord_button = ttk.Button(frame, text="Add Chord", command=lambda: add_chord(chord_name_var, chord_type_var, octave_var, arpeggio_var, apply_settings_var, chords, chord_listbox, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, chords_var, drums_var))
add_chord_button.grid(column=6, row=0, sticky=(tk.W, tk.E))

save_chord_button = ttk.Button(frame, text="Save Chord Settings", command=save_chord_settings)
save_chord_button.grid(column=6, row=1, sticky=(tk.W, tk.E))

chord_listbox = tk.Listbox(frame, height=10)
chord_listbox.grid(column=0, row=1, columnspan=6, sticky=(tk.W, tk.E))
remove_chord_button = ttk.Button(frame, text="Remove Selected Chord", command=lambda: remove_chord(chords, chord_listbox))
remove_chord_button.grid(column=6, row=2, sticky=(tk.W, tk.E))
clear_chords_button = ttk.Button(frame, text="Clear All Chords", command=lambda: clear_chords(chords, chord_listbox))
clear_chords_button.grid(column=6, row=3, sticky=(tk.W, tk.E))

# Duration, BPM, Volume, Reverb, Echo Settings, and Checkboxes
ttk.Label(frame, text="Duration (seconds)").grid(column=0, row=4, sticky=tk.W)
duration_entry = ttk.Entry(frame)
duration_entry.grid(column=1, row=4, sticky=(tk.W, tk.E))

ttk.Label(frame, text="BPM").grid(column=0, row=5, sticky=tk.W)
bpm_entry = ttk.Entry(frame)
bpm_entry.grid(column=1, row=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Time Signature (e.g., 4/4)").grid(column=0, row=6, sticky=tk.W)
time_signature_entry = ttk.Entry(frame)
time_signature_entry.grid(column=1, row=6, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Volume (dB)").grid(column=0, row=7, sticky=tk.W)
volume_entry = ttk.Entry(frame)
volume_entry.grid(column=1, row=7, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Reverb Decay").grid(column=0, row=8, sticky=tk.W)
reverb_entry = ttk.Entry(frame)
reverb_entry.grid(column=1, row=8, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Delay (ms)").grid(column=0, row=9, sticky=tk.W)
echo_delay_entry = ttk.Entry(frame)
echo_delay_entry.grid(column=1, row=9, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Echo Decay").grid(column=0, row=10, sticky=tk.W)
echo_decay_entry = ttk.Entry(frame)
echo_decay_entry.grid(column=1, row=10, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Number of Loops").grid(column=0, row=11, sticky=tk.W)
loop_entry = ttk.Entry(frame)
loop_entry.grid(column=1, row=11, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Measures").grid(column=0, row=12, sticky=tk.W)
measures_entry = ttk.Entry(frame)
measures_entry.grid(column=1, row=12, sticky=(tk.W, tk.E))

chords_var = tk.BooleanVar(value=True)
chords_checkbox = ttk.Checkbutton(frame, text="Include Chords", variable=chords_var)
chords_checkbox.grid(column=0, row=13, sticky=tk.W)

drums_var = tk.BooleanVar(value=True)
drums_checkbox = ttk.Checkbutton(frame, text="Include Drums", variable=drums_var)
drums_checkbox.grid(column=1, row=13, sticky=tk.W)

noise_var = tk.BooleanVar(value=True)
noise_checkbox = ttk.Checkbutton(frame, text="Include White Noise", variable=noise_var)
noise_checkbox.grid(column=2, row=13, sticky=tk.W)

# Generate, Save, Load Buttons and Status Label
generate_button = ttk.Button(frame, text="Generate Music", command=lambda: generate_music(chords, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, measures_entry, status_label))
generate_button.grid(column=0, row=14, columnspan=7, sticky=(tk.W, tk.E))

save_button = ttk.Button(frame, text="Save Settings", command=lambda: save_settings(chords, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, status_label))
save_button.grid(column=0, row=15, columnspan=3, sticky=(tk.W, tk.E))

load_button = ttk.Button(frame, text="Load Settings", command=lambda: load_settings(chords, chord_listbox, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, status_label))
load_button.grid(column=3, row=15, columnspan=3, sticky=(tk.W, tk.E))

preview_chord_button = ttk.Button(frame, text="Preview Chord", command=lambda: preview_chord(chords, chord_listbox))
preview_chord_button.grid(column=6, row=4, sticky=(tk.W, tk.E))

preview_song_button = ttk.Button(frame, text="Preview Song", command=lambda: preview_song(chords, chords_var, drums_var, noise_var))
preview_song_button.grid(column=6, row=5, sticky=(tk.W, tk.E))

status_label = ttk.Label(frame, text="")
status_label.grid(column=0, row=16, columnspan=7, sticky=(tk.W, tk.E))

# Bind double click event
chord_listbox.bind("<Double-1>", on_double_click)

# Bind focus out event to time_signature_entry, bpm_entry, and measures_entry
time_signature_entry.bind("<FocusOut>", lambda event: calculate_duration())
bpm_entry.bind("<FocusOut>", lambda event: calculate_duration())
measures_entry.bind("<FocusOut>", lambda event: calculate_duration())

# Add copy, paste, move buttons
copy_button = ttk.Button(frame, text="Copy", command=copy_chord)
copy_button.grid(column=6, row=6, sticky=(tk.W, tk.E))

paste_button = ttk.Button(frame, text="Paste", command=paste_chord)
paste_button.grid(column=6, row=7, sticky=(tk.W, tk.E))

move_up_button = ttk.Button(frame, text="Move Up", command=move_up)
move_up_button.grid(column=6, row=8, sticky=(tk.W, tk.E))

move_down_button = ttk.Button(frame, text="Move Down", command=move_down)
move_down_button.grid(column=6, row=9, sticky=(tk.W, tk.E))

root.mainloop()
