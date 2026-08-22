# Testing & Quality Assurance 🧪

VideoMascot follows strict **Test-Driven Development (TDD)** to guarantee mathematical precision, pixel-exact transparency, and rock-solid reliability across operating systems.

---

## 🏃 Running the Test Suite

Execute the complete automated test suite with pytest:

```bash
# Run all 38 tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest --cov=videomascot tests/ -v
```

---

## 📂 Test Suite Breakdown

```
tests/
├── test_alpha_integrity.py   # Pixel-exact transparency and border anti-aliasing
├── test_compositor.py        # Layered alpha compositing and joint overrides
├── test_kinematics.py        # Analytical 2-joint IK, FK pointing, and matrix propagation
├── test_lipsync.py           # WebVTT parsing, SpeechCue resolution, resting mouth return
├── test_manifest.py          # MascotManifest and PoseState Pydantic validation
├── test_math_2d.py           # Vectors, Transform2D matrices, and easing functions
├── test_procedural.py        # Respiration bounds, Poisson blink triggers, saccades
├── test_schema.py            # MascotActionSchema validation, placement calculations
├── test_sequencer.py         # Hermite pose interpolation and gesture kinematics
├── test_stream_engine.py     # Frame count exactness and byte buffer dimensions
└── test_video_overlay.py     # End-to-end FFmpeg streaming overlay & WebM export
```

---

## 🛡️ Critical Quality Assurance Guarantees

### 1. Alpha Integrity Verification (`test_alpha_integrity.py`)
Guarantees that no bounding boxes or solid backgrounds are ever generated:
* **Outer Corners Test**: Asserts that all 4 canvas corners strictly have $\text{Alpha} = 0$.
* **Transparent Region Cleanliness**: Verifies that any pixel with $\text{Alpha} = 0$ has zero RGB contamination.
* **Anti-Aliasing Validation**: Asserts that border edge pixels contain anti-aliased gradient alphas ($0 < \alpha < 255$) rather than harsh binary cutoffs.

```python
def test_canvas_pure_alpha_corners_and_background(tech_chibi_bundle):
    compositor = SpriteCompositor.from_bundle_dir(tech_chibi_bundle)
    frame = compositor.render_frame(PoseState(viseme="smile"))
    arr = np.array(frame)
    
    # 4 corners must be alpha 0
    assert arr[0, 0, 3] == 0
    assert arr[0, -1, 3] == 0
    assert arr[-1, 0, 3] == 0
    assert arr[-1, -1, 3] == 0
```

---

### 2. Stream Exactness & Memory Safety (`test_stream_engine.py`)
Guarantees that memory streaming produces the exact expected number of frames and bytes:
* **Frame Count**: Asserts that $\text{frames\_yielded} == \lfloor \text{duration} \times \text{FPS} \rfloor$.
* **Buffer Size**: Asserts that every chunk matches exactly $W \times H \times 4$ bytes.
* **Constant Memory**: Verifies that memory usage does not grow linearly with video duration ($O(1)$ RAM).

---

### 3. Kinematic Solvers Precision (`test_kinematics.py`)
Guarantees mathematical correctness of limb reaching:
* **Law of Cosines Verification**: Asserts that `solve_2joint_ik` calculates exact joint angles that place the wrist at the desired target vector within $\pm 0.01\text{px}$.
* **Matrix Propagation**: Asserts that child bone transforms match the product of parent world matrices.

---

### 4. End-to-End FFmpeg Subprocess Integration (`test_video_overlay.py`)
* Synthesizes a 1.5-second test video with `lavfi`.
* Streams the mascot overlay in-memory via pipe.
* Probes the output file with `ffprobe` to verify valid codec, dimensions (e.g. 640×360), and duration matching the input.
