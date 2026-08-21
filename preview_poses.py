from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.pose import PoseState
from videomascot.core.bones import solve_pointing_fk


def generate_pose_previews():
    preview_dir = Path("preview")
    preview_dir.mkdir(exist_ok=True)
    
    bundle_dir = Path("assets/mascots/chibi_tech_guide")
    compositor = SpriteCompositor.from_bundle_dir(bundle_dir)
    
    # 1. Neutral Rest Pose
    pose_rest = PoseState()
    img_rest = compositor.render_frame(pose_rest)
    img_rest.save(preview_dir / "pose_neutral_rest.png")
    print("Saved pose_neutral_rest.png")

    # 2. Pointing Right Pose with Pointer Stick
    pose_point = PoseState()
    # Tilt head slightly towards audience
    pose_point.set_joint_rotation("head", -8.0)
    # Point right arm up-right at angle -35 deg
    sh_angle, el_angle = solve_pointing_fk(aim_angle_deg=-40.0)
    pose_point.set_joint_rotation("arm_r_upper", sh_angle)
    pose_point.set_joint_rotation("arm_r_lower", el_angle)
    pose_point.set_attachment("hand_r", "point")
    pose_point.set_attachment("prop_r", "pointer_stick")
    pose_point.set_attachment("mouth", "A_I")
    
    img_point = compositor.render_frame(pose_point)
    img_point.save(preview_dir / "pose_point_stick.png")
    print("Saved pose_point_stick.png")

    # 3. Happy Wave Pose
    pose_wave = PoseState()
    pose_wave.set_joint_rotation("head", 10.0)
    pose_wave.set_joint_rotation("arm_l_upper", -110.0)
    pose_wave.set_joint_rotation("arm_l_lower", -30.0)
    pose_wave.set_attachment("hand_l", "wave")
    pose_wave.set_attachment("eye_l_sclera", "happy")
    pose_wave.set_attachment("eye_r_sclera", "happy")
    pose_wave.set_viseme("E")
    
    img_wave = compositor.render_frame(pose_wave)
    img_wave.save(preview_dir / "pose_happy_wave.png")
    print("Saved pose_happy_wave.png")

    # 4. Thumbs Up Pose
    pose_thumb = PoseState()
    pose_thumb.set_joint_rotation("arm_r_upper", -40.0)
    pose_thumb.set_joint_rotation("arm_r_lower", -45.0)
    pose_thumb.set_attachment("hand_r", "thumbs_up")
    pose_thumb.set_viseme("O")
    
    img_thumb = compositor.render_frame(pose_thumb)
    img_thumb.save(preview_dir / "pose_thumbs_up.png")
    print("Saved pose_thumbs_up.png")

    # 5. Viseme Matrix Contact Sheet (3x3 Grid of 9 visemes)
    visemes = ["rest", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"]
    grid_w, grid_h = 3, 3
    tile_w, tile_h = 300, 300
    grid_img = Image.new("RGBA", (grid_w * tile_w, grid_h * tile_h), (240, 244, 248, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for idx, v_name in enumerate(visemes):
        gx = (idx % grid_w) * tile_w
        gy = (idx // grid_w) * tile_h
        
        p = PoseState(viseme=v_name)
        f = compositor.render_frame(p, target_size=(tile_w, tile_h))
        grid_img.alpha_composite(f, (gx, gy))
        
        # Label
        draw.rectangle([gx + 10, gy + 10, gx + 100, gy + 35], fill=(30, 41, 59, 220))
        draw.text((gx + 20, gy + 14), f"/{v_name}/", fill=(255, 255, 255, 255))
        
    grid_img.save(preview_dir / "visemes_grid_9set.png")
    print("Saved visemes_grid_9set.png")


if __name__ == "__main__":
    generate_pose_previews()
