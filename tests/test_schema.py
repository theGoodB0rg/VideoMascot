import pytest
from pydantic import ValidationError
from videomascot.models.schema import (
    MascotActionSchema,
    MascotPlacementSchema,
    MascotProceduralConfig,
    SpeechCue,
    MascotStoryConfig,
)


def test_mascot_action_defaults():
    action = MascotActionSchema()
    assert action.enabled is True
    assert action.character == "chibi_tech_guide"
    assert action.emotion == "friendly"
    assert action.gesture == "idle"
    assert action.gaze == "camera"
    assert action.prop is None
    assert action.placement.anchor == "bottom_right"
    assert action.placement.scale == 0.45
    assert action.procedural.breathing is True


def test_mascot_placement_calculation():
    video_size = (1920, 1080)
    mascot_size = (400, 400)
    
    # Bottom right with 30px offset -> (1920 - 400 - 30, 1080 - 400 - 30) = (1490, 650)
    p_br = MascotPlacementSchema(anchor="bottom_right", offset=(30, 30))
    assert p_br.calculate_position(video_size, mascot_size) == (1490, 650)
    
    # Bottom left with 40px offset -> (40, 1080 - 400 - 40) = (40, 640)
    p_bl = MascotPlacementSchema(anchor="bottom_left", offset=(40, 40))
    assert p_bl.calculate_position(video_size, mascot_size) == (40, 640)
    
    # Bottom center
    p_bc = MascotPlacementSchema(anchor="bottom_center", offset=(0, 20))
    assert p_bc.calculate_position(video_size, mascot_size) == ((1920 - 400) // 2, 1080 - 400 - 20)

    # Custom
    p_custom = MascotPlacementSchema(anchor="custom", custom_pos=(100, 200))
    assert p_custom.calculate_position(video_size, mascot_size) == (100, 200)


def test_invalid_gesture_raises_validation_error():
    with pytest.raises(ValidationError) as excinfo:
        MascotActionSchema(gesture="invalid_backflip")
    assert "gesture" in str(excinfo.value)


def test_invalid_emotion_raises_validation_error():
    with pytest.raises(ValidationError) as excinfo:
        MascotActionSchema(emotion="nonexistent_emotion")
    assert "emotion" in str(excinfo.value)


def test_speech_cues_serialization():
    cue = SpeechCue(start=0.5, end=1.2, viseme="A_I", word="hello")
    action = MascotActionSchema(speech_cues=[cue])
    data = action.model_dump()
    
    restored = MascotActionSchema.model_validate(data)
    assert len(restored.speech_cues) == 1
    assert restored.speech_cues[0].viseme == "A_I"
    assert restored.speech_cues[0].word == "hello"
