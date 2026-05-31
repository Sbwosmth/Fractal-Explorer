"""
Phoenix fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class PhoenixFractal(BaseFractal):
    """
    Phoenix fractal.

    Formula: z(n+1) = z(n)^2 + p_re + p_im * z(n-1)
    Uses memory of the previous z value, creating
    distinctive flame-like patterns resembling a phoenix.
    """

    name = "Phoenix"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=0.0,
        scale=3.5,
        max_iterations=200
    )

    # Predefined interesting Phoenix parameters
    PRESETS = {
        "Classic": (0.5667, -0.5),
        "Flame": (0.2, -0.6),
        "Feather": (-0.5, 0.0),
        "Spiral": (0.56667, -0.5),
        "Dragon": (0.4, -0.65),
        "Custom": (0.5667, -0.5),
    }

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        # Default to Classic preset
        self._params['p_re'] = 0.5667
        self._params['p_im'] = -0.5

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Phoenix fractal iteration data."""
        p_re = self._params.get('p_re', 0.5667)
        p_im = self._params.get('p_im', -0.5)

        return self.backend.compute_phoenix(
            width, height,
            x_min, x_max,
            y_min, y_max,
            p_re, p_im,
            max_iter
        )

    def set_p(self, p_re: float, p_im: float):
        """Set the Phoenix parameters p."""
        self._params['p_re'] = p_re
        self._params['p_im'] = p_im

    def get_p(self) -> tuple:
        """Get the Phoenix parameters p as (re, im) tuple."""
        return (
            self._params.get('p_re', 0.5667),
            self._params.get('p_im', -0.5)
        )

    def apply_preset(self, preset_name: str):
        """Apply a named preset."""
        if preset_name in self.PRESETS:
            p_re, p_im = self.PRESETS[preset_name]
            self.set_p(p_re, p_im)

    # Interesting points for deep zoom animation
    INTERESTING_POINTS = [
        (0.0, 0.0),         # Center
        (-0.5, 0.0),        # Left wing
        (0.3, 0.4),         # Detail area
        (-0.35, 0.55),      # Spiral
    ]
