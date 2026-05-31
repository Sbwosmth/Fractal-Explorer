"""
Barnsley Fern - IFS (Iterated Function System) fractal.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class BarnsleyFernFractal(BaseFractal):
    """
    Barnsley Fern using Iterated Function System (IFS).

    Uses 4 affine transformations with probabilities:
      f1: (x,y) -> (0, 0.16y)                    p=0.01  (stem)
      f2: (x,y) -> (0.85x+0.04y, -0.04x+0.85y+1.6)  p=0.85  (leaflets)
      f3: (x,y) -> (0.2x-0.26y, 0.23x+0.22y+1.6)     p=0.07  (left branch)
      f4: (x,y) -> (-0.15x+0.28y, 0.26x+0.24y+0.44)   p=0.07  (right branch)
    """

    name = "Barnsley Fern"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=5.0,
        scale=12.0,
        max_iterations=500000
    )

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        self._params['num_points'] = 500000

    def is_iterative(self) -> bool:
        return False

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Barnsley Fern via chaos game."""
        num_points = self._params.get('num_points', max(100000, max_iter * 100))
        return _compute_barnsley_fern(
            width, height, x_min, x_max, y_min, y_max, num_points
        )


def _compute_barnsley_fern(width, height, x_min, x_max, y_min, y_max, num_points):
    """Compute Barnsley Fern density map."""
    result = np.zeros((height, width), dtype=np.float32)

    x, y = 0.0, 0.0
    rng = np.random.default_rng(42)
    randoms = rng.random(num_points)

    for i in range(num_points):
        r = randoms[i]
        if r < 0.01:
            x_new = 0.0
            y_new = 0.16 * y
        elif r < 0.86:
            x_new = 0.85 * x + 0.04 * y
            y_new = -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            x_new = 0.20 * x - 0.26 * y
            y_new = 0.23 * x + 0.22 * y + 1.6
        else:
            x_new = -0.15 * x + 0.28 * y
            y_new = 0.26 * x + 0.24 * y + 0.44

        x, y = x_new, y_new

        # Map to pixel coordinates
        px = int((x - x_min) / (x_max - x_min) * width)
        py = int((y_max - y) / (y_max - y_min) * height)

        if 0 <= px < width and 0 <= py < height:
            result[py, px] += 1.0

    # Log-scale for better visualization
    result = np.log1p(result)
    max_val = result.max()
    if max_val > 0:
        result = result / max_val * 255.0

    return result
