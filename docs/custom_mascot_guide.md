# Custom Mascot Creation Guide 🎨

This guide walks artists and developers through creating, slicing, rigging, and testing a brand new 2.5D character bundle in VideoMascot.

---

## 📁 Character Bundle Directory Structure

Every character bundle in VideoMascot lives in its own directory within `assets/mascots/<character_id>/` and contains a `manifest.json` along with transparent RGBA PNG sprite layers:

```
assets/mascots/my_custom_mascot/
├── manifest.json                # Master rig and bone configuration
├── head/
│   ├── head_base.png            # Main head contour with neck stem
│   ├── eyes/
│   │   ├── sclera_left.png      # White eye base (Left)
│   │   ├── sclera_right.png     # White eye base (Right)
│   │   ├── pupil.png            # Iris + Pupil with studio catchlight
│   │   ├── eyelid_blink.png     # Closed eyelid curve for blinking
│   │   └── eye_happy.png        # Curved happy eye (^^)
│   ├── eyebrows/
│   │   ├── left.png             # Left eyebrow
│   │   └── right.png            # Right eyebrow
│   └── mouth/
│       ├── rest.png             # Neutral closed resting mouth
│       ├── smile.png            # Friendly resting smile
│       ├── open_smile.png       # Excited wide smile
│       ├── A_I.png              # Wide open jaw (/aɪ/, /æ/)
│       ├── E.png                # Horizontal teeth stretch (/iː/, /eɪ/)
│       ├── O.png                # Rounded open circle (/oʊ/)
│       ├── U.png                # Tight puckered circle (/uː/)
│       ├── M_B_P.png            # Pressed closed lips (M, B, P)
│       ├── F_V.png              # Teeth on lower lip (F, V)
│       ├── L_D_T_N.png          # Tongue behind teeth (L, D, T, N)
│       └── W_Q.png              # Outward puckered lips (W, Q, R)
├── body/
│   ├── torso.png                # Torso and collar base
│   ├── arm_upper.png            # Upper arm (Shoulder to elbow)
│   ├── arm_lower.png            # Forearm (Elbow to wrist)
│   └── hands/
│       ├── rest.png             # Relaxed resting hand
│       ├── point.png            # Pointing index finger
│       ├── wave.png             # Open palm for waving
│       └── thumbs_up.png        # Thumbs up gesture
└── props/
    └── pointer_stick.png        # Optional props attached to hand bones
```

---

## 🎨 Asset Guidelines & Best Practices

1. **Resolution**: Design character master assets at a native resolution around **1000×1000px** on a transparent canvas.
2. **Pure Alpha**: Ensure all exported PNG files are **32-bit RGBA with transparent backgrounds**.
3. **Pivots & Overlaps**:
   - **Neck Stem**: Extend the neck stem inside `head_base.png` 30–40px below the chin so that tilting the head never creates a neck gap.
   - **Limb Joint Circles**: Draw rounded caps at the ends of upper and lower arm sprites to ensure seamless rotations at the elbow and shoulder.
4. **Pupil Highlights (Keylight Catchlights)**:
   - Always place the keylight specular highlight in the **top-left corner** of both pupils. This ensures the character looks alert and confident rather than cross-eyed or tearful.

---

## 📝 Authoring `manifest.json`

The `manifest.json` defines bone hierarchies, rotation pivots, and modular slot attachments:

```json
{
  "id": "my_custom_mascot",
  "name": "My Custom Mascot",
  "version": "1.0.0",
  "canvas_size": [1000, 1000],
  "bones": {
    "root": {
      "position": [500, 750],
      "pivot": [0, 0],
      "z_index": 0
    },
    "torso": {
      "parent": "root",
      "position": [0, -100],
      "pivot": [90, 150],
      "z_index": 1
    },
    "head": {
      "parent": "torso",
      "position": [0, -140],
      "pivot": [150, 210],
      "z_index": 2
    },
    "arm_r_upper": {
      "parent": "torso",
      "position": [70, -100],
      "pivot": [16, 16],
      "length": 80,
      "z_index": 3
    },
    "arm_r_lower": {
      "parent": "arm_r_upper",
      "position": [80, 0],
      "pivot": [14, 14],
      "length": 75,
      "z_index": 4
    }
  },
  "slots": {
    "torso": {
      "bone": "torso",
      "default_attachment": "default",
      "offset": [-90, -150],
      "attachments": { "default": "body/torso.png" },
      "z_index": 1
    },
    "head": {
      "bone": "head",
      "default_attachment": "default",
      "offset": [-150, -210],
      "attachments": { "default": "head/head_base.png" },
      "z_index": 2
    },
    "mouth": {
      "bone": "head",
      "default_attachment": "smile",
      "offset": [-40, -25],
      "attachments": {
        "rest": "head/mouth/rest.png",
        "smile": "head/mouth/smile.png",
        "open_smile": "head/mouth/open_smile.png",
        "A_I": "head/mouth/A_I.png",
        "E": "head/mouth/E.png",
        "O": "head/mouth/O.png",
        "U": "head/mouth/U.png",
        "M_B_P": "head/mouth/M_B_P.png",
        "F_V": "head/mouth/F_V.png",
        "L_D_T_N": "head/mouth/L_D_T_N.png",
        "W_Q": "head/mouth/W_Q.png"
      },
      "z_index": 6
    }
  },
  "viseme_slot": "mouth",
  "visemes": {
    "rest": "rest",
    "smile": "smile",
    "open_smile": "open_smile",
    "A_I": "A_I",
    "E": "E",
    "O": "O",
    "U": "U",
    "M_B_P": "M_B_P",
    "F_V": "F_V",
    "L_D_T_N": "L_D_T_N",
    "W_Q": "W_Q"
  }
}
```

---

## 🔍 Testing Your Custom Mascot Live in the Web Inspector

You can instantly test your character's joint rotations, pivots, and mouth shapes in your browser without writing any code:

```python
from pathlib import Path
from videomascot.inspector_builder import generate_html_inspector

bundle_path = Path("assets/mascots/my_custom_mascot")
html_output = Path("preview/my_custom_inspector.html")

generate_html_inspector(bundle_path, html_output)
print(f"Generated live inspector at: {html_output}")
```

Open `preview/my_custom_inspector.html` in your web browser to interact with your new character in real time!
