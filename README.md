# VideoMascot 🎭

A modular, scalable, test-driven, AI-ready layered puppet and mascot animation engine designed for automated video pipelines (faceless channels, explainer videos, educational content).

---

## 🎬 Visual Demos & Previews

### 1. Flagship Asset: "Nexus Bot" (Sleek Futuristic Tech Companion)
*High-fidelity modern motion graphics benchmark with floating magnetic limbs (zero joint crease clipping), curved obsidian visor, and digital acoustic visemes.*

| Nexus Bot In-Memory Streaming Overlay | Standalone Transparent Alpha Stream (Hover & Speech) |
| :---: | :---: |
| ![Nexus Bot Overlay Demo](preview/nexus_bot/demo_nexus_overlay.gif) | ![Transparent Nexus Bot](preview/nexus_bot/demo_nexus_alpha.gif) |
| [Download Full MP4 (`preview/nexus_bot/demo_nexus_overlay.mp4`)](preview/nexus_bot/demo_nexus_overlay.mp4) | [Download Transparent WebM (`preview/nexus_bot/demo_nexus_alpha.webm`)](preview/nexus_bot/demo_nexus_alpha.webm) |

---

### 2. Digital 9-Viseme Acoustic Speech Waveforms
*Real-time speech synchronization mapping phonetic timestamps and WebVTT subtitles directly onto emissive visor surfaces.*

![Nexus Bot 9-Viseme Digital Set](preview/nexus_bot/visemes_grid_9set.png)

---

### 3. Kinematic Gesture & Expression Gallery
*2-joint Forward & Inverse Kinematics (`solve_pointing_fk`, `solve_2joint_ik`) with magnetic levitation joints and holographic props.*

| Cheerful Wave | Point Up-Right (Hologram Stylus) | Confident Thumbs Up | Thinking Pose |
| :---: | :---: | :---: | :---: |
| <img src="preview/nexus_bot/pose_happy_wave.png" width="220"/> | <img src="preview/nexus_bot/pose_point_up_right.png" width="220"/> | <img src="preview/nexus_bot/pose_thumbs_up.png" width="220"/> | <img src="preview/nexus_bot/pose_thinking.png" width="220"/> |

---

### 4. Character Asset: "Brick Dev" (Lego-Style Senior Software Engineer)
*Modular brick-minifigure software developer with textured curly hair, trimmed mustache/goatee, sky-blue striped polo, and classic C-hands.*

| Brick Dev In-Memory Streaming Overlay | Standalone Transparent Alpha Stream (Wave & Speech) |
| :---: | :---: |
| ![Brick Dev Overlay Demo](preview/brick_dev/demo_brick_overlay.gif) | ![Transparent Brick Dev](preview/brick_dev/demo_brick_alpha.gif) |
| [Download Full MP4 (`preview/brick_dev/demo_brick_overlay.mp4`)](preview/brick_dev/demo_brick_overlay.mp4) | [Download Transparent WebM (`preview/brick_dev/demo_brick_alpha.webm`)](preview/brick_dev/demo_brick_alpha.webm) |

#### Brick Dev 9-Viseme Acoustic Speech Set & Kinematics Gallery
![Brick Dev 9-Viseme Set](preview/brick_dev/visemes_grid_9set.png)

| Neutral Rest | Cheerful High Wave | Point Up-Right | Confident Thumbs Up | Thinking Pose |
| :---: | :---: | :---: | :---: | :---: |
| <img src="preview/brick_dev/pose_neutral_rest.png" width="180"/> | <img src="preview/brick_dev/pose_happy_wave.png" width="180"/> | <img src="preview/brick_dev/pose_point_up_right.png" width="180"/> | <img src="preview/brick_dev/pose_thumbs_up.png" width="180"/> | <img src="preview/brick_dev/pose_thinking.png" width="180"/> |

*Interactive Live Web Inspector: [`preview/brick_dev/inspector.html`](preview/brick_dev/inspector.html)*

---

## 🌟 Key Features

- **Decoupled Multi-Mascot Registry (`MascotRegistry`)**: Dynamically discovers and loads self-contained character bundles from `assets/mascots/`. The system is 100% aesthetic-agnostic.
- **Organic Motion Dynamics & Secondary Spring Physics**: Continuous 1D damped harmonic spring-damper solvers (`SpringDamper1D`, `BoneSpringSimulator`) generating realistic inertia on antennae and props.
- **Motion Graphics Cubic Bezier Easing**: Replaces linear interpolation with industry-standard parametric Cubic Bezier curves (`SPRING_OVERSHOOT`, `ANTICIPATION`, `EASE_OUT_EXPO`).
- **High-Performance Bounding-Box Compositor**: Replaces full-canvas transforms with cropped local bounding-box affine blitting, delivering over $3\times$ faster rendering speeds.
- **Floating Magnetic Articulation**: Eliminates cardboard joint crease seams during $360^\circ$ limb rotations.
- **100% Background-less Alpha Canvas**: Pure transparent RGBA rendering with zero bounding box artifacts.
- **Standard 9-Viseme Lip-Sync (Preston Blair Set)**: Real-time mouth shaping for speech synchronization (`rest`, `smile`, `open_smile`, `A_I`, `E`, `O`, `U`, `M_B_P`, `F_V`, `L_D_T_N`, `W_Q`).
- **Continuous Procedural Life & Hover Layer**: Multi-harmonic levitation hover drift, Poisson-distributed natural eye blinks, and saccadic pupil gaze tracking.
- **In-Memory Zero-Disk Streaming Engine**: Streams raw uncompressed RGBA pixel buffers directly to FFmpeg subprocess pipes in constant $O(1)$ memory.
- **Standalone Alpha Video Exporters**: Export transparent videos to WebM VP9 (`yuva420p`) or Apple ProRes 4444 (`yuva444p10le`).
- **Interactive Live Web Inspector**: Single-file HTML5/Canvas preview tool (`preview/nexus_bot/inspector.html`) to test joint angles, visemes, and poses live in your browser.


---

## 🚀 Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/theGoodB0rg/VideoMascot.git
cd VideoMascot

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Tests (100% Green Test-Driven Suite)

```bash
pytest tests/ -v
```

### Generating Sample Poses, Demos & Live Inspector

```bash
# Generate static poses & web inspector
python preview_poses.py

# Generate in-memory animated streaming overlay & transparent WebM/GIFs
python preview_stream.py
```

### Launching the Live Web Inspector

Open `preview/inspector.html` in any modern web browser to interact with joint angles, visemes, and expressions live.

---

## 📐 Architecture Overview

```
src/videomascot/
├── core/
│   ├── math_2d.py           # 2D Vectors, Transform matrices, Easing functions
│   ├── bones.py             # Bone hierarchy, 2-joint IK/FK solvers
│   └── slots.py             # Modular slot attachment management
├── models/
│   ├── manifest.py          # Pydantic schemas for MascotManifest & configs
│   ├── pose.py              # Runtime PoseState & joint definitions
│   └── schema.py            # Declarative action, placement, and speech cue schemas
├── animation/
│   ├── procedural.py        # Breathing oscillation, Poisson eye blinks, saccades
│   ├── lipsync.py           # VTT and timestamped 9-viseme lip-sync engine
│   └── sequencer.py         # Kinematic gesture sequencer & pose interpolation
├── compositor/
│   ├── sprite_engine.py     # Multi-layer alpha sprite compositor
│   └── stream_engine.py     # In-memory raw RGBA stream frame generator
├── pipeline/
│   └── video_overlay.py     # Direct FFmpeg subprocess streaming video compositor
├── assets/
│   └── starter_mascot.py    # Starter asset bundle generator (Chibi Tech Guide)
├── inspector_builder.py     # Standalone HTML5 inspector builder
└── engine.py                # High-level MascotEngine facade
```

---

## 💡 Consumer Usage Example (e.g. inside `video-pipe`)

```python
from videomascot import MascotEngine, VideoOverlayCompositor, MascotActionSchema, MascotPlacementSchema

# 1. Initialize engine from mascot bundle directory
engine = MascotEngine.from_bundle_dir("assets/mascots/chibi_tech_guide")

# 2. Configure action declaratively (or deserialize from story.json/story.yaml)
action = MascotActionSchema(
    emotion="excited",
    gesture="point_up_left",
    gaze="point_target",
    prop="pointer_stick",
    placement=MascotPlacementSchema(anchor="bottom_right", scale=0.45)
)

# 3. Stream uncompressed RGBA bytes directly into FFmpeg stdin pipe (Zero Disk I/O)
for frame_bytes in engine.stream_scene(action=action, duration=4.5, fps=24):
    ffmpeg_process.stdin.write(frame_bytes)

# Or overlay directly onto an existing background video file in one call
compositor = VideoOverlayCompositor(engine=engine)
compositor.overlay_onto_video(
    input_video="scene_bg.mp4",
    output_video="scene_with_mascot.mp4",
    action=action
)
```

## 📚 Documentation & Guides

Comprehensive guides and architectural references are available in the [`/docs/`](docs/index.md) folder:

* **[Getting Started](docs/getting_started.md)**: Installation, prerequisites, quickstart, and demo generation.
* **[Declarative Schema Guide](docs/schema_guide.md)**: Reference for YAML/JSON directives (emotions, gestures, placements, speech cues).
* **[Animation & 9-Viseme Lip-Sync](docs/animation_and_lipsync.md)**: Preston Blair mouth sets, WebVTT/EdgeTTS speech sync, and procedural breathing.
* **[Rigging & Kinematics](docs/rigging_and_kinematics.md)**: 2.5D bone hierarchy, 3x3 affine transforms, and 2-joint analytical IK/FK solvers.
* **[Custom Mascot Guide](docs/custom_mascot_guide.md)**: Tutorial for creating, slicing, and rigging new character bundles.
* **[Video Pipeline Integration](docs/video_pipeline_integration.md)**: In-memory zero-disk FFmpeg streaming and automated pipeline bridges.
* **[Testing & Quality Assurance](docs/testing_and_qa.md)**: TDD principles, alpha integrity testing, and test suite execution.
* **[Changelog](CHANGELOG.md)**: Release history and version notes.

---

## License

MIT
