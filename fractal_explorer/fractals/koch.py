"""
Koch Snowflake - L-system geometric fractal.
"""

import numpy as np
import math
from .base import BaseFractal, FractalDefaults


class KochSnowflakeFractal(BaseFractal):
    """
    Koch Snowflake fractal.

    Constructed by recursively replacing each line segment with 4 segments
    forming a triangular bump. Starting from an equilateral triangle.

    Fractal dimension: log(4)/log(3) ~ 1.2619
    """

    name = "Koch Snowflake"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=0.0,
        scale=3.5,
        max_iterations=6
    )

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        self._params['depth'] = 5

    def is_iterative(self) -> bool:
        return False

    def get_depth(self) -> int:
        return self._params.get('depth', 5)

    def set_depth(self, depth: int):
        self._params['depth'] = max(1, min(7, depth))

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Koch Snowflake."""
        depth = self._params.get('depth', min(6, max_iter))
        return _compute_koch(width, height, x_min, x_max, y_min, y_max, depth)


def _koch_points(p1, p2, depth):
    """Recursively generate Koch curve points between p1 and p2."""
    if depth == 0:
        return [p1]

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    # Divide segment into thirds
    a = p1
    b = (p1[0] + dx / 3, p1[1] + dy / 3)
    d = (p1[0] + 2 * dx / 3, p1[1] + 2 * dy / 3)
    e = p2

    # Peak of the equilateral triangle
    cx = (p1[0] + p2[0]) / 2 + math.sqrt(3) / 6 * (p1[1] - p2[1])
    cy = (p1[1] + p2[1]) / 2 + math.sqrt(3) / 6 * (p2[0] - p1[0])
    c = (cx, cy)

    points = []
    points.extend(_koch_points(a, b, depth - 1))
    points.extend(_koch_points(b, c, depth - 1))
    points.extend(_koch_points(c, d, depth - 1))
    points.extend(_koch_points(d, e, depth - 1))

    return points


def _compute_koch(width, height, x_min, x_max, y_min, y_max, depth):
    """Compute Koch Snowflake rasterized to a grid."""
    result = np.zeros((height, width), dtype=np.float32)

    # Starting equilateral triangle
    s = 1.5
    h_tri = s * math.sqrt(3) / 2
    cy_offset = -h_tri / 3

    v1 = (-s / 2, cy_offset)
    v2 = (s / 2, cy_offset)
    v3 = (0.0, cy_offset + h_tri)

    # Generate Koch curve points for each side
    all_points = []
    all_points.extend(_koch_points(v1, v3, depth))
    all_points.extend(_koch_points(v3, v2, depth))
    all_points.extend(_koch_points(v2, v1, depth))
    all_points.append(all_points[0])  # Close the curve

    # Draw lines between consecutive points using Bresenham
    for i in range(len(all_points) - 1):
        x1, y1 = all_points[i]
        x2, y2 = all_points[i + 1]

        # Convert to pixel coordinates
        px1 = int((x1 - x_min) / (x_max - x_min) * width)
        py1 = int((y_max - y1) / (y_max - y_min) * height)
        px2 = int((x2 - x_min) / (x_max - x_min) * width)
        py2 = int((y_max - y2) / (y_max - y_min) * height)

        # Bresenham line
        _draw_line(result, px1, py1, px2, py2, width, height, float(depth))

    # Normalize
    max_val = result.max()
    if max_val > 0:
        result = result / max_val * 255.0

    return result


def _draw_line(grid, x0, y0, x1, y1, width, height, value):
    """Draw a line on the grid using Bresenham's algorithm."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            grid[y0, x0] = value
            # Anti-aliasing: paint neighbors slightly
            for nx, ny in [(x0-1, y0), (x0+1, y0), (x0, y0-1), (x0, y0+1)]:
                if 0 <= nx < width and 0 <= ny < height:
                    grid[ny, nx] = max(grid[ny, nx], value * 0.4)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
