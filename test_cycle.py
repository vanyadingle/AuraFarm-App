import os
import numpy as np
from edit_engine import PhonkEditEngine
from audio_player import PhonkAudioPlayer

def test():
    print("Testing Audio...")
    audio = PhonkAudioPlayer()
    audio_path = os.path.join(os.path.dirname(__file__), "assets", "audio", "capcut_audio_1.wav")
    print(f"Audio file exists: {os.path.exists(audio_path)}")
    audio.play(audio_path)
    audio.stop()
    print("Audio test passed!")

    print("Testing Pure CapCut Edit Engine...")
    engine = PhonkEditEngine(os.path.join(os.path.dirname(__file__), "assets"))
    snaps = [
        np.zeros((360, 280, 3), dtype=np.uint8),
        np.full((360, 280, 3), 100, dtype=np.uint8),
        np.full((360, 280, 3), 200, dtype=np.uint8)
    ]
    
    for tmpl in engine.templates:
        print(f"Testing: {tmpl['name']}")
        for t in [0.0, 1.0, 2.5, 4.0, 6.0]:
            frame = engine.render_frame(tmpl, t, snaps, (280, 360))
            assert frame.shape == (360, 280, 3), f"Wrong shape: {frame.shape}"
    print("All pure CapCut templates verified!")

if __name__ == "__main__":
    test()
