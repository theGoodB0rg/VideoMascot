"""VideoMascot - Modular, scalable AI-ready layered puppet and mascot animation engine."""

from videomascot.core.math_2d import Vector2D, Transform2D, ease_in_out_quad, ease_out_back, spring_lerp
from videomascot.core.registry import (
    MascotRegistry,
    get_default_registry,
    get_bundled_assets_dir,
    list_available_mascots,
    list_character_ids,
    MascotMetadata,
    MascotNotFoundError,
    MascotBundleValidationError,
)
from videomascot.core.bones import Bone, BoneHierarchy, solve_2joint_ik, solve_pointing_fk, solve_aim_to_target
from videomascot.core.slots import Slot
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig, PhysicsConfig, JointConstraintConfig
from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotActionSchema, MascotPlacementSchema, MascotProceduralConfig, SpeechCue, MascotStoryConfig
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.compositor.stream_engine import StreamEngine
from videomascot.animation.procedural import ProceduralLifeEngine
from videomascot.animation.lipsync import LipSyncEngine
from videomascot.animation.sequencer import MascotSequencer
from videomascot.pipeline.video_overlay import VideoOverlayCompositor
from videomascot.engine import MascotEngine

__version__ = "0.3.0"
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
    "PhysicsConfig",
    "JointConstraintConfig",
    "PoseState",
    "MascotRegistry",
    "get_default_registry",
    "get_bundled_assets_dir",
    "list_available_mascots",
    "list_character_ids",
    "MascotMetadata",
    "MascotNotFoundError",
    "MascotBundleValidationError",
    "MascotActionSchema",
    "MascotPlacementSchema",
    "MascotProceduralConfig",
    "SpeechCue",
    "MascotStoryConfig",
    "SpriteCompositor",
    "StreamEngine",
    "ProceduralLifeEngine",
    "LipSyncEngine",
    "MascotSequencer",
    "VideoOverlayCompositor",
    "MascotEngine",
]
