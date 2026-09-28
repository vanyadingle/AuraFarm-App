import os
import math
import struct
import wave
import numpy as np

SAMPLE_RATE = 44100

def save_wav(filename, samples, sample_rate=SAMPLE_RATE):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Normalize and clip
    samples = np.clip(samples, -0.98, 0.98)
    int_samples = (samples * 32767).astype(np.int16)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())
    print(f"Generated {filename} ({len(samples)/sample_rate:.2f}s)")

def cowbell_note(freq, duration, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Phonk 808 cowbell signature: two detuned square/triangle oscillators with quick pitch drop
    f1 = freq
    f2 = freq * 1.48
    env = np.exp(-t * 9.0) + 0.3 * np.exp(-t * 2.5)
    wave1 = np.sign(np.sin(2 * np.pi * f1 * t)) * 0.5 + np.sin(2 * np.pi * f1 * t) * 0.5
    wave2 = np.sign(np.sin(2 * np.pi * f2 * t)) * 0.3 + np.sin(2 * np.pi * f2 * t) * 0.3
    cowbell = (wave1 + wave2) * env * 0.6
    # Phonk saturation / distortion
    cowbell = np.tanh(cowbell * 2.5) * 0.8
    return cowbell

def kick_808(duration=0.4, pitch_start=140, pitch_end=42, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Exponential pitch decay
    freq = pitch_end + (pitch_start - pitch_end) * np.exp(-t * 30.0)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    env = np.exp(-t * 4.0)
    sine = np.sin(phase) * env
    # Heavy Brazilian Phonk 808 saturation / overdrive
    distorted = np.tanh(sine * 4.0) * 0.9
    return distorted

def snare_hit(duration=0.25, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 18.0)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22.0)
    snare = (noise * 0.7 + tone * 0.5) * 0.7
    return np.clip(snare, -1, 1)

def brazilian_funk_beat(bpm=135, bars=4, sample_rate=SAMPLE_RATE):
    # Brazilian Baile Funk signature rhythm:
    # Beat pattern (16th notes): Kick . . Kick | . . Snare . | Kick . . Kick | . . Snare .
    beat_dur = 60.0 / bpm
    total_time = beat_dur * 4 * bars
    total_samples = int(total_time * sample_rate)
    buffer = np.zeros(total_samples, dtype=np.float32)
    
    kick = kick_808(duration=0.35, pitch_start=150, pitch_end=45)
    snare = snare_hit(duration=0.22)
    
    step_time = beat_dur / 4.0 # 16th note
    total_steps = bars * 16
    
    # Baile Funk syncopated pattern per 16 steps:
    # 0 (Kick), 3 (Kick), 6 (Snare), 8 (Kick), 11 (Kick), 14 (Snare)
    funk_kick_steps = [0, 3, 8, 11]
    funk_snare_steps = [6, 14]
    
    for bar in range(bars):
        offset_step = bar * 16
        for ks in funk_kick_steps:
            st = int((offset_step + ks) * step_time * sample_rate)
            if st < total_samples:
                end_st = min(st + len(kick), total_samples)
                buffer[st:end_st] += kick[:end_st - st]
        for ss in funk_snare_steps:
            st = int((offset_step + ss) * step_time * sample_rate)
            if st < total_samples:
                end_st = min(st + len(snare), total_samples)
                buffer[st:end_st] += snare[:end_st - st]
                
    return buffer

def add_melody(buffer, bpm, notes_sequence, start_time, sample_rate=SAMPLE_RATE):
    beat_dur = 60.0 / bpm
    for note, dur_beats, time_beats in notes_sequence:
        if note > 0:
            cb = cowbell_note(note, dur_beats * beat_dur * 0.95, sample_rate)
            st = int((start_time + time_beats * beat_dur) * sample_rate)
            if st < len(buffer):
                end_st = min(st + len(cb), len(buffer))
                buffer[st:end_st] += cb[:end_st - st] * 0.85

def generate_track_1(output_path):
    # Template 1: Skull Top vs Phonk (Buildup, freeze frame drop, aggressive phonk cowbell)
    bpm = 138
    beat_dur = 60.0 / bpm
    duration = 6.8
    total_samples = int(duration * SAMPLE_RATE)
    buf = np.zeros(total_samples, dtype=np.float32)
    
    # 0s - 2.0s: Buildup riser & fast cowbells
    t_rise = np.linspace(0, 2.0, int(2.0 * SAMPLE_RATE), False)
    riser = np.sin(2 * np.pi * (100 + 400 * (t_rise/2.0)**2) * t_rise) * (t_rise/2.0) * 0.35
    buf[:len(riser)] += riser
    
    # Fast intro notes
    intro_notes = [
        (440, 0.5, 0.0), (440, 0.5, 0.5), (523, 0.5, 1.0), (587, 0.5, 1.5)
    ]
    add_melody(buf, bpm, intro_notes, 0.0)
    
    # 2.0s: FREEZE IMPACT / BASS DROP
    # Huge impact slam
    impact_t = np.linspace(0, 1.2, int(1.2 * SAMPLE_RATE), False)
    impact = np.sin(2 * np.pi * 50 * np.exp(-impact_t * 5.0) * impact_t) * np.exp(-impact_t * 3.0) * 1.5
    impact = np.tanh(impact * 3.0) * 0.95
    st_impact = int(2.0 * SAMPLE_RATE)
    buf[st_impact:st_impact+len(impact)] += impact
    
    # Drop beat from 2.0s to 6.8s (Brazilian Funk rhythm)
    drop_beat = brazilian_funk_beat(bpm=bpm, bars=3)
    end_drop = min(st_impact + len(drop_beat), total_samples)
    buf[st_impact:end_drop] += drop_beat[:end_drop - st_impact]
    
    # Aggressive Skull Phonk Cowbell riff in drop
    # Notes: E5 (659), D5 (587), C5 (523), B4 (494), A4 (440), G#4 (415)
    drop_melody = [
        (659, 0.5, 0.0), (659, 0.25, 0.5), (587, 0.25, 0.75), (659, 0.5, 1.0), (784, 0.5, 1.5),
        (659, 0.5, 2.0), (523, 0.5, 2.5), (587, 0.5, 3.0), (494, 0.5, 3.5),
        (440, 0.5, 4.0), (440, 0.25, 4.5), (523, 0.25, 4.75), (659, 0.5, 5.0), (587, 0.5, 5.5),
        (523, 0.5, 6.0), (494, 0.5, 6.5), (440, 1.0, 7.0), (415, 1.0, 8.0)
    ]
    add_melody(buf, bpm, drop_melody, 2.0)
    
    save_wav(output_path, np.tanh(buf * 1.3) * 0.95)

def generate_track_2(output_path):
    # Template 2: Funk Sigilo Brazilian Phonk (Heavy bouncy phonk beat, sync chops)
    bpm = 142
    duration = 6.5
    total_samples = int(duration * SAMPLE_RATE)
    buf = np.zeros(total_samples, dtype=np.float32)
    
    # Immediate heavy Brazilian beat
    drop_beat = brazilian_funk_beat(bpm=bpm, bars=4)
    end_drop = min(len(drop_beat), total_samples)
    buf[:end_drop] += drop_beat[:end_drop]
    
    # Montagem Funksigilo signature cowbell hook
    sigilo_notes = [
        (587, 0.25, 0.0), (587, 0.25, 0.25), (587, 0.25, 0.5), (659, 0.5, 0.75),
        (587, 0.25, 1.5), (523, 0.25, 1.75), (494, 0.5, 2.0), (440, 0.5, 2.5),
        (587, 0.25, 3.0), (587, 0.25, 3.25), (587, 0.25, 3.5), (659, 0.5, 3.75),
        (784, 0.5, 4.5), (659, 0.5, 5.0), (587, 0.5, 5.5), (523, 0.5, 6.0),
        (440, 0.25, 6.5), (440, 0.25, 6.75), (523, 0.5, 7.0), (587, 0.5, 7.5),
        (659, 0.5, 8.0), (587, 0.5, 8.5), (523, 0.5, 9.0), (440, 1.0, 9.5)
    ]
    add_melody(buf, bpm, sigilo_notes, 0.0)
    
    save_wav(output_path, np.tanh(buf * 1.35) * 0.95)

def generate_track_3(output_path):
    # Template 3: Skull Freeze-Frame Trend (Dark sub bass, stutter drop, skull slam)
    bpm = 132
    duration = 6.0
    total_samples = int(duration * SAMPLE_RATE)
    buf = np.zeros(total_samples, dtype=np.float32)
    
    # Intro dark bell 0-1.8s
    intro_notes = [(392, 0.6, 0.0), (440, 0.6, 0.8), (494, 0.6, 1.4)]
    add_melody(buf, bpm, intro_notes, 0.0)
    
    # 1.8s Freeze Glitch Sound
    st_freeze = int(1.8 * SAMPLE_RATE)
    t_glitch = np.linspace(0, 0.3, int(0.3 * SAMPLE_RATE), False)
    glitch = np.sin(2 * np.pi * 1200 * t_glitch) * np.sin(2 * np.pi * 60 * t_glitch) * 0.6
    buf[st_freeze:st_freeze+len(glitch)] += glitch
    
    # 2.1s DROP
    st_drop = int(2.1 * SAMPLE_RATE)
    drop_beat = brazilian_funk_beat(bpm=bpm, bars=3)
    end_drop = min(st_drop + len(drop_beat), total_samples)
    buf[st_drop:end_drop] += drop_beat[:end_drop - st_drop]
    
    # Phonk riff
    skull_notes = [
        (440, 0.5, 0.0), (440, 0.25, 0.5), (440, 0.25, 0.75), (523, 0.5, 1.0),
        (659, 0.5, 1.5), (587, 0.5, 2.0), (523, 0.5, 2.5), (494, 0.5, 3.0),
        (440, 0.5, 3.5), (415, 0.5, 4.0), (440, 1.0, 4.5), (523, 0.5, 5.5),
        (659, 1.0, 6.0)
    ]
    add_melody(buf, bpm, skull_notes, 2.1)
    
    save_wav(output_path, np.tanh(buf * 1.4) * 0.95)

def generate_track_4(output_path):
    # Template 4: Viral Aura Overload Phonk (High tempo, euphoric Brazilian phonk anthem)
    bpm = 145
    duration = 6.2
    total_samples = int(duration * SAMPLE_RATE)
    buf = np.zeros(total_samples, dtype=np.float32)
    
    drop_beat = brazilian_funk_beat(bpm=bpm, bars=4)
    end_drop = min(len(drop_beat), total_samples)
    buf[:end_drop] += drop_beat[:end_drop] * 1.1
    
    aura_notes = [
        (659, 0.25, 0.0), (784, 0.25, 0.25), (880, 0.5, 0.5), (784, 0.25, 1.0),
        (659, 0.25, 1.25), (587, 0.5, 1.5), (523, 0.5, 2.0), (659, 0.5, 2.5),
        (784, 0.25, 3.0), (880, 0.25, 3.25), (1046, 0.5, 3.5), (880, 0.5, 4.0),
        (784, 0.5, 4.5), (659, 0.5, 5.0), (587, 0.5, 5.5), (523, 0.5, 6.0),
        (494, 0.5, 6.5), (440, 1.0, 7.0)
    ]
    add_melody(buf, bpm, aura_notes, 0.0)
    
    save_wav(output_path, np.tanh(buf * 1.35) * 0.95)

if __name__ == "__main__":
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
    generate_track_1(os.path.join(audio_dir, "phonk_skull_top.wav"))
    generate_track_2(os.path.join(audio_dir, "phonk_funk_sigilo.wav"))
    generate_track_3(os.path.join(audio_dir, "phonk_skull_freeze.wav"))
    generate_track_4(os.path.join(audio_dir, "phonk_aura_overload.wav"))
    print("All Brazilian Phonk audio tracks generated successfully!")
