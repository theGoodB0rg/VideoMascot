# Getting Started with VideoMascot 🚀

This guide walks you through installing VideoMascot, verifying your environment, generating sample assets, and executing your first mascot animation.

---

## 🛠️ Prerequisites

Before installing VideoMascot, ensure you have:

1. **Python 3.10 or newer** (`python --version`)
2. **FFmpeg installed and available on your system `PATH`** (`ffmpeg -version`):
   - **Windows**: Install via `winget install Gyan.FFmpeg` or `choco install ffmpeg`.
   - **macOS**: Install via `brew install ffmpeg`.
   - **Linux**: Install via `sudo apt update && sudo apt install ffmpeg`.

---

## 📦 Installation

Clone the repository and install it in editable mode with development dependencies:

```bash
# Clone repository
git clone https://github.com/theGoodB0rg/VideoMascot.git
cd VideoMascot

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install package with test and dev tools
pip install -e ".[dev]"
```

---

## 🧪 Verifying Installation (Running Tests)

VideoMascot is built with strict Test-Driven Development (TDD). Verify all 38 automated test cases:

```bash
pytest tests/ -v
```

You should see all tests pass with green checkmarks:
```
============================= 38 passed in 25.83s =============================
```

---

## 🎨 Generating Sample Previews & Demos

VideoMascot comes with built-in scripts to generate static poses, animated video demos, and the live web inspector.

### 1. Generate Static Poses & Web Inspector
```bash
python preview_poses.py
```
This generates:
* `preview/pose_neutral_rest.png` (Warm friendly smile)
* `preview/pose_point_up_right.png` (Pointing up-right with stick prop)
* `preview/pose_point_up_left.png` (Pointing up-left)
* `preview/pose_happy_wave.png` (High cheerful wave)
* `preview/pose_thumbs_up.png` (Encouraging thumbs up)
* `preview/pose_thinking.png` (Thoughtful chin pose)
* `preview/pose_shock.png` (Surprised expression)
* `preview/visemes_grid_9set.png` (9-viseme speech contact sheet)
* `preview/inspector.html` (Interactive web tool)

### 2. Launch the Live Web Inspector
Open `preview/inspector.html` in any browser:
* **Interactive Joint Sliders**: Adjust torso, head, shoulder, elbow, and hand rotations live.
* **Viseme Selector**: Switch between speech mouth shapes in real-time on an HTML5 Canvas.
* **Gesture Buttons**: Test preset animations with one click.

### 3. Generate Video Demos & Transparent WebM Clips
```bash
python preview_stream.py
```
This generates:
* `preview/demo_mascot_alpha.webm` (Transparent alpha video with lip-sync and breathing)
* `preview/demo_overlay.mp4` (In-memory streaming video overlay over a background scene)
* `preview/demo_overlay.gif` and `preview/demo_mascot_alpha.gif` (Animated demo GIFs)

---

## 💻 Quick Code Examples

### Example 1: Render a Single Transparent PNG
```python
from videomascot import MascotEngine, PoseState

# Initialize engine from starter bundle
engine = MascotEngine.from_bundle_dir("assets/mascots/chibi_tech_guide")

# Configure a pose
pose = PoseState(viseme="smile")
pose.set_joint_rotation("arm_r_upper", -40.0)
pose.set_attachment("hand_r", "thumbs_up")

# Render transparent RGBA image
frame = engine.render_frame(pose, target_size=(500, 500))
frame.save("my_mascot.png")
print("Saved transparent PNG!")
```

### Example 2: Stream Animated Frames in Python
```python
from videomascot import MascotEngine, MascotActionSchema, SpeechCue

engine = MascotEngine.from_bundle_dir("assets/mascots/chibi_tech_guide")

# Configure declarative action
action = MascotActionSchema(
    emotion="excited",
    gesture="happy_wave",
    gaze="camera",
    speech_cues=[
        SpeechCue(start=0.2, end=0.8, viseme="A_I"),
        SpeechCue(start=0.8, end=1.5, viseme="O"),
    ]
)

# Stream raw RGBA byte frames (24 fps for 3.0 seconds = 72 frames)
for frame_bytes in engine.stream_scene(action=action, duration=3.0, fps=24, target_size=(360, 360)):
    # frame_bytes is uncompressed RGBA bytes (360 * 360 * 4 = 518,400 bytes)
    pass
```

---

## ⏭️ Next Steps

* Learn how to write declarative story scripts in the **[Declarative Schema Guide](schema_guide.md)**.
* Understand the lip-sync and procedural breathing engine in **[Animation & Lip-Sync](animation_and_lipsync.md)**.
* Learn how to connect VideoMascot to automated video generators in **[Video Pipeline Integration](video_pipeline_integration.md)**.
