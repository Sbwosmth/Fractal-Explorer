"""
Main rendering coordinator.
"""

import time
import numpy as np
from typing import Dict, Any, Optional, Tuple

from .viewport import Viewport
from .colormap import ColorMapper
from ..compute.backend import ComputeBackend
from ..fractals.base import BaseFractal
from ..fractals.mandelbrot import MandelbrotFractal
from ..fractals.julia import JuliaFractal
from ..fractals.newton import NewtonFractal
from ..fractals.pythagoras_tree import PythagorasTreeFractal
from ..fractals.burning_ship import BurningShipFractal
from ..fractals.tricorn import TricornFractal
from ..fractals.phoenix import PhoenixFractal
from ..fractals.barnsley_fern import BarnsleyFernFractal
from ..fractals.sierpinski import SierpinskiFractal
from ..fractals.koch import KochSnowflakeFractal
from ..fractals.buddhabrot import BuddhabrotFractal


class FractalRenderer:
    """
    Coordinates fractal computation and rendering.

    Manages the viewport, colormap, compute backend, and fractal instances.
    """

    FRACTAL_TYPES = {
        'mandelbrot': MandelbrotFractal,
        'julia': JuliaFractal,
        'newton': NewtonFractal,
        'pythagoras': PythagorasTreeFractal,
        'burning_ship': BurningShipFractal,
        'tricorn': TricornFractal,
        'phoenix': PhoenixFractal,
        'barnsley_fern': BarnsleyFernFractal,
        'sierpinski': SierpinskiFractal,
        'koch': KochSnowflakeFractal,
        'buddhabrot': BuddhabrotFractal,
    }

    # IFS fractals that don't use iteration-based rendering
    IFS_FRACTALS = {'barnsley_fern', 'sierpinski', 'koch', 'buddhabrot'}

    def __init__(self):
        """Initialize the renderer."""
        self.backend = ComputeBackend()
        self.viewport = Viewport()
        self.colormap = ColorMapper()

        # Create fractal instances
        self.fractals: Dict[str, BaseFractal] = {}
        for name, fractal_class in self.FRACTAL_TYPES.items():
            self.fractals[name] = fractal_class(self.backend)

        # Current state
        self._current_fractal_name = 'mandelbrot'
        self._max_iterations = 200
        self._last_render_time = 0.0
        self._last_iterations: Optional[np.ndarray] = None

        # Initialize viewport to default for current fractal
        self._apply_default_viewport()

    def _apply_default_viewport(self):
        """Apply default viewport for current fractal."""
        fractal = self.get_current_fractal()
        center_re, center_im, scale = fractal.get_default_viewport()
        self.viewport.reset(center_re, center_im, scale)
        self._max_iterations = fractal.get_default_iterations()

    @property
    def current_fractal_name(self) -> str:
        """Get current fractal type name."""
        return self._current_fractal_name

    def get_current_fractal(self) -> BaseFractal:
        """Get the current fractal instance."""
        return self.fractals[self._current_fractal_name]

    def set_fractal_type(self, fractal_name: str):
        """
        Change the current fractal type.

        Args:
            fractal_name: One of 'mandelbrot', 'julia', 'newton', 'pythagoras'
        """
        if fractal_name not in self.FRACTAL_TYPES:
            return

        self._current_fractal_name = fractal_name
        self._apply_default_viewport()

    def set_max_iterations(self, max_iter: int):
        """Set maximum iterations."""
        self._max_iterations = max(50, min(2000, max_iter))

    def get_max_iterations(self) -> int:
        """Get maximum iterations."""
        return self._max_iterations

    def set_colormap(self, name: str):
        """Change the colormap."""
        self.colormap.set_colormap(name)

    def render(self, width: int, height: int) -> Tuple[np.ndarray, float]:
        """
        Render the current fractal.

        Args:
            width: Output width in pixels
            height: Output height in pixels

        Returns:
            Tuple of (RGBA image array, render time in ms)
        """
        if width <= 0 or height <= 0:
            return np.zeros((1, 1, 4), dtype=np.uint8), 0.0

        start_time = time.perf_counter()

        # Get viewport bounds
        aspect_ratio = width / height
        x_min, x_max, y_min, y_max = self.viewport.get_bounds(aspect_ratio)

        # Compute fractal
        fractal = self.get_current_fractal()
        iterations = fractal.compute(
            width, height,
            x_min, x_max, y_min, y_max,
            self._max_iterations
        )

        self._last_iterations = iterations

        # Apply colormap
        if self._current_fractal_name == 'newton':
            rgba = self.colormap.apply_newton(iterations, self._max_iterations)
        elif self._current_fractal_name == 'pythagoras':
            rgba = self.colormap.apply_tree(iterations, self._max_iterations)
        elif self._current_fractal_name in self.IFS_FRACTALS:
            rgba = self.colormap.apply_ifs(iterations)
        else:
            rgba = self.colormap.apply(iterations, self._max_iterations)

        end_time = time.perf_counter()
        self._last_render_time = (end_time - start_time) * 1000  # Convert to ms

        return rgba, self._last_render_time

    def get_last_render_time(self) -> float:
        """Get the last render time in milliseconds."""
        return self._last_render_time

    def reset_view(self):
        """Reset viewport to default for current fractal."""
        self._apply_default_viewport()

    def zoom(self, factor: float, mouse_x: int = None, mouse_y: int = None,
             width: int = None, height: int = None):
        """
        Zoom the viewport.

        Args:
            factor: Zoom factor (>1 zooms in)
            mouse_x, mouse_y: Mouse position for zoom center
            width, height: Viewport dimensions
        """
        mouse_re, mouse_im = None, None

        if all(v is not None for v in [mouse_x, mouse_y, width, height]):
            mouse_re, mouse_im = self.viewport.pixel_to_complex(
                mouse_x, mouse_y, width, height
            )

        self.viewport.zoom(factor, mouse_re, mouse_im)

    def pan(self, dx: int, dy: int, width: int, height: int):
        """
        Pan the viewport by pixel amounts.

        Args:
            dx, dy: Pixel deltas
            width, height: Viewport dimensions
        """
        self.viewport.pan_pixels(dx, dy, width, height)

    def get_complex_coords(self, px: int, py: int,
                          width: int, height: int) -> Tuple[float, float]:
        """
        Get complex coordinates for a pixel position.

        Args:
            px, py: Pixel coordinates
            width, height: Viewport dimensions

        Returns:
            Tuple of (real, imaginary) coordinates
        """
        return self.viewport.pixel_to_complex(px, py, width, height)

    def get_info(self) -> Dict[str, Any]:
        """
        Get current state information.

        Returns:
            Dictionary with render info
        """
        return {
            'fractal': self._current_fractal_name,
            'center_re': self.viewport.center_re,
            'center_im': self.viewport.center_im,
            'scale': self.viewport.scale,
            'zoom': self.viewport.get_zoom_string(),
            'max_iterations': self._max_iterations,
            'render_time_ms': self._last_render_time,
            'backend': self.backend.get_status(),
            'colormap': self.colormap.get_colormap_name(),
        }

    def set_julia_c(self, c_re: float, c_im: float):
        """Set Julia set constant c."""
        julia = self.fractals['julia']
        julia.set_c(c_re, c_im)

    def get_julia_c(self) -> Tuple[float, float]:
        """Get Julia set constant c."""
        julia = self.fractals['julia']
        return julia.get_c()

    def set_tree_params(self, angle: float = None, depth: int = None):
        """Set Pythagoras tree parameters."""
        tree = self.fractals['pythagoras']
        if angle is not None:
            tree.set_angle(angle)
        if depth is not None:
            tree.set_depth(depth)

    def get_tree_params(self) -> Tuple[float, int]:
        """Get Pythagoras tree parameters (angle, depth)."""
        tree = self.fractals['pythagoras']
        return tree.get_angle(), tree.get_depth()

    def set_phoenix_p(self, p_re: float, p_im: float):
        """Set Phoenix fractal parameters p."""
        phoenix = self.fractals['phoenix']
        phoenix.set_p(p_re, p_im)

    def get_phoenix_p(self) -> Tuple[float, float]:
        """Get Phoenix fractal parameters p."""
        phoenix = self.fractals['phoenix']
        return phoenix.get_p()

    def set_koch_depth(self, depth: int):
        """Set Koch snowflake depth."""
        koch = self.fractals['koch']
        koch.set_depth(depth)

    def get_koch_depth(self) -> int:
        """Get Koch snowflake depth."""
        koch = self.fractals['koch']
        return koch.get_depth()

    def get_last_iterations(self) -> Optional[np.ndarray]:
        """Get the last computed iteration data (for analysis)."""
        return self._last_iterations

    def is_iterative_fractal(self) -> bool:
        """Check if current fractal uses iteration-based computation."""
        return self._current_fractal_name not in self.IFS_FRACTALS
