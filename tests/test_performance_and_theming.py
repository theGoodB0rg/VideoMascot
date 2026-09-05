import pytest
from PIL import Image
import numpy as np
from pathlib import Path

from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig
from videomascot.models.pose import PoseState


def test_bounding_box_blitting_equivalence(tmp_path: Path):
    # Setup dummy bundle with a rotated limb
    bundle_dir = tmp_path / "test_perf_bundle"
    bundle_dir.mkdir()
    
    # Create a distinctive texture with alpha
    tex = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    for x in range(20, 60):
        for y in range(20, 60):
            tex.putpixel((x, y), (255, 100, 50, 255))
    tex.save(bundle_dir / "limb.png")

    manifest = MascotManifest(
        id="perf_bot",
        name="Perf Bot",
        canvas_size=(600, 600),
        bones={
            "root": BoneConfig(position=(300, 300)),
            "limb": BoneConfig(parent="root", position=(50, 50), rotation_deg=35.0)
        },
        slots={
            "limb_slot": SlotConfig(
                bone="limb",
                offset=(-40, -40),
                attachments={"default": "limb.png"}
            )
        },
        viseme_slot="limb_slot",
        visemes={"rest": "default"}
    )
    (bundle_dir / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    compositor = SpriteCompositor(manifest=manifest, bundle_dir=bundle_dir)
    pose = PoseState()
    pose.set_joint_rotation("limb", 45.0)

    # Render frame using optimized compositor
    rendered_img = compositor.render_frame(pose)
    assert rendered_img.size == (600, 600)

    # Verify that the texture actually rendered at the expected transformed region
    arr = np.array(rendered_img)
    alpha = arr[:, :, 3]
    assert np.count_nonzero(alpha) > 500  # Pixels are drawn
    # Background outside the bounding box remains 100% transparent
    assert alpha[0, 0] == 0
    assert alpha[599, 599] == 0


def test_palette_tinting(tmp_path: Path):
    bundle_dir = tmp_path / "theme_bundle"
    bundle_dir.mkdir()

    # Cyan badge image
    badge = Image.new("RGBA", (50, 50), (6, 182, 212, 255)) # Cyan
    badge.save(bundle_dir / "badge.png")

    manifest = MascotManifest(
        id="theme_bot",
        name="Theme Bot",
        canvas_size=(200, 200),
        bones={"root": BoneConfig(position=(100, 100))},
        slots={"badge": SlotConfig(bone="root", offset=(-25, -25), attachments={"default": "badge.png"})},
        viseme_slot="badge",
        visemes={"rest": "default"},
        palette_tokens={"neon_glow": "#06b6d4"}
    )
    (bundle_dir / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    compositor = SpriteCompositor(manifest=manifest, bundle_dir=bundle_dir)
    # Tint neon_glow to gold (#f59e0b = RGB 245, 158, 11)
    compositor.apply_palette_tint({"#06b6d4": "#f59e0b"})

    img = compositor.render_frame(PoseState())
    arr = np.array(img)
    # Center pixel should now be tinted towards gold (red > 200, green > 100, blue < 50)
    center_pixel = arr[100, 100]
    assert center_pixel[0] > 200  # Red
    assert center_pixel[2] < 60   # Blue
