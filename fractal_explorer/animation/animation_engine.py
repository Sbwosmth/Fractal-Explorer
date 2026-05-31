"""
Main animation engine for rendering fractal animations.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Callable, Tuple
import numpy as np

from .animation_types import AnimationBase, AnimationState
from .frame_exporter import FrameExporter
from .video_encoder import VideoEncoder


class AnimationEngine:
    """
    Main animation engine for rendering fractal animations.

    Handles GPU batch rendering, frame export, and video encoding.
    """

    def __init__(self, renderer):
        """
        Initialize animation engine.

        Args:
            renderer: FractalRenderer instance
        """
        self.renderer = renderer
        self.video_encoder = VideoEncoder()
        self._cancelled = False
        self._original_state = None

    def _save_state(self):
        """Save current renderer state."""
        self._original_state = {
            'center_re': self.renderer.viewport.center_re,
            'center_im': self.renderer.viewport.center_im,
            'scale': self.renderer.viewport.scale,
            'fractal': self.renderer.current_fractal_name,
        }

        # Save fractal-specific parameters
        if self.renderer.current_fractal_name == 'julia':
            self._original_state['julia_c'] = self.renderer.get_julia_c()
        elif self.renderer.current_fractal_name == 'phoenix':
            self._original_state['phoenix_p'] = self.renderer.get_phoenix_p()

    def _restore_state(self):
        """Restore saved renderer state."""
        if self._original_state is None:
            return

        self.renderer.viewport.center_re = self._original_state['center_re']
        self.renderer.viewport.center_im = self._original_state['center_im']
        self.renderer.viewport.scale = self._original_state['scale']

        # Restore fractal-specific parameters
        if 'julia_c' in self._original_state:
            self.renderer.set_julia_c(*self._original_state['julia_c'])
        if 'phoenix_p' in self._original_state:
            self.renderer.set_phoenix_p(*self._original_state['phoenix_p'])

        self._original_state = None

    def _apply_state(self, state: AnimationState):
        """Apply animation state to renderer."""
        self.renderer.viewport.center_re = state.center_re
        self.renderer.viewport.center_im = state.center_im
        self.renderer.viewport.scale = state.scale

        # Apply optional parameters
        if state.julia_c_re is not None and state.julia_c_im is not None:
            self.renderer.set_julia_c(state.julia_c_re, state.julia_c_im)
        if state.phoenix_p_re is not None and state.phoenix_p_im is not None:
            self.renderer.set_phoenix_p(state.phoenix_p_re, state.phoenix_p_im)

    def cancel(self):
        """Cancel ongoing animation rendering."""
        self._cancelled = True

    def reset(self):
        """Reset cancellation state."""
        self._cancelled = False

    def is_cancelled(self) -> bool:
        """Check if rendering was cancelled."""
        return self._cancelled

    def render_animation(self,
                         animation: AnimationBase,
                         width: int,
                         height: int,
                         output_path: str,
                         format: str = "mp4",
                         progress_callback: Optional[Callable[[int, int, str], None]] = None,
                         keep_frames: bool = False) -> bool:
        """
        Render complete animation to video file.

        Args:
            animation: Animation definition
            width: Output width in pixels
            height: Output height in pixels
            output_path: Output video file path
            format: Output format ("mp4" or "gif")
            progress_callback: Callback(current_frame, total_frames, status_message)
            keep_frames: If True, keep PNG frames after encoding

        Returns:
            True if successful, False if cancelled or failed
        """
        self._cancelled = False
        self._save_state()

        # Create temporary directory for frames
        temp_dir = tempfile.mkdtemp(prefix="fractal_anim_")
        exporter = FrameExporter(temp_dir, "frame")
        exporter.setup()

        total_frames = animation.total_frames

        try:
            # Phase 1: Render frames
            for frame in range(total_frames):
                if self._cancelled:
                    self._restore_state()
                    return False

                # Get animation state and apply to renderer
                state = animation.get_state(frame)
                self._apply_state(state)

                # Render frame
                rgba, _ = self.renderer.render(width, height)

                # Export frame
                exporter.export_frame(rgba, frame)

                if progress_callback:
                    progress_callback(frame + 1, total_frames, "Рендеринг кадрів...")

            if self._cancelled:
                self._restore_state()
                return False

            # Phase 2: Encode video
            if progress_callback:
                progress_callback(total_frames, total_frames, "Кодування відео...")

            if format.lower() == "gif":
                success = self.video_encoder.encode_gif(
                    exporter.get_frame_pattern(),
                    output_path,
                    fps=animation.fps,
                    width=min(width, 640)  # Limit GIF width
                )
            else:
                success = self.video_encoder.encode_mp4(
                    exporter.get_frame_pattern(),
                    output_path,
                    fps=animation.fps
                )

            if progress_callback:
                progress_callback(total_frames, total_frames, "Завершено!" if success else "Помилка кодування")

            return success

        finally:
            # Cleanup
            if not keep_frames:
                exporter.cleanup()
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass

            # Restore original state
            self._restore_state()

    def render_frames_only(self,
                           animation: AnimationBase,
                           width: int,
                           height: int,
                           output_dir: str,
                           prefix: str = "frame",
                           progress_callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        """
        Render animation frames without encoding.

        Args:
            animation: Animation definition
            width: Output width in pixels
            height: Output height in pixels
            output_dir: Directory for output frames
            prefix: Frame filename prefix
            progress_callback: Callback(current_frame, total_frames, status_message)

        Returns:
            True if successful
        """
        self._cancelled = False
        self._save_state()

        exporter = FrameExporter(output_dir, prefix)
        exporter.setup()

        total_frames = animation.total_frames

        try:
            for frame in range(total_frames):
                if self._cancelled:
                    self._restore_state()
                    return False

                state = animation.get_state(frame)
                self._apply_state(state)

                rgba, _ = self.renderer.render(width, height)
                exporter.export_frame(rgba, frame)

                if progress_callback:
                    progress_callback(frame + 1, total_frames, "Експорт кадрів...")

            if progress_callback:
                progress_callback(total_frames, total_frames, "Завершено!")

            return True

        finally:
            self._restore_state()

    def preview_frame(self,
                      animation: AnimationBase,
                      frame: int,
                      width: int,
                      height: int) -> Tuple[np.ndarray, float]:
        """
        Render a single preview frame.

        Args:
            animation: Animation definition
            frame: Frame number to preview
            width: Output width
            height: Output height

        Returns:
            Tuple of (rgba_array, render_time_ms)
        """
        self._save_state()

        try:
            state = animation.get_state(frame)
            self._apply_state(state)
            return self.renderer.render(width, height)
        finally:
            self._restore_state()

    @property
    def ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available for video encoding."""
        return self.video_encoder.is_available
