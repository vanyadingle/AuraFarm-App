import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def generate_capcut_skull(path, size=(400, 400)):
    # Create the authentic 3D CapCut / Apple style Skull with glowing eyes
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    
    # 1. Outer Glow / Aura
    for r in range(160, 120, -5):
        alpha = int((160 - r) * 3)
        draw.ellipse([cx - r, cy - r + 10, cx + r, cy + r - 10], fill=(0, 255, 120, alpha))
        
    # 2. Main Cranium (3D Bone gradient)
    # Head dome
    head_box = [cx - 130, cy - 140, cx + 130, cy + 50]
    draw.ellipse(head_box, fill=(245, 245, 250, 255), outline=(180, 185, 195, 255), width=4)
    
    # Cheekbones & Temporal bones
    draw.ellipse([cx - 140, cy - 40, cx - 70, cy + 40], fill=(240, 240, 245, 255))
    draw.ellipse([cx + 70, cy - 40, cx + 140, cy + 40], fill=(240, 240, 245, 255))
    
    # Upper Jaw
    jaw_poly = [
        (cx - 95, cy + 30),
        (cx - 75, cy + 120),
        (cx + 75, cy + 120),
        (cx + 95, cy + 30)
    ]
    draw.polygon(jaw_poly, fill=(235, 235, 240, 255), outline=(180, 185, 195, 255))
    
    # 3. Eye Sockets (Deep dark cavities with angle)
    left_eye = [(cx - 85, cy - 35), (cx - 25, cy - 15), (cx - 35, cy + 35), (cx - 80, cy + 25)]
    right_eye = [(cx + 85, cy - 35), (cx + 25, cy - 15), (cx + 35, cy + 35), (cx + 80, cy + 25)]
    draw.polygon(left_eye, fill=(15, 15, 20, 255))
    draw.polygon(right_eye, fill=(15, 15, 20, 255))
    
    # Glowing Laser Pupils inside Eye Sockets (CapCut phonk red / cyan laser flare)
    draw.ellipse([cx - 62, cy - 10, cx - 42, cy + 10], fill=(255, 40, 40, 255))
    draw.ellipse([cx + 42, cy - 10, cx + 62, cy + 10], fill=(255, 40, 40, 255))
    draw.ellipse([cx - 56, cy - 4, cx - 48, cy + 4], fill=(255, 255, 255, 255))
    draw.ellipse([cx + 48, cy - 4, cx + 56, cy + 4], fill=(255, 255, 255, 255))
    
    # 4. Nasal Cavity (Inverted heart / triangle)
    nose = [(cx, cy + 15), (cx - 18, cy + 50), (cx + 18, cy + 50)]
    draw.polygon(nose, fill=(15, 15, 20, 255))
    
    # 5. Teeth (Upper & lower rows)
    teeth_top_y = cy + 70
    teeth_bot_y = cy + 115
    for tx in range(cx - 60, cx + 61, 20):
        # Tooth outline
        draw.rectangle([tx - 7, teeth_top_y, tx + 7, teeth_bot_y], fill=(250, 250, 255, 255), outline=(100, 100, 110, 255), width=2)
    # Center separation line between jaws
    draw.line([(cx - 70, cy + 92), (cx + 70, cy + 92)], fill=(40, 40, 45, 255), width=3)
    
    # Smooth anti-aliasing
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(path)
    print(f"Generated CapCut Skull asset: {path}")

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
    os.makedirs(img_dir, exist_ok=True)
    generate_capcut_skull(os.path.join(img_dir, "capcut_skull.png"))
