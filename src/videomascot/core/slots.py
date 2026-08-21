from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image

from videomascot.core.math_2d import Vector2D, Transform2D
from videomascot.core.bones import Bone


class Slot:
    """A slot attached to a bone that displays one active attachment texture at a time."""
    def __init__(
        self,
        name: str,
        bone: Bone,
        offset: Optional[Vector2D] = None,
        scale: Optional[Vector2D] = None,
        rotation_deg: float = 0.0,
        z_index: int = 0,
        default_attachment: str = "default"
    ) -> None:
        self.name = name
        self.bone = bone
        self.offset = offset or Vector2D(0.0, 0.0)
        self.scale = scale or Vector2D(1.0, 1.0)
        self.rotation_deg = float(rotation_deg)
        self.z_index = int(z_index)
        self.default_attachment = default_attachment
        self.active_attachment: str = default_attachment
        self.attachments: Dict[str, Image.Image] = {}

    def add_attachment(self, name: str, image: Image.Image) -> None:
        self.attachments[name] = image

    def set_active_attachment(self, name: str) -> None:
        if name in self.attachments:
            self.active_attachment = name

    def get_active_image(self) -> Optional[Image.Image]:
        return self.attachments.get(self.active_attachment)

    def get_slot_transform(self) -> Transform2D:
        """Returns the world transformation matrix for the slot attachment."""
        local_slot_t = Transform2D.from_trs(
            translation=self.offset,
            rotation_deg=self.rotation_deg,
            scale=self.scale
        )
        return self.bone.world_transform.compose(local_slot_t)

    @property
    def composite_z(self) -> int:
        return self.bone.z_index * 1000 + self.z_index
