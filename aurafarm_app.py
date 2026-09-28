import os
import sys
import time
import math
import shutil
import threading
import glob
import webbrowser
import cv2
import numpy as np

from face_tracker import AuraFaceTracker
from audio_player import PhonkAudioPlayer
from edit_engine import PhonkEditEngine

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

class ThreadedCamera:
    """Non-blocking high FPS camera capture with DirectShow."""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(src)
            
        self.is_opened = self.cap.isOpened()
        if self.is_opened:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
        self.grabbed, self.frame = False, None
        self.running = self.is_opened
        self.lock = threading.Lock()
        
        if self.is_opened:
            self.thread = threading.Thread(target=self._update, daemon=True)
            self.thread.start()

    def _update(self):
        while self.running:
            grabbed, frame = self.cap.read()
            if grabbed:
                with self.lock:
                    self.grabbed = grabbed
                    self.frame = frame
            else:
                time.sleep(0.01)

    def read(self):
        with self.lock:
            if self.frame is not None:
                return self.grabbed, self.frame.copy()
            return False, None

    def release(self):
        self.running = False
        if self.is_opened:
            self.cap.release()

class CapCutVideoPlayer:
    """Player for exported CapCut MP4 videos."""
    def __init__(self, side_w=280, side_h=360):
        self.side_w = side_w
        self.side_h = side_h
        self.cap = None
        self.fps = 30.0
        self.total_frames = 0
        self.is_loaded = False
        self.duration = 0.0

    def load(self, video_path):
        self.close()
        if not os.path.exists(video_path):
            return False
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            return False
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps
        self.is_loaded = True
        return True

    def get_frame_at(self, elapsed_time):
        if not self.is_loaded or self.cap is None:
            return None
            
        frame_idx = int(elapsed_time * self.fps)
        if frame_idx >= self.total_frames:
            frame_idx = self.total_frames - 1
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if ret and frame is not None:
            return cv2.resize(frame, (self.side_w, self.side_h))
        return None

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_loaded = False

class AuraFarmMasterApp:
    def __init__(self):
        self.window_name = "AuraFarm Master"
        self.width = 1280
        self.height = 720
        
        # Directories
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.captures_dir = os.path.join(self.root_dir, "AuraFarm_Captures")
        self.edits_dir = os.path.join(self.root_dir, "CapCut_Edits_Input")
        self.downloads_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
        self.temp_dir = os.path.join(self.root_dir, "temp_aura_cache")
        
        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(self.edits_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Track start timestamp to watch only NEW downloads
        self.app_start_time = time.time()
        self.played_downloads = set()
        
        # Initialize modules
        self.tracker = AuraFaceTracker()
        self.audio = PhonkAudioPlayer()
        self.edit_engine = PhonkEditEngine(assets_dir=get_resource_path("assets"))
        self.capcut_player = CapCutVideoPlayer(side_w=280, side_h=360)
        
        # Top-Right "AURA HERE" Box Dimensions
        self.side_w = 280
        self.side_h = 360
        self.side_margin_x = 30
        self.side_margin_y = 25
        self.side_x = self.width - self.side_w - self.side_margin_x
        self.side_y = self.side_margin_y
        
        # State Machine: "CAPTURING", "PLAYING_EDIT", "COOLDOWN"
        self.state = "CAPTURING"
        
        # Media Capture settings (Photos + Live Video Buffer, up to 8 slots)
        self.current_template = self.edit_engine.templates[0]
        self.required_snapshots = self.current_template.get("required_slots", 6)
        self.snapshots = []
        self.prepared_snapshots = []
        self.video_buffer = []          # Live face motion video frames buffer
        self.prepared_video_frames = []
        
        self.last_snapshot_time = 0
        self.snapshot_interval = 0.9    # Fast responsive capture interval
        self.shutter_flash_time = 0
        
        # Edit Playback settings
        self.edit_start_time = 0
        self.edit_duration = 0
        self.playing_custom_file = False
        self.current_edit_title = "Brazilian Phonk Greenscreen Edit"
        
        # Cooldown settings
        self.cooldown_start_time = 0
        self.cooldown_duration = 2.0
        
        # Camera Capture
        self.camera = ThreadedCamera(0)
        self.use_virtual_cam = not self.camera.is_opened
        if self.use_virtual_cam:
            print("[Camera] No physical webcam detected. Running in Cyber Demo Mode.")
            
        self.running = True

    def check_for_new_capcut_downloads(self):
        """Check Downloads and CapCut_Edits_Input folder for new exported videos."""
        candidates = []
        for f in glob.glob(os.path.join(self.edits_dir, "*.mp4")):
            mtime = os.path.getmtime(f)
            if mtime > self.app_start_time and f not in self.played_downloads:
                candidates.append((f, mtime))
                
        if os.path.exists(self.downloads_dir):
            for f in glob.glob(os.path.join(self.downloads_dir, "*.mp4")):
                mtime = os.path.getmtime(f)
                if mtime > self.app_start_time and f not in self.played_downloads:
                    candidates.append((f, mtime))
                    
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            new_file = candidates[0][0]
            self.played_downloads.add(new_file)
            return new_file
        return None

    def clean_temp_files(self):
        """Clean up saved photos and temporary edit files after playback."""
        try:
            for d in [self.temp_dir, self.captures_dir]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        fp = os.path.join(d, f)
                        if os.path.isfile(fp):
                            os.remove(fp)
        except Exception:
            pass

    def open_current_capcut_template(self):
        """Open the current CapCut Web template in default browser."""
        url = "https://www.capcut.com/editor-template?create_id=7452270956178935093"
        print(f"[CapCut Browser] Opening {url}...")
        webbrowser.open(url)

    def generate_virtual_frame(self, t):
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        grid_color = (25, 35, 25)
        for gx in range(0, self.width, 40):
            cv2.line(frame, (gx, 0), (gx, self.height), grid_color, 1)
        for gy in range(0, self.height, 40):
            cv2.line(frame, (0, gy), (self.width, gy), grid_color, 1)
            
        cx = int(self.width // 2 + math.sin(t * 1.5) * 80)
        cy = int(self.height // 2 + math.cos(t * 1.2) * 40)
        
        cv2.ellipse(frame, (cx, cy + 180), (160, 100), 0, 0, 360, (70, 90, 80), -1)
        cv2.circle(frame, (cx, cy), 90, (140, 160, 150), -1)
        cv2.circle(frame, (cx - 35, cy - 15), 14, (30, 30, 30), -1)
        cv2.circle(frame, (cx + 35, cy - 15), 14, (30, 30, 30), -1)
        cv2.ellipse(frame, (cx, cy + 35), (35, 12), 0, 0, 180, (40, 40, 40), 4)
        
        cv2.putText(frame, "VIRTUAL WEBCAM MODE", (30, self.height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 150), 1, cv2.LINE_AA)
        return frame

    def draw_side_box(self, canvas, t):
        sx, sy, sw, sh = self.side_x, self.side_y, self.side_w, self.side_h
        
        # 1. Determine Content inside the Side Box
        if self.state == "PLAYING_EDIT":
            elapsed = time.time() - self.edit_start_time
            if self.playing_custom_file and self.capcut_player.is_loaded:
                frame = self.capcut_player.get_frame_at(elapsed)
                side_content = frame if frame is not None else np.zeros((sh, sw, 3), dtype=np.uint8)
            elif self.current_template is not None and (len(self.prepared_snapshots) > 0 or len(self.prepared_video_frames) > 0):
                side_content = self.edit_engine.render_frame(
                    self.current_template,
                    elapsed,
                    self.prepared_snapshots,
                    video_frames=self.prepared_video_frames,
                    target_size=(sw, sh)
                )
            else:
                side_content = np.zeros((sh, sw, 3), dtype=np.uint8)
        else:
            # Standby Animated Radar Screen
            side_content = np.zeros((sh, sw, 3), dtype=np.uint8)
            side_content[:] = (12, 20, 14)
            
            rcx, rcy = sw // 2, sh // 2
            radius = min(sw, sh) // 3
            cv2.circle(side_content, (rcx, rcy), radius, (20, 60, 30), 1)
            cv2.circle(side_content, (rcx, rcy), radius // 2, (20, 60, 30), 1)
            
            angle = t * 3.0
            rx = int(rcx + math.cos(angle) * radius)
            ry = int(rcy + math.sin(angle) * radius)
            cv2.line(side_content, (rcx, rcy), (rx, ry), (0, 255, 100), 2, cv2.LINE_AA)
            
            if self.state == "CAPTURING":
                txt = f"FARMING AURA [{len(self.snapshots)}/{self.required_snapshots}]"
                color = (0, 255, 150)
            elif self.state == "COOLDOWN":
                remain = max(0.0, self.cooldown_duration - (time.time() - self.cooldown_start_time))
                txt = f"NEXT DROP IN {remain:.1f}s..."
                color = (0, 220, 255)
            else:
                txt = "STANDBY // READY"
                color = (0, 255, 150)
                
            cv2.putText(side_content, txt, (sw//2 - 95, sh - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)

        # Place side content onto main canvas
        canvas[sy:sy+sh, sx:sx+sw] = side_content
        
        # 2. Glowing Green Neon Border around the Side Box
        pulse = 0.5 + 0.5 * math.sin(t * 6.0)
        border_col = (20, int(200 + 55 * pulse), 60)
        
        cv2.rectangle(canvas, (sx - 2, sy - 2), (sx + sw + 2, sy + sh + 2), (10, int(120 * pulse + 80), 20), 1)
        cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), border_col, 2)
        
        # Cyber Corner Accents
        c_len = 16
        cv2.line(canvas, (sx, sy), (sx + c_len, sy), (255, 255, 255), 2)
        cv2.line(canvas, (sx, sy), (sx, sy + c_len), (255, 255, 255), 2)
        cv2.line(canvas, (sx + sw, sy), (sx + sw - c_len, sy), (255, 255, 255), 2)
        cv2.line(canvas, (sx + sw, sy), (sx + sw, sy + c_len), (255, 255, 255), 2)
        cv2.line(canvas, (sx, sy + sh), (sx + c_len, sy + sh), (255, 255, 255), 2)
        cv2.line(canvas, (sx, sy + sh), (sx, sy + sh - c_len), (255, 255, 255), 2)
        cv2.line(canvas, (sx + sw, sy + sh), (sx + sw - c_len, sy + sh), (255, 255, 255), 2)
        cv2.line(canvas, (sx + sw, sy + sh), (sx + sw, sy + sh - c_len), (255, 255, 255), 2)

        # 3. "aura here" Neon Subtitle
        label_y = sy + sh + 24
        cv2.rectangle(canvas, (sx + sw//2 - 75, sy + sh + 6), (sx + sw//2 + 75, sy + sh + 32), (10, 30, 15), -1)
        cv2.rectangle(canvas, (sx + sw//2 - 75, sy + sh + 6), (sx + sw//2 + 75, sy + sh + 32), border_col, 1)
        cv2.putText(canvas, "aura here", (sx + sw//2 - 50, label_y + 1),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, border_col, 2, cv2.LINE_AA)

    def draw_top_hud(self, canvas, t):
        cv2.rectangle(canvas, (20, 20), (450, 75), (10, 25, 15), -1)
        cv2.rectangle(canvas, (20, 20), (450, 75), (0, 255, 100), 1)
        
        cv2.putText(canvas, "AURAFARM MASTER", (35, 48),
                    cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 120), 2, cv2.LINE_AA)
        
        status_str = f"STATUS: {self.state}"
        if self.state == "PLAYING_EDIT":
            status_str += f" // {self.current_edit_title}"
        cv2.putText(canvas, status_str, (35, 66),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 220, 255), 1, cv2.LINE_AA)

    def start_edit_playback(self):
        """Play newly exported CapCut video, or run Greenscreen template with user media."""
        new_export = self.check_for_new_capcut_downloads()
        if new_export and self.capcut_player.load(new_export):
            self.playing_custom_file = True
            self.current_edit_title = os.path.basename(new_export)
            self.edit_duration = min(15.0, self.capcut_player.duration)
            self.edit_start_time = time.time()
            print(f"[AuraFarm] Playing downloaded CapCut Export: {new_export}")
            self.state = "PLAYING_EDIT"
            return

        if len(self.snapshots) == 0 and len(self.video_buffer) == 0:
            return
            
        tmpl = self.edit_engine.get_next_template()
        self.current_template = tmpl
        self.required_snapshots = tmpl.get("required_slots", 6)
        self.playing_custom_file = False
        self.current_edit_title = tmpl["name"]
        
        # Prepare high-res snapshots
        self.prepared_snapshots = [cv2.resize(s, (self.side_w, self.side_h)) for s in self.snapshots]
        # Prepare live video buffer
        self.prepared_video_frames = [cv2.resize(f, (self.side_w, self.side_h)) for f in self.video_buffer]
        
        self.edit_duration = tmpl["duration"]
        self.edit_start_time = time.time()
        
        print(f"[AuraFarm] Playing Template: {tmpl['name']} (Slots: {len(self.prepared_snapshots)}, Video frames: {len(self.prepared_video_frames)})...")
        
        if os.path.exists(tmpl["audio"]):
            self.audio.play(tmpl["audio"])
            
        self.state = "PLAYING_EDIT"

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        
        print("[AuraFarm Master] Running. Hotkeys: 'O' = Open CapCut Web Template, 'Q' = Exit.")
        self.last_snapshot_time = time.time()
        
        while self.running:
            now = time.time()
            
            # 1. Grab camera frame
            ret, cam_frame = False, None
            if not self.use_virtual_cam:
                ret, cam_frame = self.camera.read()
                
            if ret and cam_frame is not None:
                frame = cv2.flip(cam_frame, 1)
                frame = cv2.resize(frame, (self.width, self.height))
            else:
                frame = self.generate_virtual_frame(now)

            # 2. Fast face detection
            face_box = self.tracker.detect_face(frame)
            
            # 3. State Machine Processing
            if self.state == "CAPTURING":
                # Record live face video buffer (last ~60 frames = 2 seconds of smooth video motion)
                if face_box is not None:
                    fx, fy, fw, fh = face_box
                    pad_x = int(fw * 0.25)
                    pad_y = int(fh * 0.35)
                    cx1 = max(0, fx - pad_x)
                    cy1 = max(0, fy - pad_y)
                    cx2 = min(self.width, fx + fw + pad_x)
                    cy2 = min(self.height, fy + fh + pad_y)
                    crop_face = frame[cy1:cy2, cx1:cx2].copy()
                    if crop_face.shape[0] > 20 and crop_face.shape[1] > 20:
                        self.video_buffer.append(crop_face)
                        if len(self.video_buffer) > 60:
                            self.video_buffer.pop(0)
                            
                # Capture high-res photo snapshots at interval
                if (now - self.last_snapshot_time) >= self.snapshot_interval:
                    if face_box is not None:
                        fx, fy, fw, fh = face_box
                        pad_x = int(fw * 0.25)
                        pad_y = int(fh * 0.35)
                        crop_x1 = max(0, fx - pad_x)
                        crop_y1 = max(0, fy - pad_y)
                        crop_x2 = min(self.width, fx + fw + pad_x)
                        crop_y2 = min(self.height, fy + fh + pad_y)
                        
                        snap = frame[crop_y1:crop_y2, crop_x1:crop_x2].copy()
                        if snap.shape[0] > 20 and snap.shape[1] > 20:
                            self.snapshots.append(snap)
                            self.last_snapshot_time = now
                            self.shutter_flash_time = now
                            snap_p = os.path.join(self.captures_dir, f"face_snap_{len(self.snapshots)}.jpg")
                            threading.Thread(target=cv2.imwrite, args=(snap_p, snap), daemon=True).start()
                            print(f"[AuraFarm] Captured snapshot {len(self.snapshots)}/{self.required_snapshots}")
                    else:
                        snap = frame.copy()
                        self.snapshots.append(snap)
                        self.last_snapshot_time = now
                        self.shutter_flash_time = now
                
                # When required snapshots collected -> start edit playback
                if len(self.snapshots) >= self.required_snapshots:
                    self.start_edit_playback()
                    
            elif self.state == "PLAYING_EDIT":
                elapsed = now - self.edit_start_time
                if elapsed >= self.edit_duration:
                    print("[AuraFarm] Edit finished. Cleaning up files...")
                    self.audio.stop()
                    self.capcut_player.close()
                    self.clean_temp_files()
                    self.snapshots = []
                    self.prepared_snapshots = []
                    self.video_buffer = []
                    self.prepared_video_frames = []
                    self.state = "COOLDOWN"
                    self.cooldown_start_time = now
                    
            elif self.state == "COOLDOWN":
                if (now - self.cooldown_start_time) >= self.cooldown_duration:
                    self.state = "CAPTURING"
                    self.last_snapshot_time = now

            # 4. Render Shimmering Green Face Tracking Box
            is_capt = (self.state == "CAPTURING")
            prog = (len(self.snapshots) / max(1, self.required_snapshots)) if is_capt else 0.0
            frame = self.tracker.draw_aura_box(frame, face_box, capture_progress=prog, is_capturing=is_capt)
            
            # 5. Shutter Flash Effect
            if (now - self.shutter_flash_time) < 0.12:
                flash_alpha = 1.0 - ((now - self.shutter_flash_time) / 0.12)
                flash_layer = np.full_like(frame, int(150 * flash_alpha))
                frame = cv2.add(frame, flash_layer)

            # 6. Render Side 'AURA HERE' Box
            self.draw_side_box(frame, now)
            
            # 7. Render Top HUD
            self.draw_top_hud(frame, now)
            
            # Display frame
            cv2.imshow(self.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('o') or key == ord('O'):
                self.open_current_capcut_template()
                
        self.cleanup()

    def cleanup(self):
        print("[AuraFarm Master] Shutting down...")
        self.audio.stop()
        self.capcut_player.close()
        self.edit_engine.close()
        self.clean_temp_files()
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = AuraFarmMasterApp()
    app.run()
