from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple
from videomascot.core.math_2d import Vector2D, Transform2D


class Bone:
    """A single bone/joint in the mascot kinematic hierarchy."""
    def __init__(
        self,
        name: str,
        local_position: Optional[Vector2D] = None,
        local_rotation_deg: float = 0.0,
        local_scale: Optional[Vector2D] = None,
        pivot: Optional[Vector2D] = None,
        length: float = 0.0,
        z_index: int = 0
    ) -> None:
        self.name = name
        self.local_position = local_position or Vector2D(0.0, 0.0)
        self.local_rotation_deg = float(local_rotation_deg)
        self.local_scale = local_scale or Vector2D(1.0, 1.0)
        self.pivot = pivot or Vector2D(0.0, 0.0)
        self.length = float(length)
        self.z_index = int(z_index)
        
        self.parent: Optional[Bone] = None
        self.children: List[Bone] = []
        self.world_transform: Transform2D = Transform2D.identity()

    def get_local_transform(self) -> Transform2D:
        return Transform2D.from_trs(
            translation=self.local_position,
            rotation_deg=self.local_rotation_deg,
            scale=self.local_scale,
            pivot=self.pivot
        )

    def update_world_transform(self, parent_transform: Optional[Transform2D] = None) -> None:
        local_t = self.get_local_transform()
        if parent_transform is None:
            self.world_transform = local_t
        else:
            self.world_transform = parent_transform.compose(local_t)
            
        for child in self.children:
            child.update_world_transform(self.world_transform)

    def get_world_position(self) -> Vector2D:
        return self.world_transform.transform_point(Vector2D(0.0, 0.0))

    def get_world_tip(self) -> Vector2D:
        """Returns the world position of the bone tip (along local X-axis by `length`)."""
        return self.world_transform.transform_point(Vector2D(self.length, 0.0))


class BoneHierarchy:
    """Manages the full tree of bones for a character rig."""
    def __init__(self) -> None:
        self.bones: Dict[str, Bone] = {}
        self.roots: List[Bone] = []

    def add_bone(self, bone: Bone, parent_name: Optional[str] = None) -> None:
        self.bones[bone.name] = bone
        if parent_name:
            if parent_name not in self.bones:
                raise ValueError(f"Parent bone '{parent_name}' not found in hierarchy.")
            parent = self.bones[parent_name]
            bone.parent = parent
            parent.children.append(bone)
        else:
            bone.parent = None
            if bone not in self.roots:
                self.roots.append(bone)

    def get_bone(self, name: str) -> Bone:
        if name not in self.bones:
            raise KeyError(f"Bone '{name}' not found.")
        return self.bones[name]

    def update_world_transforms(self) -> None:
        """Propagates transformations from root bones down to all leaf bones."""
        for root in self.roots:
            root.update_world_transform(parent_transform=None)

    def get_bones_sorted_by_z(self) -> List[Bone]:
        """Returns all bones sorted in rendering order (lowest z_index to highest)."""
        return sorted(self.bones.values(), key=lambda b: b.z_index)


# --- Kinematics Solvers ---

def solve_2joint_ik(
    shoulder_pos: Vector2D,
    target_pos: Vector2D,
    l1: float,
    l2: float,
    flip_elbow: bool = False
) -> Tuple[float, float]:
    """Analytical 2-Joint Inverse Kinematics solver (using Law of Cosines).
    
    Returns:
        (shoulder_angle_deg, elbow_relative_angle_deg)
    """
    diff = target_pos - shoulder_pos
    dist = diff.magnitude()
    
    # Clamp distance to maximum reachable arm length
    max_reach = l1 + l2 - 1e-4
    min_reach = abs(l1 - l2) + 1e-4
    clamped_dist = max(min_reach, min(max_reach, dist))
    
    # Angle from shoulder to target
    base_angle = math.atan2(diff.y, diff.x)
    
    # Law of cosines for shoulder angle offset
    cos_alpha = (l1 * l1 + clamped_dist * clamped_dist - l2 * l2) / (2.0 * l1 * clamped_dist)
    cos_alpha = max(-1.0, min(1.0, cos_alpha))
    alpha = math.acos(cos_alpha)
    
    # Law of cosines for elbow angle
    cos_beta = (l1 * l1 + l2 * l2 - clamped_dist * clamped_dist) / (2.0 * l1 * l2)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)
    
    if flip_elbow:
        shoulder_angle = base_angle + alpha
        elbow_angle = math.pi - beta
    else:
        shoulder_angle = base_angle - alpha
        elbow_angle = -(math.pi - beta)
        
    return (math.degrees(shoulder_angle), math.degrees(elbow_angle))


def solve_pointing_fk(
    aim_angle_deg: float,
    is_right_arm: bool = True,
    bend_ratio: float = 0.05
) -> Tuple[float, float]:
    """Forward Kinematics solver for natural pointing at a target angle.
    
    Coordinate convention:
    - 0 deg: Horizontal forward (pointing right for right arm, left for left arm)
    - +45 deg: Pointing Upwards & Outwards (towards top corner)
    - -45 deg: Pointing Downwards & Outwards
    - +90 deg: Pointing Straight Up
    
    Since the rest sprite hangs vertically down (270 deg / -90 deg from horizontal):
    We map the requested aim angle into proper joint rotation offsets relative to vertical rest.
    """
    if is_right_arm:
        # Vertical down rest is -90 deg relative to horizontal.
        # To reach aim_angle_deg, we rotate by (aim_angle_deg + 90) counter-clockwise (in screen space).
        total_rot = -(aim_angle_deg + 90.0)
    else:
        # Left arm
        total_rot = (aim_angle_deg + 90.0)
        
    elbow_bend = total_rot * bend_ratio
    shoulder_angle = total_rot - elbow_bend * 0.5
    return (shoulder_angle, elbow_bend)


def solve_aim_to_target(
    shoulder_world_pos: Vector2D,
    target_world_pos: Vector2D,
    is_right_arm: bool = True
) -> Tuple[float, float]:
    """Calculates shoulder and elbow rotation angles to aim directly at a screen coordinate."""
    diff = target_world_pos - shoulder_world_pos
    # Screen angle (in degrees): 0 deg is right (+X), 90 deg is down (+Y) in screen coords
    # Convert to mathematical angle (0 deg right, 90 deg up)
    math_angle_deg = math.degrees(math.atan2(-diff.y, diff.x))
    
    if not is_right_arm:
        # For left arm, 0 deg is left (-X)
        math_angle_deg = math.degrees(math.atan2(-diff.y, -diff.x))
        
    return solve_pointing_fk(aim_angle_deg=math_angle_deg, is_right_arm=is_right_arm)

