from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image

from videomascot.core.math_2d import Vector2D, Transform2D
from videomascot.core.bones import Bone, BoneHierarchy
from videomascot.core.slots import Slot
from videomascot.models.manifest import MascotManifest
from videomascot.models.pose import PoseState


class SpriteCompositor:
    """Headless 2.5D Layered Puppet Compositor.
    
    Transforms and composites layered AI/illustrated sprite slots onto a high-res RGBA canvas.
    """
    def __init__(self, manifest: MascotManifest, bundle_dir: Path) -> None:
        self.manifest = manifest
        self.bundle_dir = Path(bundle_dir)
        self.canvas_size: Tuple[int, int] = manifest.canvas_size
        
        self.hierarchy = BoneHierarchy()
        self.slots: Dict[str, Slot] = {}
        
        self._build_rig()
        self._load_textures()

    @classmethod
    def from_bundle_dir(cls, bundle_dir: Union[str, Path]) -> SpriteCompositor:
        bundle_path = Path(bundle_dir)
        manifest_file = bundle_path / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"manifest.json not found in {bundle_path}")
            
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        manifest = MascotManifest.model_validate(data)
        return cls(manifest=manifest, bundle_dir=bundle_path)

    def _build_rig(self) -> None:
        # Build bones in order of dependencies
        for bone_name, cfg in self.manifest.bones.items():
            bone = Bone(
                name=bone_name,
                local_position=Vector2D(*cfg.position),
                local_rotation_deg=cfg.rotation_deg,
                local_scale=Vector2D(*cfg.scale),
                pivot=Vector2D(*cfg.pivot),
                length=cfg.length,
                z_index=cfg.z_index
            )
            self.hierarchy.add_bone(bone, parent_name=cfg.parent)
            
        # Build slots
        for slot_name, cfg in self.manifest.slots.items():
            bone = self.hierarchy.get_bone(cfg.bone)
            slot = Slot(
                name=slot_name,
                bone=bone,
                offset=Vector2D(*cfg.offset),
                scale=Vector2D(*cfg.scale),
                rotation_deg=cfg.rotation_deg,
                z_index=cfg.z_index,
                default_attachment=cfg.default_attachment
            )
            self.slots[slot_name] = slot

    def _load_textures(self) -> None:
        for slot_name, cfg in self.manifest.slots.items():
            slot = self.slots[slot_name]
            for att_name, rel_path in cfg.attachments.items():
                if not rel_path:
                    continue
                full_path = self.bundle_dir / rel_path
                if full_path.is_file():
                    img = Image.open(full_path).convert("RGBA")
                    slot.add_attachment(att_name, img)

    def render_frame(
        self,
        pose: PoseState,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """Renders a single frame of the mascot at the given pose."""
        # 1. Apply pose parameters to bones
        for bone_name, bone in self.hierarchy.bones.items():
            # Reset to base manifest config
            cfg = self.manifest.bones[bone_name]
            base_pos = Vector2D(*cfg.position)
            base_rot = cfg.rotation_deg
            base_scale = Vector2D(*cfg.scale)
            
            # Apply pose overrides
            if bone_name in pose.joint_translations:
                dx, dy = pose.joint_translations[bone_name]
                base_pos = base_pos + Vector2D(dx, dy)
            if bone_name in pose.joint_rotations:
                base_rot += pose.joint_rotations[bone_name]
            if bone_name in pose.joint_scales:
                sx, sy = pose.joint_scales[bone_name]
                base_scale = Vector2D(base_scale.x * sx, base_scale.y * sy)
                
            bone.local_position = base_pos
            bone.local_rotation_deg = base_rot
            bone.local_scale = base_scale

        # 2. Update bone world transforms
        self.hierarchy.update_world_transforms()

        # 3. Apply active attachments
        for slot_name, slot in self.slots.items():
            if slot_name in pose.active_attachments:
                slot.set_active_attachment(pose.active_attachments[slot_name])
            else:
                slot.set_active_attachment(slot.default_attachment)

        # 4. Apply viseme to viseme_slot
        if self.manifest.viseme_slot in self.slots:
            v_slot = self.slots[self.manifest.viseme_slot]
            if pose.viseme in self.manifest.visemes:
                v_att = self.manifest.visemes[pose.viseme]
                v_slot.set_active_attachment(v_att)

        # 5. Composite layers sorted by composite_z
        canvas = Image.new("RGBA", self.canvas_size, (0, 0, 0, 0))
        sorted_slots = sorted(self.slots.values(), key=lambda s: s.composite_z)

        for slot in sorted_slots:
            tex = slot.get_active_image()
            if tex is None:
                continue

            world_t = slot.get_slot_transform()
            affine_params = world_t.to_pillow_affine()
            
            # Transform texture to canvas coordinate space
            transformed_layer = tex.transform(
                self.canvas_size,
                Image.AFFINE,
                data=affine_params,
                resample=Image.BICUBIC
            )
            
            # Alpha composite onto canvas
            canvas = Image.alpha_composite(canvas, transformed_layer)

        if target_size and target_size != self.canvas_size:
            canvas = canvas.resize(target_size, Image.LANCZOS)

        return canvas
