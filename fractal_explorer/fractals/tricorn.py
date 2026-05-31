"""
Tricorn (Mandelbar) fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class TricornFractal(BaseFractal):
    """
    Tricorn (Mandelbar) fractal.

    Formula: z(n+1) = conj(z(n))^2 + c
    Uses the complex conjugate of z before squaring,
    creating a distinctive three-cornered shape.
    """

    name = "Tricorn"
    defaults = FractalDefaults(
        center_re=-0.3,
        center_im=0.0,
        scale=3.5,
        max_iterations=200
    )

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Tricorn fractal iteration data."""
        return self.backend.compute_tricorn(
            width, height,
            x_min, x_max,
            y_min, y_max,
            max_iter
        )

    # Interesting points for deep zoom animation
    INTERESTING_POINTS = [
        (-1.0, 0.0),        # Left horn
        (0.25, 0.5),        # Upper region
        (-0.4, 0.58),       # Detail area
        (-1.292, -0.43),    # Spiral structure
    ]
