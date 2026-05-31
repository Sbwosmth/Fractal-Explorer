"""
Sierpinski Triangle - Chaos Game fractal.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class SierpinskiFractal(BaseFractal):
    """
    Sierpinski Triangle using the Chaos Game algorithm.

    Algorithm:
    1. Define 3 vertices of an equilateral triangle.
    2. Pick a random starting point.
    3. Randomly choose a vertex, move halfway toward it.
    4. Plot the new point. Repeat.

    Fractal dimension: log(3)/log(2) ~ 1.585
    """

    name = "Sierpinski Triangle"
    defaults = FractalDefaults(
        center_re=0.5,
        center_im=0.33,
        scale=1.4,
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
        """Compute Sierpinski Triangle via chaos game."""
        num_points = self._params.get('num_points', max(100000, max_iter * 100))
        return _compute_sierpinski(
            width, height, x_min, x_max, y_min, y_max, num_points
        )


def _compute_sierpinski(width, height, x_min, x_max, y_min, y_max, num_points):
    """Compute Sierpinski Triangle density map."""
    result = np.zeros((height, width), dtype=np.float32)

    # Equilateral triangle vertices
    v = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, np.sqrt(3) / 2]
    ])

    x, y = 0.5, 0.25
    rng = np.random.default_rng(42)
    choices = rng.integers(0, 3, size=num_points)

    for i in range(num_points):
        vertex = v[choices[i]]
        x = (x + vertex[0]) / 2.0
        y = (y + vertex[1]) / 2.0

        px = int((x - x_min) / (x_max - x_min) * width)
        py = int((y_max - y) / (y_max - y_min) * height)

        if 0 <= px < width and 0 <= py < height:
            result[py, px] += 1.0

    # Log-scale
    result = np.log1p(result)
    max_val = result.max()
    if max_val > 0:
        result = result / max_val * 255.0

    return result
