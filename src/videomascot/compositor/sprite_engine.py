from __future__ import annotations
import json
import math
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

    def apply_palette_tint(self, color_map: Dict[str, str]) -> None:
        """Remaps colors in loaded textures according to a hex-to-hex mapping.
        
        Useful for dynamic brand palette swapping (e.g. changing cyan visor glow to amber).
        """
        def hex_to_rgb(h: str) -> Tuple[int, int, int]:
            h = h.lstrip("#")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

        import numpy as np

        parsed_map = {hex_to_rgb(src): hex_to_rgb(dst) for src, dst in color_map.items()}

        for slot in self.slots.values():
            for att_name, img in slot.attachments.items():
                if img is None:
                    continue
                arr = np.array(img, copy=True)
                for src_rgb, dst_rgb in parsed_map.items():
                    diff = np.sqrt(
                        (arr[:, :, 0].astype(float) - src_rgb[0]) ** 2 +
                        (arr[:, :, 1].astype(float) - src_rgb[1]) ** 2 +
                        (arr[:, :, 2].astype(float) - src_rgb[2]) ** 2
                    )
                    mask = (diff < 45.0) & (arr[:, :, 3] > 0)
                    if np.any(mask):
                        arr[mask, 0] = dst_rgb[0]
                        arr[mask, 1] = dst_rgb[1]
                        arr[mask, 2] = dst_rgb[2]
                slot.attachments[att_name] = Image.fromarray(arr, mode="RGBA")

    def render_frame(
        self,
        pose: PoseState,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """Renders a single frame of the mascot at the given pose with local bounding-box blitting."""
        # 1. Apply pose parameters to bones
        for bone_name, bone in self.hierarchy.bones.items():
            cfg = self.manifest.bones[bone_name]
            base_pos = Vector2D(*cfg.position)
            base_rot = cfg.rotation_deg
            base_scale = Vector2D(*cfg.scale)
            
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

        # 5. Composite layers sorted by composite_z using high-performance bounding box blitting
        canvas = Image.new("RGBA", self.canvas_size, (0, 0, 0, 0))
        sorted_slots = sorted(self.slots.values(), key=lambda s: s.composite_z)
        cw, ch = self.canvas_size

        for slot in sorted_slots:
            tex = slot.get_active_image()
            if tex is None:
                continue

            tw, th = tex.size
            world_t = slot.get_slot_transform()
            
            # Compute transformed 4-corner bounding box in canvas coordinates
            p0 = world_t.transform_point(Vector2D(0.0, 0.0))
            p1 = world_t.transform_point(Vector2D(float(tw), 0.0))
            p2 = world_t.transform_point(Vector2D(float(tw), float(th)))
            p3 = world_t.transform_point(Vector2D(0.0, float(th)))

            min_x = max(0, int(math.floor(min(p0.x, p1.x, p2.x, p3.x))))
            min_y = max(0, int(math.floor(min(p0.y, p1.y, p2.y, p3.y))))
            max_x = min(cw, int(math.ceil(max(p0.x, p1.x, p2.x, p3.x))))
            max_y = min(ch, int(math.ceil(max(p0.y, p1.y, p2.y, p3.y))))

            # Skip layer if outside canvas
            if max_x <= min_x or max_y <= min_y:
                continue

            sub_w = max_x - min_x
            sub_h = max_y - min_y

            affine_params = world_t.to_pillow_affine()
            a, b, c, d, e, f = affine_params

            # Adjust translation component for local bounding-box sub-canvas
            sub_affine = (
                a, b, a * min_x + b * min_y + c,
                d, e, d * min_x + e * min_y + f
            )

            sub_layer = tex.transform(
                (sub_w, sub_h),
                Image.AFFINE,
                data=sub_affine,
                resample=Image.BICUBIC
            )

            canvas.alpha_composite(sub_layer, (min_x, min_y))

        if target_size and target_size != self.canvas_size:
            canvas = canvas.resize(target_size, Image.LANCZOS)

        return canvas

