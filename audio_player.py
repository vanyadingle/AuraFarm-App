import os
import sys
import threading
import winsound

class PhonkAudioPlayer:
    def __init__(self):
        self._is_playing = False
        self._lock = threading.Lock()

    def play(self, wav_path):
        def _play_worker(path):
            with self._lock:
                try:
                    if not os.path.exists(path):
                        return
                    abs_path = os.path.abspath(path)
                    # Play asynchronously without blocking UI thread
                    winsound.PlaySound(abs_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                    self._is_playing = True
                except Exception as e:
                    print(f"[Audio] Playback error: {e}")

        t = threading.Thread(target=_play_worker, args=(wav_path,), daemon=True)
        t.start()

    def stop(self):
        def _stop_worker():
            with self._lock:
                try:
                    winsound.PlaySound(None, winsound.SND_PURGE)
                except Exception:
                    pass
                self._is_playing = False

        t = threading.Thread(target=_stop_worker, daemon=True)
        t.start()

    def is_playing(self):
        return self._is_playing
