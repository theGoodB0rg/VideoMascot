from __future__ import annotations
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field


class PoseState(BaseModel):
    """Runtime pose configuration specifying joint angles, active attachments, viseme, and eye state."""
    joint_rotations: Dict[str, float] = Field(default_factory=dict)
    joint_translations: Dict[str, Tuple[float, float]] = Field(default_factory=dict)
    joint_scales: Dict[str, Tuple[float, float]] = Field(default_factory=dict)
    
    active_attachments: Dict[str, str] = Field(default_factory=dict)
    viseme: str = "rest"
    
    # Eye tracking & blinking
    gaze_target: Optional[Tuple[float, float]] = None
    pupil_offset: Tuple[float, float] = (0.0, 0.0)
    blink_progress: float = 0.0  # 0.0 = open, 1.0 = fully closed
    
    def set_joint_rotation(self, bone_name: str, angle_deg: float) -> PoseState:
        self.joint_rotations[bone_name] = float(angle_deg)
        return self

    def set_joint_translation(self, bone_name: str, dx: float, dy: float) -> PoseState:
        self.joint_translations[bone_name] = (float(dx), float(dy))
        return self

    def set_joint_scale(self, bone_name: str, sx: float, sy: float) -> PoseState:
        self.joint_scales[bone_name] = (float(sx), float(sy))
        return self

    def set_attachment(self, slot_name: str, attachment_name: str) -> PoseState:
        self.active_attachments[slot_name] = attachment_name
        return self

    def set_viseme(self, viseme: str) -> PoseState:
        self.viseme = viseme
        return self

    def clone(self) -> PoseState:
        return self.model_copy(deep=True)
