# Rigging & Kinematics 🦾

This guide covers the mathematical foundations, 2.5D bone hierarchy propagation, and analytical Inverse/Forward Kinematics (IK/FK) in VideoMascot.

---

## 📐 2.5D Kinematic Architecture

In VideoMascot, characters are modeled as **hierarchical 2.5D planar skeletons**:

```
[root] (Position on canvas)
  └── [torso] (Pivot at hips/chest)
        ├── [arm_l_upper] ──> [arm_l_lower] ──> [hand_l] ──> [prop_l]
        ├── [arm_r_upper] ──> [arm_r_lower] ──> [hand_r] ──> [prop_r]
        └── [head] (Pivot at neck base)
              ├── [eye_l] ──> [pupil_l]
              ├── [eye_r] ──> [pupil_r]
              ├── [eyebrow_l]
              ├── [eyebrow_r]
              └── [mouth] (Viseme slot)
```

Every bone defines:
* `local_position`: Offset vector $(x, y)$ relative to its parent bone.
* `local_rotation_deg`: Rotation angle in degrees relative to its parent.
* `local_scale`: Scaling multiplier $(s_x, s_y)$.
* `pivot`: Center of rotation $(p_x, p_y)$ in the local texture coordinates.
* `z_index`: Depth sorting order for alpha layer compositing.

---

## 🧮 3x3 Affine Transform Propagation

World transformations are propagated from the root down to every leaf node using 3x3 affine matrices.

In [`Transform2D`](file:///c:/Users/HP/Desktop/Personal%20Websites/VideoMascot/src/videomascot/core/math_2d.py):

$$M = \begin{bmatrix} a & c & t_x \\ b & d & t_y \\ 0 & 0 & 1 \end{bmatrix}$$

Where:
* $a = s_x \cos(\theta), \quad c = -s_y \sin(\theta)$
* $b = s_x \sin(\theta), \quad d = s_y \cos(\theta)$
* $t_x, t_y$ are translation coordinates.

### Pivot-Aware Local Matrix:
When rotating around a pivot point $P = (p_x, p_y)$:

$$M_{\text{local}} = T(t_x, t_y) \cdot T(p_x, p_y) \cdot R(\theta) \cdot S(s_x, s_y) \cdot T(-p_x, -p_y)$$

### Hierarchy Propagation:
$$M_{\text{world}}^{\text{child}} = M_{\text{world}}^{\text{parent}} \cdot M_{\text{local}}^{\text{child}}$$

This guarantees that rotating the torso automatically moves and rotates the neck, head, eyes, and arms without trigonometric drift.

---

## 🎯 Kinematic Solvers

VideoMascot includes closed-form analytical solvers for natural limb positioning:

### 1. Analytical 2-Joint Inverse Kinematics (`solve_2joint_ik`)
Solves the shoulder ($\theta_1$) and elbow ($\theta_2$) angles required for a hand to reach an arbitrary 2D target coordinate $(T_x, T_y)$.

Using the Law of Cosines on an upper arm of length $L_1$ and forearm of length $L_2$:

$$D = \sqrt{\Delta x^2 + \Delta y^2}$$

$$\cos(\alpha) = \frac{L_1^2 + D^2 - L_2^2}{2 L_1 D}, \quad \cos(\beta) = \frac{L_1^2 + L_2^2 - D^2}{2 L_1 L_2}$$

$$\theta_2 = 180^\circ - \beta \quad (\text{Elbow bend angle})$$

$$\theta_1 = \text{atan2}(\Delta y, \Delta x) \pm \alpha \quad (\text{Shoulder angle})$$

```python
from videomascot.core.bones import solve_2joint_ik
from videomascot.core.math_2d import Vector2D

shoulder_pos = Vector2D(100.0, 200.0)
target_pos = Vector2D(250.0, 180.0)

sh_angle, el_angle = solve_2joint_ik(
    shoulder_pos=shoulder_pos,
    target_pos=target_pos,
    length_upper=100.0,
    length_lower=100.0,
    bend_positive=True
)
print(f"Shoulder: {sh_angle:.1f}°, Elbow: {el_angle:.1f}°")
```

---

### 2. Aim & Pointing Forward Kinematics (`solve_pointing_fk`)
Calculates natural, appealing arm angles for pointing at charts, titles, or screen elements at an angle $\phi$:

* Applies a slight natural elbow bend (`bend_ratio = 0.08`) so the arm looks organic rather than like a stiff rod.
* Handles left-arm vs. right-arm coordinate symmetry automatically:

```python
from videomascot.core.bones import solve_pointing_fk

# Point right arm up-right at +40 degrees
sh_r, el_r = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True)

# Point left arm up-left at +40 degrees
sh_l, el_l = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=False)
```

---

## 🥞 Z-Index Layer Ordering & Compositing

During frame rendering, all active slots are sorted by `composite_z = bone.z_index * 1000 + slot.z_index` before being alpha-composited:

```
Z=0   : Torso / Body base
Z=1   : Collar & Neck shadow
Z=2   : Head base contour
Z=3   : Eye Scleras (Left & Right)
Z=4   : Eye Pupils (clipped within sclera bounds)
Z=5   : Eyebrows
Z=6   : Mouth Viseme shape
Z=7   : Upper Arms
Z=8   : Forearms
Z=9   : Hands
Z=10  : Props (Pointer stick, tablet, coffee cup)
```
This strict ordering ensures limbs and props correctly occlude or appear behind body parts according to the animation's needs.
