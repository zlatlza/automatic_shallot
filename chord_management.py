import tkinter as tk

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
    "Minor-Major 7th": [0, 3, 7, 11],
    "Suspended 2nd": [0, 2, 7],
    "Suspended 4th": [0, 5, 7],
    "Major 6th": [0, 4, 7, 9],
    "Minor 6th": [0, 3, 7, 9],
    "9th": [0, 4, 7, 10, 14],
    "Major 9th": [0, 4, 7, 11, 14],
    "Minor 9th": [0, 3, 7, 10, 14],
    "11th": [0, 4, 7, 10, 14, 17],
    "Major 11th": [0, 4, 7, 11, 14, 17],
    "Minor 11th": [0, 3, 7, 10, 14, 17],
    "13th": [0, 4, 7, 10, 14, 17, 21],
    "Major 13th": [0, 4, 7, 11, 14, 17, 21],
    "Minor 13th": [0, 3, 7, 10, 14, 17, 21],
    "Add 9": [0, 4, 7, 14],
    "Minor Add 9": [0, 3, 7, 14],
    "Augmented 7th": [0, 4, 8, 10],
    "Augmented Major 7th": [0, 4, 8, 11]
}

chords = []
copied_chord = None

def add_chord(chord_name_var, chord_type_var, octave_var, arpeggio_var, apply_settings_var, chords, chord_listbox, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, chords_var, drums_var):
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
    octave = int(octave_var.get())
    arpeggio = arpeggio_var.get()
    include_drums = drums_var.get()
    include_chords = chords_var.get()
    
    if chord_name in CHORD_FREQUENCIES and chord_type in CHORD_TYPES:
        if apply_settings:
            chords.append((chord_name, chord_type, arpeggio, include_drums, include_chords, duration, bpm, time_signature, volume_db, reverb_decay, echo_delay_ms, echo_decay, octave))
        else:
            # Default values if apply settings is not checked
            chords.append((chord_name, chord_type, arpeggio, include_drums, include_chords, 60, 120, "4/4", -10, 0.5, 300, 0.5, 4))
        
        arpeggio_text = " (Arpeggio)" if arpeggio else ""
        drum_text = " (Drums)" if include_drums else ""
        chord_text = " (Chords)" if include_chords else ""
        chord_listbox.insert(tk.END, f"{chord_name}{octave} {chord_type}{arpeggio_text}{drum_text}{chord_text}")
    else:
        print("Invalid chord name or type. Please select valid options.")

def remove_chord(chords, chord_listbox):
    selected_indices = chord_listbox.curselection()
    for index in selected_indices[::-1]:
        chord_listbox.delete(index)
        del chords[index]

def clear_chords(chords, chord_listbox):
    chord_listbox.delete(0, tk.END)
    chords.clear()
