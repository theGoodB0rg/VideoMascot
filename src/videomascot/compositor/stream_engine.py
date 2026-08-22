from __future__ import annotations
from typing import Iterator, Optional, Tuple
from PIL import Image
import numpy as np

from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.animation.sequencer import MascotSequencer


class StreamEngine:
    """High-performance frame generator streaming uncompressed RGBA pixel buffers in memory."""

    def __init__(
        self,
        compositor: SpriteCompositor,
        sequencer: MascotSequencer
    ) -> None:
        self.compositor = compositor
        self.sequencer = sequencer

    def iter_pil_frames(
        self,
        duration: float,
        fps: int = 24,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Iterator[Image.Image]:
        """Yields PIL RGBA Image instances frame-by-frame."""
        num_frames = max(1, int(round(duration * fps)))
        dt = 1.0 / fps
        
        for frame_idx in range(num_frames):
            t = frame_idx * dt
            pose = self.sequencer.evaluate_pose(t)
            frame = self.compositor.render_frame(pose, target_size=target_size)
            yield frame

    def iter_rgba_bytes(
        self,
        duration: float,
        fps: int = 24,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Iterator[bytes]:
        """Yields uncompressed raw RGBA bytes directly for FFmpeg stdin piping."""
        for frame in self.iter_pil_frames(duration=duration, fps=fps, target_size=target_size):
            yield frame.tobytes("raw", "RGBA")

    def iter_numpy_frames(
        self,
        duration: float,
        fps: int = 24,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Iterator[np.ndarray]:
        """Yields uint8 NumPy arrays (H, W, 4) frame-by-frame."""
        for frame in self.iter_pil_frames(duration=duration, fps=fps, target_size=target_size):
            yield np.array(frame)
