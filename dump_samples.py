import os
import cv2

video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "samples")
os.makedirs(sample_dir, exist_ok=True)

for i in range(1, 5):
    vid_path = os.path.join(video_dir, f"template_{i}.mp4")
    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Save frames at 0.5s, 1.5s, 2.5s, 3.5s
    for t_sec in [0.5, 1.5, 2.5, 3.5, 5.0]:
        f_idx = int(t_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if ret:
            out_p = os.path.join(sample_dir, f"tmpl_{i}_t{int(t_sec*10)}.jpg")
            cv2.imwrite(out_p, frame)
            print(f"Saved {out_p} ({w}x{h})")
    cap.release()
