# VideoMascot Documentation 🎭

Welcome to the official documentation for **VideoMascot** — a modular, scalable, test-driven, AI-ready layered puppet and mascot animation engine designed for automated video pipelines (faceless YouTube channels, educational explainers, marketing bots, and dynamic video generation).

---

## 🏛️ Core Design Philosophy

VideoMascot was built from the ground up to solve the challenges of character animation in automated video production:

1. **100% Background-Less Transparency (Pure Alpha)**: Every frame and video stream is rendered on a transparent RGBA canvas (`alpha=0`). There are zero bounding box artifacts, solid rectangles, or green-screen keying requirements.
2. **Zero-Disk I/O In-Memory Streaming**: Long videos (thousands of frames) are streamed directly from RAM into FFmpeg subprocess pipes using raw uncompressed RGBA pixel buffers ($O(1)$ memory overhead), eliminating disk bottlenecks.
3. **100% Declarative & Schema-Driven**: Control the entire character (emotions, gestures, placements, gaze, speech sync) through simple Pydantic-validated dictionaries, making it easy for LLMs and YAML-to-JSON compilers (like `video-pipe`) to direct videos automatically.
4. **Procedural Life & Micro-Motion**: Characters never feel frozen. Continuous sinusoidal torso breathing, Poisson-distributed natural eye blinking, and harmonic gaze micro-saccades run automatically in the background.
5. **Analytical 2.5D Kinematics**: Universal 3x3 affine matrix propagation with analytical 2-joint Forward and Inverse Kinematics (`solve_2joint_ik`, `solve_pointing_fk`) for arm pointing, waving, and gesturing.

---

## 📚 Documentation Index

| Guide | Description |
| :--- | :--- |
| **[Getting Started](getting_started.md)** | Installation, prerequisites, quickstart, and generating sample poses/previews. |
| **[Declarative Schema Guide](schema_guide.md)** | Complete reference for YAML/JSON directives: emotions, gestures, placements, and speech cues. |
| **[Animation & 9-Viseme Lip-Sync](animation_and_lipsync.md)** | Preston Blair mouth sets, WebVTT/EdgeTTS speech synchronization, and procedural life physics. |
| **[Rigging & Kinematics](rigging_and_kinematics.md)** | 2.5D bone hierarchies, 3x3 affine transforms, and analytical 2-joint IK/FK solvers. |
| **[Custom Mascot Guide](custom_mascot_guide.md)** | Step-by-step tutorial for artists and developers to draw, slice, and rig custom 2.5D characters. |
| **[Video Pipeline Integration](video_pipeline_integration.md)** | Technical reference for integrating VideoMascot into automated engines (e.g. `video-pipe`), FFmpeg overlay filters, and alpha video exports. |
| **[Testing & Quality Assurance](testing_and_qa.md)** | Test-driven architecture, pixel-exact alpha integrity tests, and test suite execution. |

---

## 📐 High-Level Architecture Map

```
src/videomascot/
├── core/                    # Mathematical foundations
│   ├── math_2d.py           # Vectors, Transform2D, Matrices, Easings
│   ├── bones.py             # Kinematic bone hierarchy, 2-joint IK/FK solvers
│   └── slots.py             # Modular sprite attachments
├── models/                  # Pydantic data schemas
│   ├── manifest.py          # Character rig configuration (bones, slots, pivots)
│   ├── pose.py              # Single-frame PoseState & joint definitions
│   └── schema.py            # Declarative scene action, placement, & speech schemas
├── animation/               # Temporal sequencing & life layers
│   ├── procedural.py        # Respiration oscillation, Poisson blinking, saccades
│   ├── lipsync.py           # WebVTT & timestamped 9-viseme speech sync
│   └── sequencer.py         # Kinematic gesture sequencer & pose interpolation
├── compositor/              # Alpha rendering & memory streaming
│   ├── sprite_engine.py     # Multi-layer alpha sprite compositor
│   └── stream_engine.py     # In-memory raw RGBA stream frame generator
├── pipeline/                # Production video exporters & bridges
│   └── video_overlay.py     # Direct FFmpeg subprocess streaming video compositor
├── assets/                  # Starter assets & character bundles
│   └── starter_mascot.py    # Shaded Chibi Tech Guide generator
├── inspector_builder.py     # Standalone single-file HTML5 web inspector builder
└── engine.py                # High-level MascotEngine facade
```
