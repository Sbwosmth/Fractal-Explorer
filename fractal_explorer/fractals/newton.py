"""
Newton fractal implementation.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class NewtonFractal(BaseFractal):
    """
    Newton fractal based on Newton's method for z^3 - 1 = 0.

    Visualizes convergence to the three roots of the equation.
    Color is determined by which root the point converges to
    and how many iterations it takes.

    Formula: z(n+1) = z(n) - f(z(n))/f'(z(n))
           = z(n) - (z(n)^3 - 1)/(3*z(n)^2)
    """

    name = "Newton"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=0.0,
        scale=3.0,
        max_iterations=50
    )

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        self._params['tolerance'] = 1e-6

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Newton fractal iteration data."""
        tolerance = self._params.get('tolerance', 1e-6)

        return self.backend.compute_newton(
            width, height,
            x_min, x_max,
            y_min, y_max,
            max_iter,
            tolerance
        )

    def set_tolerance(self, tolerance: float):
        """Set convergence tolerance."""
        self._params['tolerance'] = max(1e-12, min(1e-2, tolerance))

    def get_tolerance(self) -> float:
        """Get current convergence tolerance."""
        return self._params.get('tolerance', 1e-6)
