"""``posture_shift`` separates the entrance settle from the slide-in.

``transition_in`` used to drive both a subtle torso/head settle and a 500px slide up from
off-screen. A host that wanted a grounded presenter on a hard cut had to switch the flag
off, which silently cost it the settle too. The two are now independent.
"""

import pytest

from videomascot.animation.sequencer import MascotSequencer
from videomascot.models.schema import MascotActionSchema


def _root_dy(sequencer: MascotSequencer, t: float) -> float:
    return sequencer.evaluate_pose(t=t).joint_translations.get("root", (0.0, 0.0))[1]


def _torso(sequencer: MascotSequencer, t: float) -> float:
    """Torso rotation, defaulted: the idle pose sets no torso key, the settle adds one."""
    return sequencer.evaluate_pose(t=t).joint_rotations.get("torso", 0.0)


def _sequencer(**action_kwargs) -> MascotSequencer:
    action = MascotActionSchema(gesture="idle", duration=3.0, **action_kwargs)
    return MascotSequencer(action=action)


class TestSchema:
    def test_defaults_off(self):
        assert MascotActionSchema().posture_shift is False

    def test_is_independent_of_transition_in(self):
        action = MascotActionSchema(posture_shift=True)
        assert action.posture_shift is True
        assert action.transition_in is False


class TestRendering:
    def test_posture_shift_does_not_slide_the_root(self):
        """The settle must stay put; only transition_in may displace the root."""
        assert _root_dy(_sequencer(posture_shift=True), 0.0) == pytest.approx(0.0, abs=1e-6)

    def test_transition_in_still_slides_the_root(self):
        assert _root_dy(_sequencer(transition_in=True), 0.0) > 100.0

    def test_slide_settles_by_the_end_of_its_window(self):
        assert _root_dy(_sequencer(transition_in=True), 0.5) == pytest.approx(0.0, abs=1e-6)

    def test_posture_shift_leans_then_settles(self):
        sequencer = _sequencer(posture_shift=True)
        assert _torso(sequencer, 0.0) != pytest.approx(_torso(sequencer, 2.0))

    def test_neither_flag_means_a_grounded_pose_from_frame_one(self):
        sequencer = _sequencer()
        assert _root_dy(sequencer, 0.0) == pytest.approx(0.0, abs=1e-6)
        assert _torso(sequencer, 0.0) == pytest.approx(_torso(sequencer, 2.0))

    def test_slide_still_implies_a_settle(self):
        """transition_in keeps its old meaning; it is a superset, not a sibling."""
        sequencer = _sequencer(transition_in=True)
        assert _torso(sequencer, 0.0) != pytest.approx(_torso(sequencer, 2.0))
