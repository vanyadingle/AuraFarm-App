import os
import cv2
import numpy as np
import math

class PhonkEditEngine:
    """Dynamic Phonk Edit & Chroma Key Compositor Engine."""
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.assets_dir = assets_dir
        self.audio_dir = os.path.join(assets_dir, "audio")
        self.skulls_dir = os.path.join(assets_dir, "skulls")
        self.greenscreen_dir = os.path.join(assets_dir, "greenscreen_templates")
        
        # Load user-provided skulls
        self.skulls = {}
        skull_files = {
            "smoke": "skull_smoke.png",
            "sigma": "skull_sigma.png",
            "real": "skull_real.png",
            "3d": "skull_3d.png"
        }
        for key, fname in skull_files.items():
            p = os.path.join(self.skulls_dir, fname)
            if os.path.exists(p):
                img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
                if img is not None and len(img.shape) == 3 and img.shape[2] == 4:
                    self.skulls[key] = img
                    
        self.skull_keys = list(self.skulls.keys()) if self.skulls else []
        
        # Video capture cache for green screen templates
        self.video_caps = {}
        
        # Define Template Library (Chroma Key + Dynamic User Media)
        self.templates = [
            {
                "id": 1,
                "name": "Greenscreen Brazilian Phonk 1",
                "type": "greenscreen",
                "video": os.path.join(self.greenscreen_dir, "template_1.mp4"),
                "audio": os.path.join(self.audio_dir, "template_1.wav"),
                "duration": 10.5,
                "required_slots": 6,
                "beat_dur": 0.435
            },
            {
                "id": 2,
                "name": "Greenscreen Brazilian Phonk 2",
                "type": "greenscreen",
                "video": os.path.join(self.greenscreen_dir, "template_2.mp4"),
                "audio": os.path.join(self.audio_dir, "template_2.wav"),
                "duration": 11.0,
                "required_slots": 8,
                "beat_dur": 0.42
            },
            {
                "id": 3,
                "name": "Greenscreen Skull Freezeframe 3",
                "type": "greenscreen",
                "video": os.path.join(self.greenscreen_dir, "template_3.mp4"),
                "audio": os.path.join(self.audio_dir, "template_3.wav"),
                "duration": 9.5,
                "required_slots": 4,
                "beat_dur": 0.45
            },
            {
                "id": 4,
                "name": "Greenscreen Funk Sigilo 5",
                "type": "greenscreen",
                "video": os.path.join(self.greenscreen_dir, "template_5.mp4"),
                "audio": os.path.join(self.audio_dir, "template_5.wav"),
                "duration": 10.0,
                "required_slots": 6,
                "beat_dur": 0.422
            },
            {
                "id": 5,
                "name": "Greenscreen Phonk Master 6",
                "type": "greenscreen",
                "video": os.path.join(self.greenscreen_dir, "template_6.mp4"),
                "audio": os.path.join(self.audio_dir, "template_6.wav"),
                "duration": 11.5,
                "required_slots": 8,
                "beat_dur": 0.40
            },
            {
                "id": 6,
                "name": "Multi-Skull 4X Trend Mix",
                "type": "procedural",
                "audio": os.path.join(self.audio_dir, "capcut_audio_4.wav"),
                "duration": 8.5,
                "required_slots": 6,
                "beat_dur": 0.422
            }
        ]
        self.current_template_idx = 0

    def get_next_template(self):
        tmpl = self.templates[self.current_template_idx]
        self.current_template_idx = (self.current_template_idx + 1) % len(self.templates)
        return tmpl

    def get_template_video_frame(self, video_path, elapsed_time, target_size=(280, 360)):
        """Fast thread-safe random access frame reader for template videos."""
        if not os.path.exists(video_path):
            return None
            
        if video_path not in self.video_caps:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_caps[video_path] = {"cap": cap, "fps": fps, "total": total}
            
        vinfo = self.video_caps[video_path]
        cap = vinfo["cap"]
        fps = vinfo["fps"]
        total = vinfo["total"]
        
        frame_idx = int(elapsed_time * fps)
        if frame_idx >= total:
            frame_idx = total - 1
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret and frame is not None:
            return cv2.resize(frame, target_size)
        return None

    @staticmethod
    def apply_zoom_crop(img, zoom_factor=1.1, offset_center=(0, 0)):
        H, W = img.shape[:2]
        if zoom_factor <= 1.001:
            return img
        
        new_w = max(10, int(W / zoom_factor))
        new_h = max(10, int(H / zoom_factor))
        
        cx = W // 2 + offset_center[0]
        cy = H // 2 + offset_center[1]
        
        x1 = max(0, min(W - new_w, cx - new_w // 2))
        y1 = max(0, min(H - new_h, cy - new_h // 2))
        x2 = min(W, x1 + new_w)
        y2 = min(H, y1 + new_h)
        
        cropped = img[y1:y2, x1:x2]
        return cv2.resize(cropped, (W, H), interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def apply_rgb_split(img, offset_x=4, offset_y=0):
        if offset_x == 0 and offset_y == 0:
            return img
        H, W = img.shape[:2]
        b, g, r = cv2.split(img)
        M_r = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        M_b = np.float32([[1, 0, -offset_x], [0, 1, -offset_y]])
        r_shifted = cv2.warpAffine(r, M_r, (W, H), borderMode=cv2.BORDER_REFLECT)
        b_shifted = cv2.warpAffine(b, M_b, (W, H), borderMode=cv2.BORDER_REFLECT)
        return cv2.merge([b_shifted, g, r_shifted])

    def overlay_skull(self, canvas, skull_key, scale=1.0, offset_y=0, alpha_mult=1.0):
        if skull_key not in self.skulls:
            return canvas
            
        sk = self.skulls[skull_key]
        H_c, W_c = canvas.shape[:2]
        H_s, W_s = sk.shape[:2]
        
        base_w = int(W_c * 0.65 * scale)
        if base_w < 10:
            return canvas
            
        base_h = int(H_s * (base_w / W_s))
        if base_h > H_c:
            base_h = int(H_c * 0.85)
            base_w = int(W_s * (base_h / H_s))
            
        sk_res = cv2.resize(sk, (base_w, base_h), interpolation=cv2.INTER_AREA)
        
        x1 = (W_c - base_w) // 2
        y1 = (H_c - base_h) // 2 + offset_y
        x2 = x1 + base_w
        y2 = y1 + base_h
        
        cx1, cy1 = max(0, x1), max(0, y1)
        cx2, cy2 = min(W_c, x2), min(H_c, y2)
        
        if cx1 >= cx2 or cy1 >= cy2:
            return canvas
            
        sx1 = cx1 - x1
        sy1 = cy1 - y1
        sx2 = sx1 + (cx2 - cx1)
        sy2 = sy1 + (cy2 - cy1)
        
        sk_crop = sk_res[sy1:sy2, sx1:sx2]
        b, g, r, a = cv2.split(sk_crop)
        
        alpha = (a.astype(float) / 255.0 * alpha_mult)[:, :, np.newaxis]
        sk_rgb = cv2.merge([b, g, r]).astype(float)
        
        roi = canvas[cy1:cy2, cx1:cx2].astype(float)
        blended = (sk_rgb * alpha + roi * (1.0 - alpha)).astype(np.uint8)
        canvas[cy1:cy2, cx1:cx2] = blended
        return canvas

    def render_chroma_key_frame(self, tmpl, elapsed, snapshots, video_frames=None, target_size=(280, 360)):
        """Composite user media (video buffer + photos) under the green screen template."""
        tw, th = target_size
        
        # 1. Get current template frame
        tmpl_frame = self.get_template_video_frame(tmpl["video"], elapsed, target_size=target_size)
        if tmpl_frame is None:
            tmpl_frame = np.zeros((th, tw, 3), dtype=np.uint8)
            
        # 2. Select background user media (video clip or photo)
        beat_dur = tmpl.get("beat_dur", 0.435)
        num_snaps = max(1, len(snapshots))
        slot_idx = int(elapsed / beat_dur) % num_snaps
        
        # Beat animation physics
        beat_pos = (elapsed % beat_dur) / beat_dur
        punch = math.exp(-beat_pos * 5.0)
        
        # Determine whether to use moving live video frame or photo
        if video_frames and len(video_frames) > 0 and (int(elapsed / 2.0) % 2 == 0):
            # Play live moving video frame buffer
            vf_idx = int(elapsed * 30.0) % len(video_frames)
            user_base = video_frames[vf_idx]
            if user_base.shape[:2] != (th, tw):
                user_base = cv2.resize(user_base, (tw, th))
        else:
            # Use high-res captured photo
            user_base = snapshots[slot_idx]
            if user_base.shape[:2] != (th, tw):
                user_base = cv2.resize(user_base, (tw, th))
                
        # Subtle cinematic contrast & beat zoom on background
        user_bg = (user_base.copy().astype(float) * 0.70).astype(np.uint8)
        zoom = 1.04 + 0.12 * punch
        user_bg = self.apply_zoom_crop(user_bg, zoom)
        
        if punch > 0.4:
            user_bg = self.apply_rgb_split(user_bg, offset_x=int(punch * 6))
            
        # 3. Chroma Key Segmentation (Green screen detection & alpha blending)
        hsv = cv2.cvtColor(tmpl_frame, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, np.array([35, 60, 60]), np.array([85, 255, 255]))
        
        # Calculate green coverage percentage
        green_pct = (green_mask > 0).mean()
        
        if green_pct > 0.05:
            # Foreground mask: 0 where green (show user background), 1 where foreground
            fg_alpha = (cv2.bitwise_not(green_mask).astype(float) / 255.0)
            fg_alpha = cv2.GaussianBlur(fg_alpha, (3, 3), 0)[:, :, np.newaxis]
            
            # De-spill green fringe on template foreground
            b, g, r = cv2.split(tmpl_frame)
            max_rb = np.maximum(r, b)
            g_clean = np.where(g > max_rb, max_rb, g)
            fg_clean = cv2.merge([b, g_clean, r]).astype(float)
            
            composite = (fg_clean * fg_alpha + user_bg.astype(float) * (1.0 - fg_alpha)).astype(np.uint8)
            return composite
        else:
            # Fullscreen template animation / transition
            return tmpl_frame

    def render_procedural_frame(self, tmpl, elapsed, snapshots, video_frames=None, target_size=(280, 360)):
        """Dynamic multi-skull Brazilian Phonk procedural renderer (up to 8 slots)."""
        tw, th = target_size
        n = max(1, len(snapshots))
        beat_dur = tmpl.get("beat_dur", 0.422)
        slot_idx = int(elapsed / beat_dur) % n
        
        curr_media = snapshots[slot_idx]
        if video_frames and len(video_frames) > 0 and (int(elapsed / 1.5) % 2 == 1):
            vf_idx = int(elapsed * 30.0) % len(video_frames)
            curr_media = video_frames[vf_idx]
            
        if curr_media.shape[:2] != (th, tw):
            curr_media = cv2.resize(curr_media, (tw, th))
            
        beat_pos = (elapsed % beat_dur) / beat_dur
        punch = math.exp(-beat_pos * 6.0)
        
        frame = (curr_media.copy().astype(float) * 0.48).astype(np.uint8)
        zoom = 1.04 + 0.18 * punch
        frame = self.apply_zoom_crop(frame, zoom)
        
        # Cycle across all 4 user skulls
        skull_order = ["3d", "smoke", "real", "sigma"]
        beat_idx = int(elapsed / beat_dur) % len(skull_order)
        skull_name = skull_order[beat_idx]
        
        skull_scale = 1.0 + 0.26 * punch
        frame = self.overlay_skull(frame, skull_name, scale=skull_scale)
        
        if punch > 0.35:
            frame = self.apply_rgb_split(frame, offset_x=int(punch * 7))
            
        return frame

    def render_frame(self, template, elapsed_time, snapshots, video_frames=None, target_size=(280, 360)):
        if not snapshots and not video_frames:
            return np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
            
        if template.get("type") == "greenscreen":
            return self.render_chroma_key_frame(template, elapsed_time, snapshots, video_frames, target_size)
        else:
            return self.render_procedural_frame(template, elapsed_time, snapshots, video_frames, target_size)

    def close(self):
        for k, v in self.video_caps.items():
            try:
                v["cap"].release()
            except Exception:
                pass
        self.video_caps.clear()
