from __future__ import annotations
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig


def create_starter_tech_chibi(output_dir: Path) -> Path:
    """Generates a complete, high-resolution layered starter mascot bundle (Chibi Tech Guide)
    with studio-grade anatomy, seamless neck/collar overlap, and clear silhouette poses.
    """
    bundle_dir = output_dir / "chibi_tech_guide"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    (bundle_dir / "head").mkdir(exist_ok=True)
    (bundle_dir / "head" / "eyes").mkdir(exist_ok=True)
    (bundle_dir / "head" / "mouth").mkdir(exist_ok=True)
    (bundle_dir / "head" / "eyebrows").mkdir(exist_ok=True)
    (bundle_dir / "body").mkdir(exist_ok=True)
    (bundle_dir / "body" / "hands").mkdir(exist_ok=True)
    (bundle_dir / "props").mkdir(exist_ok=True)

    # Color Palette
    C_OUTLINE = (30, 41, 59, 255)       # Slate 800
    C_SKIN = (254, 240, 222, 255)       # Warm skin tone
    C_SKIN_SHADOW = (241, 196, 160, 255)# Warm neck shadow
    C_CHEEK = (251, 146, 150, 160)      # Rose blush
    C_TORSO = (37, 99, 235, 255)        # Tech Blue
    C_TORSO_SHADOW = (29, 78, 216, 255)
    C_ACCENT = (245, 158, 11, 255)      # Amber gold
    C_IRIS = (14, 165, 233, 255)        # Vibrant Cyan
    C_PUPIL = (15, 23, 42, 255)
    C_WHITE = (255, 255, 255, 255)
    C_MOUTH_INSIDE = (159, 18, 57, 255) # Rose 900
    C_TONGUE = (244, 63, 94, 255)       # Rose 500
    C_TEETH = (255, 255, 255, 255)

    # 1. Head Base with Anatomical Neck Stem (300x280)
    head_img = Image.new("RGBA", (300, 280), (0, 0, 0, 0))
    d = ImageDraw.Draw(head_img)
    
    # Neck stem extending down to y=270 (anchors deeply into torso collar)
    d.rectangle([115, 190, 185, 270], fill=C_SKIN_SHADOW, outline=C_OUTLINE, width=5)
    
    # Head contour (rounded soft chibi face)
    d.ellipse([30, 15, 270, 235], fill=C_SKIN, outline=C_OUTLINE, width=6)
    
    # Cheek blushes
    d.ellipse([50, 155, 95, 180], fill=C_CHEEK)
    d.ellipse([205, 155, 250, 180], fill=C_CHEEK)
    
    # Tech ear muff / antennas
    d.rounded_rectangle([15, 95, 35, 145], radius=8, fill=C_ACCENT, outline=C_OUTLINE, width=4)
    d.rounded_rectangle([265, 95, 285, 145], radius=8, fill=C_ACCENT, outline=C_OUTLINE, width=4)
    
    # Antenna atop head
    d.rectangle([145, 0, 155, 22], fill=C_ACCENT, outline=C_OUTLINE, width=3)
    d.ellipse([138, 0, 162, 18], fill=(56, 189, 248, 255), outline=C_OUTLINE, width=3)
    head_img.save(bundle_dir / "head" / "head_base.png")

    # 2. Eyes: Sclera, Pupil, Eyelids
    # Left Eye Sclera (50x65)
    sclera = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    d = ImageDraw.Draw(sclera)
    d.ellipse([2, 2, 48, 63], fill=C_WHITE, outline=C_OUTLINE, width=4)
    sclera.save(bundle_dir / "head" / "eyes" / "sclera_left.png")
    sclera.save(bundle_dir / "head" / "eyes" / "sclera_right.png")

    # Pupil (32x40) with dynamic reflections
    pupil = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(pupil)
    d.ellipse([0, 0, 31, 39], fill=C_IRIS)
    d.ellipse([6, 8, 26, 32], fill=C_PUPIL)
    # High-gloss highlights
    d.ellipse([6, 4, 16, 14], fill=C_WHITE)
    d.ellipse([18, 22, 24, 28], fill=C_WHITE)
    pupil.save(bundle_dir / "head" / "eyes" / "pupil.png")

    # Eyelid Blink (50x65)
    blink = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    d = ImageDraw.Draw(blink)
    d.arc([4, 15, 46, 45], start=0, end=180, fill=C_OUTLINE, width=6)
    blink.save(bundle_dir / "head" / "eyes" / "eyelid_blink.png")

    # Happy Eyes (^^)
    eye_happy = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    d = ImageDraw.Draw(eye_happy)
    d.arc([4, 10, 46, 42], start=180, end=360, fill=C_OUTLINE, width=6)
    eye_happy.save(bundle_dir / "head" / "eyes" / "eye_happy.png")

    # 3. Eyebrows (40x15)
    brow_l = Image.new("RGBA", (40, 15), (0, 0, 0, 0))
    d = ImageDraw.Draw(brow_l)
    d.line([(2, 10), (38, 4)], fill=C_OUTLINE, width=5)
    brow_l.save(bundle_dir / "head" / "eyebrows" / "left.png")

    brow_r = Image.new("RGBA", (40, 15), (0, 0, 0, 0))
    d = ImageDraw.Draw(brow_r)
    d.line([(2, 4), (38, 10)], fill=C_OUTLINE, width=5)
    brow_r.save(bundle_dir / "head" / "eyebrows" / "right.png")

    # 4. Mouth Set (Preston Blair 9 Visemes) (80x50 each)
    def create_mouth(name: str, draw_fn) -> None:
        m = Image.new("RGBA", (80, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(m)
        draw_fn(draw)
        m.save(bundle_dir / "head" / "mouth" / f"{name}.png")

    create_mouth("rest", lambda d: d.arc([20, 10, 60, 30], start=10, end=170, fill=C_OUTLINE, width=5))
    
    def draw_A_I(d):
        d.pieslice([15, 5, 65, 45], start=0, end=180, fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4)
        d.rectangle([25, 6, 55, 14], fill=C_TEETH)
        d.ellipse([25, 28, 55, 46], fill=C_TONGUE)
    create_mouth("A_I", draw_A_I)

    def draw_E(d):
        d.rounded_rectangle([15, 15, 65, 35], radius=6, fill=C_TEETH, outline=C_OUTLINE, width=4)
        d.line([(16, 25), (64, 25)], fill=C_OUTLINE, width=3)
    create_mouth("E", draw_E)

    def draw_O(d):
        d.ellipse([25, 5, 55, 45], fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4)
        d.ellipse([30, 25, 50, 42], fill=C_TONGUE)
    create_mouth("O", draw_O)

    create_mouth("U", lambda d: d.ellipse([30, 15, 50, 35], fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4))
    create_mouth("M_B_P", lambda d: d.line([(20, 25), (60, 25)], fill=C_OUTLINE, width=5))

    def draw_F_V(d):
        d.rounded_rectangle([20, 18, 60, 32], radius=4, fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4)
        d.rectangle([25, 19, 55, 25], fill=C_TEETH)
    create_mouth("F_V", draw_F_V)

    def draw_L(d):
        d.pieslice([18, 10, 62, 40], start=0, end=180, fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4)
        d.rectangle([25, 11, 55, 18], fill=C_TEETH)
        d.ellipse([32, 18, 48, 28], fill=C_TONGUE)
    create_mouth("L_D_T_N", draw_L)

    create_mouth("W_Q", lambda d: d.ellipse([32, 18, 48, 32], fill=C_MOUTH_INSIDE, outline=C_OUTLINE, width=4))

    # 5. Torso / Body with Overlapping Collar & Shoulder Sockets (220x240)
    torso = Image.new("RGBA", (220, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(torso)
    
    # Body silhouette with shoulders
    d.rounded_rectangle([30, 35, 190, 225], radius=35, fill=C_TORSO, outline=C_OUTLINE, width=6)
    
    # Chest badge / energy core
    d.ellipse([95, 100, 125, 130], fill=C_ACCENT, outline=C_OUTLINE, width=4)
    
    # Front Collar Notch (overlaps the neck base)
    d.polygon([(110, 65), (75, 25), (145, 25)], fill=C_SKIN_SHADOW, outline=C_OUTLINE, width=4)
    d.polygon([(110, 55), (85, 25), (135, 25)], fill=C_SKIN)
    
    # Shoulder cap trims
    d.rounded_rectangle([25, 35, 60, 65], radius=10, fill=C_TORSO_SHADOW)
    d.rounded_rectangle([160, 35, 195, 65], radius=10, fill=C_TORSO_SHADOW)
    
    # Bottom waistband
    d.rounded_rectangle([40, 205, 180, 225], radius=8, fill=C_TORSO_SHADOW, outline=C_OUTLINE, width=4)
    torso.save(bundle_dir / "body" / "torso.png")

    # 6. Upper Arm & Forearm (60x100)
    arm_up = Image.new("RGBA", (60, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(arm_up)
    d.rounded_rectangle([15, 10, 45, 90], radius=15, fill=C_TORSO, outline=C_OUTLINE, width=5)
    # Joint accent
    d.ellipse([22, 12, 38, 28], fill=C_ACCENT)
    arm_up.save(bundle_dir / "body" / "arm_upper.png")

    arm_low = Image.new("RGBA", (60, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(arm_low)
    d.rounded_rectangle([15, 10, 45, 90], radius=15, fill=C_SKIN, outline=C_OUTLINE, width=5)
    # Cuff sleeve
    d.rounded_rectangle([12, 10, 48, 28], radius=6, fill=C_TORSO_SHADOW, outline=C_OUTLINE, width=4)
    arm_low.save(bundle_dir / "body" / "arm_lower.png")

    # 7. Hands (70x70)
    # Pointing Hand: Finger extended out from wrist
    hand_point = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand_point)
    # Palm base
    d.ellipse([18, 28, 52, 58], fill=C_SKIN, outline=C_OUTLINE, width=4)
    # Index finger extended along tip axis
    d.rounded_rectangle([14, 5, 28, 42], radius=7, fill=C_SKIN, outline=C_OUTLINE, width=4)
    hand_point.save(bundle_dir / "body" / "hands" / "point.png")

    # Wave / Open Hand
    hand_wave = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand_wave)
    d.ellipse([15, 22, 55, 60], fill=C_SKIN, outline=C_OUTLINE, width=4)
    for fx in [18, 28, 38, 48]:
        d.rounded_rectangle([fx, 6, fx + 10, 28], radius=5, fill=C_SKIN, outline=C_OUTLINE, width=3)
    hand_wave.save(bundle_dir / "body" / "hands" / "wave.png")

    # Thumbs Up Hand
    hand_thumb = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand_thumb)
    d.ellipse([15, 25, 55, 60], fill=C_SKIN, outline=C_OUTLINE, width=4)
    d.rounded_rectangle([18, 4, 34, 34], radius=7, fill=C_SKIN, outline=C_OUTLINE, width=4)
    hand_thumb.save(bundle_dir / "body" / "hands" / "thumbs_up.png")

    # Rest Hand
    hand_rest = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(hand_rest)
    d.ellipse([10, 10, 50, 50], fill=C_SKIN, outline=C_OUTLINE, width=4)
    hand_rest.save(bundle_dir / "body" / "hands" / "rest.png")

    # 8. Props: Pointer Stick (Aligned with hand grip) (24x180)
    pointer = Image.new("RGBA", (24, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(pointer)
    # Metallic shaft
    d.rounded_rectangle([8, 18, 16, 175], radius=4, fill=(203, 213, 225, 255), outline=C_OUTLINE, width=3)
    # Laser / Crystal emitter tip
    d.ellipse([3, 2, 21, 20], fill=C_ACCENT, outline=C_OUTLINE, width=3)
    d.ellipse([7, 6, 17, 16], fill=(56, 189, 248, 255))
    pointer.save(bundle_dir / "props" / "pointer_stick.png")

    # 9. Write Anatomically Correct manifest.json
    # Root at (400, 700)
    # Torso at (0, -220) relative to Root -> World (400, 480)
    # Head at (0, -85) relative to Torso -> World (400, 395)
    # Head Pivot at (150, 240) (the exact neck socket pivot!)
    manifest = MascotManifest(
        id="chibi_tech_guide",
        name="Chibi Tech Guide",
        description="High-resolution, anatomically anchored 2.5D modular tech mascot with seamless neck overlap.",
        canvas_size=(800, 800),
        bones={
            "root": BoneConfig(position=(400, 700), pivot=(0, 0), z_index=0),
            "torso": BoneConfig(parent="root", position=(0, -220), pivot=(0, 0), z_index=10),
            "head": BoneConfig(parent="torso", position=(0, -85), pivot=(0, 0), z_index=20),
            "arm_l_upper": BoneConfig(parent="torso", position=(-65, -55), pivot=(0, 0), length=70, z_index=5),
            "arm_l_lower": BoneConfig(parent="arm_l_upper", position=(0, 70), pivot=(0, 0), length=70, z_index=6),
            "hand_l": BoneConfig(parent="arm_l_lower", position=(0, 70), pivot=(0, 0), z_index=7),
            "arm_r_upper": BoneConfig(parent="torso", position=(65, -55), pivot=(0, 0), length=70, z_index=15),
            "arm_r_lower": BoneConfig(parent="arm_r_upper", position=(0, 70), pivot=(0, 0), length=70, z_index=16),
            "hand_r": BoneConfig(parent="arm_r_lower", position=(0, 70), pivot=(0, 0), z_index=17),
            "prop_r": BoneConfig(parent="hand_r", position=(0, 10), pivot=(0, 0), z_index=18)
        },
        slots={
            "torso": SlotConfig(
                bone="torso",
                default_attachment="default",
                offset=(-110, -120),
                attachments={"default": "body/torso.png"},
                z_index=1
            ),
            "head_base": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-150, -240),
                attachments={"default": "head/head_base.png"},
                z_index=1
            ),
            "eye_l_sclera": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-75, -135),
                attachments={
                    "default": "head/eyes/sclera_left.png",
                    "blink": "head/eyes/eyelid_blink.png",
                    "happy": "head/eyes/eye_happy.png"
                },
                z_index=2
            ),
            "eye_l_pupil": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-66, -122),
                attachments={"default": "head/eyes/pupil.png"},
                z_index=3
            ),
            "eye_r_sclera": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(25, -135),
                attachments={
                    "default": "head/eyes/sclera_right.png",
                    "blink": "head/eyes/eyelid_blink.png",
                    "happy": "head/eyes/eye_happy.png"
                },
                z_index=2
            ),
            "eye_r_pupil": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(34, -122),
                attachments={"default": "head/eyes/pupil.png"},
                z_index=3
            ),
            "eyebrow_l": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-70, -155),
                attachments={"default": "head/eyebrows/left.png"},
                z_index=4
            ),
            "eyebrow_r": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(30, -155),
                attachments={"default": "head/eyebrows/right.png"},
                z_index=4
            ),
            "mouth": SlotConfig(
                bone="head",
                default_attachment="rest",
                offset=(-40, -85),
                attachments={
                    "rest": "head/mouth/rest.png",
                    "A_I": "head/mouth/A_I.png",
                    "E": "head/mouth/E.png",
                    "O": "head/mouth/O.png",
                    "U": "head/mouth/U.png",
                    "M_B_P": "head/mouth/M_B_P.png",
                    "F_V": "head/mouth/F_V.png",
                    "L_D_T_N": "head/mouth/L_D_T_N.png",
                    "W_Q": "head/mouth/W_Q.png"
                },
                z_index=5
            ),
            "arm_l_up": SlotConfig(
                bone="arm_l_upper",
                offset=(-30, -20),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_l_low": SlotConfig(
                bone="arm_l_lower",
                offset=(-30, -15),
                attachments={"default": "body/arm_lower.png"},
                z_index=1
            ),
            "hand_l": SlotConfig(
                bone="hand_l",
                default_attachment="rest",
                offset=(-35, -20),
                attachments={
                    "rest": "body/hands/rest.png",
                    "wave": "body/hands/wave.png",
                    "point": "body/hands/point.png",
                    "thumbs_up": "body/hands/thumbs_up.png"
                },
                z_index=2
            ),
            "arm_r_up": SlotConfig(
                bone="arm_r_upper",
                offset=(-30, -20),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_r_low": SlotConfig(
                bone="arm_r_lower",
                offset=(-30, -15),
                attachments={"default": "body/arm_lower.png"},
                z_index=1
            ),
            "hand_r": SlotConfig(
                bone="hand_r",
                default_attachment="rest",
                offset=(-35, -20),
                attachments={
                    "rest": "body/hands/rest.png",
                    "wave": "body/hands/wave.png",
                    "point": "body/hands/point.png",
                    "thumbs_up": "body/hands/thumbs_up.png"
                },
                z_index=2
            ),
            "prop_r": SlotConfig(
                bone="prop_r",
                default_attachment="none",
                offset=(-12, -160),
                attachments={
                    "none": "",
                    "pointer_stick": "props/pointer_stick.png"
                },
                z_index=3
            )
        },
        viseme_slot="mouth",
        visemes={
            "rest": "rest",
            "A_I": "A_I",
            "E": "E",
            "O": "O",
            "U": "U",
            "M_B_P": "M_B_P",
            "F_V": "F_V",
            "L_D_T_N": "L_D_T_N",
            "W_Q": "W_Q"
        }
    )

    with open(bundle_dir / "manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return bundle_dir
