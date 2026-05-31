"""
Burning Ship fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class BurningShipFractal(BaseFractal):
    """
    Burning Ship fractal.

    Formula: z(n+1) = (|Re(z)| + i|Im(z)|)^2 + c
    Uses absolute values of real and imaginary parts before squaring,
    creating a distinctive ship-like shape.
    """

    name = "Burning Ship"
    defaults = FractalDefaults(
        center_re=-0.4,
        center_im=-0.5,
        scale=3.5,
        max_iterations=200
    )

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Burning Ship fractal iteration data."""
        return self.backend.compute_burning_ship(
            width, height,
            x_min, x_max,
            y_min, y_max,
            max_iter
        )

    # Interesting points for deep zoom animation
    INTERESTING_POINTS = [
        (-1.762, -0.028),   # Main ship
        (-1.756, -0.0235),  # Antenna
        (-1.771, -0.054),   # Mini ship
        (-0.524, -0.526),   # Spiral structure
    ]
