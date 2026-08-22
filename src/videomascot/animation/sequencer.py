from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotActionSchema, SpeechCue
from videomascot.core.bones import solve_pointing_fk
from videomascot.animation.procedural import ProceduralLifeEngine
from videomascot.animation.lipsync import LipSyncEngine


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite smooth interpolation between edge0 and edge1."""
    x = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0))) if edge1 != edge0 else 1.0
    return x * x * (3.0 - 2.0 * x)


class MascotSequencer:
    """Temporal animation sequencer that synthesizes gestures, procedural motion,
    and 9-viseme lip-sync into frame-by-frame PoseState evaluations.
    """

    def __init__(
        self,
        action: Optional[MascotActionSchema] = None,
        lipsync: Optional[LipSyncEngine] = None,
        procedural: Optional[ProceduralLifeEngine] = None
    ) -> None:
        self.action = action or MascotActionSchema()
        self.lipsync = lipsync or LipSyncEngine(
            cues=self.action.speech_cues,
            default_resting_viseme=self._get_resting_viseme_for_emotion(self.action.emotion)
        )
        self.procedural = procedural or ProceduralLifeEngine(config=self.action.procedural)

    @classmethod
    def _get_resting_viseme_for_emotion(cls, emotion: str) -> str:
        if emotion in ("friendly", "happy"):
            return "smile"
        elif emotion == "excited":
            return "open_smile"
        elif emotion == "shocked":
            return "O"
        elif emotion == "thinking":
            return "smile"
        return "rest"

    def get_base_gesture_pose(self, gesture: str, emotion: str, prop: Optional[str] = None) -> PoseState:
        """Returns the canonical kinematic PoseState for a named gesture."""
        pose = PoseState(viseme=self._get_resting_viseme_for_emotion(emotion))
        
        # 1. Base Emotion Setup
        if emotion in ("friendly", "happy"):
            pose.set_joint_rotation("head", 2.0)
        elif emotion == "excited":
            pose.set_joint_rotation("head", 4.0)
            pose.set_attachment("eye_l_sclera", "happy")
            pose.set_attachment("eye_r_sclera", "happy")
        elif emotion == "thinking":
            pose.set_joint_rotation("head", 10.0)
        elif emotion == "shocked":
            pose.set_joint_rotation("head", 0.0)

        # 2. Kinematic Gesture Setup
        if gesture == "idle":
            # Natural resting stance
            pose.set_joint_rotation("arm_r_upper", -10.0)
            pose.set_joint_rotation("arm_r_lower", -10.0)
            pose.set_joint_rotation("arm_l_upper", 10.0)
            pose.set_joint_rotation("arm_l_lower", 10.0)
            pose.set_attachment("hand_r", "rest")
            pose.set_attachment("hand_l", "rest")

        elif gesture == "point_up_right":
            pose.set_joint_rotation("torso", -3.0)
            pose.set_joint_rotation("head", 6.0)
            sh_r, el_r = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=True, bend_ratio=0.08)
            pose.set_joint_rotation("arm_r_upper", sh_r)
            pose.set_joint_rotation("arm_r_lower", el_r)
            pose.set_attachment("hand_r", "point")
            if prop:
                pose.set_attachment("prop_r", prop)
            # Left arm on hip
            pose.set_joint_rotation("arm_l_upper", 25.0)
            pose.set_joint_rotation("arm_l_lower", -30.0)
            pose.set_attachment("hand_l", "rest")

        elif gesture == "point_up_left":
            pose.set_joint_rotation("torso", 3.0)
            pose.set_joint_rotation("head", -6.0)
            sh_l, el_l = solve_pointing_fk(aim_angle_deg=40.0, is_right_arm=False, bend_ratio=0.08)
            pose.set_joint_rotation("arm_l_upper", sh_l)
            pose.set_joint_rotation("arm_l_lower", el_l)
            pose.set_attachment("hand_l", "point")
            if prop:
                pose.set_attachment("prop_l", prop)
            # Right arm on hip
            pose.set_joint_rotation("arm_r_upper", -25.0)
            pose.set_joint_rotation("arm_r_lower", 30.0)
            pose.set_attachment("hand_r", "rest")

        elif gesture == "happy_wave":
            pose.set_joint_rotation("head", 8.0)
            pose.set_joint_rotation("arm_l_upper", 125.0)
            pose.set_joint_rotation("arm_l_lower", 25.0)
            pose.set_attachment("hand_l", "wave")
            pose.set_attachment("eye_l_sclera", "happy")
            pose.set_attachment("eye_r_sclera", "happy")
            pose.set_joint_rotation("arm_r_upper", -15.0)
            pose.set_joint_rotation("arm_r_lower", -10.0)

        elif gesture == "thumbs_up":
            pose.set_joint_rotation("head", -4.0)
            pose.set_joint_rotation("arm_r_upper", -50.0)
            pose.set_joint_rotation("arm_r_lower", -55.0)
            pose.set_attachment("hand_r", "thumbs_up")
            pose.set_joint_rotation("arm_l_upper", 15.0)
            pose.set_joint_rotation("arm_l_lower", -20.0)

        elif gesture == "thinking":
            pose.set_joint_rotation("head", 12.0)
            pose.set_joint_rotation("arm_r_upper", -115.0)
            pose.set_joint_rotation("arm_r_lower", -90.0)
            pose.set_attachment("hand_r", "rest")
            pose.set_joint_rotation("arm_l_upper", 20.0)
            pose.set_joint_rotation("arm_l_lower", -30.0)

        elif gesture == "shock":
            pose.set_joint_rotation("arm_l_upper", 70.0)
            pose.set_joint_rotation("arm_l_lower", 40.0)
            pose.set_joint_rotation("arm_r_upper", -70.0)
            pose.set_joint_rotation("arm_r_lower", -40.0)
            pose.set_attachment("hand_l", "wave")
            pose.set_attachment("hand_r", "wave")
            pose.viseme = "O"

        elif gesture == "shrug":
            pose.set_joint_rotation("head", 0.0)
            pose.set_joint_rotation("arm_l_upper", 50.0)
            pose.set_joint_rotation("arm_l_lower", 45.0)
            pose.set_joint_rotation("arm_r_upper", -50.0)
            pose.set_joint_rotation("arm_r_lower", -45.0)
            pose.set_attachment("hand_l", "wave")
            pose.set_attachment("hand_r", "wave")

        # 3. Gaze Pupil Offset Setup
        gaze = self.action.gaze
        if gaze == "point_target":
            if "left" in gesture:
                pose.pupil_offset = (-8.0, -4.0)
            else:
                pose.pupil_offset = (8.0, -4.0)
        elif gaze == "up_left":
            pose.pupil_offset = (-8.0, -6.0)
        elif gaze == "up_right":
            pose.pupil_offset = (8.0, -6.0)
        elif gaze == "down":
            pose.pupil_offset = (0.0, 6.0)
        else: # camera
            pose.pupil_offset = (0.0, 0.0)

        return pose

    def evaluate_pose(self, t: float, transition_duration: float = 0.4) -> PoseState:
        """Evaluates and returns the complete, fully composited PoseState at timestamp t."""
        # 1. Evaluate Gesture Base Pose (Smoothly eased in from idle if t < transition_duration)
        target_pose = self.get_base_gesture_pose(
            gesture=self.action.gesture,
            emotion=self.action.emotion,
            prop=self.action.prop
        )
        
        if self.action.gesture != "idle" and t < transition_duration:
            idle_pose = self.get_base_gesture_pose("idle", self.action.emotion)
            weight = smoothstep(0.0, transition_duration, t)
            
            evaluated_pose = idle_pose.clone()
            # Interpolate all joint rotations
            for bone, target_angle in target_pose.joint_rotations.items():
                idle_angle = idle_pose.joint_rotations.get(bone, 0.0)
                evaluated_pose.set_joint_rotation(bone, idle_angle + weight * (target_angle - idle_angle))
                
            # Switch attachments at halfway transition
            if weight > 0.5:
                evaluated_pose.active_attachments = target_pose.active_attachments.copy()
                evaluated_pose.pupil_offset = target_pose.pupil_offset
        else:
            evaluated_pose = target_pose.clone()

        # 2. Resolve Lip-Sync Viseme
        active_viseme, is_speaking = self.lipsync.get_viseme_at(t)
        evaluated_pose.set_viseme(active_viseme)

        # 3. Apply Continuous Procedural Life (Breathing, Blinking, Saccades)
        evaluated_pose = self.procedural.apply(evaluated_pose, t=t, is_speaking=is_speaking)

        return evaluated_pose
