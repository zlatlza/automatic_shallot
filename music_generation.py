from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
from chord_management import CHORD_FREQUENCIES, CHORD_TYPES
import random

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
    tom = generate_sine_wave(150, beat_duration_ms // 2, volume_db).low_pass_filter(200)
    crash = generate_white_noise(beat_duration_ms, volume_db).high_pass_filter(2000)
    
    for beat in range(0, duration_ms, beat_duration_ms):
        measure_position = (beat // beat_duration_ms) % beats_per_measure
        
        # Create variations in the drum pattern
        if measure_position == 0:
            drum = drum.overlay(kick, position=beat)
        elif measure_position == beats_per_measure - 1:
            drum = drum.overlay(kick, position=beat).overlay(crash, position=beat)
        elif measure_position % 2 == 0:
            drum = drum.overlay(snare, position=beat)
        
        # Add hi-hats and toms for more rhythm
        if measure_position % 4 == 0:
            drum = drum.overlay(hi_hat, position=beat)
        if measure_position == beats_per_measure // 2:
            drum = drum.overlay(tom, position=beat)
        
        # Randomly add variations
        if random.random() > 0.7:
            drum = drum.overlay(hi_hat, position=beat)
        if random.random() > 0.8:
            drum = drum.overlay(tom, position=beat)

    return drum

def apply_reverb(audio_segment, decay=0.5):
    return audio_segment.overlay(audio_segment - decay)

def apply_echo(audio_segment, delay_ms=300, decay=0.5):
    echo = audio_segment[:delay_ms].overlay(audio_segment, gain_during_overlay=-decay)
    return audio_segment.overlay(echo)
def generate_music(chords, duration_entry, bpm_entry, time_signature_entry, volume_entry, reverb_entry, echo_delay_entry, echo_decay_entry, loop_entry, chords_var, drums_var, noise_var, measures_entry, status_label):
    try:
        base_freqs = [CHORD_FREQUENCIES[chord[0]] * (2 ** (chord[12] - 4)) for chord in chords]
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

        try:
            duration_ms = sum(durations) * 1000
        except Exception as e:
            status_label.config(text=f"Error calculating duration: {str(e)}")
            return

        try:
            loops = int(loop_entry.get())
        except ValueError:
            loops = 1  # Default to 1 loop if invalid or empty

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
