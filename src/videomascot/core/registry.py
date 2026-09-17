from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel

from videomascot.models.manifest import MascotManifest


class MascotNotFoundError(KeyError):
    """Raised when a requested mascot ID is not registered in the MascotRegistry."""
    pass


class MascotBundleValidationError(ValueError):
    """Raised when a mascot bundle directory is missing manifest.json or required assets."""
    pass


class MascotMetadata(BaseModel):
    id: str
    name: str
    version: str
    description: Optional[str] = None
    canvas_size: Tuple[int, int]
    bundle_dir: str


class MascotRegistry:
    """Central registry and asset manager for discovering and loading character bundles.
    
    Guarantees VideoMascot is completely decoupled from any single character aesthetic.
    """

    def __init__(self, search_paths: Optional[List[Union[str, Path]]] = None) -> None:
        self._bundles: Dict[str, Tuple[MascotManifest, Path]] = {}
        if search_paths:
            for p in search_paths:
                self.discover_from_directory(p)

    def register_bundle_dir(self, bundle_dir: Union[str, Path]) -> MascotManifest:
        """Validates and registers a single mascot bundle directory."""
        bundle_path = Path(bundle_dir)
        if not bundle_path.is_dir():
            raise MascotBundleValidationError(f"Mascot bundle path is not a directory: {bundle_path}")

        manifest_file = bundle_path / "manifest.json"
        if not manifest_file.is_file():
            raise MascotBundleValidationError(f"Bundle directory missing 'manifest.json': {bundle_path}")

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            manifest = MascotManifest.model_validate(data)
        except Exception as e:
            raise MascotBundleValidationError(f"Failed to parse manifest at {manifest_file}: {e}") from e

        self._bundles[manifest.id] = (manifest, bundle_path)
        return manifest

    def discover_from_directory(self, root_dir: Union[str, Path]) -> List[str]:
        """Scans immediate subdirectories of root_dir and registers valid mascot bundles."""
        root_path = Path(root_dir)
        if not root_path.exists():
            return []

        registered_ids: List[str] = []
        for child in root_path.iterdir():
            if child.is_dir() and (child / "manifest.json").is_file():
                try:
                    manifest = self.register_bundle_dir(child)
                    registered_ids.append(manifest.id)
                except MascotBundleValidationError:
                    continue
        return registered_ids

    def get_manifest(self, character_id: str) -> MascotManifest:
        if character_id not in self._bundles:
            raise MascotNotFoundError(f"Mascot character '{character_id}' not found in registry. Registered: {list(self._bundles.keys())}")
        return self._bundles[character_id][0]

    def get_bundle_dir(self, character_id: str) -> Path:
        if character_id not in self._bundles:
            raise MascotNotFoundError(f"Mascot character '{character_id}' not found in registry. Registered: {list(self._bundles.keys())}")
        return self._bundles[character_id][1]

    def list_character_ids(self) -> List[str]:
        return list(self._bundles.keys())

    def list_available_mascots(self) -> List[MascotMetadata]:
        result = []
        for m_id, (manifest, bundle_path) in self._bundles.items():
            result.append(MascotMetadata(
                id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                description=manifest.description,
                canvas_size=manifest.canvas_size,
                bundle_dir=str(bundle_path.resolve())
            ))
        return result


def get_bundled_assets_dir() -> Optional[Path]:
    """Resolves the built-in bundled mascot assets directory in the VideoMascot repository/package."""
    candidate = (Path(__file__).resolve().parent.parent.parent.parent / "assets" / "mascots").resolve()
    if candidate.is_dir():
        return candidate
    return None


_DEFAULT_REGISTRY: Optional[MascotRegistry] = None


def get_default_registry() -> MascotRegistry:
    """Returns or initializes the global default MascotRegistry with assets/mascots scanned."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = MascotRegistry()
        # 1. Auto-discover default local mascots root if present in current working directory
        cwd_assets = Path("assets/mascots").resolve()
        if cwd_assets.is_dir():
            _DEFAULT_REGISTRY.discover_from_directory(cwd_assets)

        # 2. Auto-discover bundled package/repository mascots root
        pkg_assets = get_bundled_assets_dir()
        if pkg_assets and pkg_assets != cwd_assets and pkg_assets.is_dir():
            _DEFAULT_REGISTRY.discover_from_directory(pkg_assets)
    return _DEFAULT_REGISTRY


def list_available_mascots() -> List[MascotMetadata]:
    """Returns metadata for all discovered mascot characters in the default registry."""
    return get_default_registry().list_available_mascots()


def list_character_ids() -> List[str]:
    """Returns list of all registered mascot character IDs in the default registry."""
    return get_default_registry().list_character_ids()
