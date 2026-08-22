"""VideoMascot - Modular, scalable AI-ready layered puppet and mascot animation engine."""

from videomascot.core.math_2d import Vector2D, Transform2D, ease_in_out_quad, ease_out_back, spring_lerp
from videomascot.core.bones import Bone, BoneHierarchy, solve_2joint_ik, solve_pointing_fk, solve_aim_to_target
from videomascot.core.slots import Slot
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig
from videomascot.models.pose import PoseState
from videomascot.compositor.sprite_engine import SpriteCompositor

__version__ = "0.1.0"
__all__ = [
    "Vector2D",
    "Transform2D",
    "ease_in_out_quad",
    "ease_out_back",
    "spring_lerp",
    "Bone",
    "BoneHierarchy",
    "solve_2joint_ik",
    "solve_pointing_fk",
    "solve_aim_to_target",
    "Slot",
    "MascotManifest",
    "BoneConfig",
    "SlotConfig",
    "PoseState",
    "SpriteCompositor",
]
