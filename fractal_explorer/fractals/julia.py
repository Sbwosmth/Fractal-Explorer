"""
Julia set fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class JuliaFractal(BaseFractal):
    """
    Julia set fractal.

    Formula: z(n+1) = z(n)^2 + c, where c is a fixed constant.
    The shape dramatically changes with different values of c.
    """

    name = "Julia"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=0.0,
        scale=3.5,
        max_iterations=200
    )

    # Predefined interesting Julia set parameters
    PRESETS = {
        "Rabbit": (-0.123, 0.745),
        "Dragon": (-0.8, 0.156),
        "Spiral": (-0.4, 0.6),
        "Dendrite": (0.0, 1.0),
        "Galaxy": (-0.7269, 0.1889),
        "Feather": (-0.194, 0.6557),
        "Custom": (0.0, 0.0),
    }

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        # Default to Spiral preset
        self._params['c_re'] = -0.4
        self._params['c_im'] = 0.6

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Julia set iteration data."""
        c_re = self._params.get('c_re', -0.4)
        c_im = self._params.get('c_im', 0.6)

        return self.backend.compute_julia(
            width, height,
            x_min, x_max,
            y_min, y_max,
            c_re, c_im,
            max_iter
        )

    def set_c(self, c_re: float, c_im: float):
        """Set the Julia constant c."""
        self._params['c_re'] = c_re
        self._params['c_im'] = c_im

    def get_c(self) -> tuple:
        """Get the Julia constant c as (re, im) tuple."""
        return (
            self._params.get('c_re', -0.4),
            self._params.get('c_im', 0.6)
        )

    def apply_preset(self, preset_name: str):
        """Apply a named preset."""
        if preset_name in self.PRESETS:
            c_re, c_im = self.PRESETS[preset_name]
            self.set_c(c_re, c_im)
