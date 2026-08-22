from pathlib import Path
import pytest
import numpy as np
from PIL import Image

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.pose import PoseState
from videomascot.core.bones import solve_pointing_fk


@pytest.fixture(scope="module")
def tech_chibi_bundle(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("mascots")
    return create_starter_tech_chibi(out_dir)


def test_canvas_pure_alpha_corners_and_background(tech_chibi_bundle):
    """Guarantees that rendered frames have 100% transparent backgrounds with zero rectangular box."""
    compositor = SpriteCompositor.from_bundle_dir(tech_chibi_bundle)
    
    # 1. Render default rest pose
    pose = PoseState(viseme="smile")
    frame = compositor.render_frame(pose)
    
    assert frame.mode == "RGBA"
    w, h = frame.size
    
    arr = np.array(frame)
    
    # All 4 outer corners MUST have alpha == 0
    assert arr[0, 0, 3] == 0, "Top-left corner must be 100% transparent"
    assert arr[0, w - 1, 3] == 0, "Top-right corner must be 100% transparent"
    assert arr[h - 1, 0, 3] == 0, "Bottom-left corner must be 100% transparent"
    assert arr[h - 1, w - 1, 3] == 0, "Bottom-right corner must be 100% transparent"
    
    # Check that any pixel with alpha == 0 has zero RGB contribution
    zero_alpha_mask = arr[:, :, 3] == 0
    assert np.all(arr[zero_alpha_mask][:, :3] == 0), "Transparent pixels must have zero RGB values"
    
    # Check that the mascot actually rendered non-empty pixels
    non_zero_alpha_mask = arr[:, :, 3] > 0
    assert np.any(non_zero_alpha_mask), "Mascot must have rendered visible pixels"


def test_alpha_integrity_under_extreme_kinematics(tech_chibi_bundle):
    """Guarantees transparency holds even during rotated arm gestures and pointer stick extensions."""
    compositor = SpriteCompositor.from_bundle_dir(tech_chibi_bundle)
    
    # Arm pointing with pointer stick prop
    pose = PoseState(viseme="open_smile")
    sh, el = solve_pointing_fk(aim_angle_deg=45.0, is_right_arm=True)
    pose.set_joint_rotation("arm_r_upper", sh)
    pose.set_joint_rotation("arm_r_lower", el)
    pose.set_attachment("hand_r", "point")
    pose.set_attachment("prop_r", "pointer_stick")
    
    frame = compositor.render_frame(pose)
    arr = np.array(frame)
    
    # Verify corners remain untouched
    assert arr[0, 0, 3] == 0
    assert arr[-1, 0, 3] == 0
    assert arr[-1, -1, 3] == 0
    
    # Alpha values must be in [0, 255] and edges must be anti-aliased (not binary thresholded)
    alphas = arr[:, :, 3]
    edge_pixels = alphas[(alphas > 0) & (alphas < 255)]
    assert len(edge_pixels) > 50, "Anti-aliasing requires intermediate alpha gradient pixels on edges"
