import json
import tkinter as tk

def save_settings(chords, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, status_label):
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

def load_settings(chords, chord_listbox, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, status_label):
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
        chords.clear()
        chord_listbox.delete(0, tk.END)
        chords.extend(settings["chords"])
        for chord in chords:
            arpeggio_text = " (Arpeggio)" if chord[2] else ""
            drum_text = " (Drums)" if chord[3] else ""
            chord_text = " (Chords)" if chord[4] else ""
            chord_listbox.insert(tk.END, f"{chord[0]}{chord[12]} {chord[1]}{arpeggio_text}{drum_text}{chord_text}")
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
