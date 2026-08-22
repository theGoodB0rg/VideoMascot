import pytest
from videomascot.models.schema import SpeechCue
from videomascot.animation.lipsync import LipSyncEngine, parse_vtt_timestamp


def test_parse_vtt_timestamp():
    assert parse_vtt_timestamp("00:00:01.500") == 1.5
    assert parse_vtt_timestamp("00:02.300") == 2.3
    assert parse_vtt_timestamp("01:05.100") == 65.1


def test_lipsync_from_explicit_cues():
    cues = [
        SpeechCue(start=1.0, end=1.5, viseme="A_I"),
        SpeechCue(start=1.5, end=2.0, viseme="O"),
    ]
    engine = LipSyncEngine(cues=cues, default_resting_viseme="smile")
    
    # Before speech: resting smile
    v, speaking = engine.get_viseme_at(0.5)
    assert v == "smile"
    assert speaking is False
    
    # During first cue
    v, speaking = engine.get_viseme_at(1.2)
    assert v == "A_I"
    assert speaking is True
    
    # During second cue
    v, speaking = engine.get_viseme_at(1.8)
    assert v == "O"
    assert speaking is True
    
    # After speech: returns to smile
    v, speaking = engine.get_viseme_at(2.5)
    assert v == "smile"
    assert speaking is False


def test_lipsync_from_vtt_content():
    vtt_data = """WEBVTT

00:00.500 --> 00:02.000
<v Narrator>Welcome to the system architecture tutorial.</v>

00:03.000 --> 00:04.500
Notice how fast it scales up.
"""
    engine = LipSyncEngine.from_vtt_content(vtt_data, default_resting_viseme="smile")
    assert len(engine.cues) > 0
    
    # Mid-first-sentence: should be actively speaking
    v, speaking = engine.get_viseme_at(1.0)
    assert speaking is True
    assert v in ("A_I", "E", "O", "U", "M_B_P", "F_V", "L_D_T_N", "W_Q")
    
    # Pause between sentences (t = 2.5s): resting smile
    v_pause, speaking_pause = engine.get_viseme_at(2.5)
    assert v_pause == "smile"
    assert speaking_pause is False
