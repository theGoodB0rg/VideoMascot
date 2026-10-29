"""Motion controls for rigs built from painted sprites rather than drawn limbs.

A painted presenter cannot bend an arm; every gesture is a whole-body sprite. What makes it
read as alive is head motion that follows speech, slow sway, blinking, and pose changes that
blend instead of popping. These tests pin those controls and, just as importantly, that
their defaults leave every existing character exactly as it was.
"""
import math

import numpy as np
import pytest
from PIL import Image

from videomascot.animation.procedural import ProceduralLifeEngine
from videomascot.animation.sequencer import MascotSequencer
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.models.manifest import MascotManifest, PresentationProfileConfig
from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotActionSchema, MascotProceduralConfig


def _sample(engine, fn, speaking, t0=0.0, t1=6.0, fps=24):
    return [fn(t0 + i / fps, speaking) for i in range(int((t1 - t0) * fps))]


class TestDefaultsAreUnchanged:
    def test_nod_keeps_its_historical_amplitude(self):
        engine = ProceduralLifeEngine(MascotProceduralConfig(bounce_on_speak=True))
        peak = max(_sample(engine, engine.get_emphasis_nod_offset, True, 0.0, 0.4),
                   key=lambda v: v[1])
        assert peak[0] == pytest.approx(-0.5, abs=0.02)
        assert peak[1] == pytest.approx(0.6, abs=0.02)

    def test_new_motion_is_off_unless_configured(self):
        engine = ProceduralLifeEngine(MascotProceduralConfig())
        assert all(v == (0.0, 0.0) for v in _sample(engine, engine.get_speech_head_motion, True))
        assert engine.get_sway(3.7) == (0.0, 0.0)

    def test_pose_angles_are_unscaled_by_default(self):
        seq = MascotSequencer(MascotActionSchema(gesture="point_up_left"))
        assert seq.get_base_gesture_pose("point_up_left", "friendly").joint_rotations["head"] == -6.0


class TestSpeechHeadMotion:
    def _engine(self):
        return ProceduralLifeEngine(MascotProceduralConfig(speech_head_motion_deg=3.0,
                                                           speech_head_motion_px=2.0))

    def test_head_moves_while_speaking(self):
        engine = self._engine()
        rots = [r for r, _ in _sample(engine, engine.get_speech_head_motion, True)]
        assert max(rots) - min(rots) > 2.0

    def test_head_settles_in_silence(self):
        engine = self._engine()
        _sample(engine, engine.get_speech_head_motion, True, 0.0, 3.0)
        tail = _sample(engine, engine.get_speech_head_motion, False, 3.0, 7.0)[-24:]
        assert max(abs(r) for r, _ in tail) < 0.1

    def test_motion_is_bounded_by_its_amplitude(self):
        engine = self._engine()
        values = _sample(engine, engine.get_speech_head_motion, True, 0.0, 30.0)
        assert max(abs(r) for r, _ in values) <= 3.0 + 1e-9
        assert max(abs(d) for _, d in values) <= 2.0 + 1e-9

    def test_render_is_reproducible(self):
        a, b = self._engine(), self._engine()
        assert (_sample(a, a.get_speech_head_motion, True)
                == _sample(b, b.get_speech_head_motion, True))

    def test_a_backwards_clock_restarts_from_silence(self):
        engine = self._engine()
        _sample(engine, engine.get_speech_head_motion, True, 5.0, 8.0)
        assert engine._speech_envelope(0.0, True) == 0.0


class TestConfigurableNodAndSway:
    def test_nod_amplitude_is_configurable(self):
        engine = ProceduralLifeEngine(MascotProceduralConfig(nod_amplitude_px=3.0,
                                                             nod_amplitude_deg=1.8))
        peak = max(_sample(engine, engine.get_emphasis_nod_offset, True, 0.0, 0.4),
                   key=lambda v: v[1])
        assert peak[1] == pytest.approx(1.8, abs=0.05)

    def test_body_sway_rotates_the_torso(self):
        engine = ProceduralLifeEngine(MascotProceduralConfig(body_sway_deg=0.7, breathing=False))
        angles = {round(engine.apply(PoseState(), t=t).joint_rotations.get("torso", 0.0), 3)
                  for t in np.linspace(0, 12, 40)}
        assert len(angles) > 10 and max(abs(a) for a in angles) <= 0.7


class TestStagedGestureCrossfade:
    def _manifest(self):
        return MascotManifest.model_validate({
            "id": "t", "name": "t", "canvas_size": [8, 8],
            "bones": {"root": {}, "torso": {"parent": "root"}},
            "slots": {"torso": {"bone": "torso", "attachments": {"default": "a.png", "shrug": "b.png"}}},
        })

    def _seq(self, **procedural):
        action = MascotActionSchema(gesture="shrug",
                                    procedural=MascotProceduralConfig(breathing=False, blinking=False,
                                                                      **procedural))
        return MascotSequencer(action, manifest=self._manifest())

    def test_idle_is_held_through_the_lead_in(self):
        pose = self._seq(gesture_lead_in=0.7, pose_crossfade=0.24).evaluate_pose(0.5)
        assert pose.active_attachments["torso"] == "default"
        assert pose.attachment_blends == {}

    def test_mid_blend_carries_both_poses(self):
        pose = self._seq(gesture_lead_in=0.7, pose_crossfade=0.24).evaluate_pose(0.82)
        assert pose.active_attachments["torso"] == "shrug"
        outgoing, weight = pose.attachment_blends["torso"]
        assert outgoing == "default" and 0.0 < weight < 1.0

    def test_blend_finishes_on_the_gesture(self):
        pose = self._seq(gesture_lead_in=0.7, pose_crossfade=0.24).evaluate_pose(1.0)
        assert pose.active_attachments["torso"] == "shrug"
        assert pose.attachment_blends == {}

    def test_without_crossfade_the_historical_swap_applies(self):
        pose = self._seq().evaluate_pose(0.25)
        assert pose.attachment_blends == {}
        assert pose.active_attachments["torso"] == "shrug"


class TestPoseAngleScale:
    def test_scales_every_fixed_angle(self):
        action = MascotActionSchema(gesture="point_up_left",
                                    procedural=MascotProceduralConfig(pose_angle_scale=0.25))
        pose = MascotSequencer(action).get_base_gesture_pose("point_up_left", "friendly")
        assert pose.joint_rotations["head"] == pytest.approx(-1.5)
        assert pose.joint_rotations["torso"] == pytest.approx(0.75)


def _solid(color, size=(20, 20), box=None):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (box[2] - box[0], box[3] - box[1]) if box else size, color),
              box[:2] if box else (0, 0))
    return img


class TestCompositor:
    def _compositor(self, tmp_path, limit=None):
        _solid((200, 30, 30, 255), box=(0, 0, 20, 12)).save(tmp_path / "a.png")
        _solid((30, 30, 200, 255), box=(0, 6, 20, 20)).save(tmp_path / "b.png")
        _solid((0, 255, 0, 255), size=(6, 6)).save(tmp_path / "h.png")
        manifest = MascotManifest.model_validate({
            "id": "t", "name": "t", "canvas_size": [60, 60],
            "bones": {"root": {"position": [30, 50]}, "torso": {"parent": "root"},
                      "head": {"parent": "torso", "position": [0, -30],
                               "constraints": None if limit is None else
                               {"min_rotation_deg": -limit, "max_rotation_deg": limit}}},
            "slots": {"torso": {"bone": "torso", "offset": [-10, -20],
                                "attachments": {"default": "a.png", "shrug": "b.png"}},
                      "head": {"bone": "head", "offset": [-3, -12], "attachments": {"default": "h.png"}}},
        })
        return SpriteCompositor(manifest, tmp_path)

    def test_declared_joint_limits_are_enforced(self, tmp_path):
        comp = self._compositor(tmp_path, limit=5.0)
        at_limit = np.asarray(comp.render_frame(PoseState(joint_rotations={"head": 5.0})))
        beyond = np.asarray(comp.render_frame(PoseState(joint_rotations={"head": 40.0})))
        assert np.array_equal(at_limit, beyond)

    def test_unconstrained_joints_still_rotate_freely(self, tmp_path):
        comp = self._compositor(tmp_path)
        a = np.asarray(comp.render_frame(PoseState(joint_rotations={"head": 5.0})))
        b = np.asarray(comp.render_frame(PoseState(joint_rotations={"head": 40.0})))
        assert not np.array_equal(a, b)

    @pytest.mark.parametrize("outgoing_weight", [0.75, 0.5, 0.25])
    def test_crossfade_never_turns_the_body_transparent(self, tmp_path, outgoing_weight):
        """Where both poses are solid, every blend frame is solid too."""
        comp = self._compositor(tmp_path)
        frame = comp.render_frame(PoseState(active_attachments={"torso": "shrug"},
                                            attachment_blends={"torso": ("default", outgoing_weight)}))
        # The torso slot starts at canvas (20, 30): pose a covers rows 30-41, b rows 36-49.
        overlap = np.asarray(frame)[36:42, 20:40, 3]
        assert overlap.min() == 255

    def test_crossfade_endpoints_match_the_poses(self, tmp_path):
        comp = self._compositor(tmp_path)
        target = np.asarray(comp.render_frame(PoseState(active_attachments={"torso": "shrug"})))
        done = np.asarray(comp.render_frame(PoseState(active_attachments={"torso": "shrug"},
                                                      attachment_blends={"torso": ("default", 0.0)})))
        assert np.array_equal(target, done)


class TestFraming:
    def test_defaults_to_full_figure(self):
        assert PresentationProfileConfig().framing == "full_figure"

    def test_accepts_waist_up_and_rejects_unknown(self):
        assert PresentationProfileConfig(framing="waist_up").framing == "waist_up"
        with pytest.raises(Exception):
            PresentationProfileConfig(framing="head_only")
