# Animation & 9-Viseme Lip-Sync 👄

This document details VideoMascot's speech synchronization subsystem and continuous procedural life layers.

---

## 🎭 The Preston Blair 9-Viseme Lip-Sync Standard

In professional 2D and 2.5D character animation (the Preston Blair standard used by Disney and Warner Bros), human speech is categorized into **9 distinct mouth shapes (visemes)** rather than attempting to draw hundreds of microscopic phonemes.

Holding each viseme for **2 to 3 frames at 24fps** (~80ms to 125ms) produces smooth, readable, natural articulation without high-frequency mouth "chattering".

---

## 📖 Viseme Reference Table

| Viseme Name | Spoken Sounds / Phonemes | Visual Appearance | Example Words |
| :--- | :--- | :--- | :--- |
| **`rest`** | Silence / Neutral pause | Closed relaxed mouth | *(Pause)* |
| **`smile`** | Friendly resting state | Closed warm upward curve | *(Pause during friendly scenes)* |
| **`open_smile`** | Excited resting state | Wide open cheerful smile | *(Pause during excited scenes)* |
| **`A_I`** | Vowels /aɪ/, /æ/, /ɑː/ (A, I, Y) | Wide open jaw, teeth & tongue visible | *apple, pipe, architecture* |
| **`E`** | Vowels /iː/, /eɪ/, /ɛ/ (E, EE, EA) | Wide horizontal stretch, teeth clamped | *system, see, tech* |
| **`O`** | Vowel /oʊ/, /ɔː/ (O, OA, OH) | Rounded open circle | *growth, go, boat* |
| **`U`** | Vowels /uː/, /ʊ/ (U, OO, OU) | Tight puckered narrow circle | *you, through, new* |
| **`M_B_P`** | Bilabial consonants (M, B, P) | Lips fully pressed together | *mascot, build, pipeline* |
| **`F_V`** | Labiodental consonants (F, V, PH) | Upper teeth resting on lower lip | *fast, video, frame* |
| **`L_D_T_N`** | Alveolar consonants (L, D, T, N, S, Z) | Open teeth with tongue behind upper teeth | *test, data, scale, learn* |
| **`W_Q`** | Rounded consonants (W, Q, R, WH) | Narrow rounded lips extending outward | *world, quick, run* |

---

## 🎙️ Speech Synchronization with EdgeTTS & WebVTT

VideoMascot synchronizes character speech with audio using [`LipSyncEngine`](file:///c:/Users/HP/Desktop/Personal%20Websites/VideoMascot/src/videomascot/animation/lipsync.py).

### Workflow:
1. **TTS Audio Generation**: EdgeTTS synthesizes audio and emits subtitle timecodes via `edge_tts.SubMaker()`.
2. **Timecode Parsing**: `LipSyncEngine` reads the `.vtt` file and extracts active speech intervals:
   ```
   00:00.500 --> 00:02.100
   Welcome to the architecture tutorial.
   ```
3. **Phonetic Syllable Mapping**: Words are split proportionally into syllables and mapped through `PHONEME_MAP` to Preston Blair visemes.
4. **Resting Return**: In pauses between sentences (e.g. `t = 2.5s`), `LipSyncEngine` automatically detects silence (`is_speaking = False`) and returns the mouth to the active emotional baseline (e.g. `smile`).

```python
from videomascot.animation.lipsync import LipSyncEngine

# Load directly from a WebVTT file
lipsync = LipSyncEngine.from_vtt_file("narration_001.vtt", default_resting_viseme="smile")

# Query mouth shape at any timestamp t (in seconds)
viseme, is_speaking = lipsync.get_viseme_at(t=1.2)
print(f"Active Viseme: {viseme}, Speaking: {is_speaking}")
```

---

## 🌬️ Procedural Respiration (Breathing)

To prevent characters from looking static during long pauses or monologue scenes, [`ProceduralLifeEngine`](file:///c:/Users/HP/Desktop/Personal%20Websites/VideoMascot/src/videomascot/animation/procedural.py) applies continuous sinusoidal breathing physics to the torso and head.

### Mathematical Formulation:

$$\text{Phase: } \phi(t) = 2\pi \cdot f_{\text{respiration}} \cdot t \quad \text{where } f = \frac{\text{BPM}}{60}$$

$$\text{Torso Y-Scale: } s_y(t) = 1.0 + A \cdot 0.018 \cdot \sin(\phi(t))$$

$$\text{Torso X-Scale (Volume Preservation): } s_x(t) = 1.0 - A \cdot 0.006 \cdot \sin(\phi(t))$$

$$\text{Head Bobbing Offset: } \Delta y_{\text{head}}(t) = A \cdot 1.5 \cdot \sin(\phi(t)) \text{ px}$$

* **Volume Preservation**: As the chest expands vertically, it contracts slightly horizontally, preserving visual mass.
* **Bounded Amplitude**: Subtle organic scaling ($\pm 1.8\%$) that feels lifelike without exaggerated stretching.

---

## 👁️ Poisson-Distributed Natural Eye Blinking

Natural human blinking is not an evenly spaced metronome—it follows a **Poisson distribution process** with a mean interval of ~3.5 seconds.

### Blinking Mechanics:
* **Blink Interval**: Generated via exponential random distribution:
  $$\Delta t_{\text{interval}} \sim \text{Exp}\left(\frac{1}{\mu}\right) \quad \text{clamped to } [1.5\text{s}, 7.0\text{s}]$$
* **Blink Duration**: 140ms total duration.
* **Progress Curve**: Triangular progression ($0.0 \to 1.0 \to 0.0$). When $\text{progress} > 0.4$, sclera attachments swap to `eyelid_blink` and pupils are hidden.

---

## 🎯 Gaze Tracking & Micro-Saccades

1. **Gaze Direction**: The `gaze` parameter in `MascotActionSchema` adjusts pupil position relative to the camera or pointing targets.
2. **Saccadic Micro-Drift**: High-frequency harmonic oscillation is applied to the pupils:
   $$\Delta x_{\text{pupil}} = 1.2 \sin(0.8t + 0.3) + 0.6 \sin(1.9t)$$
   $$\Delta y_{\text{pupil}} = 0.8 \cos(0.7t + 0.5) + 0.4 \sin(2.3t)$$
   This prevents the "dead gaze" effect common in robotic avatars.

---

## 🗣️ Secondary Speech Micro-Bounce

When `is_speaking = True`, the head and torso receive a subtle vertical bounce:

$$\Delta y_{\text{speech}} = 1.8 \cdot |\sin(10.0 \cdot t)| \text{ px}$$

This mimics the natural head nodding and postural engagement humans display while vocalizing words.
