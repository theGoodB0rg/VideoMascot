import pytest
from pathlib import Path
from PIL import Image

from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.engine import MascotEngine
from videomascot.models.schema import MascotActionSchema, SpeechCue


@pytest.fixture(scope="module")
def tech_chibi_bundle(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("mascots")
    return create_starter_tech_chibi(out_dir)


def test_mascot_engine_stream_exact_frames_and_bytes(tech_chibi_bundle):
    engine = MascotEngine.from_bundle_dir(tech_chibi_bundle)
    
    duration = 1.5
    fps = 24
    expected_frames = int(round(duration * fps)) # 36 frames
    target_w, target_h = 300, 300
    expected_bytes_per_frame = target_w * target_h * 4 # RGBA = 360,000 bytes
    
    action = MascotActionSchema(
        emotion="excited",
        gesture="happy_wave",
        gaze="camera"
    )
    
    stream = engine.stream_scene(
        action=action,
        duration=duration,
        fps=fps,
        target_size=(target_w, target_h)
    )
    
    frame_count = 0
    for chunk in stream:
        assert len(chunk) == expected_bytes_per_frame
        frame_count += 1
        
    assert frame_count == expected_frames


def test_mascot_engine_stream_from_scene_dict(tech_chibi_bundle):
    engine = MascotEngine.from_bundle_dir(tech_chibi_bundle)
    
    scene_dict = {
        "scene_type": "tech_office",
        "emotion": "excited",
        "mascot": {
            "gesture": "point_up_right",
            "prop": "pointer_stick"
        }
    }
    
    cues = [
        SpeechCue(start=0.2, end=0.8, viseme="A_I"),
        SpeechCue(start=0.8, end=1.5, viseme="O"),
    ]
    
    stream = engine.stream_from_scene_dict(
        scene_dict=scene_dict,
        duration=1.0,
        fps=20,
        target_size=(200, 200)
    )
    
    frames = list(stream)
    assert len(frames) == 20
    assert len(frames[0]) == 200 * 200 * 4
