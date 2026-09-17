import os
import math
from PIL import Image, ImageDraw
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ref_path = os.path.join(project_root, 'preview', 'brick_dev_perfect_cutout.png')
tex_dir = os.path.join(project_root, 'assets', 'mascots', 'brick_dev', 'textures')
os.makedirs(tex_dir, exist_ok=True)

ref_img = Image.open(ref_path).convert('RGBA')
ref_arr = np.array(ref_img)

print("=== 1. Building High-Res Head Cylindrical Texture ===")
# Head dimensions in reference:
# Center x0 = 512, radius r_head = 227
# Chin is at y = 478
# Forehead top is at y = 135
x0 = 512.0
r_head = 227.0
y_chin = 478.0
y_top = 135.0

tex_w = 2048
tex_h = 1024

# Base skin tone sampled from clean cheek of Brick Dev:
base_skin = np.array([154, 87, 46, 255], dtype=np.uint8)

head_tex = np.zeros((tex_h, tex_w, 4), dtype=np.uint8)
head_tex[:, :] = base_skin

# Vertical range on cylinder: v from 0.18 (chin) to 0.84 (top)
v_chin = 0.18
v_top = 0.84

for ty in range(tex_h):
    v = 1.0 - (ty / (tex_h - 1))
    if v < v_chin or v > v_top:
        continue
    
    frac_y = (v - v_chin) / (v_top - v_chin)
    ref_y = int(round(y_chin - frac_y * (y_chin - y_top)))
    if ref_y < 0 or ref_y >= 1024:
        continue

    for tx in range(tex_w):
        u = tx / (tex_w - 1)
        theta = (u - 0.5) * 2.0 * math.pi
        
        max_theta = 60.0 * math.pi / 180.0
        if abs(theta) > max_theta:
            continue
        
        sin_t = math.sin(theta)
        ref_x = int(round(x0 + r_head * sin_t))
        if ref_x < 0 or ref_x >= 1024:
            continue
        
        src_pixel = ref_arr[ref_y, ref_x]
        if src_pixel[3] < 30:
            continue
        
        deg = abs(theta) * 180.0 / math.pi
        # Feather lateral edges into base skin
        if deg > 42.0:
            weight = (max_theta * 180.0 / math.pi - deg) / (max_theta * 180.0 / math.pi - 42.0)
            weight = max(0.0, min(1.0, weight))
            blended = src_pixel[:3].astype(float) * weight + base_skin[:3].astype(float) * (1.0 - weight)
            head_tex[ty, tx, :3] = blended.astype(np.uint8)
            head_tex[ty, tx, 3] = 255
        else:
            head_tex[ty, tx] = src_pixel

head_img = Image.fromarray(head_tex, 'RGBA')
head_path = os.path.join(tex_dir, 'brick_dev_face_2k.png')
head_img.save(head_path)
print(f"Saved: {head_path}")


print("=== 2. Building Clean Unwarped Torso Polo Texture ===")
# Unwarp the torso trapezoid from the reference image into a clean 1024x1024 texture
y_top_torso = 490
y_bot_torso = 876

torso_arr = np.zeros((1024, 1024, 4), dtype=np.uint8)
for ty in range(1024):
    v = ty / 1023.0
    ref_y = int(round(y_top_torso + v * (y_bot_torso - y_top_torso)))
    
    # Trapezoid coordinates
    x_left = 372.0 - v * (372.0 - 268.0)
    x_right = 652.0 + v * (756.0 - 652.0)
    w_row = x_right - x_left
    
    for tx in range(1024):
        u = tx / 1023.0
        ref_x = int(round(x_left + u * w_row))
        if 0 <= ref_x < 1024 and 0 <= ref_y < 1024:
            torso_arr[ty, tx] = ref_arr[ref_y, ref_x]

torso_img = Image.fromarray(torso_arr, 'RGBA')
torso_path = os.path.join(tex_dir, 'brick_dev_torso_1k.png')
torso_img.save(torso_path)
print(f"Saved: {torso_path}")


print("=== 3. Building Sleeve Striped Texture ===")
# Generate clean continuous horizontal stripes matching the polo shirt:
# Light blue: RGB(155, 195, 234)
# Soft white: RGB(244, 248, 252)
sleeve_img = Image.new('RGBA', (512, 512), (244, 248, 252, 255))
draw = ImageDraw.Draw(sleeve_img)
stripe_h = 512 // 8
for i in range(8):
    if i % 2 == 0:
        draw.rectangle([0, i * stripe_h, 512, (i + 1) * stripe_h], fill=(155, 195, 234, 255))
sleeve_path = os.path.join(tex_dir, 'brick_dev_sleeve_1k.png')
sleeve_img.save(sleeve_path)
print(f"Saved: {sleeve_path}")


print("=== 4. Building Forearm Cuff + Skin Texture ===")
# Top 28% is light blue sleeve cuff with dark blue seam
# Bottom 72% is rich brown skin
forearm_img = Image.new('RGBA', (512, 512), (154, 87, 46, 255))
f_draw = ImageDraw.Draw(forearm_img)
# Cuff (top 140 px)
f_draw.rectangle([0, 0, 512, 136], fill=(155, 195, 234, 255))
# Dark blue hem seam
f_draw.rectangle([0, 136, 512, 144], fill=(58, 103, 151, 255))
forearm_path = os.path.join(tex_dir, 'brick_dev_forearm_1k.png')
forearm_img.save(forearm_path)
print(f"Saved: {forearm_path}")

print("=== All textures ready! ===")
