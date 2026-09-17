from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.pose import PoseState
from videomascot.core.bones import solve_pointing_fk, solve_aim_to_target
from videomascot.core.math_2d import Vector2D
from videomascot.inspector_builder import generate_html_inspector


def generate_senior_animator_poses():
    preview_dir = Path("preview")
    preview_dir.mkdir(exist_ok=True)
    
    # 1. Regenerate assets with friendly expressions & fixed dual-arm anatomy
    bundle_dir = create_starter_tech_chibi(Path("assets/mascots"))
    compositor = SpriteCompositor.from_bundle_dir(bundle_dir)

    # 2. Neutral Rest Pose (Warm, friendly smile)
    pose_rest = PoseState(viseme="smile")
    img_rest = compositor.render_frame(pose_rest)
    img_rest.save(preview_dir / "pose_neutral_rest.png")
    print("Saved pose_neutral_rest.png")

    # 3. Point Up-Right at Chart (Friendly confident smile, right arm raised UP-RIGHT +40 deg)
    pose_point_r = PoseState(viseme="smile")
    pose_point_r.set_joint_rotation("torso", -3.0)
    pose_point_r.set_joint_rotation("head", 6.0)
    # Right arm points up-right at +40 deg
    sh_angle, el_angle = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True, bend_ratio=0.08)
    pose_point_r.set_joint_rotation("arm_r_upper", sh_angle)
    pose_point_r.set_joint_rotation("arm_r_lower", el_angle)
    pose_point_r.set_attachment("hand_r", "point")
    pose_point_r.set_attachment("prop_r", "pointer_stick")
    # Left hand resting comfortably on hip
    pose_point_r.set_joint_rotation("arm_l_upper", 25.0)
    pose_point_r.set_joint_rotation("arm_l_lower", -30.0)
    
    img_point_r = compositor.render_frame(pose_point_r)
    img_point_r.save(preview_dir / "pose_point_up_right.png")
    print("Saved pose_point_up_right.png")

    # 4. Point Up-Left (Left arm points UP-LEFT +40 deg)
    pose_point_l = PoseState(viseme="smile")
    pose_point_l.set_joint_rotation("torso", 3.0)
    pose_point_l.set_joint_rotation("head", -6.0)
    sh_angle_l, el_angle_l = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=False, bend_ratio=0.08)
    pose_point_l.set_joint_rotation("arm_l_upper", sh_angle_l)
    pose_point_l.set_joint_rotation("arm_l_lower", el_angle_l)
    pose_point_l.set_attachment("hand_l", "point")
    # Right arm on hip
    pose_point_l.set_joint_rotation("arm_r_upper", -25.0)
    pose_point_l.set_joint_rotation("arm_r_lower", 30.0)
    
    img_point_l = compositor.render_frame(pose_point_l)
    img_point_l.save(preview_dir / "pose_point_up_left.png")
    print("Saved pose_point_up_left.png")

    # 5. Cheerful High Wave (Left arm raised high +125 deg waving outside body, warm open smile)
    pose_wave = PoseState(viseme="open_smile")
    pose_wave.set_joint_rotation("head", 8.0)
    # Left arm rotates positive (counter-clockwise) to extend UP-LEFT outwards
    pose_wave.set_joint_rotation("arm_l_upper", 125.0)
    pose_wave.set_joint_rotation("arm_l_lower", 25.0)
    pose_wave.set_attachment("hand_l", "wave")
    pose_wave.set_attachment("eye_l_sclera", "happy")
    pose_wave.set_attachment("eye_r_sclera", "happy")
    
    img_wave = compositor.render_frame(pose_wave)
    img_wave.save(preview_dir / "pose_happy_wave.png")
    print("Saved pose_happy_wave.png")

    # 6. Thumbs Up Pose (Encouraging friendly smile)
    pose_thumb = PoseState(viseme="open_smile")
    pose_thumb.set_joint_rotation("head", -4.0)
    pose_thumb.set_joint_rotation("arm_r_upper", -50.0)
    pose_thumb.set_joint_rotation("arm_r_lower", -55.0)
    pose_thumb.set_attachment("hand_r", "thumbs_up")
    
    img_thumb = compositor.render_frame(pose_thumb)
    img_thumb.save(preview_dir / "pose_thumbs_up.png")
    print("Saved pose_thumbs_up.png")

    # 7. Thinking Pose (Thoughtful smile, hand to chin, eyes up-left)
    pose_think = PoseState(viseme="smile")
    pose_think.set_joint_rotation("head", 12.0)
    pose_think.set_joint_rotation("arm_r_upper", -115.0)
    pose_think.set_joint_rotation("arm_r_lower", -90.0)
    pose_think.set_attachment("hand_r", "rest")
    
    img_think = compositor.render_frame(pose_think)
    img_think.save(preview_dir / "pose_thinking.png")
    print("Saved pose_thinking.png")

    # 8. Surprised Shock Pose
    pose_shock = PoseState(viseme="O")
    pose_shock.set_joint_rotation("head", 0.0)
    pose_shock.set_joint_rotation("arm_l_upper", 70.0)
    pose_shock.set_joint_rotation("arm_l_lower", 40.0)
    pose_shock.set_joint_rotation("arm_r_upper", -70.0)
    pose_shock.set_joint_rotation("arm_r_lower", -40.0)
    pose_shock.set_attachment("hand_l", "wave")
    pose_shock.set_attachment("hand_r", "wave")
    
    img_shock = compositor.render_frame(pose_shock)
    img_shock.save(preview_dir / "pose_shock.png")
    print("Saved pose_shock.png")

    # 9. Viseme 9-Set Contact Sheet
    visemes = ["smile", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"]
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
        
        draw.rectangle([gx + 10, gy + 10, gx + 110, gy + 35], fill=(30, 41, 59, 220))
        draw.text((gx + 20, gy + 14), f"/{v_name}/", fill=(255, 255, 255, 255))
        
    grid_img.save(preview_dir / "visemes_grid_9set.png")
    print("Saved visemes_grid_9set.png")

def generate_nexus_bot_poses():
    from videomascot.assets.starter_nexus_bot import create_starter_nexus_bot
    from videomascot.engine import MascotEngine

    preview_dir = Path("preview/nexus_bot")
    preview_dir.mkdir(parents=True, exist_ok=True)

    create_starter_nexus_bot(Path("assets/mascots"))
    engine = MascotEngine.for_character("nexus_bot")
    compositor = engine.compositor

    # 1. Neutral Rest Pose
    pose_rest = PoseState(viseme="rest")
    img_rest = compositor.render_frame(pose_rest)
    img_rest.save(preview_dir / "pose_neutral_rest.png")
    print("Saved nexus_bot/pose_neutral_rest.png")

    # 2. Point Up-Right at Chart with Holographic Light Stylus
    pose_point_r = PoseState(viseme="smile")
    pose_point_r.set_attachment("eyes", "focused")
    pose_point_r.set_joint_rotation("torso", -4.0)
    pose_point_r.set_joint_rotation("head", 6.0)
    sh_angle, el_angle = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True, bend_ratio=0.08)
    pose_point_r.set_joint_rotation("arm_r_upper", sh_angle)
    pose_point_r.set_joint_rotation("arm_r_lower", el_angle)
    pose_point_r.set_attachment("hand_r", "point")
    pose_point_r.set_attachment("prop_r", "hologram_pointer")
    pose_point_r.set_joint_rotation("arm_l_upper", 25.0)
    pose_point_r.set_joint_rotation("arm_l_lower", -30.0)
    img_point_r = compositor.render_frame(pose_point_r)
    img_point_r.save(preview_dir / "pose_point_up_right.png")
    print("Saved nexus_bot/pose_point_up_right.png")

    # 3. Point Up-Left
    pose_point_l = PoseState(viseme="smile")
    pose_point_l.set_attachment("eyes", "focused")
    pose_point_l.set_joint_rotation("torso", 4.0)
    pose_point_l.set_joint_rotation("head", -6.0)
    sh_angle_l, el_angle_l = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=False, bend_ratio=0.08)
    pose_point_l.set_joint_rotation("arm_l_upper", sh_angle_l)
    pose_point_l.set_joint_rotation("arm_l_lower", el_angle_l)
    pose_point_l.set_attachment("hand_l", "point")
    pose_point_l.set_joint_rotation("arm_r_upper", -25.0)
    pose_point_l.set_joint_rotation("arm_r_lower", 30.0)
    img_point_l = compositor.render_frame(pose_point_l)
    img_point_l.save(preview_dir / "pose_point_up_left.png")
    print("Saved nexus_bot/pose_point_up_left.png")

    # 4. Cheerful High Wave
    pose_wave = PoseState(viseme="open_smile")
    pose_wave.set_attachment("eyes", "happy")
    pose_wave.set_joint_rotation("head", 8.0)
    pose_wave.set_joint_rotation("arm_l_upper", 125.0)
    pose_wave.set_joint_rotation("arm_l_lower", 25.0)
    pose_wave.set_attachment("hand_l", "wave")
    pose_wave.set_joint_rotation("arm_r_upper", -15.0)
    pose_wave.set_joint_rotation("arm_r_lower", -10.0)
    img_wave = compositor.render_frame(pose_wave)
    img_wave.save(preview_dir / "pose_happy_wave.png")
    print("Saved nexus_bot/pose_happy_wave.png")

    # 5. Thumbs Up Pose
    pose_thumb = PoseState(viseme="open_smile")
    pose_thumb.set_attachment("eyes", "happy")
    pose_thumb.set_joint_rotation("head", -4.0)
    pose_thumb.set_joint_rotation("arm_r_upper", -50.0)
    pose_thumb.set_joint_rotation("arm_r_lower", -55.0)
    pose_thumb.set_attachment("hand_r", "thumbs_up")
    img_thumb = compositor.render_frame(pose_thumb)
    img_thumb.save(preview_dir / "pose_thumbs_up.png")
    print("Saved nexus_bot/pose_thumbs_up.png")

    # 6. Thinking Pose
    pose_think = PoseState(viseme="smile")
    pose_think.set_attachment("eyes", "focused")
    pose_think.set_joint_rotation("head", 12.0)
    pose_think.set_joint_rotation("arm_r_upper", -115.0)
    pose_think.set_joint_rotation("arm_r_lower", -90.0)
    pose_think.set_attachment("hand_r", "rest")
    img_think = compositor.render_frame(pose_think)
    img_think.save(preview_dir / "pose_thinking.png")
    print("Saved nexus_bot/pose_thinking.png")

    # 7. Visemes 9-Set Contact Sheet
    visemes = ["smile", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"]
    grid_w, grid_h = 3, 3
    tile_w, tile_h = 320, 320
    grid_img = Image.new("RGBA", (grid_w * tile_w, grid_h * tile_h), (15, 23, 42, 255)) # Dark obsidian background
    draw = ImageDraw.Draw(grid_img)

    for idx, v_name in enumerate(visemes):
        gx = (idx % grid_w) * tile_w
        gy = (idx // grid_w) * tile_h
        p = PoseState(viseme=v_name)
        f = compositor.render_frame(p, target_size=(tile_w, tile_h))
        grid_img.alpha_composite(f, (gx, gy))
        draw.rectangle([gx + 12, gy + 12, gx + 120, gy + 38], fill=(30, 41, 59, 220))
        draw.text((gx + 22, gy + 17), f"/{v_name}/", fill=(0, 245, 255, 255))

    grid_img.save(preview_dir / "visemes_grid_9set.png")
    print("Saved nexus_bot/visemes_grid_9set.png")


def generate_brick_dev_poses():
    from videomascot.assets.starter_brick_dev import create_starter_brick_dev
    from videomascot.engine import MascotEngine
    from videomascot.inspector_builder import generate_html_inspector

    preview_dir = Path("preview/brick_dev")
    preview_dir.mkdir(parents=True, exist_ok=True)

    bundle_dir = create_starter_brick_dev(Path("assets/mascots"))
    engine = MascotEngine.for_character("brick_dev")
    compositor = engine.compositor

    # 1. Neutral Rest Pose
    pose_rest = PoseState(viseme="smile")
    pose_rest.set_attachment("torso", "default")
    pose_rest.set_attachment("head_base", "default")
    pose_rest.set_attachment("eyes", "default")
    img_rest = compositor.render_frame(pose_rest)
    img_rest.save(preview_dir / "pose_neutral_rest.png")
    dark_rest = Image.new("RGB", img_rest.size, (15, 23, 42))
    dark_rest.paste(img_rest, (0, 0), img_rest)
    dark_rest.save(preview_dir / "pose_neutral_on_dark.png")
    print("Saved brick_dev/pose_neutral_rest.png and pose_neutral_on_dark.png")

    # 2. Point Up-Right at Chart
    pose_point_r = PoseState(viseme="smile")
    pose_point_r.set_attachment("torso", "point_up_right")
    pose_point_r.set_attachment("head_base", "point_up_right")
    pose_point_r.set_attachment("eyes", "default")
    img_point_r = compositor.render_frame(pose_point_r)
    img_point_r.save(preview_dir / "pose_point_up_right.png")
    dark_point = Image.new("RGB", img_point_r.size, (15, 23, 42))
    dark_point.paste(img_point_r, (0, 0), img_point_r)
    dark_point.save(preview_dir / "pose_point_up_right_on_dark.png")
    print("Saved brick_dev/pose_point_up_right.png and pose_point_up_right_on_dark.png")

    # 3. Point Up-Left
    pose_point_l = PoseState(viseme="smile")
    pose_point_l.set_attachment("torso", "point_up_left")
    pose_point_l.set_attachment("head_base", "point_up_left")
    pose_point_l.set_attachment("eyes", "default")
    img_point_l = compositor.render_frame(pose_point_l)
    img_point_l.save(preview_dir / "pose_point_up_left.png")
    print("Saved brick_dev/pose_point_up_left.png")

    # 4. Cheerful High Wave
    pose_wave = PoseState(viseme="smile")
    pose_wave.set_attachment("torso", "happy_wave")
    pose_wave.set_attachment("head_base", "happy_wave")
    pose_wave.set_attachment("eyes", "default")
    img_wave = compositor.render_frame(pose_wave)
    img_wave.save(preview_dir / "pose_happy_wave.png")
    dark_wave = Image.new("RGB", img_wave.size, (15, 23, 42))
    dark_wave.paste(img_wave, (0, 0), img_wave)
    dark_wave.save(preview_dir / "pose_happy_wave_on_dark.png")
    print("Saved brick_dev/pose_happy_wave.png and pose_happy_wave_on_dark.png")

    # 5. Thumbs Up Pose
    pose_thumb = PoseState(viseme="smile")
    pose_thumb.set_attachment("torso", "thumbs_up")
    pose_thumb.set_attachment("head_base", "thumbs_up")
    pose_thumb.set_attachment("eyes", "default")
    img_thumb = compositor.render_frame(pose_thumb)
    img_thumb.save(preview_dir / "pose_thumbs_up.png")
    print("Saved brick_dev/pose_thumbs_up.png")

    # 6. Thinking Pose
    pose_think = PoseState(viseme="smile")
    pose_think.set_attachment("torso", "thinking")
    pose_think.set_attachment("head_base", "thinking")
    pose_think.set_attachment("eyes", "default")
    img_think = compositor.render_frame(pose_think)
    img_think.save(preview_dir / "pose_thinking.png")
    print("Saved brick_dev/pose_thinking.png")
    img_think.save(preview_dir / "pose_thinking.png")
    print("Saved brick_dev/pose_thinking.png")

    # 7. Visemes 9-Set Contact Sheet
    visemes = ["smile", "A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q"]
    grid_w, grid_h = 3, 3
    tile_w, tile_h = 320, 320
    grid_img = Image.new("RGBA", (grid_w * tile_w, grid_h * tile_h), (15, 23, 42, 255))
    draw = ImageDraw.Draw(grid_img)

    for idx, v_name in enumerate(visemes):
        gx = (idx % grid_w) * tile_w
        gy = (idx // grid_w) * tile_h
        p = PoseState(viseme=v_name)
        f = compositor.render_frame(p, target_size=(tile_w, tile_h))
        grid_img.alpha_composite(f, (gx, gy))
        draw.rectangle([gx + 12, gy + 12, gx + 120, gy + 38], fill=(30, 41, 59, 220))
        draw.text((gx + 22, gy + 17), f"/{v_name}/", fill=(255, 255, 255, 255))

    grid_img.save(preview_dir / "visemes_grid_9set.png")
    print("Saved brick_dev/visemes_grid_9set.png")

    # 8. Interactive HTML5 Live Rig Inspector
    inspector_file = preview_dir / "inspector.html"
    generate_html_inspector(bundle_dir, inspector_file)
    print(f"Generated brick_dev inspector at {inspector_file}")


if __name__ == "__main__":
    generate_senior_animator_poses()
    generate_nexus_bot_poses()
    generate_brick_dev_poses()

