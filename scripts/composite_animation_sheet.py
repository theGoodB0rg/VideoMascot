import os
import shutil
from PIL import Image, ImageDraw, ImageFont

debug_dir = os.path.join('preview', 'debug')
out_path = os.path.join('preview', 'check_facial_animation_sheet.png')
artifact_dir = r'C:\Users\HP\.gemini\antigravity\brain\05b13561-3b49-4578-838b-bf57f8a31539'

# Canvas dimensions: 1920 wide, 1920 high
sheet_w = 1920
sheet_h = 1920
sheet = Image.new('RGB', (sheet_w, sheet_h), (13, 17, 23))
draw = ImageDraw.Draw(sheet)

# Header
draw.rectangle([(0, 0), (sheet_w, 90)], fill=(18, 24, 38))
draw.text((sheet_w // 2, 35), "EXPRESSIVE 3D FACIAL ANIMATION, DIRECTIONAL GAZE & 9-VISEME LIP-SYNC", 
          fill=(56, 189, 248), anchor="mm")
draw.text((sheet_w // 2, 65), "100% Procedural WebGL Lego Mascot: Arbitrary Degree Gaze, Emotional Brow/Eyelid Morphs, & Preston Blair Speech", 
          fill=(148, 163, 184), anchor="mm")

def load_and_resize(filename, size=(300, 300)):
    p = os.path.join(debug_dir, filename)
    if os.path.exists(p):
        im = Image.open(p)
        return im.resize(size, Image.Resampling.LANCZOS)
    # Placeholder
    ph = Image.new('RGB', size, (30, 30, 40))
    return ph

# SECTION 1: DIRECTIONAL GAZE (User requested: "look in any degree of direction like left right 30 degrees right etc")
draw.rectangle([(40, 110), (sheet_w - 40, 145)], fill=(22, 30, 48))
draw.text((60, 127), "SECTION 1: CONTINUOUS DIRECTIONAL GAZE TRACKING (ARBITRARY DEGREE YAW & PITCH)", fill=(56, 189, 248), anchor="lm")

gaze_items = [
    ('gaze_left_30.png', '1. Look Left 30° (Yaw -30°)', 'Pupils track naturally within almond sclera'),
    ('gaze_center.png', '2. Center Gaze (0°, 0°)', 'Direct forward engagement, 1:30 catchlights'),
    ('gaze_right_30.png', '3. Look Right 30° (Yaw +30°)', 'Explicit user request: smooth rightward glance'),
    ('gaze_up_right.png', '4. Look Up-Right (25°, 18°)', 'Multi-axis 2D/3D tracking with cornea parallax'),
]

col_w = (sheet_w - 80) // 4
for i, (fn, label, sub) in enumerate(gaze_items):
    x_pos = 40 + i * col_w + (col_w - 320) // 2
    y_pos = 160
    card_img = load_and_resize(fn, (320, 320))
    # Border
    border_col = (56, 189, 248) if 'right_30' in fn else (40, 60, 90)
    draw.rectangle([(x_pos - 3, y_pos - 3), (x_pos + 323, y_pos + 323)], outline=border_col, width=2)
    sheet.paste(card_img, (x_pos, y_pos))
    draw.rectangle([(x_pos, y_pos + 324), (x_pos + 320, y_pos + 376)], fill=(20, 27, 44))
    draw.text((x_pos + 160, y_pos + 342), label, fill=(241, 245, 249), anchor="mm")
    draw.text((x_pos + 160, y_pos + 360), sub, fill=(148, 163, 184), anchor="mm")

# SECTION 2: EMOTIONAL RANGE & EYELID CONTROLS
sec2_y = 570
draw.rectangle([(40, sec2_y), (sheet_w - 40, sec2_y + 35)], fill=(22, 30, 48))
draw.text((60, sec2_y + 17), "SECTION 2: EMOTIONAL EXPRESSIONS & EYELID MORPHING (BROWS + SQUINT + BLINK)", fill=(56, 189, 248), anchor="lm")

emotion_items = [
    ('emotion_happy.png', 'Happy (Smiling Eyes)', 'Cheek squint crescent + cheerful brows'),
    ('emotion_thinking.png', 'Thinking (Code Review)', 'Asymmetric brow arch + thoughtful glance'),
    ('emotion_surprised.png', 'Surprised', 'High arched brows + wide circular eyes'),
    ('emotion_skeptical.png', 'Skeptical (PR Review)', 'Raised brow + quizzical squint'),
    ('emotion_blink.png', 'Blink (Closed)', 'Natural curved lash line + lid fold'),
]

col5_w = (sheet_w - 80) // 5
for i, (fn, label, sub) in enumerate(emotion_items):
    x_pos = 40 + i * col5_w + (col5_w - 280) // 2
    y_pos = sec2_y + 50
    card_img = load_and_resize(fn, (280, 280))
    draw.rectangle([(x_pos - 2, y_pos - 2), (x_pos + 282, y_pos + 282)], outline=(40, 60, 90), width=1)
    sheet.paste(card_img, (x_pos, y_pos))
    draw.rectangle([(x_pos, y_pos + 283), (x_pos + 280, y_pos + 330)], fill=(20, 27, 44))
    draw.text((x_pos + 140, y_pos + 299), label, fill=(241, 245, 249), anchor="mm")
    draw.text((x_pos + 140, y_pos + 316), sub, fill=(148, 163, 184), anchor="mm")

# SECTION 3: REALISTIC SPEECH LIP-SYNC (PRESTON BLAIR 9-VISEME SET)
sec3_y = 990
draw.rectangle([(40, sec3_y), (sheet_w - 40, sec3_y + 35)], fill=(22, 30, 48))
draw.text((60, sec3_y + 17), "SECTION 3: REALISTIC SPEECH LIP-SYNC (PRESTON BLAIR 9-VISEME PHONETIC SET)", fill=(56, 189, 248), anchor="lm")

viseme_items = [
    ('viseme_rest.png', 'REST / IDLE', 'Closed confident smile'),
    ('viseme_a_i.png', 'A / I (AH)', 'Jaw drop, teeth & tongue'),
    ('viseme_e.png', 'E (EE)', 'Wide dental smile grin'),
    ('viseme_o.png', 'O (OH)', 'Rounded open oral cavity'),
    ('viseme_u.png', 'U (OO)', 'Small forward pucker'),
    ('viseme_m_b_p.png', 'M / B / P', 'Pressed bilabial seal'),
    ('viseme_f_v.png', 'F / V', 'Upper teeth on lower lip'),
    ('viseme_l_th.png', 'L / TH', 'Tongue behind upper teeth'),
    ('viseme_w_q.png', 'W / Q', 'Tight rounded pucker'),
]

# 2 rows for visemes: 5 in top row, 4 in bottom row
row1_w = (sheet_w - 80) // 5
for i in range(5):
    fn, label, sub = viseme_items[i]
    x_pos = 40 + i * row1_w + (row1_w - 240) // 2
    y_pos = sec3_y + 50
    card_img = load_and_resize(fn, (240, 240))
    draw.rectangle([(x_pos - 2, y_pos - 2), (x_pos + 242, y_pos + 242)], outline=(40, 60, 90), width=1)
    sheet.paste(card_img, (x_pos, y_pos))
    draw.rectangle([(x_pos, y_pos + 243), (x_pos + 240, y_pos + 285)], fill=(20, 27, 44))
    draw.text((x_pos + 120, y_pos + 258), label, fill=(241, 245, 249), anchor="mm")
    draw.text((x_pos + 120, y_pos + 273), sub, fill=(148, 163, 184), anchor="mm")

row2_w = (sheet_w - 80) // 4
for i in range(4):
    fn, label, sub = viseme_items[5 + i]
    x_pos = 40 + i * row2_w + (row2_w - 240) // 2
    y_pos = sec3_y + 355
    card_img = load_and_resize(fn, (240, 240))
    draw.rectangle([(x_pos - 2, y_pos - 2), (x_pos + 242, y_pos + 242)], outline=(40, 60, 90), width=1)
    sheet.paste(card_img, (x_pos, y_pos))
    draw.rectangle([(x_pos, y_pos + 243), (x_pos + 240, y_pos + 285)], fill=(20, 27, 44))
    draw.text((x_pos + 120, y_pos + 258), label, fill=(241, 245, 249), anchor="mm")
    draw.text((x_pos + 120, y_pos + 273), sub, fill=(148, 163, 184), anchor="mm")

# Bottom summary bar
draw.rectangle([(0, sheet_h - 60), (sheet_w, sheet_h)], fill=(18, 24, 38))
draw.text((sheet_w // 2, sheet_h - 30), 
          "INTERACTIVE TESTING: Open http://localhost:3000 to test 30° Gaze Slider, Emotions & Live Speech Lip-Sync in Real Time", 
          fill=(56, 189, 248), anchor="mm")

sheet.save(out_path, quality=95)
print(f"Saved contact sheet to {out_path}")

# Copy to brain artifact directory
artifact_out = os.path.join(artifact_dir, 'check_facial_animation_sheet.png')
shutil.copy(out_path, artifact_out)
print(f"Copied to artifact: {artifact_out}")
