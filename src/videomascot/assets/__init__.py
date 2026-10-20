"""Starter character bundles, and a registry so hosts need not hardcode their names.

Every bundle in this package is generated from code rather than drawn by hand: a few
hundred lines of PIL that emit the sprite set and a validated manifest. That makes a new
character a reviewable diff instead of an art hand-off, and it makes an existing one
reproducible.

Host pipelines keep their own copy of the generated bundles, which is how those copies
drift from the generators that made them. Iterate :data:`STARTER_BUNDLES` to regenerate
them all rather than importing each factory by name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Tuple

from videomascot.assets.starter_brick_dev import create_starter_brick_dev
from videomascot.assets.starter_ink_chronicler import create_starter_ink_chronicler
from videomascot.assets.starter_mascot import create_starter_tech_chibi
from videomascot.assets.starter_nexus_bot import create_starter_nexus_bot

#: Bundle id -> factory. The id matches the directory and ``manifest.id`` each factory writes.
STARTER_BUNDLES: Dict[str, Callable[[Path], Path]] = {
    "chibi_tech_guide": create_starter_tech_chibi,
    "nexus_bot": create_starter_nexus_bot,
    "brick_dev": create_starter_brick_dev,
    "ink_chronicler": create_starter_ink_chronicler,
}


def list_starter_bundles() -> Tuple[str, ...]:
    """Ids of every starter bundle this release can generate."""
    return tuple(sorted(STARTER_BUNDLES))


def generate_starter_bundle(bundle_id: str, output_dir: Path) -> Path:
    """Generate one starter bundle into ``output_dir`` and return its directory.

    Raises ``KeyError`` naming the available ids, so a typo fails immediately rather than
    producing a host that silently falls back to a different character.
    """
    try:
        factory = STARTER_BUNDLES[bundle_id]
    except KeyError:
        raise KeyError(
            f"Unknown starter bundle '{bundle_id}'. Available: {', '.join(list_starter_bundles())}"
        ) from None
    return factory(Path(output_dir))


def generate_all_starter_bundles(output_dir: Path) -> Dict[str, Path]:
    """Generate every starter bundle into ``output_dir``, keyed by id."""
    return {name: factory(Path(output_dir)) for name, factory in STARTER_BUNDLES.items()}


__all__ = [
    "STARTER_BUNDLES",
    "create_starter_brick_dev",
    "create_starter_ink_chronicler",
    "create_starter_nexus_bot",
    "create_starter_tech_chibi",
    "generate_all_starter_bundles",
    "generate_starter_bundle",
    "list_starter_bundles",
]
