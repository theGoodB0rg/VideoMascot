import subprocess
from pathlib import Path
import pytest

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.engine import MascotEngine
from videomascot.models.schema import MascotActionSchema, SpeechCue
from videomascot.pipeline.video_overlay import VideoOverlayCompositor, probe_video_info


@pytest.fixture(scope="module")
def tech_chibi_bundle(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("mascots")
    return create_starter_tech_chibi(out_dir)


def create_synthetic_test_video(output_path: Path, duration: float = 1.5, width: int = 640, height: int = 360, fps: int = 24) -> Path:
    """Generates a synthetic MP4 video using ffmpeg's lavfi color test source."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=navy:s={width}x{height}:d={duration}:r={fps}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def test_video_overlay_compositor_end_to_end(tmp_path, tech_chibi_bundle):
    # 1. Create synthetic 1.5-second background video
    bg_video = tmp_path / "bg_scene.mp4"
    out_video = tmp_path / "scene_with_mascot.mp4"
    create_synthetic_test_video(bg_video, duration=1.5, width=640, height=360, fps=24)
    
    # 2. Configure mascot action
    action = MascotActionSchema(
        emotion="excited",
        gesture="happy_wave",
        speech_cues=[
            SpeechCue(start=0.2, end=0.6, viseme="A_I"),
            SpeechCue(start=0.6, end=1.2, viseme="O")
        ]
    )
    
    # 3. Perform in-memory streaming overlay
    compositor = VideoOverlayCompositor.from_bundle_dir(tech_chibi_bundle)
    result = compositor.overlay_onto_video(
        input_video=bg_video,
        output_video=out_video,
        action=action
    )
    
    assert result.exists()
    assert result.stat().st_size > 1000
    
    # 4. Probe output video
    w, h, dur, fps = probe_video_info(result)
    assert w == 640
    assert h == 360
    assert abs(dur - 1.5) < 0.2
    assert abs(fps - 24.0) < 1.0


def test_mascot_engine_export_alpha_video_webm(tmp_path, tech_chibi_bundle):
    engine = MascotEngine.from_bundle_dir(tech_chibi_bundle)
    out_webm = tmp_path / "mascot_alpha.webm"
    
    action = MascotActionSchema(
        emotion="friendly",
        gesture="point_up_right",
        prop="pointer_stick"
    )
    
    result = engine.export_alpha_video(
        action=action,
        duration=1.0,
        output_path=out_webm,
        fps=20,
        codec="vp9",
        target_size=(200, 200)
    )
    
    assert result.exists()
    assert result.stat().st_size > 1000
