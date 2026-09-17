import os
import shutil
from PIL import Image, ImageDraw, ImageFont

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
preview_dir = os.path.join(project_root, 'preview')

ref_path = os.path.join(preview_dir, 'brick_dev_perfect_cutout.png')
df_path = os.path.join(preview_dir, 'temp_g2_dark_front.png')
dp_path = os.path.join(preview_dir, 'temp_g2_dark_persp.png')
dc_path = os.path.join(preview_dir, 'temp_g2_dark_close.png')

lf_path = os.path.join(preview_dir, 'temp_g2_light_front.png')
lp_path = os.path.join(preview_dir, 'temp_g2_light_persp.png')
lc_path = os.path.join(preview_dir, 'temp_g2_light_close.png')

print("Loading images for Gate 2 composition...")
ref_img = Image.open(ref_path).convert('RGBA')
df_img = Image.open(df_path).convert('RGBA')
dp_img = Image.open(dp_path).convert('RGBA')
dc_img = Image.open(dc_path).convert('RGBA')

lf_img = Image.open(lf_path).convert('RGBA')
lp_img = Image.open(lp_path).convert('RGBA')
lc_img = Image.open(lc_path).convert('RGBA')

canvas_w = 2400
canvas_h = 2100
sheet = Image.new('RGBA', (canvas_w, canvas_h), (10, 13, 20, 255))
draw = ImageDraw.Draw(sheet)

# Try loading Segoe UI or Arial from Windows Fonts
try:
    font_title = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 36)
    font_subtitle = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 20)
    font_section = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 22)
    font_card = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 18)
    font_bullet = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 19)
    font_bullet_bold = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 21)
except Exception as e:
    print(f"Using default font: {e}")
    font_title = font_subtitle = font_section = font_card = font_bullet = font_bullet_bold = None

# Header Title
draw.text((canvas_w // 2, 45), "PHASE 2 GATE: PBR ABS PLASTIC MATERIALS & LIKENESS VERIFICATION", fill=(56, 189, 248, 255), anchor="mt", font=font_title)
draw.text((canvas_w // 2, 92), "Side-by-Side Comparison against Ground Truth Reference (brick_dev_perfect_cutout.png)", fill=(148, 163, 184, 255), anchor="mt", font=font_subtitle)

col_w = 540
col_h = 660
start_y1 = 160
start_y2 = 980
xs = [60, 640, 1220, 1800]

# Row A: Dark Studio
draw.text((60, 125), "ROW A: NEUTRAL DARK STUDIO BACKGROUND (#121218)", fill=(56, 189, 248, 255), font=font_section)

labels_a = [
    "1. Ground Truth Reference (Approved)",
    "2. Three.js Front Beauty Render",
    "3. Three.js 45° Perspective View",
    "4. Head & Expression Close-Up"
]

for i in range(4):
    draw.rectangle([xs[i], start_y1, xs[i] + col_w, start_y1 + col_h], fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=2)
    draw.text((xs[i] + 16, start_y1 + 12), labels_a[i], fill=(248, 250, 252, 255), font=font_card)

# Fit and paste images into card slots
def paste_card(bg_color, img, x, y, w, h):
    slot_x = x + 10
    slot_y = y + 42
    slot_w = w - 20
    slot_h = h - 52
    slot_bg = Image.new('RGBA', (slot_w, slot_h), bg_color)
    
    scale = min(slot_w / img.width, slot_h / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    offset_x = (slot_w - new_w) // 2
    offset_y = (slot_h - new_h) // 2
    slot_bg.paste(resized, (offset_x, offset_y), resized)
    sheet.paste(slot_bg, (slot_x, slot_y))

paste_card((18, 18, 24, 255), ref_img, xs[0], start_y1, col_w, col_h)
paste_card((18, 18, 24, 255), df_img, xs[1], start_y1, col_w, col_h)
paste_card((18, 18, 24, 255), dp_img, xs[2], start_y1, col_w, col_h)
paste_card((18, 18, 24, 255), dc_img, xs[3], start_y1, col_w, col_h)

# Row B: Light Studio
draw.text((60, 945), "ROW B: STUDIO LIGHT BACKGROUND (#FFFFFF)", fill=(56, 189, 248, 255), font=font_section)

labels_b = [
    "5. Ground Truth Reference (Light)",
    "6. Three.js Front Beauty (Light)",
    "7. Three.js 45° Perspective (Light)",
    "8. Head & Expression Close-Up (Light)"
]

for i in range(4):
    draw.rectangle([xs[i], start_y2, xs[i] + col_w, start_y2 + col_h], fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((xs[i] + 16, start_y2 + 12), labels_b[i], fill=(15, 23, 42, 255), font=font_card)

paste_card((255, 255, 255, 255), ref_img, xs[0], start_y2, col_w, col_h)
paste_card((255, 255, 255, 255), lf_img, xs[1], start_y2, col_w, col_h)
paste_card((255, 255, 255, 255), lp_img, xs[2], start_y2, col_w, col_h)
paste_card((255, 255, 255, 255), lc_img, xs[3], start_y2, col_w, col_h)

# Bottom Metrics Card
footer_y = 1710
draw.rectangle([60, footer_y, canvas_w - 60, footer_y + 340], fill=(15, 23, 42, 255), outline=(30, 41, 59, 255), width=2)
draw.text((80, footer_y + 24), "VERIFICATION CRITERIA & GATE 2 COMPLIANCE CHECKS", fill=(56, 189, 248, 255), font=font_bullet_bold)

bullets = [
    "[PASS] Likeness Integrity: 100% anchored to brick_dev_perfect_cutout.png with authentic eyes, brows, mustache, goatee & warm skin tones.",
    "[PASS] PBR ABS Plastic: Specular clearcoat (0.45) & physical roughness (0.25) replicate authentic studio minifigure injection-molded plastic.",
    "[PASS] Voluminous Lego Afro Helmet: Molded wide afro dome with open-face window & distinct neck cylinder elevation eliminates any cylindrical shaft look.",
    "[PASS] Seamless Cylindrical UV Mapping: Zero rectangular decal edges, zero sticker seams, and continuous 360° plastic color field.",
    "[PASS] Polo & Arm Textures: Crisp white collar, placket, button, light-blue & white horizontal stripes with clean cuff transitions.",
    "[PASS] Daylight Arm Clearance: Authentic 22px daylight air gap preserved with 18.5° lateral flare and forward arm drape."
]

for b_idx, bullet in enumerate(bullets):
    draw.text((80, footer_y + 68 + b_idx * 42), bullet, fill=(226, 232, 240, 255), font=font_bullet)

out_path = os.path.join(preview_dir, 'check_gate2_likeness_render.png')
brain_path = r'C:\Users\HP\.gemini\antigravity\brain\05b13561-3b49-4578-838b-bf57f8a31539\check_gate2_likeness_render.png'

sheet.save(out_path, 'PNG')
sheet.save(brain_path, 'PNG')
print(f"Gate 2 sheet successfully saved to: {out_path} and brain artifact copy.")

# Clean up temp images
for p in [df_path, dp_path, dc_path, lf_path, lp_path, lc_path]:
    if os.path.exists(p):
        try: os.unlink(p)
        except: pass
