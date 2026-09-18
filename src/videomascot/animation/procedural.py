from __future__ import annotations
import math
import random
from typing import Dict, List, Optional, Tuple

from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotProceduralConfig
from videomascot.models.manifest import MascotManifest


class SpringDamper1D:
    """1D physical damped harmonic oscillator (semi-implicit Euler solver)."""
    __slots__ = ("stiffness", "damping", "mass", "position", "velocity")

    def __init__(
        self,
        stiffness: float = 150.0,
        damping: float = 12.0,
        mass: float = 1.0,
        initial_pos: float = 0.0
    ) -> None:
        self.stiffness = float(stiffness)
        self.damping = float(damping)
        self.mass = max(1e-4, float(mass))
        self.position = float(initial_pos)
        self.velocity = 0.0

    def update(self, target: float, dt: float) -> float:
        dt = max(1e-5, min(0.1, dt))
        # Semi-implicit Euler integration:
        # F = -k*(x - target) - c*v
        force = -self.stiffness * (self.position - target) - self.damping * self.velocity
        acc = force / self.mass
        self.velocity += acc * dt
        self.position += self.velocity * dt
        return self.position

    def reset(self, pos: float = 0.0) -> None:
        self.position = float(pos)
        self.velocity = 0.0


class BoneSpringSimulator:
    """Simulates secondary rotational inertia for bones configured with PhysicsConfig."""

    def __init__(self, manifest: MascotManifest) -> None:
        self.manifest = manifest
        self._springs: Dict[str, SpringDamper1D] = {}
        self._last_parent_rotations: Dict[str, float] = {}

        for b_name, b_cfg in manifest.bones.items():
            if b_cfg.physics:
                self._springs[b_name] = SpringDamper1D(
                    stiffness=b_cfg.physics.stiffness,
                    damping=b_cfg.physics.damping,
                    mass=b_cfg.physics.mass,
                    initial_pos=b_cfg.physics.resting_offset_deg
                )

    def step(self, pose: PoseState, dt: float) -> PoseState:
        for b_name, spring in self._springs.items():
            b_cfg = self.manifest.bones[b_name]
            parent_name = b_cfg.parent
            parent_rot = pose.joint_rotations.get(parent_name, 0.0) if parent_name else 0.0
            last_rot = self._last_parent_rotations.get(parent_name, parent_rot) if parent_name else 0.0
            parent_vel = (parent_rot - last_rot) / max(1e-4, dt)

            if parent_name:
                self._last_parent_rotations[parent_name] = parent_rot

            # Rotational inertia: child springs against parent acceleration/velocity
            # Dampen head bone coupling to prevent erratic side-to-side wagging during speech
            coupling = 0.015 if b_name == "head" else 0.06
            target_offset = b_cfg.physics.resting_offset_deg - coupling * parent_vel
            simulated_offset = spring.update(target_offset, dt)

            current_rot = pose.joint_rotations.get(b_name, 0.0)
            pose.set_joint_rotation(b_name, current_rot + simulated_offset)

        return pose



class ProceduralLifeEngine:
    """Procedural life engine generating natural continuous micro-motion.
    
    Adds breathing oscillation, Poisson-distributed natural eye blinks,
    and saccadic pupil gaze drift to a character rig.
    """

    def __init__(
        self,
        config: Optional[MascotProceduralConfig] = None,
        seed: Optional[int] = 42
    ) -> None:
        self.config = config or MascotProceduralConfig()
        self.seed = seed
        self._rng = random.Random(seed)
        
        # Pre-generate deterministic blink timestamps for up to 600 seconds
        self._blink_times = self._generate_blink_schedule(max_duration=600.0)

    def _generate_blink_schedule(self, max_duration: float) -> List[float]:
        """Generates Poisson-distributed blink timestamps."""
        t = 1.0 + self._rng.uniform(0.5, 2.0) # first blink after ~1.5-3s
        times = []
        mean_interval = self.config.blink_interval_mean
        
        while t < max_duration:
            times.append(t)
            # Exponential distribution for Poisson process
            interval = self._rng.expovariate(1.0 / mean_interval)
            # Bound interval between 1.5s and 7.0s for natural feel
            interval = max(1.5, min(interval, 7.0))
            t += interval
        return times

    def get_breathing_offsets(self, t: float) -> Tuple[float, float, float]:
        """Calculates (torso_scale_x, torso_scale_y, head_dy) for timestamp t in seconds."""
        if not self.config.breathing:
            return (1.0, 1.0, 0.0)
            
        freq_hz = self.config.breathing_bpm / 60.0
        phase = 2.0 * math.pi * freq_hz * t
        
        amplitude = self.config.breathing_intensity
        # Subtle expansion and contraction
        sy = 1.0 + amplitude * 0.018 * math.sin(phase)
        sx = 1.0 - amplitude * 0.006 * math.sin(phase) # Volume preservation
        head_dy = amplitude * 1.5 * math.sin(phase)
        return (sx, sy, head_dy)

    def get_blink_progress(self, t: float) -> float:
        """Returns blink progress in [0.0, 1.0] where 1.0 is fully closed."""
        if not self.config.blinking:
            return 0.0
            
        dur = self.config.blink_duration
        for b_start in self._blink_times:
            if b_start <= t <= b_start + dur:
                # Triangular progress: 0 -> 1 -> 0
                rel_t = (t - b_start) / dur
                if rel_t < 0.5:
                    return rel_t * 2.0
                else:
                    return (1.0 - rel_t) * 2.0
            if b_start > t + dur:
                break
        return 0.0

    def get_gaze_saccades(self, t: float) -> Tuple[float, float]:
        """Returns subtle micro-saccade offset (dx, dy) in pixels."""
        if not self.config.gaze_saccades:
            return (0.0, 0.0)
            
        # Slow pseudo-random harmonic drift
        dx = 1.2 * math.sin(0.8 * t + 0.3) + 0.6 * math.sin(1.9 * t)
        dy = 0.8 * math.cos(0.7 * t + 0.5) + 0.4 * math.sin(2.3 * t)
        return (dx, dy)

    def get_hover_offsets(self, t: float) -> Tuple[float, float]:
        """Calculates multi-harmonic levitation hover (dy, tilt_rot) in pixels and degrees."""
        if not self.config.hover:
            return (0.0, 0.0)
        freq = self.config.hover_bpm / 60.0
        phase = 2.0 * math.pi * freq * t
        amp = min(3.2, self.config.hover_amplitude)
        # Multi-harmonic floating bob
        dy = amp * (math.sin(phase) + 0.3 * math.sin(2.3 * phase + 0.8))
        rot = 0.30 * math.sin(0.8 * phase + 0.4)
        return (dy, rot)

    def get_emphasis_nod_offset(self, t: float, is_speaking: bool) -> Tuple[float, float]:
        """Subtle periodic conversational emphasis nod.
        
        Rather than continuous 2 Hz bounce, fires a brief 0.35s nod every ~4.5s
        during active speech, remaining completely still for the rest of dialogue.
        Returns (nod_dy, nod_pitch_rot_deg).
        """
        if not is_speaking or not self.config.bounce_on_speak:
            return (0.0, 0.0)
        cycle_t = t % 4.5
        nod_dur = 0.35
        if cycle_t < nod_dur:
            # Smooth bell curve / Hann window: 0 -> 1 -> 0
            w = 0.5 * (1.0 - math.cos(2.0 * math.pi * (cycle_t / nod_dur)))
            return (-0.5 * w, 0.6 * w)
        return (0.0, 0.0)

    def apply(self, pose: PoseState, t: float, is_speaking: bool = False) -> PoseState:
        """Applies procedural life transformations to a PoseState at time t."""
        # 1. Apply hover levitation if enabled (takes precedence over breathing for robots)
        if self.config.hover:
            hover_dy, hover_rot = self.get_hover_offsets(t)
            r_dx, r_dy = pose.joint_translations.get("root", (0.0, 0.0))
            pose.set_joint_translation("root", r_dx, r_dy + hover_dy)
            r_rot = pose.joint_rotations.get("torso", 0.0)
            pose.set_joint_rotation("torso", r_rot + hover_rot)
        else:
            # Apply standard organic breathing
            sx, sy, head_dy = self.get_breathing_offsets(t)
            curr_sx, curr_sy = pose.joint_scales.get("torso", (1.0, 1.0))
            pose.set_joint_scale("torso", curr_sx * sx, curr_sy * sy)
            curr_dx, curr_dy = pose.joint_translations.get("head", (0.0, 0.0))
            pose.set_joint_translation("head", curr_dx, curr_dy + head_dy)
        
        # 2. Speaking conversational emphasis nod (periodic subtle accent, not continuous)
        if is_speaking and self.config.bounce_on_speak:
            nod_dy, nod_rot = self.get_emphasis_nod_offset(t, is_speaking)
            if abs(nod_dy) > 1e-4 or abs(nod_rot) > 1e-4:
                h_dx, h_dy = pose.joint_translations.get("head", (0.0, 0.0))
                pose.set_joint_translation("head", h_dx, h_dy + nod_dy)
                h_rot = pose.joint_rotations.get("head", 0.0)
                pose.set_joint_rotation("head", h_rot + nod_rot)

        # 3. Apply eye blinking
        blink = self.get_blink_progress(t)
        pose.blink_progress = blink
        if blink > 0.4:
            pose.set_attachment("eye_l_sclera", "eyelid_blink")
            pose.set_attachment("eye_r_sclera", "eyelid_blink")
            pose.set_attachment("pupil_l", "")
            pose.set_attachment("pupil_r", "")
            pose.set_attachment("eyes", "blink")


        # 4. Apply saccade pupil offset
        saccade_x, saccade_y = self.get_gaze_saccades(t)
        base_px, base_py = pose.pupil_offset
        pose.pupil_offset = (base_px + saccade_x, base_py + saccade_y)

        return pose

