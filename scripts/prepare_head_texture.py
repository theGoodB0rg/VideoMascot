import os
import math
from PIL import Image
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ref_path = os.path.join(project_root, 'preview', 'brick_dev_perfect_cutout.png')
tex_dir = os.path.join(project_root, 'assets', 'mascots', 'brick_dev', 'textures')
os.makedirs(tex_dir, exist_ok=True)

ref_img = Image.open(ref_path).convert('RGBA')
ref_arr = np.array(ref_img)

print("=== 1. Calibrating Head Texture Verticals ===")
x0 = 512.0
r_head = 227.0
# Chin bottom in reference
y_chin = 482.0
# Forehead top in reference
y_top = 132.0

tex_w = 2048
tex_h = 1024

base_skin = np.array([154, 87, 46, 255], dtype=np.uint8)

head_tex = np.zeros((tex_h, tex_w, 4), dtype=np.uint8)
head_tex[:, :] = base_skin

# v = 0.14 (chin bottom, well above bevel) to v = 0.78 (forehead hairline)
v_chin = 0.14
v_top = 0.78

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
        
        # 80 degrees sweep on each side
        max_theta = 82.0 * math.pi / 180.0
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
        if deg > 64.0:
            weight = (max_theta * 180.0 / math.pi - deg) / (max_theta * 180.0 / math.pi - 64.0)
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
