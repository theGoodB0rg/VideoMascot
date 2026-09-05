from pathlib import Path
import subprocess

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.engine import MascotEngine
from videomascot.models.schema import MascotActionSchema, SpeechCue, MascotPlacementSchema
from videomascot.pipeline.video_overlay import VideoOverlayCompositor


def generate_demos():
    preview_dir = Path("preview")
    preview_dir.mkdir(exist_ok=True)
    
    bundle_dir = create_starter_tech_chibi(Path("assets/mascots"))
    engine = MascotEngine.from_bundle_dir(bundle_dir)
    
    # 1. Export Standalone Transparent Alpha WebM
    print("[1/3] Exporting Standalone Transparent Alpha WebM (preview/demo_mascot_alpha.webm)...")
    action = MascotActionSchema(
        emotion="excited",
        gesture="happy_wave",
        gaze="camera",
        speech_cues=[
            SpeechCue(start=0.3, end=0.8, viseme="A_I", word="Welcome"),
            SpeechCue(start=0.8, end=1.4, viseme="O", word="everyone"),
            SpeechCue(start=1.4, end=2.2, viseme="smile", word="today"),
        ]
    )
    
    webm_path = preview_dir / "demo_mascot_alpha.webm"
    engine.export_alpha_video(
        action=action,
        duration=3.0,
        output_path=webm_path,
        fps=24,
        codec="vp9",
        target_size=(360, 360)
    )
    print("Exported demo_mascot_alpha.webm")

    # 2. Convert transparent WebM to animated GIF for README embedding
    print("[2/3] Generating Animated GIF for Transparent Mascot (preview/demo_mascot_alpha.gif)...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-vf", "fps=15,scale=260:-1:flags=lanczos,split[s0][s1];[s0]palettegen=reserve_transparent=1[p];[s1][p]paletteuse=alpha_threshold=128",
        str(preview_dir / "demo_mascot_alpha.gif")
    ], check=True, capture_output=True)
    print("Generated demo_mascot_alpha.gif")

    # 3. Generating Synthetic Background & In-Memory Streaming Overlay
    print("\n[3/3] Generating Synthetic Background and Streaming In-Memory Overlay (preview/demo_overlay.mp4)...")
    bg_video = preview_dir / "demo_bg.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=0x1e293b:s=1280x720:d=3.0:r=24",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(bg_video)
    ], check=True, capture_output=True)
    
    action_overlay = MascotActionSchema(
        emotion="friendly",
        gesture="point_up_left",
        gaze="point_target",
        prop="pointer_stick",
        placement=MascotPlacementSchema(anchor="bottom_right", scale=0.45, offset=(40, 40)),
        speech_cues=[
            SpeechCue(start=0.2, end=0.9, viseme="A_I"),
            SpeechCue(start=0.9, end=1.8, viseme="O"),
            SpeechCue(start=1.8, end=2.8, viseme="smile"),
        ]
    )
    
    compositor = VideoOverlayCompositor.from_bundle_dir(bundle_dir)
    out_video = preview_dir / "demo_overlay.mp4"
    compositor.overlay_onto_video(
        input_video=bg_video,
        output_video=out_video,
        action=action_overlay
    )
    print(f"Generated in-memory streaming overlay demo: {out_video}")

    # Convert overlay video to animated GIF for README
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(out_video),
        "-vf", "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        str(preview_dir / "demo_overlay.gif")
    ], check=True, capture_output=True)
    print("Generated demo_overlay.gif")


def generate_nexus_stream_demos():
    preview_dir = Path("preview/nexus_bot")
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    engine = MascotEngine.for_character("nexus_bot")
    
    # 1. Export Standalone Transparent Alpha WebM for Nexus Bot
    print("[1/3] Exporting Nexus Bot Transparent Alpha WebM (preview/nexus_bot/demo_nexus_alpha.webm)...")
    action = MascotActionSchema(
        character="nexus_bot",
        emotion="excited",
        gesture="happy_wave",
        gaze="camera",
        procedural={"hover": True, "hover_amplitude": 12.0, "blinking": True},
        speech_cues=[
            SpeechCue(start=0.3, end=0.8, viseme="A_I", word="Welcome"),
            SpeechCue(start=0.8, end=1.4, viseme="O", word="everyone"),
            SpeechCue(start=1.4, end=2.2, viseme="smile", word="today"),
        ]
    )
    
    webm_path = preview_dir / "demo_nexus_alpha.webm"
    engine.export_alpha_video(
        action=action,
        duration=3.0,
        output_path=webm_path,
        fps=24,
        codec="vp9",
        target_size=(380, 380)
    )
    print("Exported demo_nexus_alpha.webm")

    # 2. Convert transparent WebM to animated GIF
    print("[2/3] Generating Animated GIF for Transparent Nexus Bot...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-vf", "fps=15,scale=280:-1:flags=lanczos,split[s0][s1];[s0]palettegen=reserve_transparent=1[p];[s1][p]paletteuse=alpha_threshold=128",
        str(preview_dir / "demo_nexus_alpha.gif")
    ], check=True, capture_output=True)
    print("Generated demo_nexus_alpha.gif")

    # 3. Generating Tech Gradient Background and In-Memory Streaming Overlay
    print("[3/3] Generating Tech Overlay Demo (preview/nexus_bot/demo_nexus_overlay.mp4)...")
    bg_video = preview_dir / "nexus_bg.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=0x0b0f19:s=1280x720:d=3.0:r=24",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(bg_video)
    ], check=True, capture_output=True)

    action_overlay = MascotActionSchema(
        character="nexus_bot",
        emotion="friendly",
        gesture="point_up_right",
        gaze="point_target",
        prop="hologram_pointer",
        procedural={"hover": True, "hover_amplitude": 8.0, "blinking": True},
        placement=MascotPlacementSchema(anchor="bottom_right", scale=0.55, offset=(40, 30)),
        speech_cues=[
            SpeechCue(start=0.2, end=0.9, viseme="A_I"),
            SpeechCue(start=0.9, end=1.8, viseme="O"),
            SpeechCue(start=1.8, end=2.8, viseme="smile"),
        ]
    )

    compositor = VideoOverlayCompositor(engine=engine)
    out_video = preview_dir / "demo_nexus_overlay.mp4"
    compositor.overlay_onto_video(
        input_video=bg_video,
        output_video=out_video,
        action=action_overlay
    )
    print(f"Generated in-memory streaming overlay demo: {out_video}")

    # Convert overlay video to animated GIF
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(out_video),
        "-vf", "fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        str(preview_dir / "demo_nexus_overlay.gif")
    ], check=True, capture_output=True)
    print("Generated demo_nexus_overlay.gif")


if __name__ == "__main__":
    generate_demos()
    generate_nexus_stream_demos()

