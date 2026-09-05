from __future__ import annotations
from typing import Dict, List, Optional, Tuple
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

