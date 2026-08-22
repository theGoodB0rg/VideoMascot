from __future__ import annotations
import math
import random
from typing import Dict, List, Optional, Tuple

from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotProceduralConfig


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

    def apply(self, pose: PoseState, t: float, is_speaking: bool = False) -> PoseState:
        """Applies procedural life transformations to a PoseState at time t."""
        # 1. Apply breathing
        sx, sy, head_dy = self.get_breathing_offsets(t)
        
        # Multiply with existing joint scales
        curr_sx, curr_sy = pose.joint_scales.get("torso", (1.0, 1.0))
        pose.set_joint_scale("torso", curr_sx * sx, curr_sy * sy)
        
        curr_dx, curr_dy = pose.joint_translations.get("head", (0.0, 0.0))
        pose.set_joint_translation("head", curr_dx, curr_dy + head_dy)
        
        # 2. Speaking micro-bounce
        if is_speaking and self.config.bounce_on_speak:
            speak_bounce = 1.8 * abs(math.sin(10.0 * t))
            h_dx, h_dy = pose.joint_translations.get("head", (0.0, 0.0))
            pose.set_joint_translation("head", h_dx, h_dy + speak_bounce)

        # 3. Apply eye blinking
        blink = self.get_blink_progress(t)
        pose.blink_progress = blink
        if blink > 0.4:
            pose.set_attachment("eye_l_sclera", "eyelid_blink")
            pose.set_attachment("eye_r_sclera", "eyelid_blink")
            pose.set_attachment("pupil_l", "")
            pose.set_attachment("pupil_r", "")

        # 4. Apply saccade pupil offset
        saccade_x, saccade_y = self.get_gaze_saccades(t)
        base_px, base_py = pose.pupil_offset
        pose.pupil_offset = (base_px + saccade_x, base_py + saccade_y)

        return pose
