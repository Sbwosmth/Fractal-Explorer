"""
Mandelbrot set fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class MandelbrotFractal(BaseFractal):
    """
    Mandelbrot set fractal.

    Formula: z(n+1) = z(n)^2 + c, where c is the coordinate
    A point belongs to the set if |z| <= 2 after N iterations.
    """

    name = "Mandelbrot"
    defaults = FractalDefaults(
        center_re=-0.5,
        center_im=0.0,
        scale=3.5,
        max_iterations=200
    )

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Mandelbrot set iteration data."""
        return self.backend.compute_mandelbrot(
            width, height,
            x_min, x_max,
            y_min, y_max,
            max_iter
        )

    # Interesting points for deep zoom animation
    INTERESTING_POINTS = [
        (-0.74364388703, 0.13182590421),  # Spiral
        (-0.7435669, 0.1314023),           # Double spiral
        (-0.5, 0.0),                       # Main cardioid
        (-1.25, 0.0),                      # Period-2 bulb
        (-0.1011, 0.9563),                 # Seahorse valley
        (-0.749, 0.1),                     # Julia island
    ]
