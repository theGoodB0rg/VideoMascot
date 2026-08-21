import math
import pytest
from videomascot.core.math_2d import Vector2D, Transform2D
from videomascot.core.bones import Bone, BoneHierarchy, solve_2joint_ik, solve_pointing_fk


def test_bone_hierarchy_transform_propagation():
    hierarchy = BoneHierarchy()
    
    # Root at (100, 200)
    root = Bone(name="root", local_position=Vector2D(100.0, 200.0))
    hierarchy.add_bone(root)
    
    # Torso attached to root at local (0, -50)
    torso = Bone(name="torso", local_position=Vector2D(0.0, -50.0))
    hierarchy.add_bone(torso, parent_name="root")
    
    # Head attached to torso at local (0, -80)
    head = Bone(name="head", local_position=Vector2D(0.0, -80.0), local_rotation_deg=45.0)
    hierarchy.add_bone(head, parent_name="torso")
    
    hierarchy.update_world_transforms()
    
    # Root world pos
    assert pytest.approx(root.get_world_position().x) == 100.0
    assert pytest.approx(root.get_world_position().y) == 200.0
    
    # Torso world pos: (100, 200) + (0, -50) = (100, 150)
    assert pytest.approx(torso.get_world_position().x) == 100.0
    assert pytest.approx(torso.get_world_position().y) == 150.0
    
    # Head world pos: (100, 150) + (0, -80) = (100, 70)
    assert pytest.approx(head.get_world_position().x) == 100.0
    assert pytest.approx(head.get_world_position().y) == 70.0


def test_bone_rotation_propagation():
    hierarchy = BoneHierarchy()
    
    # Shoulder rotated by 90 deg
    shoulder = Bone(name="shoulder", local_position=Vector2D(0.0, 0.0), local_rotation_deg=90.0)
    hierarchy.add_bone(shoulder)
    
    # Upper arm with length 50 extending along local X axis
    upper_arm = Bone(name="upper_arm", local_position=Vector2D(50.0, 0.0), length=50.0)
    hierarchy.add_bone(upper_arm, parent_name="shoulder")
    
    hierarchy.update_world_transforms()
    
    # Upper arm world position should be rotated 90 deg -> (0, 50)
    arm_pos = upper_arm.get_world_position()
    assert pytest.approx(arm_pos.x, abs=1e-4) == 0.0
    assert pytest.approx(arm_pos.y, abs=1e-4) == 50.0


def test_solve_2joint_ik_reach():
    # Shoulder at (0, 0), upper arm length L1 = 100, forearm length L2 = 100
    # Target at (141.42, 0) -> roughly 45 deg triangle
    shoulder_pos = Vector2D(0.0, 0.0)
    target = Vector2D(100.0 * math.sqrt(2), 0.0)
    
    angle1, angle2 = solve_2joint_ik(
        shoulder_pos=shoulder_pos,
        target_pos=target,
        l1=100.0,
        l2=100.0,
        flip_elbow=False
    )
    
    # In a 100-100-141.4 right triangle, shoulder is -45 deg, elbow bends 90 deg
    assert pytest.approx(abs(angle1), abs=1e-2) == 45.0
    assert pytest.approx(abs(angle2), abs=1e-2) == 90.0


def test_solve_pointing_fk():
    # Aiming at angle 30 degrees above horizontal with a slightly relaxed arm
    angle_shoulder, angle_elbow = solve_pointing_fk(aim_angle_deg=30.0, bend_ratio=0.1)
    
    # Should point straight along aim angle with subtle natural bend
    assert pytest.approx(angle_shoulder + angle_elbow * 0.5, abs=5.0) == 30.0
