import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_skull_overlay(path, size=(500, 500)):
    # Create stylized sigma / phonk skull with glowing eyes
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    
    # Cranium / head outline
    head_box = [cx - 140, cy - 180, cx + 140, cy + 50]
    draw.ellipse(head_box, fill=(240, 240, 240, 230), outline=(20, 255, 120, 255), width=6)
    
    # Jaw / cheekbones
    jaw_points = [
        (cx - 120, cy + 20),
        (cx - 80, cy + 150),
        (cx - 50, cy + 180),
        (cx + 50, cy + 180),
        (cx + 80, cy + 150),
        (cx + 120, cy + 20),
    ]
    draw.polygon(jaw_points, fill=(240, 240, 240, 230), outline=(20, 255, 120, 255))
    
    # Eye sockets (dark angled aggressive eyes)
    left_eye = [(cx - 90, cy - 40), (cx - 30, cy - 20), (cx - 40, cy + 30), (cx - 85, cy + 20)]
    right_eye = [(cx + 90, cy - 40), (cx + 30, cy - 20), (cx + 40, cy + 30), (cx + 85, cy + 20)]
    draw.polygon(left_eye, fill=(10, 10, 10, 255))
    draw.polygon(right_eye, fill=(10, 10, 10, 255))
    
    # Glowing red / cyan laser pupils
    draw.ellipse([cx - 65, cy - 15, cx - 45, cy + 5], fill=(255, 30, 30, 255))
    draw.ellipse([cx + 45, cy - 15, cx + 65, cy + 5], fill=(255, 30, 30, 255))
    
    # Nose cavity (inverted heart/triangle)
    nose = [(cx, cy + 20), (cx - 20, cy + 60), (cx + 20, cy + 60)]
    draw.polygon(nose, fill=(10, 10, 10, 255))
    
    # Teeth / mouth slits
    for tx in range(cx - 60, cx + 61, 20):
        draw.line([(tx, cy + 110), (tx, cy + 160)], fill=(10, 10, 10, 255), width=5)
    draw.line([(cx - 70, cy + 135), (cx + 70, cy + 135)], fill=(10, 10, 10, 255), width=5)
    
    # Add subtle glow
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(path)
    print(f"Saved {path}")

def create_aura_particles(path, size=(600, 600)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    
    # Speedlines / aura shockwave rays
    for i in range(36):
        angle = i * (2 * math.pi / 36)
        r1 = np.random.uniform(80, 140)
        r2 = np.random.uniform(220, 290)
        x1 = cx + math.cos(angle) * r1
        y1 = cy + math.sin(angle) * r1
        x2 = cx + math.cos(angle) * r2
        y2 = cy + math.sin(angle) * r2
        color = (0, 255, 150, int(np.random.uniform(120, 230)))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=int(np.random.uniform(2, 6)))
        
    img = img.filter(ImageFilter.GaussianBlur(1))
    img.save(path)
    print(f"Saved {path}")

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
    os.makedirs(img_dir, exist_ok=True)
    create_skull_overlay(os.path.join(img_dir, "sigma_skull.png"))
    create_aura_particles(os.path.join(img_dir, "aura_burst.png"))
