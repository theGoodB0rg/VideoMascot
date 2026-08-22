import pytest
from videomascot.models.schema import MascotActionSchema, SpeechCue
from videomascot.animation.sequencer import MascotSequencer


def test_sequencer_base_pose_and_emotion():
    action = MascotActionSchema(
        emotion="excited",
        gesture="happy_wave",
        gaze="camera"
    )
    seq = MascotSequencer(action=action)
    
    # Evaluate at t = 1.0s (past transition)
    pose = seq.evaluate_pose(t=1.0)
    
    assert pose.viseme == "open_smile"
    assert "arm_l_upper" in pose.joint_rotations
    assert pose.joint_rotations["arm_l_upper"] == 125.0
    assert pose.active_attachments.get("hand_l") == "wave"


def test_sequencer_pointing_gesture_with_prop():
    action = MascotActionSchema(
        emotion="friendly",
        gesture="point_up_right",
        gaze="point_target",
        prop="pointer_stick"
    )
    seq = MascotSequencer(action=action)
    
    pose = seq.evaluate_pose(t=1.0)
    assert pose.active_attachments.get("hand_r") == "point"
    assert pose.active_attachments.get("prop_r") == "pointer_stick"
    assert pose.pupil_offset[0] > 0.0 # Gaze looks rightwards towards point target


def test_sequencer_smooth_gesture_transition():
    action = MascotActionSchema(
        gesture="point_up_right",
        emotion="friendly"
    )
    seq = MascotSequencer(action=action)
    
    # At t = 0.0 (start of transition), arm rotation should be close to idle
    pose_start = seq.evaluate_pose(t=0.0, transition_duration=0.4)
    # At t = 0.2 (mid transition)
    pose_mid = seq.evaluate_pose(t=0.2, transition_duration=0.4)
    # At t = 0.4 (completed transition)
    pose_end = seq.evaluate_pose(t=0.4, transition_duration=0.4)
    
    r_start = pose_start.joint_rotations["arm_r_upper"]
    r_mid = pose_mid.joint_rotations["arm_r_upper"]
    r_end = pose_end.joint_rotations["arm_r_upper"]
    
    # Must be monotonically transitioning
    assert (r_start < r_mid < r_end) or (r_start > r_mid > r_end)
