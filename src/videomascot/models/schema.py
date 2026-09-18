from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Literal
from pydantic import BaseModel, Field


class MascotPlacementSchema(BaseModel):
    """Screen placement and scaling configuration for mascot overlay."""
    anchor: Literal[
        "bottom_right",
        "bottom_left",
        "bottom_center",
        "center_right",
        "center_left",
        "top_right",
        "top_left",
        "custom"
    ] = "bottom_right"
    scale: float = Field(default=0.45, ge=0.05, le=2.0, description="Scale relative to video height (e.g. 0.45 of 1080p = ~486px)")
    offset: Tuple[int, int] = Field(default=(30, 30), description="Margin offset (x, y) from anchor edge in pixels")
    custom_pos: Optional[Tuple[int, int]] = Field(default=None, description="Absolute canvas coordinates (x, y) if anchor is 'custom'")

    def calculate_position(
        self,
        video_size: Tuple[int, int],
        mascot_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Calculates exact top-left (x, y) placement on video canvas."""
        vw, vh = video_size
        mw, mh = mascot_size
        ox, oy = self.offset

        if self.anchor == "custom" and self.custom_pos is not None:
            return self.custom_pos
        elif self.anchor == "bottom_right":
            return (vw - mw - ox, vh - mh - oy)
        elif self.anchor == "bottom_left":
            return (ox, vh - mh - oy)
        elif self.anchor == "bottom_center":
            return ((vw - mw) // 2, vh - mh - oy)
        elif self.anchor == "center_right":
            return (vw - mw - ox, (vh - mh) // 2)
        elif self.anchor == "center_left":
            return (ox, (vh - mh) // 2)
        elif self.anchor == "top_right":
            return (vw - mw - ox, oy)
        elif self.anchor == "top_left":
            return (ox, oy)
        return (vw - mw - ox, vh - mh - oy)


class MascotProceduralConfig(BaseModel):
    """Configuration for automated continuous micro-motion."""
    breathing: bool = Field(default=True, description="Enables subtle sinusoidal torso respiration")
    breathing_bpm: float = Field(default=18.0, ge=5.0, le=60.0, description="Respiration breaths per minute")
    breathing_intensity: float = Field(default=1.0, ge=0.0, le=3.0, description="Torso expansion amplitude multiplier")
    
    blinking: bool = Field(default=True, description="Enables automated natural eye blinks")
    blink_interval_mean: float = Field(default=3.5, ge=1.0, le=10.0, description="Mean seconds between natural blinks")
    blink_duration: float = Field(default=0.14, ge=0.05, le=0.4, description="Duration of single blink in seconds")
    
    gaze_saccades: bool = Field(default=True, description="Enables subtle lifelike pupil micro-movements")
    bounce_on_speak: bool = Field(default=True, description="Enables secondary micro-bounce during speech visemes")
    hover: bool = Field(default=False, description="Enables multi-harmonic levitation hover dynamics for tech bots")
    hover_amplitude: float = Field(default=6.0, ge=0.0, le=30.0, description="Vertical levitation drift amplitude in pixels")
    hover_bpm: float = Field(default=22.0, ge=5.0, le=60.0, description="Levitation hover cycles per minute")



class SpeechCue(BaseModel):
    """Single speech phonetic / viseme cue event."""
    start: float = Field(..., ge=0.0, description="Start timestamp in seconds")
    end: float = Field(..., ge=0.0, description="End timestamp in seconds")
    viseme: str = Field(..., description="Target viseme mouth shape (e.g. 'A_I', 'O', 'smile')")
    word: Optional[str] = Field(default=None, description="Optional spoken word transcription")


class MascotActionSchema(BaseModel):
    """Declarative scene-level mascot action and emotion specification."""
    enabled: bool = Field(default=True, description="Whether mascot is visible in this scene")
    character: str = Field(default="chibi_tech_guide", description="Mascot character bundle ID")
    placement: MascotPlacementSchema = Field(default_factory=MascotPlacementSchema)
    
    emotion: Literal[
        "friendly",
        "excited",
        "serious",
        "thinking",
        "shocked",
        "neutral",
        "happy"
    ] = Field(default="friendly", description="Base facial expression")
    
    gesture: Literal[
        "idle",
        "point_up_right",
        "point_up_left",
        "happy_wave",
        "thumbs_up",
        "thinking",
        "shock",
        "shrug"
    ] = Field(default="idle", description="Kinematic pose / arm gesture")
    
    gaze: Literal[
        "camera",
        "point_target",
        "up_left",
        "up_right",
        "down"
    ] = Field(default="camera", description="Eye pupil gaze target")
    
    prop: Optional[str] = Field(default=None, description="Optional attached prop (e.g. 'pointer_stick')")
    procedural: MascotProceduralConfig = Field(default_factory=MascotProceduralConfig)
    speech_cues: List[SpeechCue] = Field(default_factory=list, description="Explicit phoneme / viseme timing cues")
    transition_in: bool = Field(default=False, description="Whether to slide in from bottom on start")
    transition_out: bool = Field(default=False, description="Whether to slide out downwards on exit")
    duration: Optional[float] = Field(default=None, description="Clip duration in seconds for timing transitions")


class MascotStoryConfig(BaseModel):
    """Global story-level default mascot configuration."""
    character: str = Field(default="chibi_tech_guide")
    placement: MascotPlacementSchema = Field(default_factory=MascotPlacementSchema)
    default_emotion: str = Field(default="friendly")
    procedural: MascotProceduralConfig = Field(default_factory=MascotProceduralConfig)
