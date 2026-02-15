import os
from PIL import Image

# 配置
INPUT_DIR = "bing-wallpaper"
OUTPUT_DIR = "bing-wallpaper-compressed"
TARGET_WIDTH = 2560  # 或 1920
QUALITY = 85         # WebP 质量 (70-90)

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0] + ".webp")

    with Image.open(input_path) as img:
        # 自动旋转（处理手机拍摄的 EXIF）
        img = img.convert("RGB")  # WebP 不支持 RGBA（除非带透明）
        
        # 按比例缩放
        img.thumbnail((TARGET_WIDTH, TARGET_WIDTH), Image.LANCZOS)
        
        # 保存为 WebP
        img.save(output_path, "WEBP", quality=QUALITY, method=6)
        print(f"✅ {filename} → {output_path} ({img.size})")
