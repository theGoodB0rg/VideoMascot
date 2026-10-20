"""The starter-bundle registry: hosts regenerate from this, not from hardcoded imports."""

import pytest

from videomascot.assets import (
    STARTER_BUNDLES,
    generate_all_starter_bundles,
    generate_starter_bundle,
    list_starter_bundles,
)
from videomascot.models.manifest import MascotManifest


def _manifest(bundle):
    return MascotManifest.model_validate_json((bundle / "manifest.json").read_text(encoding="utf-8"))


class TestRegistry:
    def test_lists_every_registered_bundle(self):
        assert set(list_starter_bundles()) == set(STARTER_BUNDLES)

    def test_listing_is_stable_and_sorted(self):
        assert list(list_starter_bundles()) == sorted(STARTER_BUNDLES)

    def test_registry_is_not_empty(self):
        assert STARTER_BUNDLES


class TestGeneration:
    @pytest.mark.parametrize("bundle_id", sorted(STARTER_BUNDLES))
    def test_generated_directory_matches_its_id(self, bundle_id, tmp_path):
        bundle = generate_starter_bundle(bundle_id, tmp_path)
        assert bundle.name == bundle_id

    @pytest.mark.parametrize("bundle_id", sorted(STARTER_BUNDLES))
    def test_manifest_id_matches_the_registry_key(self, bundle_id, tmp_path):
        """A mismatch would make a host resolve a different character than it asked for."""
        bundle = generate_starter_bundle(bundle_id, tmp_path)
        assert _manifest(bundle).id == bundle_id

    @pytest.mark.parametrize("bundle_id", sorted(STARTER_BUNDLES))
    def test_generated_bundle_is_self_consistent(self, bundle_id, tmp_path):
        _manifest(generate_starter_bundle(bundle_id, tmp_path)).validate_presentation()

    def test_generate_all_returns_every_bundle(self, tmp_path):
        built = generate_all_starter_bundles(tmp_path)
        assert set(built) == set(STARTER_BUNDLES)
        assert all(path.is_dir() for path in built.values())

    def test_manifests_are_deterministic(self, tmp_path):
        """Hosts diff regenerated manifests against committed ones to detect drift."""
        first = generate_all_starter_bundles(tmp_path / "a")
        second = generate_all_starter_bundles(tmp_path / "b")
        for name in STARTER_BUNDLES:
            assert ((first[name] / "manifest.json").read_text(encoding="utf-8")
                    == (second[name] / "manifest.json").read_text(encoding="utf-8"))

    @pytest.mark.parametrize("bundle_id", sorted(STARTER_BUNDLES))
    def test_every_referenced_sprite_exists(self, bundle_id, tmp_path):
        """An empty path is the documented 'nothing attached' sentinel, e.g. an empty hand."""
        bundle = generate_starter_bundle(bundle_id, tmp_path)
        manifest = _manifest(bundle)
        for slot_name, slot in manifest.slots.items():
            for attachment, relative in slot.attachments.items():
                if not relative:
                    continue
                assert (bundle / relative).is_file(), (
                    f"{bundle_id}: slot '{slot_name}' attachment '{attachment}' -> missing {relative}"
                )

    @pytest.mark.parametrize("bundle_id", sorted(STARTER_BUNDLES))
    def test_empty_attachment_paths_are_only_the_none_sentinel(self, bundle_id, tmp_path):
        """Keep the sentinel narrow: an empty path anywhere else is a missing sprite."""
        manifest = _manifest(generate_starter_bundle(bundle_id, tmp_path))
        for slot_name, slot in manifest.slots.items():
            empty = {name for name, path in slot.attachments.items() if not path}
            assert empty <= {"none"}, f"{bundle_id}: slot '{slot_name}' has empty paths {empty}"


class TestUnknownBundle:
    def test_raises_keyerror_naming_the_alternatives(self, tmp_path):
        with pytest.raises(KeyError) as excinfo:
            generate_starter_bundle("no_such_character", tmp_path)
        message = str(excinfo.value)
        assert "no_such_character" in message
        assert "chibi_tech_guide" in message
