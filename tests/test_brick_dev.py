from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from videomascot.engine import MascotEngine
from videomascot.core.registry import get_default_registry
from videomascot.models.manifest import MascotManifest
from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotActionSchema, SpeechCue
from videomascot.core.bones import solve_pointing_fk


@pytest.fixture(scope="module")
def brick_dev_bundle():
    from videomascot.assets.starter_brick_dev import create_starter_brick_dev
    bundle_path = create_starter_brick_dev(Path("assets/mascots"))
    return bundle_path


def test_brick_dev_manifest_schema(brick_dev_bundle: Path):
    manifest_file = brick_dev_bundle / "manifest.json"
    assert manifest_file.is_file()
    
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = f.read()
    manifest = MascotManifest.model_validate_json(data)
    
    assert manifest.id == "brick_dev"
    assert manifest.name == "Brick Dev"
    assert manifest.canvas_size == (1000, 1000)
    
    # Required bones
    expected_bones = {"root", "torso", "head", "arm_l_upper", "arm_l_lower", "hand_l", "arm_r_upper", "arm_r_lower", "hand_r"}
    assert expected_bones.issubset(set(manifest.bones.keys()))
    
    # Required slots
    expected_slots = {"torso", "head_base", "hair", "eyebrows", "eyes", "beard", "mouth", "arm_l_up", "arm_l_low", "hand_l", "arm_r_up", "arm_r_low", "hand_r"}
    assert expected_slots.issubset(set(manifest.slots.keys()))
    
    # Required Preston Blair 9 visemes
    expected_visemes = {"smile", "open_smile", "rest", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"}
    assert expected_visemes.issubset(set(manifest.visemes.keys()))


def test_brick_dev_all_textures_exist(brick_dev_bundle: Path):
    manifest_file = brick_dev_bundle / "manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = MascotManifest.model_validate_json(f.read())
        
    for slot_name, slot_cfg in manifest.slots.items():
        for att_name, rel_path in slot_cfg.attachments.items():
            if not rel_path:
                continue
            texture_file = brick_dev_bundle / rel_path
            assert texture_file.is_file(), f"Missing texture file for slot '{slot_name}', attachment '{att_name}': {texture_file}"
            with Image.open(texture_file) as img:
                assert img.mode == "RGBA", f"Texture {texture_file} must be RGBA mode"
                assert img.width > 0 and img.height > 0


def test_brick_dev_alpha_integrity(brick_dev_bundle: Path):
    engine = MascotEngine.from_bundle_dir(brick_dev_bundle)
    frame = engine.render_frame(PoseState(viseme="smile"))
    
    arr = np.array(frame)
    # Check dimensions
    assert arr.shape == (1000, 1000, 4)
    # Background corners must be pure alpha (0)
    assert arr[0, 0, 3] == 0
    assert arr[0, 999, 3] == 0
    assert arr[999, 0, 3] == 0
    assert arr[999, 999, 3] == 0
    
    # Check that character pixels actually exist
    opaque_pixels = np.count_nonzero(arr[:, :, 3] > 0)
    assert opaque_pixels > 20000, "Rendered character frame is suspiciously empty"


def test_brick_dev_registry_discovery():
    registry = get_default_registry()
    manifest = registry.get_manifest("brick_dev")
    assert manifest.id == "brick_dev"
    
    engine = MascotEngine.for_character("brick_dev", registry=registry)
    assert engine.manifest.name == "Brick Dev"


def test_brick_dev_kinematic_gestures(brick_dev_bundle: Path):
    engine = MascotEngine.from_bundle_dir(brick_dev_bundle)
    compositor = engine.compositor
    
    # 1. Point up right
    pose_point = PoseState(viseme="smile")
    sh, el = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True)
    pose_point.set_joint_rotation("arm_r_upper", sh)
    pose_point.set_joint_rotation("arm_r_lower", el)
    pose_point.set_attachment("hand_r", "point")
    img_point = compositor.render_frame(pose_point)
    assert img_point.size == (1000, 1000)
    
    # 2. Wave
    pose_wave = PoseState(viseme="open_smile")
    pose_wave.set_joint_rotation("arm_l_upper", 125.0)
    pose_wave.set_joint_rotation("arm_l_lower", 25.0)
    pose_wave.set_attachment("hand_l", "wave")
    img_wave = compositor.render_frame(pose_wave)
    assert img_wave.size == (1000, 1000)
    
    # 3. Thumbs up
    pose_thumb = PoseState(viseme="open_smile")
    pose_thumb.set_joint_rotation("arm_r_upper", -50.0)
    pose_thumb.set_joint_rotation("arm_r_lower", -55.0)
    pose_thumb.set_attachment("hand_r", "thumbs_up")
    img_thumb = compositor.render_frame(pose_thumb)
    assert img_thumb.size == (1000, 1000)


def test_brick_dev_viseme_renders(brick_dev_bundle: Path):
    engine = MascotEngine.from_bundle_dir(brick_dev_bundle)
    visemes = ["smile", "open_smile", "rest", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"]
    
    for v in visemes:
        p = PoseState(viseme=v)
        frame = engine.render_frame(p)
        arr = np.array(frame)
        assert arr.shape == (1000, 1000, 4)
        assert np.count_nonzero(arr[:, :, 3] > 0) > 20000


def test_brick_dev_palette_tint(brick_dev_bundle: Path):
    from videomascot.compositor.sprite_engine import SpriteCompositor
    compositor = SpriteCompositor.from_bundle_dir(brick_dev_bundle)
    
    # Tint polo blue (#92c2ee) to amber (#f59e0b)
    compositor.apply_palette_tint({"#92c2ee": "#f59e0b"})
    frame = compositor.render_frame(PoseState())
    arr = np.array(frame)
    # Check that amber pixels (245, 158, 11) now appear in the image
    amber_match = (np.abs(arr[:, :, 0] - 245) < 30) & (np.abs(arr[:, :, 1] - 158) < 30) & (np.abs(arr[:, :, 2] - 11) < 30)
    assert np.any(amber_match), "Failed to find tinted amber pixels after palette remap"
