from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class BoneConfig(BaseModel):
    parent: Optional[str] = None
    position: Tuple[float, float] = (0.0, 0.0)
    rotation_deg: float = 0.0
    scale: Tuple[float, float] = (1.0, 1.0)
    pivot: Tuple[float, float] = (0.0, 0.0)
    length: float = 0.0
    z_index: int = 0


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
