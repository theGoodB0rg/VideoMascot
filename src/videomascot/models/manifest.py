from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field


class PhysicsConfig(BaseModel):
    """Secondary motion spring-damper physics for a bone."""
    stiffness: float = Field(default=150.0, description="Spring stiffness constant (k)")
    damping: float = Field(default=12.0, description="Damping coefficient (c)")
    mass: float = Field(default=1.0, description="Inertial mass (m)")
    resting_offset_deg: float = Field(default=0.0, description="Rest angle bias")


class JointConstraintConfig(BaseModel):
    """Rotation limits to prevent unnatural joint hyperextension."""
    min_rotation_deg: float = Field(default=-180.0)
    max_rotation_deg: float = Field(default=180.0)


class BoneConfig(BaseModel):
    parent: Optional[str] = None
    position: Tuple[float, float] = (0.0, 0.0)
    rotation_deg: float = 0.0
    scale: Tuple[float, float] = (1.0, 1.0)
    pivot: Tuple[float, float] = (0.0, 0.0)
    length: float = 0.0
    z_index: int = 0
    physics: Optional[PhysicsConfig] = None
    constraints: Optional[JointConstraintConfig] = None


class SlotConfig(BaseModel):
    bone: str
    default_attachment: str = "default"
    offset: Tuple[float, float] = (0.0, 0.0)
    scale: Tuple[float, float] = (1.0, 1.0)
    rotation_deg: float = 0.0
    z_index: int = 0
    attachments: Dict[str, str] = Field(default_factory=dict)


class RigControlsConfig(BaseModel):
    """Which bones a host pipeline may drive for presentation-level motion.

    A bone named here must exist in the rig. ``None`` means the character has no such
    control, which is a legitimate answer: a levitating bot has no torso to breathe with.
    """
    head: Optional[str] = "head"
    body: Optional[str] = "torso"
    root: Optional[str] = "root"


class PresentationProfileConfig(BaseModel):
    """How *this character* carries itself, shipped with the bundle that defines it.

    A bundle is meant to be slotted into a host pipeline and work immediately. Movement
    personality belongs to the character, not to the pipeline: a brick minifigure has
    restricted articulation and no lungs, a levitating bot hovers instead of breathing, a
    chibi presenter gestures broadly. Without this the host has to fall back on one shared
    default, and visually distinct mascots all animate identically.
    """
    schema_version: Literal[1] = 1
    articulation: Literal["viseme_sprite", "none"] = "viseme_sprite"
    controls: RigControlsConfig = Field(default_factory=RigControlsConfig)
    viseme_map: Dict[str, str] = Field(default_factory=dict)
    procedural: Dict[str, Any] = Field(
        default_factory=dict,
        description="Overrides onto MascotProceduralConfig; keys validated against it.",
    )
    supported_gestures: Tuple[str, ...] = Field(
        default=("idle",),
        description="Gestures this rig has the bones and hand attachments to perform.",
    )


class MascotManifest(BaseModel):
    """Schema defining a character bundle with its bone hierarchy and attachment slots."""
    id: str
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    canvas_size: Tuple[int, int] = (1000, 1000)

    bones: Dict[str, BoneConfig] = Field(default_factory=dict)
    slots: Dict[str, SlotConfig] = Field(default_factory=dict)

    viseme_slot: str = "mouth"
    visemes: Dict[str, str] = Field(default_factory=dict)

    default_palette: Dict[str, str] = Field(default_factory=dict)
    palette_tokens: Dict[str, str] = Field(default_factory=dict)

    presentation_profile: Optional[PresentationProfileConfig] = Field(
        default=None,
        description="Character-intrinsic movement personality; see PresentationProfileConfig.",
    )

    def validate_presentation(self) -> None:
        """Check the presentation profile describes *this* rig. No-op when absent.

        A profile that names a bone or viseme the bundle does not have fails silently at
        render time, which is how a mascot ends up visible but inert. Raises ``ValueError``
        so a malformed bundle is rejected at load rather than on frame 1.
        """
        profile = self.presentation_profile
        if profile is None:
            return

        from videomascot.models.schema import MascotProceduralConfig

        for role, bone in profile.controls.model_dump().items():
            if bone is not None and bone not in self.bones:
                raise ValueError(
                    f"{self.id}: presentation control '{role}' names bone '{bone}', "
                    f"which is not in the rig"
                )

        for source, target in profile.viseme_map.items():
            if target not in self.visemes:
                raise ValueError(
                    f"{self.id}: viseme_map['{source}'] targets '{target}', "
                    f"which the rig does not define"
                )

        unknown = set(profile.procedural) - set(MascotProceduralConfig.model_fields)
        if unknown:
            raise ValueError(
                f"{self.id}: unknown procedural settings {sorted(unknown)}"
            )
        # Surface out-of-range values here rather than at the first rendered frame.
        MascotProceduralConfig(**profile.procedural)

        if "idle" not in profile.supported_gestures:
            raise ValueError(
                f"{self.id}: supported_gestures must include 'idle', the resting pose "
                f"every other gesture interpolates from"
            )

