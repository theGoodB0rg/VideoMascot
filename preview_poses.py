from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.pose import PoseState
from videomascot.core.bones import solve_pointing_fk, solve_aim_to_target
from videomascot.core.math_2d import Vector2D


def generate_senior_animator_poses():
    preview_dir = Path("preview")
    preview_dir.mkdir(exist_ok=True)
    
    # Regenerate assets with new anatomy
    bundle_dir = create_starter_tech_chibi(Path("assets/mascots"))
    compositor = SpriteCompositor.from_bundle_dir(bundle_dir)

    # 1. Neutral Rest Pose
    pose_rest = PoseState()
    img_rest = compositor.render_frame(pose_rest)
    img_rest.save(preview_dir / "pose_neutral_rest.png")
    print("Saved pose_neutral_rest.png")

    # 2. Strong Silhouette: Point Up-Right at Chart (+40 deg angle)
    pose_point_r = PoseState()
    # Line of action: slight body tilt towards the left (-3 deg), head focuses on the point (+6 deg)
    pose_point_r.set_joint_rotation("torso", -3.0)
    pose_point_r.set_joint_rotation("head", 6.0)
    # Right arm points up-right at +40 deg
    sh_angle, el_angle = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True, bend_ratio=0.08)
    pose_point_r.set_joint_rotation("arm_r_upper", sh_angle)
    pose_point_r.set_joint_rotation("arm_r_lower", el_angle)
    pose_point_r.set_attachment("hand_r", "point")
    pose_point_r.set_attachment("prop_r", "pointer_stick")
    # Left hand resting comfortably on hip/side
    pose_point_r.set_joint_rotation("arm_l_upper", 25.0)
    pose_point_r.set_joint_rotation("arm_l_lower", -30.0)
    pose_point_r.set_viseme("A_I")
    
    img_point_r = compositor.render_frame(pose_point_r)
    img_point_r.save(preview_dir / "pose_point_up_right.png")
    print("Saved pose_point_up_right.png")

    # 3. Strong Silhouette: Point Up-Left (+40 deg angle)
    pose_point_l = PoseState()
    pose_point_l.set_joint_rotation("torso", 3.0)
    pose_point_l.set_joint_rotation("head", -6.0)
    sh_angle_l, el_angle_l = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=False, bend_ratio=0.08)
    pose_point_l.set_joint_rotation("arm_l_upper", sh_angle_l)
    pose_point_l.set_joint_rotation("arm_l_lower", el_angle_l)
    pose_point_l.set_attachment("hand_l", "point")
    # Right arm on hip
    pose_point_l.set_joint_rotation("arm_r_upper", -25.0)
    pose_point_l.set_joint_rotation("arm_r_lower", 30.0)
    pose_point_l.set_viseme("E")
    
    img_point_l = compositor.render_frame(pose_point_l)
    img_point_l.save(preview_dir / "pose_point_up_left.png")
    print("Saved pose_point_up_left.png")

    # 4. High Enthusiastic Wave (Hand raised high near ear level)
    pose_wave = PoseState()
    pose_wave.set_joint_rotation("head", 10.0)
    # Raise left arm high: aim_angle_deg = +65 deg
    sh_w, el_w = solve_pointing_fk(aim_angle_deg=65.0, is_right_arm=False, bend_ratio=0.3)
    pose_wave.set_joint_rotation("arm_l_upper", sh_w)
    pose_wave.set_joint_rotation("arm_l_lower", el_w)
    pose_wave.set_attachment("hand_l", "wave")
    pose_wave.set_attachment("eye_l_sclera", "happy")
    pose_wave.set_attachment("eye_r_sclera", "happy")
    pose_wave.set_viseme("E")
    
    img_wave = compositor.render_frame(pose_wave)
    img_wave.save(preview_dir / "pose_happy_wave.png")
    print("Saved pose_happy_wave.png")

    # 5. Thinking Pose (Hand to chin, head tilted, eyes looking up-left)
    pose_think = PoseState()
    pose_think.set_joint_rotation("head", 15.0)
    # Bring right hand up towards chin
    pose_think.set_joint_rotation("arm_r_upper", -115.0)
    pose_think.set_joint_rotation("arm_r_lower", -90.0)
    pose_think.set_attachment("hand_r", "rest")
    # Gaze up-left
    pose_think.set_attachment("eyebrow_l", "default")
    pose_think.set_attachment("eyebrow_r", "default")
    pose_think.set_viseme("U")
    
    img_think = compositor.render_frame(pose_think)
    img_think.save(preview_dir / "pose_thinking.png")
    print("Saved pose_thinking.png")

    # 6. Surprised / Shocked Pose (Wide eyes, mouth O, hands raised)
    pose_shock = PoseState()
    pose_shock.set_joint_rotation("head", -5.0)
    pose_shock.set_joint_rotation("arm_l_upper", 70.0)
    pose_shock.set_joint_rotation("arm_l_lower", 40.0)
    pose_shock.set_joint_rotation("arm_r_upper", -70.0)
    pose_shock.set_joint_rotation("arm_r_lower", -40.0)
    pose_shock.set_attachment("hand_l", "wave")
    pose_shock.set_attachment("hand_r", "wave")
    pose_shock.set_viseme("O")
    
    img_shock = compositor.render_frame(pose_shock)
    img_shock.save(preview_dir / "pose_shock.png")
    print("Saved pose_shock.png")

    # 7. Neck Tilt Visual Inspection Strip (Rotations from -30 deg to +30 deg)
    tilt_angles = [-30, -20, -10, 0, 10, 20, 30]
    strip_w = len(tilt_angles) * 220
    strip_img = Image.new("RGBA", (strip_w, 280), (240, 244, 248, 255))
    draw = ImageDraw.Draw(strip_img)
    
    for idx, deg in enumerate(tilt_angles):
        gx = idx * 220
        p = PoseState()
        p.set_joint_rotation("head", deg)
        frame = compositor.render_frame(p, target_size=(220, 220))
        strip_img.alpha_composite(frame, (gx, 40))
        draw.rectangle([gx + 10, 10, gx + 100, 32], fill=(30, 41, 59, 220))
        draw.text((gx + 20, 14), f"Head {deg:+d}°", fill=(255, 255, 255, 255))
        
    strip_img.save(preview_dir / "neck_tilt_inspection.png")
    print("Saved neck_tilt_inspection.png")


if __name__ == "__main__":
    generate_senior_animator_poses()
