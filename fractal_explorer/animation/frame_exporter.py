"""
Frame exporter for saving animation frames as image sequences.
"""

import os
from pathlib import Path
from typing import Optional, Callable
import numpy as np

from ..utils.export import export_image


class FrameExporter:
    """Exports animation frames as PNG sequence."""

    def __init__(self, output_dir: str, prefix: str = "frame"):
        """
        Initialize frame exporter.

        Args:
            output_dir: Directory to save frames
            prefix: Filename prefix for frames
        """
        self.output_dir = Path(output_dir)
        self.prefix = prefix
        self._frame_count = 0

    def setup(self):
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._frame_count = 0

    def export_frame(self, rgba: np.ndarray, frame_number: int) -> str:
        """
        Export a single frame.

        Args:
            rgba: RGBA image array
            frame_number: Frame number for filename

        Returns:
            Path to exported frame
        """
        filename = f"{self.prefix}_{frame_number:06d}.png"
        filepath = self.output_dir / filename
        export_image(rgba, str(filepath))
        self._frame_count += 1
        return str(filepath)

    def get_frame_pattern(self) -> str:
        """Get FFmpeg-compatible frame pattern."""
        return str(self.output_dir / f"{self.prefix}_%06d.png")

    @property
    def frame_count(self) -> int:
        """Get number of exported frames."""
        return self._frame_count

    def cleanup(self, keep_frames: bool = False):
        """
        Clean up exported frames.

        Args:
            keep_frames: If True, don't delete frames
        """
        if keep_frames:
            return

        for filepath in self.output_dir.glob(f"{self.prefix}_*.png"):
            try:
                filepath.unlink()
            except OSError:
                pass


class FrameSequenceExporter:
    """
    Batch frame sequence exporter with progress tracking.
    """

    def __init__(self,
                 output_dir: str,
                 prefix: str = "frame",
                 progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        Initialize batch exporter.

        Args:
            output_dir: Directory to save frames
            prefix: Filename prefix
            progress_callback: Callback(current_frame, total_frames)
        """
        self.exporter = FrameExporter(output_dir, prefix)
        self.progress_callback = progress_callback
        self._cancelled = False

    def cancel(self):
        """Cancel ongoing export."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if export was cancelled."""
        return self._cancelled

    def reset(self):
        """Reset cancellation state."""
        self._cancelled = False

    def export_sequence(self,
                        frames: list,
                        total_frames: int) -> bool:
        """
        Export a sequence of frames.

        Args:
            frames: List of (frame_number, rgba_array) tuples
            total_frames: Total number of frames for progress

        Returns:
            True if completed, False if cancelled
        """
        self.exporter.setup()
        self._cancelled = False

        for frame_num, rgba in frames:
            if self._cancelled:
                return False

            self.exporter.export_frame(rgba, frame_num)

            if self.progress_callback:
                self.progress_callback(frame_num + 1, total_frames)

        return True
