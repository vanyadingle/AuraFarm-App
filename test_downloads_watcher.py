import os
import glob
import time

user_profile = os.environ.get("USERPROFILE", "")
downloads_dir = os.path.join(user_profile, "Downloads")
print("Watching Downloads dir:", downloads_dir, "exists:", os.path.exists(downloads_dir))

# Find recent MP4 files in Downloads
mp4s = glob.glob(os.path.join(downloads_dir, "*.mp4"))
print(f"Found {len(mp4s)} MP4s in Downloads")
for m in sorted(mp4s, key=os.path.getmtime, reverse=True)[:3]:
    print(" -", os.path.basename(m), time.ctime(os.path.getmtime(m)))
