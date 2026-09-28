import os
import cv2
import numpy as np

def test_blend():
    vid_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
    for i in range(1, 5):
        vid_path = os.path.join(vid_dir, f"template_{i}.mp4")
        cap = cv2.VideoCapture(vid_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(cv2.resize(frame, (400, 240)))
        cap.release()
        print(f"Template {i}: loaded {len(frames)} frames successfully! Resolution: {frames[0].shape}")

if __name__ == "__main__":
    test_blend()
