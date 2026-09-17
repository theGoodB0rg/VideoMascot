from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from videomascot.models.manifest import (
    MascotManifest,
    BoneConfig,
    SlotConfig,
    PhysicsConfig,
    JointConstraintConfig
)


def create_starter_brick_dev(output_dir: Path) -> Path:
    """Generates the photorealistic 3D 'Brick Minifigure Senior Developer' (Brick Dev) mascot bundle
    in the likeness of a 3D CGI Lego-style software engineer with textured curly afro hair, trimmed mustache/goatee,
    striped sky-blue polo shirt, and classic C-hands, waist-up without prop accessories.
    
    Adopts professional industry-standard 2.5D animation architecture (Adobe Character Animator Swap Sets &
    Spine Slot Attachment Switching):
    - Ground-truth photorealistic 3D body pose bank (Rest, Wave, Point Up-Right, Point Up-Left)
      preserving continuous, unbroken 3D sculpted plastic limb curvature with zero joint slicing/creasing.
    - Matching 3D facial expressions for each ground-truth pose.
    - Full Preston Blair 9-viseme dynamic acoustic speech mouth slot (clean transparent printed decals) for real-time lip-sync.
    - Head bone articulation on the neck for natural speech bobbing, physics, and breathing.
    """
    bundle_dir = output_dir / "brick_dev"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    (bundle_dir / "head").mkdir(exist_ok=True)
    (bundle_dir / "head" / "eyes").mkdir(exist_ok=True)
    (bundle_dir / "head" / "mouth").mkdir(exist_ok=True)
    (bundle_dir / "body").mkdir(exist_ok=True)
    (bundle_dir / "body" / "hands").mkdir(exist_ok=True)

    # -------------------------------------------------------------
    # Palette Constants
    # -------------------------------------------------------------
    C_LIP = (24, 16, 14, 255)
    C_CAVITY = (45, 15, 22, 255)
    C_TEETH = (255, 255, 255, 255)
    C_TONGUE = (220, 80, 95, 255)

    # Find 3D source renders
    possible_sources = [
        Path("preview/brick_dev_perfect_cutout.png"),
        Path("preview/brick_dev/pose_neutral_rest.png"),
        Path("preview/pymatting_cutout.png"),
        Path("C:/Users/HP/.gemini/antigravity/brain/05b13561-3b49-4578-838b-bf57f8a31539/brick_dev_waist_up_1789421885708.jpg"),
    ]
    src_rest_path = None
    for p in possible_sources:
        if p.is_file():
            src_rest_path = p
            break

    possible_wave = [
        Path("preview/brick_dev_wave_cutout.png"),
        Path("C:/Users/HP/.gemini/antigravity/brain/05b13561-3b49-4578-838b-bf57f8a31539/brick_dev_wave_1789422002208.jpg"),
    ]
    src_wave_path = None
    for p in possible_wave:
        if p.is_file():
            src_wave_path = p
            break

    possible_point = [
        Path("preview/brick_dev_point_cutout.png"),
        Path("C:/Users/HP/.gemini/antigravity/brain/05b13561-3b49-4578-838b-bf57f8a31539/brick_dev_point_1789422033181.jpg"),
    ]
    src_point_path = None
    for p in possible_point:
        if p.is_file():
            src_point_path = p
            break

    if src_rest_path:
        src_rest = Image.open(src_rest_path).convert("RGBA").resize((1000, 1000), Image.LANCZOS)
        src_wave = Image.open(src_wave_path).convert("RGBA").resize((1000, 1000), Image.LANCZOS) if src_wave_path else src_rest
        src_point = Image.open(src_point_path).convert("RGBA").resize((1000, 1000), Image.LANCZOS) if src_point_path else src_rest

        # 1. Head Attachments: 3D sculpted heads matching each pose's facial expression
        def clean_head_mouth(head_img: Image.Image) -> Image.Image:
            """Cleans the static smile from the base head so moving viseme decals don't collide or double-overlay."""
            arr = np.array(head_img)
            # Interpolate skin gradient between mustache (y=325) and goatee (y=358)
            top_skin = arr[325, 150:250].astype(float)
            bot_skin = arr[358, 150:250].astype(float)
            for y in range(326, 358):
                alpha = (y - 326) / 32.0
                arr[y, 150:250] = (1.0 - alpha) * top_skin + alpha * bot_skin
            res = Image.fromarray(arr)
            # Soften blending
            mask = Image.new("L", head_img.size, 0)
            d = ImageDraw.Draw(mask)
            d.ellipse([155, 326, 245, 356], fill=255)
            from PIL import ImageFilter
            blurred = res.filter(ImageFilter.GaussianBlur(1.5))
            res.paste(blurred, mask=mask)
            return res

        head_rest = clean_head_mouth(src_rest.crop((300, 20, 700, 440)))
        head_wave = clean_head_mouth(src_wave.crop((300, 20, 700, 440)))
        head_point = clean_head_mouth(src_point.crop((300, 20, 700, 440)))

        head_rest.save(bundle_dir / "head" / "head_base.png")
        head_rest.save(bundle_dir / "head" / "head_rest.png")
        head_wave.save(bundle_dir / "head" / "head_wave.png")
        head_point.save(bundle_dir / "head" / "head_point.png")

        # 2. Pose Library / Swap Sets: Continuous unbroken 3D bodies for each gesture
        def make_body_pose(src_img: Image.Image) -> Image.Image:
            b = src_img.copy()
            d = ImageDraw.Draw(b)
            # Mask out head region above the collar line (y=430)
            d.rectangle([300, 0, 700, 430], fill=(0, 0, 0, 0))
            return b

        body_rest = make_body_pose(src_rest)
        body_wave = make_body_pose(src_wave)
        body_point_r = make_body_pose(src_point)
        body_point_l = body_point_r.transpose(Image.FLIP_LEFT_RIGHT)

        body_rest.save(bundle_dir / "body" / "torso.png")
        body_rest.save(bundle_dir / "body" / "torso_rest.png")
        body_wave.save(bundle_dir / "body" / "torso_wave.png")
        body_point_r.save(bundle_dir / "body" / "torso_point_r.png")
        body_point_l.save(bundle_dir / "body" / "torso_point_l.png")

        # 3. Transparent 1x1 placeholders for limb and hair slots
        # In professional swap-set architecture, the 3D limbs are continuous and sculpted with the torso
        trans_1x1 = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        trans_1x1.save(bundle_dir / "head" / "hair.png")
        trans_1x1.save(bundle_dir / "head" / "eyebrows.png")
        trans_1x1.save(bundle_dir / "head" / "beard.png")
        trans_1x1.save(bundle_dir / "head" / "eyes" / "default.png")
        trans_1x1.save(bundle_dir / "head" / "eyes" / "happy.png")
        trans_1x1.save(bundle_dir / "head" / "eyes" / "focused.png")
        trans_1x1.save(bundle_dir / "head" / "eyes" / "wide.png")
        trans_1x1.save(bundle_dir / "body" / "arm_upper.png")
        trans_1x1.save(bundle_dir / "body" / "arm_lower.png")
        for h in [
            "rest_l", "rest_r", "rest",
            "point_l", "point_r", "point",
            "wave_l", "wave_r", "wave",
            "thumbs_up_l", "thumbs_up_r", "thumbs_up"
        ]:
            trans_1x1.save(bundle_dir / "body" / "hands" / f"{h}.png")

        # Blink and Wink eyelid decals
        def make_eyelid_decal(draw_fn, w=220, h=90) -> Image.Image:
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            draw_fn(d, w, h)
            return img

        make_eyelid_decal(lambda d, w, h: [
            d.arc([cx - 22, 35, cx + 22, 60], start=10, end=170, fill=(24, 20, 18, 255), width=5)
            for cx in [60, 160]
        ]).save(bundle_dir / "head" / "eyes" / "blink.png")

        make_eyelid_decal(lambda d, w, h: [
            d.arc([60 - 22, 35, 60 + 22, 60], start=10, end=170, fill=(24, 20, 18, 255), width=5)
        ]).save(bundle_dir / "head" / "eyes" / "wink.png")

        # 4. Clean Printed Mouth Viseme Decals (Transparent background, fits between mustache and goatee)
        def make_decal(draw_fn, w=100, h=44) -> Image.Image:
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            draw_fn(d, w, h)
            return img

        # Smile / Rest
        make_decal(lambda d, w, h: d.arc([15, 8, w - 15, 36], start=10, end=170, fill=C_LIP, width=4)).save(bundle_dir / "head" / "mouth" / "smile.png")
        make_decal(lambda d, w, h: d.arc([15, 8, w - 15, 36], start=10, end=170, fill=C_LIP, width=4)).save(bundle_dir / "head" / "mouth" / "rest.png")

        # Open Smile
        make_decal(lambda d, w, h: (
            d.pieslice([14, 6, w - 14, 38], start=0, end=180, fill=C_CAVITY, outline=C_LIP, width=3),
            d.rectangle([24, 7, w - 24, 16], fill=C_TEETH),
            d.ellipse([28, 22, w - 28, 36], fill=C_TONGUE)
        )).save(bundle_dir / "head" / "mouth" / "open_smile.png")

        # A_I
        make_decal(lambda d, w, h: (
            d.pieslice([12, 4, w - 12, 40], start=0, end=180, fill=C_CAVITY, outline=C_LIP, width=4),
            d.rectangle([22, 5, w - 22, 15], fill=C_TEETH),
            d.ellipse([26, 24, w - 26, 38], fill=C_TONGUE)
        )).save(bundle_dir / "head" / "mouth" / "A_I.png")

        # E
        make_decal(lambda d, w, h: (
            d.rounded_rectangle([14, 10, w - 14, 34], radius=6, fill=C_TEETH, outline=C_LIP, width=3),
            d.line([(18, 22), (w - 18, 22)], fill=C_LIP, width=3)
        )).save(bundle_dir / "head" / "mouth" / "E.png")

        # O
        make_decal(lambda d, w, h: (
            d.ellipse([25, 4, w - 25, 40], fill=C_CAVITY, outline=C_LIP, width=4),
            d.ellipse([30, 24, w - 30, 36], fill=C_TONGUE)
        )).save(bundle_dir / "head" / "mouth" / "O.png")

        # U
        make_decal(lambda d, w, h: (
            d.ellipse([32, 10, w - 32, 34], fill=C_CAVITY, outline=C_LIP, width=4)
        )).save(bundle_dir / "head" / "mouth" / "U.png")

        # M_B_P
        make_decal(lambda d, w, h: (
            d.line([(18, 22), (w - 18, 22)], fill=C_LIP, width=5)
        )).save(bundle_dir / "head" / "mouth" / "M_B_P.png")

        # F_V
        make_decal(lambda d, w, h: (
            d.rounded_rectangle([20, 12, w - 20, 32], radius=5, fill=C_CAVITY, outline=C_LIP, width=3),
            d.rectangle([26, 13, w - 26, 20], fill=C_TEETH)
        )).save(bundle_dir / "head" / "mouth" / "F_V.png")

        # L_D_T_N
        make_decal(lambda d, w, h: (
            d.pieslice([16, 8, w - 16, 36], start=0, end=180, fill=C_CAVITY, outline=C_LIP, width=3),
            d.rectangle([24, 9, w - 24, 16], fill=C_TEETH),
            d.ellipse([32, 15, w - 32, 24], fill=C_TONGUE)
        )).save(bundle_dir / "head" / "mouth" / "L_D_T_N.png")

        # W_Q
        make_decal(lambda d, w, h: (
            d.ellipse([34, 14, w - 34, 32], fill=C_CAVITY, outline=C_LIP, width=4)
        )).save(bundle_dir / "head" / "mouth" / "W_Q.png")

    # -------------------------------------------------------------
    # 5. Manifest Architecture (Waist-Up Framing, Canvas 1000x1000)
    # -------------------------------------------------------------
    manifest = MascotManifest(
        id="brick_dev",
        name="Brick Dev",
        version="1.0.0",
        description="Photorealistic 3D Lego Minifigure Senior Developer with Swap Sets and 9-viseme lip-sync.",
        canvas_size=(1000, 1000),
        bones={
            "root": BoneConfig(
                position=(500.0, 780.0),
                pivot=(0.0, 0.0),
                z_index=0
            ),
            "torso": BoneConfig(
                parent="root",
                position=(0.0, -110.0),
                pivot=(0.0, 0.0),
                z_index=10,
                physics=PhysicsConfig(stiffness=150.0, damping=15.0, mass=1.0)
            ),
            "head": BoneConfig(
                parent="torso",
                position=(0.0, -440.0),
                pivot=(0.0, 0.0),
                z_index=20,
                physics=PhysicsConfig(stiffness=180.0, damping=16.0, mass=0.8),
                constraints=JointConstraintConfig(min_rotation_deg=-30.0, max_rotation_deg=30.0)
            ),
            "arm_l_upper": BoneConfig(
                parent="torso",
                position=(-144.0, -220.0),
                pivot=(0.0, 0.0),
                length=130.0,
                z_index=14,
                physics=PhysicsConfig(stiffness=160.0, damping=14.0, mass=0.7)
            ),
            "arm_l_lower": BoneConfig(
                parent="arm_l_upper",
                position=(0.0, 130.0),
                pivot=(0.0, 0.0),
                length=130.0,
                z_index=15
            ),
            "hand_l": BoneConfig(
                parent="arm_l_lower",
                position=(0.0, 130.0),
                pivot=(0.0, 0.0),
                z_index=16
            ),
            "arm_r_upper": BoneConfig(
                parent="torso",
                position=(144.0, -220.0),
                pivot=(0.0, 0.0),
                length=130.0,
                z_index=17,
                physics=PhysicsConfig(stiffness=160.0, damping=14.0, mass=0.7)
            ),
            "arm_r_lower": BoneConfig(
                parent="arm_r_upper",
                position=(0.0, 130.0),
                pivot=(0.0, 0.0),
                length=130.0,
                z_index=18
            ),
            "hand_r": BoneConfig(
                parent="arm_r_lower",
                position=(0.0, 130.0),
                pivot=(0.0, 0.0),
                z_index=19
            )
        },
        slots={
            "torso": SlotConfig(
                bone="torso",
                default_attachment="default",
                offset=(-500.0, -670.0),
                attachments={
                    "default": "body/torso.png",
                    "happy_wave": "body/torso_wave.png",
                    "point_up_right": "body/torso_point_r.png",
                    "point_up_left": "body/torso_point_l.png",
                    "thumbs_up": "body/torso_point_r.png",
                    "thinking": "body/torso.png"
                },
                z_index=1
            ),
            "head_base": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-200.0, -210.0),
                attachments={
                    "default": "head/head_base.png",
                    "happy_wave": "head/head_wave.png",
                    "point_up_right": "head/head_point.png",
                    "point_up_left": "head/head_point.png",
                    "thumbs_up": "head/head_point.png",
                    "thinking": "head/head_base.png"
                },
                z_index=2
            ),
            "hair": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "head/hair.png"},
                z_index=6
            ),
            "eyebrows": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "head/eyebrows.png"},
                z_index=3
            ),
            "eyes": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-110.0, -30.0),
                attachments={
                    "default": "head/eyes/default.png",
                    "happy": "head/eyes/happy.png",
                    "blink": "head/eyes/blink.png",
                    "focused": "head/eyes/focused.png",
                    "wink": "head/eyes/wink.png",
                    "wide": "head/eyes/wide.png"
                },
                z_index=4
            ),
            "beard": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "head/beard.png"},
                z_index=4
            ),
            "mouth": SlotConfig(
                bone="head",
                default_attachment="smile",
                offset=(-50.0, 95.0),
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
                z_index=5
            ),
            "arm_l_up": SlotConfig(
                bone="arm_l_upper",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_l_low": SlotConfig(
                bone="arm_l_lower",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "body/arm_lower.png"},
                z_index=2
            ),
            "hand_l": SlotConfig(
                bone="hand_l",
                default_attachment="rest",
                offset=(0.0, 0.0),
                attachments={
                    "rest": "body/hands/rest_l.png",
                    "point": "body/hands/point_l.png",
                    "wave": "body/hands/wave_l.png",
                    "thumbs_up": "body/hands/thumbs_up_l.png"
                },
                z_index=3
            ),
            "arm_r_up": SlotConfig(
                bone="arm_r_upper",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "body/arm_upper.png"},
                z_index=1
            ),
            "arm_r_low": SlotConfig(
                bone="arm_r_lower",
                default_attachment="default",
                offset=(0.0, 0.0),
                attachments={"default": "body/arm_lower.png"},
                z_index=2
            ),
            "hand_r": SlotConfig(
                bone="hand_r",
                default_attachment="rest",
                offset=(0.0, 0.0),
                attachments={
                    "rest": "body/hands/rest_r.png",
                    "point": "body/hands/point_r.png",
                    "wave": "body/hands/wave_r.png",
                    "thumbs_up": "body/hands/thumbs_up_r.png"
                },
                z_index=3
            )
        },
        visemes={
            "smile": "smile",
            "open_smile": "open_smile",
            "rest": "rest",
            "A_I": "A_I",
            "E": "E",
            "O": "O",
            "U": "U",
            "M_B_P": "M_B_P",
            "F_V": "F_V",
            "L_D_T_N": "L_D_T_N",
            "W_Q": "W_Q"
        },
        viseme_slot="mouth"
    )

    manifest_path = bundle_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return bundle_dir
