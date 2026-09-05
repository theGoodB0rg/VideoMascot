from pathlib import Path
import pytest
from videomascot.core.registry import MascotRegistry, MascotNotFoundError, MascotBundleValidationError
from videomascot.models.manifest import MascotManifest, BoneConfig, SlotConfig, PhysicsConfig, JointConstraintConfig
from videomascot.engine import MascotEngine


def test_registry_discovery_and_registration(tmp_path: Path):
    # Setup dummy mascot bundle
    bundle_dir = tmp_path / "test_bot"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "torso.png").write_bytes(b"dummy_png")

    manifest_data = {
        "id": "test_bot",
        "name": "Test Bot",
        "canvas_size": [800, 800],
        "bones": {
            "root": {"position": [400, 700], "pivot": [0, 0], "z_index": 0},
            "torso": {
                "parent": "root",
                "position": [0, -100],
                "physics": {"stiffness": 150.0, "damping": 10.0, "mass": 1.0},
                "constraints": {"min_rotation_deg": -45.0, "max_rotation_deg": 45.0}
            }
        },
        "slots": {
            "torso": {
                "bone": "torso",
                "default_attachment": "default",
                "attachments": {"default": "torso.png"}
            }
        },
        "viseme_slot": "torso",
        "visemes": {"rest": "default"},
        "palette_tokens": {
            "primary": "#2563eb",
            "glow": "#00f0ff"
        }
    }

    manifest = MascotManifest.model_validate(manifest_data)
    (bundle_dir / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    registry = MascotRegistry()
    registry.register_bundle_dir(bundle_dir)

    assert "test_bot" in registry.list_character_ids()
    retrieved_manifest = registry.get_manifest("test_bot")
    assert retrieved_manifest.name == "Test Bot"
    assert retrieved_manifest.bones["torso"].physics.stiffness == 150.0
    assert retrieved_manifest.bones["torso"].constraints.max_rotation_deg == 45.0
    assert retrieved_manifest.palette_tokens["glow"] == "#00f0ff"


def test_registry_discover_all_in_root(tmp_path: Path):
    mascots_root = tmp_path / "mascots"
    mascots_root.mkdir()

    for name in ["alpha_bot", "beta_bot"]:
        b_dir = mascots_root / name
        b_dir.mkdir()
        (b_dir / "dummy.png").write_bytes(b"png")
        manifest = MascotManifest(
            id=name,
            name=f"Bot {name}",
            canvas_size=(600, 600),
            bones={"root": BoneConfig(position=(300, 500))},
            slots={"body": SlotConfig(bone="root", attachments={"default": "dummy.png"})},
            viseme_slot="body",
            visemes={"rest": "default"}
        )
        (b_dir / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    registry = MascotRegistry()
    discovered = registry.discover_from_directory(mascots_root)
    assert set(discovered) == {"alpha_bot", "beta_bot"}
    assert len(registry.list_available_mascots()) == 2


def test_registry_missing_mascot_raises_not_found():
    registry = MascotRegistry()
    with pytest.raises(MascotNotFoundError) as exc_info:
        registry.get_manifest("non_existent_mascot")
    assert "non_existent_mascot" in str(exc_info.value)


def test_registry_invalid_bundle_raises_validation_error(tmp_path: Path):
    b_dir = tmp_path / "bad_bundle"
    b_dir.mkdir()
    # No manifest.json
    registry = MascotRegistry()
    with pytest.raises(MascotBundleValidationError):
        registry.register_bundle_dir(b_dir)


def test_mascot_engine_for_character_integration(tmp_path: Path):
    bundle_dir = tmp_path / "mini_bot"
    bundle_dir.mkdir()
    # Need a valid 1x1 png image for PIL to load
    from PIL import Image
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    img.save(bundle_dir / "body.png")

    manifest = MascotManifest(
        id="mini_bot",
        name="Mini Bot",
        canvas_size=(500, 500),
        bones={"root": BoneConfig(position=(250, 400))},
        slots={"body": SlotConfig(bone="root", attachments={"default": "body.png"})},
        viseme_slot="body",
        visemes={"rest": "default"}
    )
    (bundle_dir / "manifest.json").write_text(manifest.model_dump_json(), encoding="utf-8")

    registry = MascotRegistry()
    registry.register_bundle_dir(bundle_dir)

    # Instantiate engine using for_character
    engine = MascotEngine.for_character("mini_bot", registry=registry)
    assert engine.manifest.id == "mini_bot"
    assert engine.canvas_size == (500, 500)
