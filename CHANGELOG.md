# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.0] - 2026-10-29

### Added
- **Motion controls for rigs built from painted sprites.** A painted presenter cannot bend an
  arm, so what makes it read as alive is head motion, sway and blinking. New
  `MascotProceduralConfig` fields, all defaulting to the previous behaviour:
  - `speech_head_motion_deg` / `speech_head_motion_px`: head turn and bob that follow speech,
    shaped by a fast-attack, slow-release speaking envelope so the head settles in pauses.
    Deterministic (two incommensurate sines), so renders reproduce frame for frame.
  - `head_sway_deg` / `body_sway_deg`: slow idle drift of the head, and a weight shift of the
    whole body about its root.
  - `nod_amplitude_px` / `nod_amplitude_deg`: the emphasis nod was hard-coded at 0.5px and
    0.6deg, sized for a 1000px chibi and invisible on a painted figure.
  - `pose_angle_scale`: multiplier on the fixed head and torso angles each gesture and emotion
    sets. Those angles exist to pose jointed rigs; on a painted sprite the pose is already in
    the art, and the angles only used up the joint range live motion needed.
- **Staged gestures with pose crossfades** (`gesture_lead_in`, `pose_crossfade`). The figure
  holds idle, then blends into the gesture's attachments instead of swapping them halfway
  through a 0.5s ease. `PoseState.attachment_blends` carries the outgoing attachment and its
  weight. The compositor fades the incoming pose in *over* a still-solid outgoing pose, then
  fades the outgoing one out beneath it, so the body never turns see-through the way a
  symmetric dissolve does (the first attempt showed exactly that double exposure).
- **`PresentationProfileConfig.framing`** (`full_figure` | `waist_up`). A waist-up figure is
  cut off at the bottom of its canvas; a host must dock that edge to the frame edge and size
  it as a person rather than a whole body, and now has a declared way to know.

### Fixed
- **Bone `constraints` are enforced.** `JointConstraintConfig` was declared by `brick_dev`
  and `nexus_bot` and never applied. Rotation limits now clamp the final joint angle in the
  compositor. Neither starter rig's existing poses come near its limit, so their renders are
  unchanged.
## [0.4.0] - 2026-10-20

### Added
- **`PresentationProfileConfig` on `MascotManifest`**: a bundle now ships its own movement
  personality rather than relying on the host to invent one. It declares the rig controls a host
  may drive (`head`/`body`/`root`, each nullable), a viseme map, `procedural` overrides onto
  `MascotProceduralConfig`, and the `supported_gestures` the rig can actually strike.

  Movement personality belongs to the character, not the pipeline. Without this the host had to
  fall back on a single shared default, and three visually distinct mascots animated identically:
  the moulded brick figure breathed, the levitating bot breathed, and neither differed in gesture
  vocabulary despite having different rigs and different hand sprites.

  All three starter generators now emit one:

  | | breathing | hover | saccades | gestures | `body` control |
  |---|---|---|---|---|---|
  | `chibi_tech_guide` | yes (0.55) | no | yes | 8 | `torso` |
  | `nexus_bot` | **no** | **yes** | yes | 8 | **unbound** |
  | `brick_dev` | **no** | no | **no** | **6** | `torso` |

  `nexus_bot` leaves `body` unbound because a levitating chassis has no torso to breathe with,
  and an unbound control cannot be driven by accident. `brick_dev` poses by whole-torso sprite
  swap rather than arm rotation, so its vocabulary is exactly the set of torso sprites that
  exist: no `shock`, no `shrug`.

- **`MascotManifest.validate_presentation()`**: rejects a profile that names a bone absent from
  the rig, maps a viseme the rig does not define, sets an unknown or out-of-range procedural
  value, or omits `idle` (the resting pose every other gesture interpolates from). A profile
  that misnames a bone otherwise fails silently at render time, which is how a mascot ends up
  visible but inert. Absent profiles remain valid, so existing bundles still load.

### Changed
- **`ink_chronicler` re-proportioned for the sizes it is actually rendered at.** The first cut
  inherited the chibi skeleton's proportions wholesale and was reviewed at native sprite
  resolution, where they look stylised. At the 216px guide scale they read as a doll, and a doll
  with soft features reads female regardless of intent.

  | | before | after |
  |---|---|---|
  | head height / figure height | 0.614 | **0.303** |
  | shoulder half-width vs arm socket | 58 vs 65 (arms float) | **89 vs 65** |
  | brightest-pixel concentration in head | 1.14 | **0.54** |
  | silhouette overlap with `chibi_tech_guide` | 0.812 | **0.692** |

  Proportion is now one constant, `HEAD_SCALE`, applied to the head sprites on save and to every
  head-relative slot offset, instead of a hundred hand-placed coordinates. Bone positions are
  untouched, so all eight gesture poses and both pointing solves still apply: **sprite sizes and
  slot offsets were never the thing the sequencer depends on**, which an earlier note in this file
  got wrong.

  The masculine read is carried by silhouette rather than detail, because detail is the first
  thing lost at guide scale: an angular cowl with a brow shelf instead of a rounded bell, a beard
  that extends past the jaw outline, a squared jaw, and shoulders wide enough to carry the arms.

- **`ink_chronicler`**: an engraved hooded chronicler, for painterly history documentaries where
  a flat-vector cartoon presenter is a register mismatch. Woodblock line and hatch on warm paper
  with an amber rim; era- and culture-neutral in silhouette, so one character carries Egypt, Mali
  and Rome without impersonating any of them.

  Engraving rather than a painterly render is a deliberate choice: faking oil paint with drawing
  primitives looks cheap, whereas line and hatch is what these primitives are actually good at.

  Its rig is bone-for-bone identical to `chibi_tech_guide` — same canvas, bone positions, slot
  offsets and sprite dimensions. The sequencer's gesture poses are hand-tuned joint angles against
  that skeleton, so matching it means all eight gestures, both pointing solves and the prop
  attachment work without touching the animation code. A test pins the bone parity, because a
  moved joint would break the poses silently.

  It also supplies the `focused` and `wide` eye states the sequencer asks for on `thinking` and
  `shocked` and that `chibi_tech_guide` never had, and all 11 visemes.

- **Starter-bundle registry** (`videomascot.assets`): `STARTER_BUNDLES`, `list_starter_bundles()`,
  `generate_starter_bundle()` and `generate_all_starter_bundles()`. Host pipelines keep their own
  copy of the generated bundles, which is exactly how those copies drift from the generators that
  made them; a host can now regenerate the whole set by iterating the registry instead of importing
  three factories by name. Manifests are deterministic, so a host can diff a regenerated manifest
  against its committed one to detect drift. An unknown id raises `KeyError` naming the available
  ones, rather than letting a typo silently resolve to a different character.

- **`MascotActionSchema.posture_shift`**: separates the entrance settle from the slide-in.
  `transition_in` drove both a subtle torso/head settle *and* a 500px slide up from off-screen,
  so a host wanting a grounded presenter on a hard cut had to disable the flag and silently lost
  the settle with it. `transition_in` remains a superset and keeps its existing meaning.

### Fixed
- **Version drift**: `pyproject.toml` declared `0.1.0` while `__init__.__version__` declared
  `0.3.0`. Both now track the same release.

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
