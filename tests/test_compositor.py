import os
import pytest
from PIL import Image, ImageDraw
import numpy as np

from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig
from videomascot.models.pose import PoseState
from videomascot.compositor.sprite_engine import SpriteCompositor


@pytest.fixture
def sample_mascot_bundle(tmp_path):
    bundle_dir = tmp_path / "test_mascot"
    bundle_dir.mkdir()
    
    # Create simple solid color test sprites with alpha
    (bundle_dir / "body").mkdir()
    torso_img = Image.new("RGBA", (100, 150), (255, 0, 0, 255))
    torso_img.save(bundle_dir / "body" / "torso.png")
    
    (bundle_dir / "head").mkdir()
    head_img = Image.new("RGBA", (120, 120), (0, 255, 0, 255))
    head_img.save(bundle_dir / "head" / "head_base.png")
    
    (bundle_dir / "head" / "mouth").mkdir()
    mouth_rest = Image.new("RGBA", (40, 20), (0, 0, 255, 255))
    mouth_rest.save(bundle_dir / "head" / "mouth" / "rest.png")
    mouth_o = Image.new("RGBA", (40, 40), (255, 255, 0, 255))
    mouth_o.save(bundle_dir / "head" / "mouth" / "O.png")
    
    manifest = MascotManifest(
        id="test_mascot",
        name="Test Mascot",
        canvas_size=(400, 400),
        bones={
            "root": BoneConfig(position=(200, 200), pivot=(0, 0), z_index=0),
            "torso": BoneConfig(parent="root", position=(0, 0), pivot=(50, 75), z_index=1),
            "head": BoneConfig(parent="torso", position=(0, -80), pivot=(60, 60), z_index=2)
        },
        slots={
            "body": SlotConfig(
                bone="torso",
                default_attachment="default",
                offset=(-50, -75),
                attachments={"default": "body/torso.png"},
                z_index=1
            ),
            "head": SlotConfig(
                bone="head",
                default_attachment="default",
                offset=(-60, -60),
                attachments={"default": "head/head_base.png"},
                z_index=2
            ),
            "mouth": SlotConfig(
                bone="head",
                default_attachment="rest",
                offset=(-20, 10),
                attachments={
                    "rest": "head/mouth/rest.png",
                    "O": "head/mouth/O.png"
                },
                z_index=3
            )
        },
        viseme_slot="mouth",
        visemes={"rest": "rest", "O": "O"}
    )
    
    with open(bundle_dir / "manifest.json", "w") as f:
        f.write(manifest.model_dump_json(indent=2))
        
    return bundle_dir


def test_compositor_load_and_render_default(sample_mascot_bundle):
    compositor = SpriteCompositor.from_bundle_dir(sample_mascot_bundle)
    pose = PoseState()
    
    frame = compositor.render_frame(pose)
    
    assert frame.size == (400, 400)
    assert frame.mode == "RGBA"
    
    # Verify non-empty pixels rendered
    np_frame = np.array(frame)
    assert np.any(np_frame[:, :, 3] > 0)


def test_compositor_viseme_swap(sample_mascot_bundle):
    compositor = SpriteCompositor.from_bundle_dir(sample_mascot_bundle)
    
    # Render with rest mouth
    pose_rest = PoseState(viseme="rest")
    frame_rest = compositor.render_frame(pose_rest)
    
    # Render with O mouth
    pose_o = PoseState(viseme="O")
    frame_o = compositor.render_frame(pose_o)
    
    # Frames should differ because mouth attachment changed
    np_rest = np.array(frame_rest)
    np_o = np.array(frame_o)
    assert not np.array_equal(np_rest, np_o)


def test_compositor_joint_rotation(sample_mascot_bundle):
    compositor = SpriteCompositor.from_bundle_dir(sample_mascot_bundle)
    
    pose_straight = PoseState()
    frame_straight = compositor.render_frame(pose_straight)
    
    # Rotate head by 45 degrees
    pose_tilted = PoseState()
    pose_tilted.set_joint_rotation("head", 45.0)
    frame_tilted = compositor.render_frame(pose_tilted)
    
    assert not np.array_equal(np.array(frame_straight), np.array(frame_tilted))
