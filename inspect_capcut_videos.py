import os
import cv2
import wave
import subprocess

video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
os.makedirs(audio_dir, exist_ok=True)

for vid_name in os.listdir(video_dir):
    if vid_name.endswith(".mp4"):
        vid_path = os.path.join(video_dir, vid_name)
        base = os.path.splitext(vid_name)[0]
        
        # Check video properties
        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = count / fps
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        print(f"[{base}] Duration: {duration:.2f}s, FPS: {fps}, Res: {w}x{h}, Frames: {count}")
