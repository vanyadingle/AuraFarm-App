import os
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print("FFmpeg executable:", ffmpeg_exe)

video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
os.makedirs(audio_dir, exist_ok=True)

for i in range(1, 5):
    vid_file = os.path.join(video_dir, f"template_{i}.mp4")
    wav_file = os.path.join(audio_dir, f"capcut_audio_{i}.wav")
    
    if os.path.exists(vid_file):
        cmd = [
            ffmpeg_exe, "-y", "-i", vid_file,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            wav_file
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(wav_file):
            print(f"Extracted original CapCut audio: {wav_file} ({os.path.getsize(wav_file)} bytes)")
        else:
            print(f"Error extracting audio for template_{i}: {res.stderr.decode('utf-8', errors='ignore')}")
