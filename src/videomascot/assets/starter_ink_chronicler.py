"""The Ink Chronicler: an engraved presenter for painterly history documentaries.

Why engraving rather than a painterly render. A flat-vector chibi in an oil-painted ancient
history piece is a register mismatch no amount of animation quality fixes, but faking oil
paint with drawing primitives looks cheap. Engraving is the honest third option: it is line
and hatch, which is exactly what PIL is good at, it is period-legible for any pre-modern
subject, and it already matches the Gilded Archival Woodblock signature the host brands its
stills with (warm amber rim light over tactile paper grain).

The figure is a hooded chronicler, deliberately era- and culture-neutral in silhouette, so
one character can carry Egypt, Mali and Rome without impersonating any of them.

The rig is bone-for-bone identical to ``chibi_tech_guide``: same canvas, same bone
positions, same slot offsets, same sprite dimensions. That is not laziness, it is the
contract. The sequencer's gesture poses are hand-tuned joint angles against that skeleton,
so matching it means all eight gestures work on day one.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from videomascot.models.manifest import (
    MascotManifest,
    BoneConfig,
    SlotConfig,
    PresentationProfileConfig,
    RigControlsConfig,
)

# Sepia ink on warm paper. No pure black and no pure white: an engraving sits in the
# paper's own value range, and pure black reads as vector clip-art over a painted plate.
INK = (38, 28, 20, 255)
INK_SOFT = (74, 58, 44, 255)
PAPER = (236, 222, 196, 255)
SKIN = (210, 172, 132, 255)
SKIN_SHADE = (176, 136, 96, 255)
ROBE = (78, 62, 48, 255)
ROBE_SHADE = (52, 41, 31, 255)
ROBE_LIGHT = (104, 84, 64, 255)
AMBER = (198, 142, 58, 255)
AMBER_LIGHT = (236, 188, 104, 255)
MOUTH_DARK = (92, 54, 40, 255)

OUTLINE = 5


def _hatch(size, mask_shape, color=INK_SOFT, spacing=7, width=2, slope=1):
    """Parallel hatch lines clipped to a shape: the engraver's way of shading.

    ``mask_shape`` draws the region to keep onto an ``L`` mask in white.
    """
    width_px, height_px = size
    lines = Image.new("RGBA", size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(lines)
    for offset in range(-height_px, width_px + height_px, spacing):
        pen.line([(offset, 0), (offset + slope * height_px, height_px)], fill=color, width=width)

    mask = Image.new("L", size, 0)
    mask_shape(ImageDraw.Draw(mask))
    lines.putalpha(ImageChops.multiply(lines.getchannel("A"), mask))
    return lines


def _paper_grain(size, strength=10):
    """Faint tooth, so flat fills read as printed rather than as vector fills."""
    import random

    noise = Image.new("L", size, 128)
    pixels = noise.load()
    rng = random.Random(20261020)  # fixed: bundles must regenerate byte-identically
    for y in range(size[1]):
        for x in range(size[0]):
            pixels[x, y] = 128 + rng.randint(-strength, strength)
    return noise.filter(ImageFilter.SMOOTH)


def _grained(image):
    """Multiply faint grain through an RGBA sprite without touching its alpha."""
    grain = _paper_grain(image.size).convert("RGB")
    rgb = Image.composite(
        ImageChops.multiply(image.convert("RGB"), grain.point(lambda v: 160 + v // 4)),
        image.convert("RGB"),
        Image.new("L", image.size, 60),
    )
    out = rgb.convert("RGBA")
    out.putalpha(image.getchannel("A"))
    return out


def create_starter_ink_chronicler(output_dir: Path) -> Path:
    """Generate the ``ink_chronicler`` bundle into ``output_dir``."""
    bundle_dir = Path(output_dir) / "ink_chronicler"
    for sub in ("head/eyes", "head/mouth", "head/eyebrows", "body/hands", "props"):
        (bundle_dir / sub).mkdir(parents=True, exist_ok=True)

    _draw_head(bundle_dir)
    _draw_eyes(bundle_dir)
    _draw_eyebrows(bundle_dir)
    _draw_mouths(bundle_dir)
    _draw_body(bundle_dir)
    _draw_hands(bundle_dir)
    _draw_props(bundle_dir)

    manifest = _build_manifest()
    manifest.validate_presentation()
    (bundle_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return bundle_dir


def _draw_head(bundle_dir: Path) -> None:
    """300x280. Face and cowl only: eyes, brows and mouth are separate animated slots.

    The cowl has to drape *outside* the face silhouette and fall past the jaw, or it reads
    as a bob haircut rather than a hood. The face oval is correspondingly narrow, which is
    also what keeps an adult out of chibi proportions on a shared chibi skeleton.
    """
    image = Image.new("RGBA", (300, 280), (0, 0, 0, 0))

    # Cowl back: a wide draped mass behind everything, reaching the canvas edges.
    back = Image.new("RGBA", image.size, (0, 0, 0, 0))
    back_pen = ImageDraw.Draw(back)
    back_pen.polygon(
        [(150, 4), (248, 44), (280, 170), (266, 272), (34, 272), (20, 170), (52, 44)],
        fill=ROBE, outline=INK,
    )
    back_pen.line(
        [(150, 4), (248, 44), (280, 170), (266, 272), (34, 272), (20, 170), (52, 44), (150, 4)],
        fill=INK, width=OUTLINE, joint="curve",
    )
    back.alpha_composite(_hatch(
        back.size,
        lambda d: d.polygon([(150, 4), (52, 44), (20, 170), (34, 272), (150, 272)], fill=255),
        color=ROBE_SHADE, spacing=7, width=2, slope=1,
    ))
    image.alpha_composite(back)

    pen = ImageDraw.Draw(image)

    # Neck, in the cowl's shadow.
    pen.polygon([(120, 180), (180, 180), (186, 272), (114, 272)], fill=SKIN_SHADE, outline=INK)
    pen.line([(120, 180), (114, 272)], fill=INK, width=4)
    pen.line([(180, 180), (186, 272)], fill=INK, width=4)

    # Face: narrow and long, set down inside the hood's opening.
    face = [62, 34, 238, 246]
    pen.ellipse(face, fill=SKIN, outline=INK, width=OUTLINE)

    # Shading: a crescent down the shadowed cheek, formed by subtracting an offset
    # ellipse from the face. Masking to a half-bounding-box instead leaves a hard
    # vertical seam straight down the middle of the face, which reads as grime.
    def cheek_crescent(draw: ImageDraw.ImageDraw) -> None:
        draw.ellipse(face, fill=255)
        draw.ellipse([face[0] + 34, face[1] - 6, face[2] + 34, face[3] + 6], fill=0)

    image.alpha_composite(_hatch(
        image.size, cheek_crescent, color=SKIN_SHADE, spacing=9, width=1, slope=1,
    ))

    # A second crescent under the jaw, for weight.
    def jaw_crescent(draw: ImageDraw.ImageDraw) -> None:
        draw.ellipse(face, fill=255)
        draw.ellipse([face[0], face[1] - 30, face[2], face[3] - 30], fill=0)

    image.alpha_composite(_hatch(
        image.size, jaw_crescent, color=SKIN_SHADE, spacing=8, width=1, slope=-1,
    ))

    # Cowl front: the opening arch, drawn over the face so the hood sits on the brow.
    front = Image.new("RGBA", image.size, (0, 0, 0, 0))
    front_pen = ImageDraw.Draw(front)
    front_pen.pieslice([30, 0, 270, 230], 180, 360, fill=ROBE, outline=INK, width=OUTLINE)
    front_pen.pieslice([62, 26, 238, 250], 180, 360, fill=(0, 0, 0, 0))
    front_pen.arc([62, 26, 238, 250], 180, 360, fill=INK, width=OUTLINE)

    # The hatch mask must subtract the face opening too. Masking to the hood's bounding
    # pieslice alone paints hatching straight across the cleared face, which looks like
    # a shadow cast onto the cheek by nothing.
    def hood_shadow(draw: ImageDraw.ImageDraw) -> None:
        draw.pieslice([30, 0, 270, 230], 180, 272, fill=255)
        draw.ellipse([62, 26, 238, 250], fill=0)

    front.alpha_composite(_hatch(front.size, hood_shadow, color=ROBE_SHADE,
                                 spacing=7, width=2, slope=1))
    image.alpha_composite(front)

    # Amber rim along the lit side: the Gilded Archival Woodblock signature, one stroke.
    pen.arc([30, 0, 270, 230], 286, 358, fill=AMBER, width=5)
    pen.line([(248, 44), (280, 170)], fill=AMBER, width=4)
    pen.arc([62, 26, 238, 250], 300, 352, fill=AMBER_LIGHT, width=2)

    # Nose: one asymmetric side-plane line and a nostril tick. A centred vertical stroke
    # with a symmetric arc under it reads as a stick figure, not a face.
    pen.line([(146, 126), (140, 168)], fill=INK_SOFT, width=3)
    pen.arc([136, 158, 164, 178], 170, 300, fill=INK_SOFT, width=3)

    _grained(image).save(bundle_dir / "head" / "head_base.png")


def _draw_eyes(bundle_dir: Path) -> None:
    """50x65 sclera variants plus a 32x40 pupil, matching the shared rig."""
    eyes_dir = bundle_dir / "head" / "eyes"

    def sclera(mirror: bool) -> Image.Image:
        image = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
        pen = ImageDraw.Draw(image)
        pen.ellipse([4, 14, 46, 52], fill=PAPER, outline=INK, width=4)
        # Heavier lid line on the outer corner gives the eye a direction.
        if mirror:
            pen.arc([4, 10, 46, 52], 190, 290, fill=INK, width=5)
        else:
            pen.arc([4, 10, 46, 52], 250, 350, fill=INK, width=5)
        return image

    sclera(False).save(eyes_dir / "sclera_left.png")
    sclera(True).save(eyes_dir / "sclera_right.png")

    pupil = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    pen = ImageDraw.Draw(pupil)
    pen.ellipse([6, 10, 26, 30], fill=INK)
    pen.ellipse([12, 14, 18, 20], fill=PAPER)  # single catchlight
    pupil.save(eyes_dir / "pupil.png")

    blink = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    pen = ImageDraw.Draw(blink)
    pen.arc([4, 18, 46, 54], 200, 340, fill=INK, width=5)
    pen.line([(8, 36), (14, 44)], fill=INK_SOFT, width=2)
    pen.line([(42, 36), (36, 44)], fill=INK_SOFT, width=2)
    blink.save(eyes_dir / "eyelid_blink.png")

    happy = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    pen = ImageDraw.Draw(happy)
    pen.arc([4, 20, 46, 60], 180, 360, fill=INK, width=5)
    happy.save(eyes_dir / "eye_happy.png")

    focused = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    pen = ImageDraw.Draw(focused)
    pen.ellipse([4, 20, 46, 48], fill=PAPER, outline=INK, width=4)
    pen.arc([4, 14, 46, 48], 200, 340, fill=INK, width=6)  # lowered lid: scrutiny
    focused.save(eyes_dir / "eye_focused.png")

    wide = Image.new("RGBA", (50, 65), (0, 0, 0, 0))
    pen = ImageDraw.Draw(wide)
    pen.ellipse([2, 8, 48, 58], fill=PAPER, outline=INK, width=4)
    wide.save(eyes_dir / "eye_wide.png")


def _draw_eyebrows(bundle_dir: Path) -> None:
    """45x20. Heavy, slightly unruly: age and authority in two strokes."""
    brows_dir = bundle_dir / "head" / "eyebrows"
    for name, slope in (("left.png", 1), ("right.png", -1)):
        image = Image.new("RGBA", (45, 20), (0, 0, 0, 0))
        pen = ImageDraw.Draw(image)
        rise = 5 * slope
        pen.line([(4, 13 + rise), (40, 13 - rise)], fill=INK, width=7)
        for index in range(5):  # stray hairs, the engraved tell
            x = 8 + index * 7
            y = 13 + rise - int(2 * slope * index)
            pen.line([(x, y), (x + 3, y - 6)], fill=INK_SOFT, width=2)
        image.save(brows_dir / name)


def _draw_mouths(bundle_dir: Path) -> None:
    """80x50 visemes. All eleven the rig declares, so lip-sync never falls back."""
    mouth_dir = bundle_dir / "head" / "mouth"

    def blank():
        return Image.new("RGBA", (80, 50), (0, 0, 0, 0)), None

    def closed(curve: int, width: int = 5):
        image, _ = blank()
        pen = ImageDraw.Draw(image)
        pen.arc([18, 16 - curve, 62, 34 + curve], 0, 180, fill=INK, width=width)
        return image

    def open_shape(box, lip=4):
        image, _ = blank()
        pen = ImageDraw.Draw(image)
        pen.ellipse(box, fill=MOUTH_DARK, outline=INK, width=lip)
        return image

    shapes = {
        "rest": closed(0),
        "smile": closed(6),
        "open_smile": open_shape([22, 10, 58, 40]),
        "A_I": open_shape([22, 8, 58, 42]),
        "E": open_shape([20, 16, 60, 34]),
        "O": open_shape([28, 8, 52, 42]),
        "U": open_shape([32, 12, 48, 38]),
        "M_B_P": closed(-2, width=7),
        "F_V": None,
        "L_D_T_N": None,
        "W_Q": open_shape([30, 10, 50, 40]),
    }

    # F_V: lower lip tucked under the teeth.
    image = Image.new("RGBA", (80, 50), (0, 0, 0, 0))
    pen = ImageDraw.Draw(image)
    pen.rectangle([24, 16, 56, 24], fill=PAPER, outline=INK, width=3)
    pen.arc([22, 18, 58, 38], 0, 180, fill=INK, width=6)
    shapes["F_V"] = image

    # L_D_T_N: tongue visible against the upper teeth.
    image = Image.new("RGBA", (80, 50), (0, 0, 0, 0))
    pen = ImageDraw.Draw(image)
    pen.ellipse([22, 12, 58, 38], fill=MOUTH_DARK, outline=INK, width=4)
    pen.chord([30, 18, 50, 36], 180, 360, fill=SKIN_SHADE)
    shapes["L_D_T_N"] = image

    for name, image in shapes.items():
        image.save(mouth_dir / f"{name}.png")


def _draw_body(bundle_dir: Path) -> None:
    """220x240 robe, plus two 60x100 sleeve segments."""
    torso = Image.new("RGBA", (220, 240), (0, 0, 0, 0))
    pen = ImageDraw.Draw(torso)

    # A robe widens toward the hem, and it has to fill the canvas or it reads as a
    # jumper. The taper plus vertical folds is most of what says "not modern".
    body = [(66, 4), (154, 4), (212, 236), (8, 236)]
    pen.polygon(body, fill=ROBE, outline=INK)
    pen.line([*body, body[0]], fill=INK, width=OUTLINE, joint="curve")

    torso.alpha_composite(_hatch(
        torso.size,
        lambda d: d.polygon([(66, 4), (104, 4), (104, 236), (8, 236)], fill=255),
        color=ROBE_SHADE, spacing=8, width=2, slope=1,
    ))

    # Hanging folds: straight lines fanning from the shoulders to the hem.
    for top_x, bottom_x in ((88, 56), (110, 110), (132, 164)):
        pen.line([(top_x, 60), (bottom_x, 232)], fill=ROBE_SHADE, width=3)

    # Lit edge, opposite the hatching.
    pen.line([(154, 10), (206, 232)], fill=ROBE_LIGHT, width=6)
    pen.line([(159, 10), (211, 232)], fill=AMBER, width=3)

    # Collar and a stole running the full length: the amber trim that ties the figure
    # to the brand palette, and the strongest read at thumbnail size.
    pen.polygon([(66, 4), (154, 4), (110, 70)], fill=ROBE_SHADE, outline=INK)
    pen.line([(66, 4), (110, 70)], fill=AMBER, width=5)
    pen.line([(154, 4), (110, 70)], fill=AMBER, width=5)
    pen.line([(96, 70), (86, 234)], fill=AMBER, width=5)
    pen.line([(124, 70), (134, 234)], fill=AMBER, width=5)

    # Belt.
    pen.rectangle([46, 150, 176, 170], fill=ROBE_SHADE, outline=INK, width=3)
    pen.line([(46, 160), (176, 160)], fill=AMBER, width=3)

    _grained(torso).save(bundle_dir / "body" / "torso.png")

    def sleeve(taper: int) -> Image.Image:
        image = Image.new("RGBA", (60, 100), (0, 0, 0, 0))
        sleeve_pen = ImageDraw.Draw(image)
        shape = [(12, 6), (48, 6), (48 + taper, 94), (12 - taper, 94)]
        sleeve_pen.polygon(shape, fill=ROBE, outline=INK)
        sleeve_pen.line([*shape, shape[0]], fill=INK, width=4)
        image.alpha_composite(_hatch(
            image.size,
            lambda d: d.polygon([(12, 6), (30, 6), (30, 94), (12 - taper, 94)], fill=255),
            color=ROBE_SHADE, spacing=7, width=2, slope=1,
        ))
        return _grained(image)

    sleeve(4).save(bundle_dir / "body" / "arm_upper.png")
    sleeve(8).save(bundle_dir / "body" / "arm_lower.png")  # cuff flares


def _draw_hands(bundle_dir: Path) -> None:
    """One 60x60 rest hand and three 70x70 posed hands, matching the shared rig."""
    hands_dir = bundle_dir / "body" / "hands"

    rest = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    pen = ImageDraw.Draw(rest)
    pen.ellipse([12, 10, 48, 50], fill=SKIN, outline=INK, width=4)
    for index in range(3):
        pen.arc([16 + index * 6, 26, 40 + index * 6, 48], 0, 150, fill=INK_SOFT, width=2)
    rest.save(hands_dir / "rest.png")

    point = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    pen = ImageDraw.Draw(point)
    pen.ellipse([18, 26, 54, 62], fill=SKIN, outline=INK, width=4)
    pen.rounded_rectangle([30, 2, 44, 34], radius=7, fill=SKIN, outline=INK, width=4)
    point.save(hands_dir / "point.png")

    wave = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    pen = ImageDraw.Draw(wave)
    pen.ellipse([16, 24, 56, 62], fill=SKIN, outline=INK, width=4)
    for index in range(4):
        pen.rounded_rectangle([20 + index * 9, 8 + abs(index - 1) * 3, 29 + index * 9, 34],
                              radius=4, fill=SKIN, outline=INK, width=3)
    wave.save(hands_dir / "wave.png")

    thumbs = Image.new("RGBA", (70, 70), (0, 0, 0, 0))
    pen = ImageDraw.Draw(thumbs)
    pen.ellipse([18, 24, 54, 60], fill=SKIN, outline=INK, width=4)
    pen.rounded_rectangle([40, 6, 54, 30], radius=7, fill=SKIN, outline=INK, width=4)
    thumbs.save(hands_dir / "thumbs_up.png")


def _draw_props(bundle_dir: Path) -> None:
    """24x180, keyed ``pointer_stick`` for rig compatibility, drawn as a quill.

    The attachment key is the contract the director points at; the art is the character.
    """
    quill = Image.new("RGBA", (24, 180), (0, 0, 0, 0))
    pen = ImageDraw.Draw(quill)

    # Feather as one silhouette with an outline. Drawing it as separate barb strokes
    # reads as a striped rod at render scale, not as a plume.
    pen.polygon([(12, 30), (21, 76), (19, 124), (12, 140), (5, 124), (3, 76)],
                fill=PAPER, outline=INK)
    pen.line([(12, 30), (21, 76), (19, 124), (12, 140), (5, 124), (3, 76), (12, 30)],
             fill=INK, width=2, joint="curve")
    for index in range(7):  # barb ticks, suggesting vanes without striping the shape
        y = 54 + index * 11
        pen.line([(12, y), (6, y + 5)], fill=INK_SOFT, width=1)
        pen.line([(12, y), (18, y + 5)], fill=INK_SOFT, width=1)
    pen.line([(12, 34), (12, 170)], fill=INK, width=3)  # shaft
    pen.line([(13, 140), (13, 168)], fill=AMBER_LIGHT, width=2)
    pen.polygon([(12, 178), (7, 162), (17, 162)], fill=INK)  # nib
    quill.save(bundle_dir / "props" / "pointer_stick.png")


def _build_manifest() -> MascotManifest:
    """Bone-for-bone identical to chibi_tech_guide, so every tuned gesture pose applies."""
    return MascotManifest(
        id="ink_chronicler",
        name="Ink Chronicler",
        description=(
            "Engraved hooded chronicler for painterly history documentaries. Woodblock line "
            "and hatch on warm paper with an amber rim, era-neutral in silhouette."
        ),
        canvas_size=(800, 800),
        bones={
            "root": BoneConfig(position=(400, 700), pivot=(0, 0), z_index=0),
            "torso": BoneConfig(parent="root", position=(0, -220), pivot=(0, 0), z_index=10),
            "head": BoneConfig(parent="torso", position=(0, -85), pivot=(0, 0), z_index=20),
            "arm_l_upper": BoneConfig(parent="torso", position=(-65, -55), pivot=(0, 0), length=70, z_index=14),
            "arm_l_lower": BoneConfig(parent="arm_l_upper", position=(0, 70), pivot=(0, 0), length=70, z_index=15),
            "hand_l": BoneConfig(parent="arm_l_lower", position=(0, 70), pivot=(0, 0), z_index=16),
            "arm_r_upper": BoneConfig(parent="torso", position=(65, -55), pivot=(0, 0), length=70, z_index=17),
            "arm_r_lower": BoneConfig(parent="arm_r_upper", position=(0, 70), pivot=(0, 0), length=70, z_index=18),
            "hand_r": BoneConfig(parent="arm_r_lower", position=(0, 70), pivot=(0, 0), z_index=19),
            "prop_r": BoneConfig(parent="hand_r", position=(0, 10), pivot=(0, 0), z_index=20),
        },
        slots={
            "torso": SlotConfig(bone="torso", default_attachment="default", offset=(-110, -120),
                                attachments={"default": "body/torso.png"}, z_index=1),
            "head_base": SlotConfig(bone="head", default_attachment="default", offset=(-150, -240),
                                    attachments={"default": "head/head_base.png"}, z_index=1),
            "eye_l_sclera": SlotConfig(
                bone="head", default_attachment="default", offset=(-75, -135),
                attachments={
                    "default": "head/eyes/sclera_left.png",
                    "blink": "head/eyes/eyelid_blink.png",
                    "happy": "head/eyes/eye_happy.png",
                    "focused": "head/eyes/eye_focused.png",
                    "wide": "head/eyes/eye_wide.png",
                },
                z_index=2),
            "eye_l_pupil": SlotConfig(bone="head", default_attachment="default", offset=(-66, -122),
                                      attachments={"default": "head/eyes/pupil.png"}, z_index=3),
            "eye_r_sclera": SlotConfig(
                bone="head", default_attachment="default", offset=(25, -135),
                attachments={
                    "default": "head/eyes/sclera_right.png",
                    "blink": "head/eyes/eyelid_blink.png",
                    "happy": "head/eyes/eye_happy.png",
                    "focused": "head/eyes/eye_focused.png",
                    "wide": "head/eyes/eye_wide.png",
                },
                z_index=2),
            "eye_r_pupil": SlotConfig(bone="head", default_attachment="default", offset=(34, -122),
                                      attachments={"default": "head/eyes/pupil.png"}, z_index=3),
            "eyebrow_l": SlotConfig(bone="head", default_attachment="default", offset=(-70, -155),
                                    attachments={"default": "head/eyebrows/left.png"}, z_index=4),
            "eyebrow_r": SlotConfig(bone="head", default_attachment="default", offset=(25, -155),
                                    attachments={"default": "head/eyebrows/right.png"}, z_index=4),
            "mouth": SlotConfig(
                bone="head", default_attachment="rest", offset=(-40, -85),
                attachments={name: f"head/mouth/{name}.png" for name in (
                    "rest", "smile", "open_smile", "A_I", "E", "O", "U",
                    "M_B_P", "F_V", "L_D_T_N", "W_Q")},
                z_index=5),
            "arm_l_up": SlotConfig(bone="arm_l_upper", offset=(-30, -20),
                                   attachments={"default": "body/arm_upper.png"}, z_index=1),
            "arm_l_low": SlotConfig(bone="arm_l_lower", offset=(-30, -15),
                                    attachments={"default": "body/arm_lower.png"}, z_index=1),
            "hand_l": SlotConfig(
                bone="hand_l", default_attachment="rest", offset=(-35, -20),
                attachments={"rest": "body/hands/rest.png", "wave": "body/hands/wave.png",
                             "point": "body/hands/point.png",
                             "thumbs_up": "body/hands/thumbs_up.png"},
                z_index=2),
            "arm_r_up": SlotConfig(bone="arm_r_upper", offset=(-30, -20),
                                   attachments={"default": "body/arm_upper.png"}, z_index=1),
            "arm_r_low": SlotConfig(bone="arm_r_lower", offset=(-30, -15),
                                    attachments={"default": "body/arm_lower.png"}, z_index=1),
            "hand_r": SlotConfig(
                bone="hand_r", default_attachment="rest", offset=(-35, -20),
                attachments={"rest": "body/hands/rest.png", "wave": "body/hands/wave.png",
                             "point": "body/hands/point.png",
                             "thumbs_up": "body/hands/thumbs_up.png"},
                z_index=2),
            "prop_r": SlotConfig(bone="prop_r", default_attachment="none", offset=(-12, -160),
                                 attachments={"none": "", "pointer_stick": "props/pointer_stick.png"},
                                 z_index=3),
        },
        viseme_slot="mouth",
        visemes={name: name for name in (
            "rest", "smile", "open_smile", "A_I", "E", "O", "U",
            "M_B_P", "F_V", "L_D_T_N", "W_Q")},
        palette_tokens={
            "ink": "#261c14",
            "paper": "#ecdec4",
            "robe": "#4e3e30",
            "amber": "#c68e3a",
        },
        presentation_profile=PresentationProfileConfig(
            controls=RigControlsConfig(head="head", body="torso", root="root"),
            procedural={
                # A measured, scholarly presence: slower breath and fewer darting glances
                # than the chibi, because a history documentary is not a tutorial.
                "breathing": True,
                "breathing_intensity": 0.38,
                "breathing_bpm": 13.0,
                "blinking": True,
                "blink_interval_mean": 4.5,
                "gaze_saccades": True,
                "bounce_on_speak": True,
                "hover": False,
            },
            supported_gestures=(
                "idle", "point_up_left", "point_up_right", "happy_wave",
                "thumbs_up", "thinking", "shock", "shrug",
            ),
        ),
    )
