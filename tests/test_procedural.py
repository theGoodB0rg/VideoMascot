import math
import pytest
from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotProceduralConfig
from videomascot.animation.procedural import ProceduralLifeEngine


def test_breathing_bounded_scaling():
    cfg = MascotProceduralConfig(breathing=True, breathing_bpm=20.0, breathing_intensity=1.0)
    engine = ProceduralLifeEngine(config=cfg)
    
    # Sample over 10 seconds at 0.1s increments
    for i in range(100):
        t = i * 0.1
        sx, sy, dy = engine.get_breathing_offsets(t)
        
        # Scaling must stay strictly within subtle organic range (0.97 to 1.03)
        assert 0.97 <= sx <= 1.03
        assert 0.97 <= sy <= 1.03
        assert -2.0 <= dy <= 2.0


def test_breathing_disabled():
    cfg = MascotProceduralConfig(breathing=False)
    engine = ProceduralLifeEngine(config=cfg)
    
    sx, sy, dy = engine.get_breathing_offsets(1.5)
    assert sx == 1.0
    assert sy == 1.0
    assert dy == 0.0


def test_blinking_event_trigger():
    cfg = MascotProceduralConfig(blinking=True, blink_interval_mean=3.0, blink_duration=0.14)
    engine = ProceduralLifeEngine(config=cfg, seed=123)
    
    # Find a scheduled blink
    b_time = engine._blink_times[0]
    
    # Before blink: progress == 0.0
    assert engine.get_blink_progress(b_time - 0.1) == 0.0
    
    # Mid-blink: progress > 0.5
    mid_blink = b_time + 0.07
    prog = engine.get_blink_progress(mid_blink)
    assert prog > 0.5
    
    # After blink: progress == 0.0
    assert engine.get_blink_progress(b_time + 0.2) == 0.0


def test_procedural_apply_to_pose():
    engine = ProceduralLifeEngine(seed=42)
    b_time = engine._blink_times[0]
    
    # 1. Normal state (open eyes)
    pose = PoseState()
    pose = engine.apply(pose, t=0.0, is_speaking=False)
    assert pose.blink_progress == 0.0
    assert "torso" in pose.joint_scales
    
    # 2. Mid-blink state (eyelids swap to blink attachment)
    pose_blink = PoseState()
    pose_blink = engine.apply(pose_blink, t=b_time + 0.07, is_speaking=False)
    assert pose_blink.blink_progress > 0.4
    assert pose_blink.active_attachments.get("eye_l_sclera") == "eyelid_blink"
    assert pose_blink.active_attachments.get("eye_r_sclera") == "eyelid_blink"
