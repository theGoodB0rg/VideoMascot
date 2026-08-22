"""VideoMascot Animation Subsystem — Procedural life, 9-viseme lip-sync, and temporal sequencers."""
from videomascot.animation.procedural import ProceduralLifeEngine
from videomascot.animation.lipsync import LipSyncEngine, SpeechCue
from videomascot.animation.sequencer import MascotSequencer

__all__ = [
    "ProceduralLifeEngine",
    "LipSyncEngine",
    "SpeechCue",
    "MascotSequencer",
]
