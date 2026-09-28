import os
import sys
import shutil
import cv2
import subprocess

def build():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(root_dir, "assets")
    
    # Copy haarcascade directly into assets to guarantee standalone portability
    cascade_src = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade_dst = os.path.join(assets_dir, 'haarcascade_frontalface_default.xml')
    if os.path.exists(cascade_src):
        shutil.copyfile(cascade_src, cascade_dst)
        print(f"Copied cascade to {cascade_dst}")

    icon_path = os.path.join(assets_dir, "icon.ico")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=AuraFarmMaster",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};assets",
        os.path.join(root_dir, "aurafarm_app.py")
    ]
    
    print("Running PyInstaller build:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=root_dir)
    if res.returncode == 0:
        print("\n==========================================")
        print("SUCCESS! AuraFarm Master EXE built successfully.")
        print(f"Executable folder: {os.path.join(root_dir, 'dist', 'AuraFarmMaster')}")
        print(f"Executable file: {os.path.join(root_dir, 'dist', 'AuraFarmMaster', 'AuraFarmMaster.exe')}")
        print("==========================================\n")
    else:
        print("Build failed with code", res.returncode)

if __name__ == "__main__":
    build()
