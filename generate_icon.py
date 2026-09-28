import os
from PIL import Image, ImageDraw

def generate_icon(path):
    img = Image.new("RGBA", (256, 256), (10, 20, 15, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer neon green circle
    draw.ellipse([16, 16, 240, 240], outline=(0, 255, 120, 255), width=8)
    draw.ellipse([32, 32, 224, 224], fill=(15, 30, 20, 255), outline=(0, 200, 80, 255), width=4)
    
    # Sigma Cranium
    draw.ellipse([80, 55, 176, 150], fill=(230, 240, 230, 255), outline=(0, 255, 150, 255), width=4)
    # Jaw
    draw.polygon([(90, 130), (105, 195), (151, 195), (166, 130)], fill=(230, 240, 230, 255), outline=(0, 255, 150, 255))
    # Glowing eyes
    draw.ellipse([98, 100, 120, 120], fill=(255, 30, 30, 255))
    draw.ellipse([136, 100, 158, 120], fill=(255, 30, 30, 255))
    # Nose
    draw.polygon([(128, 130), (120, 145), (136, 145)], fill=(10, 10, 10, 255))
    
    img.save(path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Generated {path}")

if __name__ == "__main__":
    generate_icon(os.path.join(os.path.dirname(__file__), "assets", "icon.ico"))
