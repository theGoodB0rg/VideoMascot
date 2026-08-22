# Declarative Schema Guide 📋

This guide documents the Pydantic-validated declarative schemas used to control mascot animations in VideoMascot. These models are designed for declarative story pipelines (such as `video-pipe` or AI Agent Directors) and eliminate the need for writing custom Python scripts for each video.

---

## 🎯 Architectural Purpose

In automated video generation:
1. **Stories are written in YAML or JSON** by human creators or LLM Directors.
2. **Pre-flight validation** verifies that all emotion, gesture, and placement strings are valid.
3. **VideoMascot deserializes the schema** and automatically drives bone kinematics, procedural breathing, and lip-syncing.

---

## 🧩 Schema Models Reference

### 1. `MascotPlacementSchema`
Defines on-screen positioning and canvas scale relative to the background video.

```python
class MascotPlacementSchema(BaseModel):
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
    scale: float = 0.45          # Relative to video height (0.45 * 1080p = 486px)
    offset: Tuple[int, int] = (30, 30)  # Screen edge margin (x, y) in pixels
    custom_pos: Optional[Tuple[int, int]] = None  # (x, y) if anchor is 'custom'
```

#### Available Anchors

| Anchor | Placement Description | Default Offset |
| :--- | :--- | :--- |
| `bottom_right` *(Default)* | Anchored at bottom-right corner. | `(30, 30)` px from right and bottom edges |
| `bottom_left` | Anchored at bottom-left corner. | `(30, 30)` px from left and bottom edges |
| `bottom_center` | Centered horizontally along the bottom edge. | `(0, 30)` px from bottom |
| `center_right` | Vertically centered along the right edge. | `(30, 0)` px from right edge |
| `center_left` | Vertically centered along the left edge. | `(30, 0)` px from left edge |
| `top_right` | Anchored at top-right corner. | `(30, 30)` px from top-right edges |
| `top_left` | Anchored at top-left corner. | `(30, 30)` px from top-left edges |
| `custom` | Uses exact pixel coordinates from `custom_pos`. | Explicit `(x, y)` |

---

### 2. `MascotActionSchema`
Scene-level animation specification controlling gestures, emotions, and speech.

```python
class MascotActionSchema(BaseModel):
    enabled: bool = True
    character: str = "chibi_tech_guide"
    placement: MascotPlacementSchema = Field(default_factory=MascotPlacementSchema)
    emotion: Literal["friendly", "excited", "serious", "thinking", "shocked", "neutral", "happy"] = "friendly"
    gesture: Literal["idle", "point_up_right", "point_up_left", "happy_wave", "thumbs_up", "thinking", "shock", "shrug"] = "idle"
    gaze: Literal["camera", "point_target", "up_left", "up_right", "down"] = "camera"
    prop: Optional[str] = None
    procedural: MascotProceduralConfig = Field(default_factory=MascotProceduralConfig)
    speech_cues: List[SpeechCue] = Field(default_factory=list)
```

#### Emotions Reference

| Emotion | Facial Features & Baseline Mouth | Best Used For |
| :--- | :--- | :--- |
| `friendly` *(Default)* | Gentle arched eyebrows, warm closed smile (`smile`). | General narration, introductions, storytelling. |
| `excited` | Raised eyebrows, wide happy open smile (`open_smile`), happy eyes. | High-energy hooks, big reveals, enthusiastic CTAs. |
| `serious` | Level eyebrows, neutral resting mouth (`rest`). | Financial metrics, cautionary history, formal news. |
| `thinking` | Tilted eyebrows, thoughtful head tilt (+12 deg), gentle smile. | Posing questions, problem statements, rhetorical hooks. |
| `shocked` | High raised eyebrows, wide open circular mouth (`O`). | Unexpected plot twists, surprising facts, dramatic coup. |
| `neutral` | Standard neutral baseline. | Straightforward informational explainers. |

#### Gestures Reference

| Gesture | Arm & Joint Kinematics | Attachments / Props |
| :--- | :--- | :--- |
| `idle` *(Default)* | Relaxed arms resting comfortably by torso. | `hand_r: rest`, `hand_l: rest` |
| `point_up_right` | Right arm extends up-right (+40 deg) via analytical FK; left hand on hip. | `hand_r: point`, optional `prop_r: pointer_stick` |
| `point_up_left` | Left arm extends up-left (+40 deg) via analytical FK; right hand on hip. | `hand_l: point`, optional `prop_l: pointer_stick` |
| `happy_wave` | Left arm raised high (+125 deg) in a cheerful wave; warm expression. | `hand_l: wave`, happy eye sclera |
| `thumbs_up` | Right arm bent with forearm raised (+50 deg); confident expression. | `hand_r: thumbs_up` |
| `thinking` | Right hand raised to chin (-115 deg shoulder bend); head tilted. | `hand_r: rest` |
| `shock` | Both arms thrown outwards in alarm; wide eyes. | `hand_r: wave`, `hand_l: wave` |
| `shrug` | Both forearms bent outwards with palms up. | `hand_r: wave`, `hand_l: wave` |

#### Gaze Targets Reference

| Gaze Target | Pupil Offset Vector | Description |
| :--- | :--- | :--- |
| `camera` *(Default)* | `(0, 0)` | Eyes look directly forward at the viewer. |
| `point_target` | `(-8, -4)` or `(+8, -4)` | Eyes look towards the direction the mascot is pointing. |
| `up_left` | `(-8, -6)` | Looks up-left toward on-screen titles or graphics. |
| `up_right` | `(+8, -6)` | Looks up-right toward on-screen charts. |
| `down` | `(0, +6)` | Looks downwards. |

---

### 3. `MascotProceduralConfig`
Controls the automated continuous micro-motion so characters never appear frozen.

```python
class MascotProceduralConfig(BaseModel):
    breathing: bool = True               # Enables sinusoidal torso respiration
    breathing_bpm: float = 18.0          # Breaths per minute (default: 18)
    breathing_intensity: float = 1.0     # Expansion amplitude multiplier
    blinking: bool = True                # Enables Poisson-distributed eye blinks
    blink_interval_mean: float = 3.5     # Mean seconds between blinks
    blink_duration: float = 0.14         # Single blink duration (140ms)
    gaze_saccades: bool = True           # Subtle harmonic pupil micro-drift
    bounce_on_speak: bool = True         # Speech micro-bounce during narration
```

---

### 4. `SpeechCue`
Defines explicit phonetic / viseme timing for speech synchronization.

```python
class SpeechCue(BaseModel):
    start: float     # Start timestamp in seconds
    end: float       # End timestamp in seconds
    viseme: str      # Target mouth shape (e.g. 'A_I', 'O', 'smile')
    word: Optional[str] = None  # Optional word transcription
```

---

## 📝 Example Declarative Scripts

### Example YAML Script (`story.yaml`)

```yaml
title: "Tech Innovation in Lagos"
mascot_config:
  character: "chibi_tech_guide"
  placement:
    anchor: "bottom_right"
    scale: 0.45

scenes:
  - scene_type: "tech_office"
    narration: "Welcome back! Today we are exploring the tech ecosystem."
    text_overlay: "Silicon Lagoon"
    emotion: "excited"
    mascot:
      emotion: "excited"
      gesture: "happy_wave"
      gaze: "camera"

  - scene_type: "cityscape"
    narration: "Take a look at the funding growth chart on the left."
    text_overlay: "Venture Growth"
    emotion: "friendly"
    mascot:
      gesture: "point_up_left"
      gaze: "point_target"
      prop: "pointer_stick"

  - scene_type: "abstract"
    narration: "So what makes this ecosystem so resilient?"
    text_overlay: "Key Drivers"
    emotion: "thinking"
    mascot:
      emotion: "thinking"
      gesture: "thinking"
```

---

## 🧠 Smart Automatic Fallbacks

When generating video in batch pipelines, if specific mascot fields are omitted, VideoMascot applies sensible defaults:

1. **No `mascot` block in scene**: Uses global story defaults (`emotion="friendly"`, `gesture="idle"`).
2. **Missing `emotion` in mascot block**: Automatically matches the scene's top-level `emotion` tag.
3. **No explicit `speech_cues`**: Automatically resolves speech intervals from accompanying `.vtt` subtitle files or TTS audio duration.
4. **Procedural life enabled by default**: Respiration and natural blinking are always active.
