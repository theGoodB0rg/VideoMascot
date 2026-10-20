"""Every bundle ships its own movement personality, and it must describe its own rig.

A bundle is meant to be dropped into a host pipeline and work immediately. Before this,
``presentation_profile`` was a convention the host invented and no generator emitted, so
every character fell back to one shared default: a brick minifigure, a levitating bot and
a chibi presenter all animated identically.
"""

from pathlib import Path

import pytest

from videomascot.assets.starter_brick_dev import create_starter_brick_dev
from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.assets.starter_nexus_bot import create_starter_nexus_bot
from videomascot.models.manifest import (
    BoneConfig,
    MascotManifest,
    PresentationProfileConfig,
    RigControlsConfig,
)

GENERATORS = {
    "chibi_tech_guide": create_starter_tech_chibi,
    "nexus_bot": create_starter_nexus_bot,
    "brick_dev": create_starter_brick_dev,
}


@pytest.fixture(scope="module")
def manifests(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("mascots")
    built = {}
    for name, generator in GENERATORS.items():
        bundle = generator(out_dir)
        built[name] = MascotManifest.model_validate_json(
            (bundle / "manifest.json").read_text(encoding="utf-8")
        )
    return built


def _manifest(**overrides) -> MascotManifest:
    base = dict(
        id="test_rig",
        name="Test Rig",
        bones={"root": BoneConfig(), "torso": BoneConfig(parent="root"),
               "head": BoneConfig(parent="torso")},
        visemes={"rest": "rest", "A_I": "A_I"},
    )
    base.update(overrides)
    return MascotManifest(**base)


class TestStarterBundlesShipProfiles:
    @pytest.mark.parametrize("name", sorted(GENERATORS))
    def test_bundle_declares_a_profile(self, manifests, name):
        assert manifests[name].presentation_profile is not None

    @pytest.mark.parametrize("name", sorted(GENERATORS))
    def test_bundle_profile_matches_its_own_rig(self, manifests, name):
        manifests[name].validate_presentation()

    @pytest.mark.parametrize("name", sorted(GENERATORS))
    def test_declared_gestures_have_torso_or_arm_support(self, manifests, name):
        """A declared gesture the rig cannot strike would render as a silent no-op."""
        manifest = manifests[name]
        gestures = set(manifest.presentation_profile.supported_gestures)
        arm_bones = {b for b in manifest.bones if b.startswith("arm_")}
        torso_poses = set(manifest.slots["torso"].attachments) if "torso" in manifest.slots else set()

        assert gestures <= ({"idle"} | torso_poses | ({
            "point_up_left", "point_up_right", "happy_wave", "thumbs_up",
            "thinking", "shock", "shrug",
        } if arm_bones else set()))


class TestCharactersAreDistinct:
    """The point of the feature: three mascots must not animate identically."""

    def test_movement_personalities_differ(self, manifests):
        signatures = {
            name: (
                manifest.presentation_profile.procedural.get("breathing"),
                manifest.presentation_profile.procedural.get("hover"),
                manifest.presentation_profile.procedural.get("gaze_saccades"),
                manifest.presentation_profile.supported_gestures,
            )
            for name, manifest in manifests.items()
        }
        assert len(set(signatures.values())) == len(signatures)

    def test_levitating_bot_hovers_instead_of_breathing(self, manifests):
        procedural = manifests["nexus_bot"].presentation_profile.procedural
        assert procedural["hover"] is True
        assert procedural["breathing"] is False

    def test_levitating_bot_exposes_no_torso_control(self, manifests):
        """``body`` unbound stops a host driving chest respiration on a floating chassis."""
        assert manifests["nexus_bot"].presentation_profile.controls.body is None

    def test_moulded_figure_neither_breathes_nor_saccades(self, manifests):
        procedural = manifests["brick_dev"].presentation_profile.procedural
        assert procedural["breathing"] is False
        assert procedural["gaze_saccades"] is False

    def test_moulded_figure_gesture_set_is_restricted(self, manifests):
        """Sprite-swap posing means the vocabulary is the set of torso sprites that exist."""
        gestures = set(manifests["brick_dev"].presentation_profile.supported_gestures)
        assert "shock" not in gestures
        assert "shrug" not in gestures
        assert {"idle", "point_up_left", "thumbs_up"} <= gestures


class TestValidation:
    def test_absent_profile_is_permitted(self):
        _manifest().validate_presentation()  # legacy bundles must still load

    def test_rejects_control_naming_a_missing_bone(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            controls=RigControlsConfig(head="noggin"),
        ))
        with pytest.raises(ValueError, match="not in the rig"):
            manifest.validate_presentation()

    def test_permits_a_deliberately_unbound_control(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            controls=RigControlsConfig(body=None),
        ))
        manifest.validate_presentation()

    def test_rejects_viseme_map_targeting_a_missing_viseme(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            viseme_map={"A_I": "nonexistent"},
        ))
        with pytest.raises(ValueError, match="does not define"):
            manifest.validate_presentation()

    def test_rejects_unknown_procedural_key(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            procedural={"breathign": True},
        ))
        with pytest.raises(ValueError, match="unknown procedural settings"):
            manifest.validate_presentation()

    def test_rejects_out_of_range_procedural_value(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            procedural={"breathing_bpm": 500.0},
        ))
        with pytest.raises(Exception):
            manifest.validate_presentation()

    def test_rejects_gesture_set_without_idle(self):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            supported_gestures=("happy_wave",),
        ))
        with pytest.raises(ValueError, match="must include 'idle'"):
            manifest.validate_presentation()


class TestRoundTrip:
    def test_profile_survives_serialisation(self, tmp_path):
        manifest = _manifest(presentation_profile=PresentationProfileConfig(
            procedural={"hover": True},
            supported_gestures=("idle", "happy_wave"),
        ))
        path = tmp_path / "manifest.json"
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

        reloaded = MascotManifest.model_validate_json(path.read_text(encoding="utf-8"))
        assert reloaded.presentation_profile.procedural == {"hover": True}
        assert reloaded.presentation_profile.supported_gestures == ("idle", "happy_wave")
