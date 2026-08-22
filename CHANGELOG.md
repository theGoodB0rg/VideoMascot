# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-08-22

### Added
- **Declarative Pydantic Schemas**: Added `MascotActionSchema`, `MascotPlacementSchema`, `MascotProceduralConfig`, and `SpeechCue` in `videomascot.models.schema` for declarative YAML/JSON story-level animation directives.
- **Procedural Life Engine (`ProceduralLifeEngine`)**: Continuous sinusoidal torso respiration with volume preservation ($\pm 1.8\%$ expansion on a 3-second cycle), Poisson-distributed natural eye blinking cycles (~3.5s interval), harmonic micro-saccades, and vocalization speech bounce.
- **9-Viseme Preston Blair Lip-Sync Engine (`LipSyncEngine`)**: Full speech synchronization supporting phonetic syllables and WebVTT (`.vtt`) subtitle files with standard Preston Blair mouth shapes (`rest`, `smile`, `open_smile`, `A_I`, `E`, `O`, `U`, `M_B_P`, `F_V`, `L_D_T_N`, `W_Q`). Automatically returns to resting emotional smile during silence.
- **Mascot Kinematic Sequencer (`MascotSequencer`)**: Smooth Hermite (`smoothstep`) interpolation between kinematic gestures (`idle`, `point_up_right`, `point_up_left`, `happy_wave`, `thumbs_up`, `thinking`, `shock`, `shrug`) and emotional facial expressions.
- **In-Memory Zero-Disk Streaming Engine (`StreamEngine`)**: High-performance generator streaming uncompressed raw RGBA byte buffers in constant $O(1)$ RAM without writing intermediate PNG files to disk.
- **High-Level Facade (`MascotEngine`)**: Unified API providing `stream_scene()`, `stream_from_scene_dict()`, `export_alpha_video()`, and `render_frame()`.
- **In-Memory Video Overlay Pipeline (`VideoOverlayCompositor`)**: Zero-disk FFmpeg subprocess streaming pipeline to composite transparent mascot streams directly over background video clips.
- **Standalone Alpha Video Exporters**: Single-command exports to transparent WebM VP9 (`yuva420p`) and Apple ProRes 4444 (`yuva444p10le`).
- **Comprehensive TDD Test Suite**: 38 automated unit and integration tests covering pixel-exact alpha integrity (`alpha == 0`), stream buffer exactness, and video overlay composition.
- **Enhanced Visual README**: Added embedded auto-playing demo GIFs, contact sheets, and pose gallery tables.
- **Interactive Demo Generator (`preview_stream.py`)**: Script to regenerate sample WebM alpha videos, overlay MP4 clips, and README GIFs.

---

## [0.1.0] - 2026-08-20

### Added
- **Layered 2.5D Sprite Puppet Rig**: Modular slot attachment system (`Slot`, `BoneHierarchy`, `Bone`) with 3x3 affine matrix propagation.
- **Analytical Kinematics**: 2-joint Forward & Inverse Kinematics (`solve_2joint_ik`, `solve_pointing_fk`, `solve_aim_to_target`).
- **Starter Mascot Bundle**: Generated `chibi_tech_guide` character asset bundle with shaded body parts, sclera, crisp catchlight pupils, and modular props.
- **Standalone HTML5 Live Web Inspector**: Single-file browser preview tool (`preview/inspector.html`) to interactively test joint angles, visemes, and poses live via HTML5 Canvas.
- **Core Math 2D Library**: `Vector2D`, `Transform2D`, and easing functions (`ease_in_out_quad`, `ease_out_back`, `spring_lerp`).
- **Pydantic Manifest System**: Rig schema validation (`MascotManifest`, `BoneConfig`, `SlotConfig`, `PoseState`).
