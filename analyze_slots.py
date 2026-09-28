import os
import cv2
import numpy as np

vid_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")

for i in range(1, 5):
    vid_path = os.path.join(vid_dir, f"template_{i}.mp4")
    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"\n--- Template {i} ({total} frames, {total/fps:.2f}s) ---")
    
    # Sample every 0.5s
    step = int(fps * 0.5)
    for f_idx in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if ret:
            # Check brightness / color variation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_val = np.mean(gray)
            std_val = np.std(gray)
            t_sec = f_idx / fps
            print(f"t={t_sec:4.1f}s (f={f_idx:3d}): mean={mean_val:5.1f}, std={std_val:5.1f}")
    cap.release()
