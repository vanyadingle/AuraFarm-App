import os
import cv2
import numpy as np

def test_compositor():
    video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "test_composites")
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a dummy user photo with distinct colors/text
    user_photo = np.zeros((480, 480, 3), dtype=np.uint8)
    user_photo[:] = (180, 140, 90) # Skin/face tone
    cv2.circle(user_photo, (240, 240), 160, (220, 180, 140), -1)
    cv2.circle(user_photo, (180, 200), 20, (30, 30, 30), -1)
    cv2.circle(user_photo, (300, 200), 20, (30, 30, 30), -1)
    cv2.ellipse(user_photo, (240, 290), (60, 25), 0, 0, 180, (20, 20, 180), -1)
    cv2.putText(user_photo, "USER FACE", (140, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    
    for i in range(1, 5):
        vid_path = os.path.join(video_dir, f"template_{i}.mp4")
        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        # Grab frame at 2.0s
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(2.0 * fps))
        ret, capcut_frame = cap.read()
        cap.release()
        
        if ret:
            H, W = capcut_frame.shape[:2]
            user_resized = cv2.resize(user_photo, (W, H))
            
            # Composite method:
            # The CapCut video has bright overlays (skulls, text, neon rays, flashes) and dark areas.
            # When we use high-fidelity Screen + Alpha overlay:
            # We preserve 100% of CapCut's overlays and effects on top of user's photo
            
            # Extract brightness/luminance of CapCut effects
            gray_capcut = cv2.cvtColor(capcut_frame, cv2.COLOR_BGR2GRAY)
            
            # Overlay user photo, and composite CapCut template effects on top
            # Formula: Blended = User_Photo * (1 - effect_alpha) + Capcut_Effects
            norm_effects = capcut_frame.astype(np.float32) / 255.0
            norm_user = user_resized.astype(np.float32) / 255.0
            
            # Screen blending mode (Photoshop / CapCut standard for lighting/effects overlays)
            # Screen: 1 - (1 - A) * (1 - B)
            screen_blend = 1.0 - (1.0 - norm_user * 0.9) * (1.0 - norm_effects)
            result = np.clip(screen_blend * 255.0, 0, 255).astype(np.uint8)
            
            out_p = os.path.join(out_dir, f"composite_tmpl_{i}.jpg")
            cv2.imwrite(out_p, result)
            print(f"Saved {out_p}")

if __name__ == "__main__":
    test_compositor()
