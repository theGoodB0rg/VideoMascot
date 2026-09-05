from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

from videomascot.models.manifest import (
    MascotManifest,
    BoneConfig,
    SlotConfig,
    PhysicsConfig,
    JointConstraintConfig
)


def create_starter_nexus_bot(output_dir: Path) -> Path:
    """Generates the flagship high-resolution 'Sleek Futuristic Tech Bot' (Nexus Bot)
    with magnetic floating limbs, emissive curved visor, digital acoustic visemes,
    and spring-damper secondary physics.
    """
    bundle_dir = output_dir / "nexus_bot"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    (bundle_dir / "head").mkdir(exist_ok=True)
    (bundle_dir / "head" / "eyes").mkdir(exist_ok=True)
    (bundle_dir / "head" / "mouth").mkdir(exist_ok=True)
    (bundle_dir / "body").mkdir(exist_ok=True)
    (bundle_dir / "body" / "hands").mkdir(exist_ok=True)
    (bundle_dir / "props").mkdir(exist_ok=True)

    # High-End Modern Motion Graphics Cyber Palette
    C_OUTLINE = (15, 23, 42, 255)         # Deep Slate 900
    C_CHASSIS_DARK = (30, 41, 59, 255)    # Slate 800 Carbon
    C_CHASSIS_MID = (51, 65, 85, 255)     # Slate 700
    C_CHASSIS_LIGHT = (241, 245, 249, 255)# Crisp Ceramic White 100
    C_CHASSIS_SHADOW = (203, 213, 225, 255)
    C_VISOR_BG = (2, 6, 23, 255)          # Obsidian Glass 950
    C_NEON_CYAN = (6, 182, 212, 255)      # Cyber Cyan 500
    C_NEON_GLOW = (56, 189, 248, 255)     # Sky Blue Glow 400
    C_CORE_PULSE = (0, 245, 255, 255)     # Electric Cyan Peak
    C_ACCENT_AMBER = (251, 191, 36, 255)  # Laser Warning Gold 400
    C_WHITE = (255, 255, 255, 255)

    # 1. Head Base: Aerodynamic Capsule with Curved Obsidian Glass Visor (320x300)
    head_img = Image.new("RGBA", (320, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(head_img)

    # Antenna stem & pulsing tip with spring physics hook
    d.rounded_rectangle([154, 5, 166, 45], radius=5, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=3)
    d.ellipse([148, 2, 172, 24], fill=C_NEON_GLOW, outline=C_OUTLINE, width=3)
    d.ellipse([153, 7, 167, 20], fill=C_CORE_PULSE)

    # Outer Chassis Helmet (Sleek pod silhouette)
    d.rounded_rectangle([30, 35, 290, 280], radius=110, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=6)
    # Bevel shading on helmet top
    d.arc([40, 42, 280, 270], start=200, end=340, fill=C_WHITE, width=6)

    # Floating Ear Pods / Audio Comms with Glowing Neon Rings
    # Left Ear Pod
    d.rounded_rectangle([10, 115, 36, 195], radius=12, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.ellipse([15, 135, 31, 175], fill=C_NEON_GLOW, outline=C_OUTLINE, width=2)
    # Right Ear Pod
    d.rounded_rectangle([284, 115, 310, 195], radius=12, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.ellipse([289, 135, 305, 175], fill=C_NEON_GLOW, outline=C_OUTLINE, width=2)

    # Dark Obsidian Glass Visor Face
    d.rounded_rectangle([52, 75, 268, 255], radius=75, fill=C_VISOR_BG, outline=C_OUTLINE, width=5)
    # Visor glass curvature reflection highlight (top-left diagonal sweep)
    d.arc([65, 85, 255, 240], start=195, end=300, fill=(148, 163, 184, 110), width=8)
    head_img.save(bundle_dir / "head" / "head_base.png")

    # 2. Digital Emissive Eye Sets (180x80 each, centered on visor)
    def create_eyes(name: str, draw_fn) -> None:
        img = Image.new("RGBA", (180, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_fn(draw)
        img.save(bundle_dir / "head" / "eyes" / f"{name}.png")

    # Default: Sleek modern pill/capsule cyber eyes
    def draw_eyes_default(d):
        for cx in [45, 135]:
            # Outer cyan glow ring
            d.rounded_rectangle([cx - 24, 16, cx + 24, 64], radius=18, fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=2)
            d.rounded_rectangle([cx - 16, 24, cx + 16, 56], radius=12, fill=C_CORE_PULSE)
            # Crisp specular keylight
            d.ellipse([cx - 10, 26, cx - 2, 34], fill=C_WHITE)
    create_eyes("default", draw_eyes_default)

    # Happy: Upward neon crescent arcs (^^)
    def draw_eyes_happy(d):
        for cx in [45, 135]:
            d.arc([cx - 25, 18, cx + 25, 60], start=180, end=360, fill=C_CORE_PULSE, width=8)
            d.arc([cx - 28, 15, cx + 28, 63], start=180, end=360, fill=C_NEON_CYAN, width=3)
    create_eyes("happy", draw_eyes_happy)

    # Wink: Left eye closed slit, right eye open
    def draw_eyes_wink(d):
        # Left eye: sleek horizontal neon slit
        d.rounded_rectangle([20, 36, 70, 44], radius=4, fill=C_CORE_PULSE, outline=C_NEON_CYAN, width=2)
        # Right eye: full open pill
        cx = 135
        d.rounded_rectangle([cx - 24, 16, cx + 24, 64], radius=18, fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=2)
        d.rounded_rectangle([cx - 16, 24, cx + 16, 56], radius=12, fill=C_CORE_PULSE)
        d.ellipse([cx - 10, 26, cx - 2, 34], fill=C_WHITE)
    create_eyes("wink", draw_eyes_wink)

    # Blink / Sleep: Dual horizontal cyan slits
    def draw_eyes_blink(d):
        for cx in [45, 135]:
            d.rounded_rectangle([cx - 24, 37, cx + 24, 43], radius=3, fill=C_CORE_PULSE, outline=C_NEON_CYAN, width=1)
    create_eyes("blink", draw_eyes_blink)

    # Focused / Pointing: Sharp slanted tech aperture
    def draw_eyes_focused(d):
        for cx in [45, 135]:
            d.polygon([(cx - 22, 26), (cx + 22, 20), (cx + 18, 58), (cx - 18, 62)], fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=2)
            d.polygon([(cx - 14, 30), (cx + 14, 26), (cx + 10, 52), (cx - 10, 56)], fill=C_CORE_PULSE)
    create_eyes("focused", draw_eyes_focused)

    # Wide / Alert: Circular expanded aperture
    def draw_eyes_wide(d):
        for cx in [45, 135]:
            d.ellipse([cx - 26, 14, cx + 26, 66], fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=3)
            d.ellipse([cx - 16, 24, cx + 16, 56], fill=C_CORE_PULSE)
            d.ellipse([cx - 8, 28, cx, 36], fill=C_WHITE)
    create_eyes("wide", draw_eyes_wide)

    # 3. Preston Blair 9-Viseme Digital Mouth Waveforms (100x50 each)
    def create_mouth(name: str, draw_fn) -> None:
        img = Image.new("RGBA", (100, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_fn(draw)
        img.save(bundle_dir / "head" / "mouth" / f"{name}.png")

    # Rest: Sleek resting neon line
    create_mouth("rest", lambda d: d.rounded_rectangle([32, 22, 68, 28], radius=3, fill=C_CORE_PULSE, outline=C_NEON_CYAN, width=1))

    # Smile: Curved glowing neon smile arc
    create_mouth("smile", lambda d: d.arc([30, 12, 70, 36], start=10, end=170, fill=C_CORE_PULSE, width=5))

    # Open Smile: Cheerful neon acoustic aperture with tooth beam
    def draw_open_smile(d):
        d.pieslice([28, 10, 72, 42], start=0, end=180, fill=C_VISOR_BG, outline=C_NEON_CYAN, width=3)
        d.rounded_rectangle([34, 11, 66, 19], radius=3, fill=C_CORE_PULSE)
        d.ellipse([38, 25, 62, 39], fill=C_NEON_GLOW)
    create_mouth("open_smile", draw_open_smile)

    # A_I: Wide speech aperture (high dynamic range acoustic wave)
    def draw_A_I(d):
        d.pieslice([25, 8, 75, 45], start=0, end=180, fill=C_VISOR_BG, outline=C_NEON_CYAN, width=4)
        d.rounded_rectangle([32, 9, 68, 17], radius=3, fill=C_CORE_PULSE)
        d.ellipse([35, 27, 65, 42], fill=C_NEON_GLOW)
    create_mouth("A_I", draw_A_I)

    # E: Segmented digital matrix sound bar
    def draw_E(d):
        d.rounded_rectangle([25, 16, 75, 34], radius=6, fill=C_VISOR_BG, outline=C_NEON_CYAN, width=3)
        for x in [30, 38, 46, 54, 62]:
            d.line([(x, 19), (x, 31)], fill=C_CORE_PULSE, width=3)
    create_mouth("E", draw_E)

    # O: Concentric circular neon ring
    def draw_O(d):
        d.ellipse([34, 10, 66, 42], fill=C_VISOR_BG, outline=C_CORE_PULSE, width=4)
        d.ellipse([42, 18, 58, 34], fill=C_NEON_GLOW)
    create_mouth("O", draw_O)

    # U: Compact high-frequency resonant circle
    create_mouth("U", lambda d: d.ellipse([38, 16, 62, 38], fill=C_VISOR_BG, outline=C_CORE_PULSE, width=4))

    # M_B_P: Compressed closed baseline pulse
    create_mouth("M_B_P", lambda d: d.line([(28, 25), (72, 25)], fill=C_CORE_PULSE, width=5))

    # F_V: Tucked upper teeth laser notch
    def draw_F_V(d):
        d.rounded_rectangle([30, 18, 70, 32], radius=4, fill=C_VISOR_BG, outline=C_NEON_CYAN, width=3)
        d.rectangle([36, 19, 64, 24], fill=C_CORE_PULSE)
    create_mouth("F_V", draw_F_V)

    # L_D_T_N: Peak waveform arc
    def draw_L(d):
        d.pieslice([28, 12, 72, 40], start=0, end=180, fill=C_VISOR_BG, outline=C_NEON_CYAN, width=3)
        d.rounded_rectangle([34, 13, 66, 20], radius=3, fill=C_CORE_PULSE)
        d.ellipse([42, 21, 58, 32], fill=C_NEON_GLOW)
    create_mouth("L_D_T_N", draw_L)

    # W_Q: Concentric pulse with lateral flares
    def draw_W_Q(d):
        d.ellipse([40, 18, 60, 36], fill=C_CORE_PULSE, outline=C_NEON_CYAN, width=2)
        d.line([(28, 27), (36, 27)], fill=C_NEON_GLOW, width=3)
        d.line([(64, 27), (72, 27)], fill=C_NEON_GLOW, width=3)
    create_mouth("W_Q", draw_W_Q)

    # 4. Aerodynamic Chassis Torso (240x260) with Reactor Core
    torso = Image.new("RGBA", (240, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(torso)

    # Main aerodynamic chest shell
    d.rounded_rectangle([35, 30, 205, 235], radius=42, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=6)
    # Carbon fiber side armor plates
    d.rounded_rectangle([28, 65, 58, 195], radius=14, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.rounded_rectangle([182, 65, 212, 195], radius=14, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)

    # Collar socket rim
    d.rounded_rectangle([80, 22, 160, 48], radius=10, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)

    # Center Arc Reactor Core with Pulsing Glow
    d.ellipse([92, 102, 148, 158], fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.ellipse([98, 108, 142, 152], fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=3)
    d.ellipse([108, 118, 132, 142], fill=C_CORE_PULSE)
    d.ellipse([114, 124, 126, 136], fill=C_WHITE)

    # Floating Magnetic Shoulder Emitter Sockets (Left and Right)
    d.ellipse([18, 38, 56, 76], fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.ellipse([26, 46, 48, 68], fill=C_NEON_CYAN)
    d.ellipse([184, 38, 222, 76], fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=4)
    d.ellipse([192, 46, 214, 68], fill=C_NEON_CYAN)
    torso.save(bundle_dir / "body" / "torso.png")

    # 5. Floating Magnetic Limbs (Upper Arm & Forearm) (64x100 each)
    # Upper Arm: Floating pod with magnetic levitation field rings (no hinge seams!)
    arm_up = Image.new("RGBA", (64, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(arm_up)
    # Magnetic levitation ring at top
    d.ellipse([14, 6, 50, 30], fill=C_NEON_GLOW, outline=C_OUTLINE, width=2)
    # Sleek floating capsule sleeve
    d.rounded_rectangle([16, 18, 48, 88], radius=16, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=5)
    # Carbon trim stripe
    d.rounded_rectangle([20, 34, 44, 52], radius=6, fill=C_CHASSIS_DARK)
    # Lower magnetic emitter ring
    d.ellipse([18, 72, 46, 92], fill=C_NEON_CYAN)
    arm_up.save(bundle_dir / "body" / "arm_upper.png")

    # Lower Arm (Forearm): Tapered aerodynamic pod
    arm_low = Image.new("RGBA", (64, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(arm_low)
    # Top magnetic floating ring
    d.ellipse([16, 6, 48, 26], fill=C_NEON_GLOW, outline=C_OUTLINE, width=2)
    # Sleek forearm sleeve
    d.rounded_rectangle([16, 18, 48, 88], radius=15, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=5)
    # Cyan telemetry glow strip
    d.rounded_rectangle([24, 32, 40, 72], radius=6, fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=2)
    arm_low.save(bundle_dir / "body" / "arm_lower.png")

    # 6. High-Tech Floating Magnetic Hands (72x72 each)
    def create_hand(name: str, draw_fn) -> None:
        img = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_fn(draw)
        img.save(bundle_dir / "body" / "hands" / f"{name}.png")

    # Rest Hand: Floating relaxed glove with cyan knuckle nodes
    def draw_hand_rest(d):
        d.ellipse([14, 14, 58, 58], fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        d.ellipse([26, 26, 46, 46], fill=C_CHASSIS_DARK)
        d.ellipse([31, 31, 41, 41], fill=C_NEON_CYAN)
    create_hand("rest", draw_hand_rest)

    # Point Hand: Precise index finger extended with laser emitter tip
    def draw_hand_point(d):
        d.ellipse([18, 26, 54, 62], fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        # Pointing index finger
        d.rounded_rectangle([16, 4, 32, 44], radius=8, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        # Laser emitter tip on index
        d.ellipse([20, 4, 28, 14], fill=C_NEON_CYAN, outline=C_CORE_PULSE, width=2)
        d.ellipse([30, 36, 42, 48], fill=C_NEON_GLOW)
    create_hand("point", draw_hand_point)

    # Thumbs Up Hand: Clean confident thumbs up with glowing thumb knuckle
    def draw_hand_thumbs_up(d):
        d.ellipse([16, 22, 56, 62], fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        # Raised thumb
        d.rounded_rectangle([18, 4, 34, 38], radius=8, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        d.ellipse([21, 8, 31, 18], fill=C_CORE_PULSE)
    create_hand("thumbs_up", draw_hand_thumbs_up)

    # Waving / Open Hand
    def draw_hand_wave(d):
        d.ellipse([16, 24, 56, 62], fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=4)
        for fx in [18, 28, 38, 48]:
            d.rounded_rectangle([fx, 6, fx + 9, 32], radius=4, fill=C_CHASSIS_LIGHT, outline=C_OUTLINE, width=3)
        d.ellipse([28, 34, 44, 50], fill=C_NEON_CYAN)
    create_hand("wave", draw_hand_wave)

    # 7. Holographic Light Stylus / Laser Pointer Prop (28x190)
    prop = Image.new("RGBA", (28, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(prop)
    # Sleek matte titanium handle at hand grip
    d.rounded_rectangle([9, 5, 19, 160], radius=5, fill=C_CHASSIS_DARK, outline=C_OUTLINE, width=3)
    # Cyan telemetry grip ring
    d.rounded_rectangle([7, 30, 21, 50], radius=4, fill=C_NEON_CYAN)
    # Holographic laser emitter bulb at tip extending outwards
    d.ellipse([4, 166, 24, 186], fill=C_NEON_GLOW, outline=C_OUTLINE, width=3)
    d.ellipse([8, 170, 20, 182], fill=C_CORE_PULSE)
    d.ellipse([11, 173, 17, 179], fill=C_WHITE)
    prop.save(bundle_dir / "props" / "hologram_pointer.png")


    # 8. Manifest with Physics and Joint Constraints
    manifest = MascotManifest(
        id="nexus_bot",
        name="Nexus Bot",
        version="1.0.0",
        description="Flagship sleek futuristic tech companion with floating magnetic articulation and emissive visor.",
        canvas_size=(1000, 1000),
        bones={
            "root": BoneConfig(position=(500, 800), pivot=(0, 0), z_index=0),
            "torso": BoneConfig(
                parent="root",
                position=(0, -260),
                pivot=(0, 0),
                z_index=10,
                physics=PhysicsConfig(stiffness=140.0, damping=16.0, mass=1.2)
            ),
            "head": BoneConfig(
                parent="torso",
                position=(0, -110),
                pivot=(0, 0),
                z_index=20,
                physics=PhysicsConfig(stiffness=190.0, damping=18.0, mass=0.9),
                constraints=JointConstraintConfig(min_rotation_deg=-35.0, max_rotation_deg=35.0)
            ),
            "antenna": BoneConfig(
                parent="head",
                position=(0, -145),
                pivot=(0, 20),
                length=30,
                z_index=25,
                physics=PhysicsConfig(stiffness=220.0, damping=10.0, mass=0.3, resting_offset_deg=0.0)
            ),
            "arm_l_upper": BoneConfig(
                parent="torso",
                position=(-75, -70),
                pivot=(0, 0),
                length=80,
                z_index=14,
                physics=PhysicsConfig(stiffness=160.0, damping=14.0, mass=0.7)
            ),
            "arm_l_lower": BoneConfig(
                parent="arm_l_upper",
                position=(0, 80),
                pivot=(0, 0),
                length=80,
                z_index=15
            ),
            "hand_l": BoneConfig(parent="arm_l_lower", position=(0, 80), pivot=(0, 0), z_index=16),
            "arm_r_upper": BoneConfig(
                parent="torso",
                position=(75, -70),
                pivot=(0, 0),
                length=80,
                z_index=17,
                physics=PhysicsConfig(stiffness=160.0, damping=14.0, mass=0.7)
            ),
            "arm_r_lower": BoneConfig(
                parent="arm_r_upper",
                position=(0, 80),
                pivot=(0, 0),
                length=80,
                z_index=18
            ),
            "hand_r": BoneConfig(parent="arm_r_lower", position=(0, 80), pivot=(0, 0), z_index=19),
            "prop_r": BoneConfig(
                parent="hand_r",
                position=(0, 10),
                pivot=(0, 0),
                z_index=20,
                physics=PhysicsConfig(stiffness=240.0, damping=12.0, mass=0.4)
            )
        },
        slots={
            "torso": SlotConfig(
                bone="torso",
                default_attachment="default",
                offset=(-120, -130),
                attachments={"default": "body/torso.png"},
                z_index=1
            ),
            "head_base": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-160, -250),
                attachments={"default": "head/head_base.png"},
                z_index=1
            ),
            "eyes": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-90, -180),
                attachments={
                    "default": "head/eyes/default.png",
                    "happy": "head/eyes/happy.png",
                    "wink": "head/eyes/wink.png",
                    "blink": "head/eyes/blink.png",
                    "focused": "head/eyes/focused.png",
                    "wide": "head/eyes/wide.png"
                },
                z_index=2
            ),
            "mouth": SlotConfig(
                bone="head",
                default_attachment="smile",
                offset=(-50, -100),
                attachments={
                    "smile": "head/mouth/smile.png",
                    "open_smile": "head/mouth/open_smile.png",
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
                z_index=3
            ),
            "arm_l_up": SlotConfig(
                bone="arm_l_upper",
                offset=(-32, -20),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_l_low": SlotConfig(
                bone="arm_l_lower",
                offset=(-32, -15),
                attachments={"default": "body/arm_lower.png"},
                z_index=1
            ),
            "hand_l": SlotConfig(
                bone="hand_l",
                default_attachment="rest",
                offset=(-36, -20),
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
                offset=(-32, -20),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_r_low": SlotConfig(
                bone="arm_r_lower",
                offset=(-32, -15),
                attachments={"default": "body/arm_lower.png"},
                z_index=1
            ),
            "hand_r": SlotConfig(
                bone="hand_r",
                default_attachment="rest",
                offset=(-36, -20),
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
                offset=(-14, 0),
                attachments={
                    "none": "",
                    "pointer_stick": "props/hologram_pointer.png",
                    "hologram_pointer": "props/hologram_pointer.png"
                },
                z_index=3
            )

        },
        viseme_slot="mouth",
        visemes={
            "rest": "rest",
            "smile": "smile",
            "open_smile": "open_smile",
            "A_I": "A_I",
            "E": "E",
            "O": "O",
            "U": "U",
            "M_B_P": "M_B_P",
            "F_V": "F_V",
            "L_D_T_N": "L_D_T_N",
            "W_Q": "W_Q"
        },
        palette_tokens={
            "chassis_dark": "#1e293b",
            "chassis_light": "#f1f5f9",
            "neon_cyan": "#06b6d4",
            "core_pulse": "#00f5ff"
        }
    )

    with open(bundle_dir / "manifest.json", "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return bundle_dir
