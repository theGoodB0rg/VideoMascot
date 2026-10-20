"""Every bundle ships its own movement personality, and it must describe its own rig.

A bundle is meant to be dropped into a host pipeline and work immediately. Before this,
``presentation_profile`` was a convention the host invented and no generator emitted, so
every character fell back to one shared default: a brick minifigure, a levitating bot and
a chibi presenter all animated identically.
"""

from pathlib import Path

import pytest

from videomascot.assets import STARTER_BUNDLES
from videomascot.models.manifest import (
    BoneConfig,
    MascotManifest,
    PresentationProfileConfig,
    RigControlsConfig,
)

#: Drive off the registry, so a character added later is covered without editing this file.
GENERATORS = STARTER_BUNDLES


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
        """Compare the whole procedural mapping, not a handful of booleans.

        Two characters can share every on/off switch and still carry themselves
        differently: breath rate and blink cadence are personality too, and a coarser
        signature would call a brisk tutorial host and a measured chronicler identical.
        """
        signatures = {
            name: (
                tuple(sorted(manifest.presentation_profile.procedural.items())),
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

    def test_chronicler_carries_itself_more_slowly_than_the_chibi(self, manifests):
        """A history presenter is not a tutorial host: slower breath, fewer blinks."""
        chronicler = manifests["ink_chronicler"].presentation_profile.procedural
        chibi = manifests["chibi_tech_guide"].presentation_profile.procedural
        assert chronicler["breathing_bpm"] < chibi.get("breathing_bpm", 18.0)
        assert chronicler["blink_interval_mean"] > chibi.get("blink_interval_mean", 3.5)


class TestInkChronicler:
    """The engraved presenter shares the chibi skeleton so every tuned gesture applies."""

    def test_rig_is_bone_compatible_with_the_chibi(self, manifests):
        assert (set(manifests["ink_chronicler"].bones)
                == set(manifests["chibi_tech_guide"].bones))

    def test_bone_positions_match_the_chibi(self, manifests):
        """Gesture poses are hand-tuned joint angles; a moved joint silently breaks them."""
        chronicler = manifests["ink_chronicler"].bones
        chibi = manifests["chibi_tech_guide"].bones
        for name, bone in chibi.items():
            assert chronicler[name].position == bone.position, name
            assert chronicler[name].parent == bone.parent, name

    def test_supports_the_full_gesture_vocabulary(self, manifests):
        assert len(manifests["ink_chronicler"].presentation_profile.supported_gestures) == 8

    def test_defines_every_viseme_the_lipsync_can_emit(self, manifests):
        """11 visemes, so an audio-aligned run never falls back for want of a sprite."""
        assert len(manifests["ink_chronicler"].visemes) == 11

    def test_offers_the_eye_states_the_sequencer_asks_for(self, manifests):
        """default/happy/focused/wide/blink: the chibi lacks focused and wide."""
        attachments = set(manifests["ink_chronicler"].slots["eye_l_sclera"].attachments)
        assert {"default", "happy", "focused", "wide", "blink"} <= attachments

    def test_keeps_the_pointer_prop_key(self, manifests):
        """Art is a quill; the key stays 'pointer_stick' because that is what the host sets."""
        assert "pointer_stick" in manifests["ink_chronicler"].slots["prop_r"].attachments

    def test_does_not_hover(self, manifests):
        assert manifests["ink_chronicler"].presentation_profile.procedural["hover"] is False


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
