"""
Viewport management for fractal rendering.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Viewport:
    """
    Manages the viewport (viewing area) in the complex plane.

    Attributes:
        center_re: Center point real component
        center_im: Center point imaginary component
        scale: Width of the visible area in complex plane units
    """

    center_re: float = -0.5
    center_im: float = 0.0
    scale: float = 3.5

    def get_bounds(self, aspect_ratio: float) -> Tuple[float, float, float, float]:
        """
        Get the bounds of the viewport.

        Args:
            aspect_ratio: Width/height ratio of the display

        Returns:
            Tuple of (x_min, x_max, y_min, y_max)
        """
        half_width = self.scale / 2
        half_height = half_width / aspect_ratio

        x_min = self.center_re - half_width
        x_max = self.center_re + half_width
        y_min = self.center_im - half_height
        y_max = self.center_im + half_height

        return (x_min, x_max, y_min, y_max)

    def zoom(self, factor: float, mouse_re: float = None, mouse_im: float = None):
        """
        Zoom the viewport by a factor.

        Args:
            factor: Zoom factor (>1 zooms in, <1 zooms out)
            mouse_re: Real coordinate of zoom center (cursor position)
            mouse_im: Imaginary coordinate of zoom center
        """
        if mouse_re is not None and mouse_im is not None:
            # Zoom relative to cursor position
            # Move center toward cursor, then scale
            self.center_re = mouse_re + (self.center_re - mouse_re) / factor
            self.center_im = mouse_im + (self.center_im - mouse_im) / factor

        self.scale /= factor

        # Prevent extreme zoom levels
        self.scale = max(1e-14, min(20.0, self.scale))

    def pan(self, delta_re: float, delta_im: float):
        """
        Pan the viewport by a delta in complex plane coordinates.

        Args:
            delta_re: Delta in real direction
            delta_im: Delta in imaginary direction
        """
        self.center_re += delta_re
        self.center_im += delta_im

    def pan_pixels(self, dx: int, dy: int, width: int, height: int):
        """
        Pan the viewport by pixel amounts.

        Args:
            dx: Pixel delta in x
            dy: Pixel delta in y
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        # Convert pixel delta to complex plane delta
        aspect_ratio = width / height
        x_min, x_max, y_min, y_max = self.get_bounds(aspect_ratio)

        delta_re = -dx * (x_max - x_min) / width
        delta_im = dy * (y_max - y_min) / height

        self.pan(delta_re, delta_im)

    def pixel_to_complex(self, px: int, py: int,
                        width: int, height: int) -> Tuple[float, float]:
        """
        Convert pixel coordinates to complex plane coordinates.

        Args:
            px, py: Pixel coordinates
            width, height: Viewport dimensions

        Returns:
            Tuple of (real, imaginary) coordinates
        """
        aspect_ratio = width / height
        x_min, x_max, y_min, y_max = self.get_bounds(aspect_ratio)

        re = x_min + (x_max - x_min) * px / width
        im = y_max - (y_max - y_min) * py / height  # Y is flipped

        return (re, im)

    def reset(self, center_re: float = -0.5, center_im: float = 0.0, scale: float = 3.5):
        """Reset viewport to given or default values."""
        self.center_re = center_re
        self.center_im = center_im
        self.scale = scale

    def get_zoom_level(self) -> float:
        """Get the current zoom level (inverse of scale, normalized)."""
        # Default scale is ~3.5, so zoom level 1x at scale=3.5
        return 3.5 / self.scale

    def get_zoom_string(self) -> str:
        """Get a human-readable zoom level string."""
        zoom = self.get_zoom_level()
        if zoom >= 1e15:
            return f"{zoom:.2e}x"
        elif zoom >= 1e12:
            return f"{zoom/1e12:.2f}T x"
        elif zoom >= 1e9:
            return f"{zoom/1e9:.2f}G x"
        elif zoom >= 1e6:
            return f"{zoom/1e6:.2f}M x"
        elif zoom >= 1e3:
            return f"{zoom/1e3:.2f}K x"
        else:
            return f"{zoom:.2f}x"

    def copy(self) -> 'Viewport':
        """Create a copy of this viewport."""
        return Viewport(self.center_re, self.center_im, self.scale)
