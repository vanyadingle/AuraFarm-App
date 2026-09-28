import os
import sys
import cv2
import numpy as np
import time
import math

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class AuraFaceTracker:
    def __init__(self):
        self.detector = None
        self.detect_size = (320, 240)
        
        # Load OpenCV YuNet ONNX face detector
        model_path = get_resource_path(os.path.join("assets", "face_detection_yunet.onnx"))
        if os.path.exists(model_path):
            try:
                self.detector = cv2.FaceDetectorYN_create(
                    model=model_path,
                    config="",
                    input_size=self.detect_size,
                    score_threshold=0.55,
                    nms_threshold=0.3,
                    top_k=2000
                )
                print("[FaceTracker] Fast YuNet face detector initialized.")
            except Exception as e:
                print(f"[FaceTracker] Warning initializing YuNet: {e}")
                self.detector = None
        
        # Smoothed bounding box state
        self.smooth_box = None
        self.alpha_smooth = 0.4 # Responsive smoothing
        self.last_detection_time = 0
        self.frame_count = 0

    def detect_face(self, frame):
        """Ultra-fast detection using scaled frame (1-2ms execution)."""
        H, W = frame.shape[:2]
        now = time.time()
        self.frame_count += 1
        
        if self.detector is not None:
            try:
                # Downscale for lightning fast inference
                small_w, small_h = 320, int(320 * (H / W))
                if self.detect_size != (small_w, small_h):
                    self.detect_size = (small_w, small_h)
                    self.detector.setInputSize(self.detect_size)
                    
                small_frame = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_NEAREST)
                _, faces = self.detector.detect(small_frame)
                
                if faces is not None and len(faces) > 0:
                    scale_x = W / float(small_w)
                    scale_y = H / float(small_h)
                    
                    # Sort by area
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    best = faces[0]
                    
                    bx = int(best[0] * scale_x)
                    by = int(best[1] * scale_y)
                    bw = int(best[2] * scale_x)
                    bh = int(best[3] * scale_y)
                    
                    target = np.array([bx, by, bw, bh], dtype=np.float32)
                    if self.smooth_box is None:
                        self.smooth_box = target
                    else:
                        self.smooth_box = (1 - self.alpha_smooth) * self.smooth_box + self.alpha_smooth * target
                        
                    self.last_detection_time = now
                    return tuple(self.smooth_box.astype(int))
            except Exception:
                pass
                
        # Keep smooth box for 0.6s if lost
        if self.smooth_box is not None and (now - self.last_detection_time) < 0.6:
            return tuple(self.smooth_box.astype(int))
            
        # Fallback centered region
        if self.detector is None:
            cw, ch = int(W * 0.35), int(H * 0.45)
            cx, cy = (W - cw) // 2, (H - ch) // 3
            return (cx, cy, cw, ch)
            
        return None

    def draw_aura_box(self, frame, face_box, capture_progress=0.0, is_capturing=True):
        """Draw thin, glowing, shimmering neon green cyber box with HUD."""
        if face_box is None:
            return frame
        
        x, y, w, h = face_box
        H, W = frame.shape[:2]
        
        # Clamp bounds
        x = max(0, min(x, W - 1))
        y = max(0, min(y, H - 1))
        w = min(w, W - x)
        h = min(h, H - y)
        if w <= 10 or h <= 10:
            return frame

        t = time.time()
        
        # Shimmering / pulsing intensity: oscillate between 190 and 255
        pulse = 0.5 + 0.5 * math.sin(t * 8.0)
        green_val = int(200 + 55 * pulse)
        border_color = (30, green_val, 50)      # BGR
        glow_color = (10, int(green_val * 0.7), 20)
        
        # 1. Subtle glowing outer border
        glow_pad = int(4 + 2 * pulse)
        gx1, gy1 = max(0, x - glow_pad), max(0, y - glow_pad)
        gx2, gy2 = min(W, x + w + glow_pad), min(H, y + h + glow_pad)
        cv2.rectangle(frame, (gx1, gy1), (gx2, gy2), glow_color, 1, cv2.LINE_AA)
        
        # 2. Main thin bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), border_color, 1, cv2.LINE_AA)
        
        # 3. Cyber Corner Brackets [ ]
        corner_len = min(24, w // 4, h // 4)
        thickness = 2
        # Top-Left
        cv2.line(frame, (x, y), (x + corner_len, y), border_color, thickness, cv2.LINE_AA)
        cv2.line(frame, (x, y), (x, y + corner_len), border_color, thickness, cv2.LINE_AA)
        # Top-Right
        cv2.line(frame, (x + w, y), (x + w - corner_len, y), border_color, thickness, cv2.LINE_AA)
        cv2.line(frame, (x + w, y), (x + w, y + corner_len), border_color, thickness, cv2.LINE_AA)
        # Bottom-Left
        cv2.line(frame, (x, y + h), (x + corner_len, y + h), border_color, thickness, cv2.LINE_AA)
        cv2.line(frame, (x, y + h), (x, y + h - corner_len), border_color, thickness, cv2.LINE_AA)
        # Bottom-Right
        cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), border_color, thickness, cv2.LINE_AA)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), border_color, thickness, cv2.LINE_AA)

        # 4. Animated Scanning Line
        scan_y = int(y + ((t * 1.5) % 1.0) * h)
        if y <= scan_y <= y + h:
            scan_color = (50, int(green_val * 0.9), 60)
            cv2.line(frame, (x + 4, scan_y), (x + w - 4, scan_y), scan_color, 1, cv2.LINE_AA)

        # 5. Cyberpunk HUD Text
        label_text = "AURA TARGET: LOCKED" if is_capturing else "EDIT SYNC IN PROGRESS"
        cv2.putText(frame, label_text, (x, max(15, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, border_color, 1, cv2.LINE_AA)
        
        # Progress Bar below face box if capturing
        if is_capturing and capture_progress > 0:
            bar_w = int(w * capture_progress)
            cv2.rectangle(frame, (x, y + h + 6), (x + w, y + h + 10), (20, 50, 20), -1)
            cv2.rectangle(frame, (x, y + h + 6), (x + bar_w, y + h + 10), border_color, -1)
            cv2.putText(frame, f"FARMING AURA: {int(capture_progress*100)}%", (x, y + h + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, border_color, 1, cv2.LINE_AA)

        return frame
