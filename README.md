# VideoMascot 🎭

A modular, scalable, test-driven, AI-ready layered puppet and mascot animation engine designed for automated video pipelines (faceless channels, explainer videos, educational content).

---

## Key Features

- **Layered 2.5D Sprite Puppet Rig**: High-fidelity character models composed of modular slots (Head, Eyes, Pupils, Eyebrows, Viseme Mouths, Body, Limbs, Props).
- **Universal Kinematic Hierarchy**: 3x3 affine matrix propagation with analytical 2-joint Forward & Inverse Kinematics (`solve_2joint_ik`, `solve_pointing_fk`).
- **Standard 9-Viseme Lip-Sync (Preston Blair Set)**: Real-time mouth shaping for speech synchronization (`rest`, `A_I`, `E`, `O`, `U`, `M_B_P`, `F_V`, `L_D_T_N`, `W_Q`).
- **Dynamic Gaze & Procedural Life Layer**: Eyes dynamically follow screen coordinates/camera, automated natural eye-blinking cycles, and secondary bounce physics (`spring_lerp`).
- **Interactive Live Web Inspector**: Standalone single-file HTML5/Canvas preview tool (`preview/inspector.html`) to test joint angles, visemes, and poses live in your browser.
- **Automated Video Pipeline Ready**: Built to integrate directly with `video-pipe` and FFmpeg / MoviePy pipelines with transparent alpha video exports.

---

## Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/theGoodB0rg/VideoMascot.git
cd VideoMascot

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
```

### Generating Sample Poses & Previews

```bash
python preview_poses.py
```

### Launching the Live Inspector

Open `preview/inspector.html` in any modern web browser to interact with the mascot live.

---

## Architecture Overview

```
src/videomascot/
├── core/
│   ├── math_2d.py           # 2D Vectors, Transform matrices, Easing functions
│   ├── bones.py             # Bone hierarchy, 2-joint IK/FK solvers
│   └── slots.py             # Modular slot attachment management
├── models/
│   ├── manifest.py          # Pydantic schemas for MascotManifest & configs
│   └── pose.py              # Runtime PoseState & joint definitions
├── compositor/
│   └── sprite_engine.py     # Multi-layer alpha sprite compositor
├── assets/
│   └── starter_mascot.py    # Starter asset bundle generator
└── inspector_builder.py     # Standalone HTML5 inspector builder
```

---

## License

MIT
