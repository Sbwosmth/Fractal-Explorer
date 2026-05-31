"""
Pythagoras Tree fractal implementation (geometric/L-system based).
"""

import numpy as np
from .base import BaseFractal, FractalDefaults
from typing import List, Tuple


class PythagorasTreeFractal(BaseFractal):
    """
    Pythagoras Tree fractal - a geometric fractal based on recursively
    adding squares to the catheti of a right triangle.

    This is NOT an iterative fractal - it's rendered as geometry.
    """

    name = "Pythagoras Tree"
    defaults = FractalDefaults(
        center_re=0.0,
        center_im=0.0,
        scale=4.0,
        max_iterations=10  # Actually depth for this fractal
    )

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        self._params['angle'] = 45.0  # Angle in degrees
        self._params['depth'] = 10

    def is_iterative(self) -> bool:
        """Pythagoras tree is not iteration-based."""
        return False

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """
        Render Pythagoras tree to an iteration-like array.

        For consistency with other fractals, we render to an array
        where the value represents the depth level of each pixel.
        """
        result = np.zeros((height, width), dtype=np.float32)

        angle = self._params.get('angle', 45.0)
        depth = self._params.get('depth', min(max_iter, 15))
        depth = min(depth, 15)  # Cap depth for performance

        # Generate tree geometry
        squares = self._generate_tree(angle, depth)

        # Rasterize squares to the result array
        self._rasterize_squares(result, squares, width, height,
                               x_min, x_max, y_min, y_max, depth)

        return result

    def _generate_tree(self, angle_deg: float, max_depth: int) -> List[Tuple]:
        """
        Generate all squares for the Pythagoras tree.

        Returns list of (corners, depth) tuples where corners is 4 points.
        """
        squares = []
        angle_rad = np.radians(angle_deg)

        # Start with base square centered at origin
        base_size = 0.5
        base_square = np.array([
            [-base_size, 0],           # Bottom-left
            [base_size, 0],            # Bottom-right
            [base_size, base_size * 2],  # Top-right
            [-base_size, base_size * 2]  # Top-left
        ])

        self._generate_branch(squares, base_square, 0, max_depth, angle_rad)

        return squares

    def _generate_branch(self, squares: List, square: np.ndarray,
                        depth: int, max_depth: int, angle: float):
        """Recursively generate tree branches."""
        squares.append((square.copy(), depth))

        if depth >= max_depth:
            return

        # Get top edge of current square
        top_left = square[3]
        top_right = square[2]

        # Direction along top edge
        edge = top_right - top_left
        edge_len = np.linalg.norm(edge)
        edge_dir = edge / edge_len

        # Perpendicular (outward)
        perp = np.array([-edge_dir[1], edge_dir[0]])

        # Triangle apex
        apex_offset = np.tan(angle) * edge_len / 2
        side_offset = edge_len / 2 * np.cos(angle)

        # Left branch
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        # Size of child squares (based on angle)
        left_size = edge_len * cos_a
        right_size = edge_len * sin_a

        # Left square
        left_base_start = top_left
        left_base_end = top_left + edge_dir * cos_a * left_size + perp * sin_a * left_size

        # Build left square
        left_dir = left_base_end - left_base_start
        left_dir_norm = left_dir / np.linalg.norm(left_dir)
        left_perp = np.array([-left_dir_norm[1], left_dir_norm[0]])
        left_side = np.linalg.norm(left_dir)

        left_square = np.array([
            left_base_start,
            left_base_end,
            left_base_end + left_perp * left_side,
            left_base_start + left_perp * left_side
        ])

        # Right square
        right_base_end = top_right
        right_base_start = left_base_end

        right_dir = right_base_end - right_base_start
        right_dir_norm = right_dir / (np.linalg.norm(right_dir) + 1e-10)
        right_perp = np.array([-right_dir_norm[1], right_dir_norm[0]])
        right_side = np.linalg.norm(right_dir)

        if right_side > 0.001:
            right_square = np.array([
                right_base_start,
                right_base_end,
                right_base_end + right_perp * right_side,
                right_base_start + right_perp * right_side
            ])

            # Recurse
            self._generate_branch(squares, left_square, depth + 1, max_depth, angle)
            self._generate_branch(squares, right_square, depth + 1, max_depth, angle)

    def _rasterize_squares(self, result: np.ndarray,
                          squares: List[Tuple],
                          width: int, height: int,
                          x_min: float, x_max: float,
                          y_min: float, y_max: float,
                          max_depth: int):
        """Rasterize squares into the result array."""
        for corners, depth in squares:
            # Convert corners to pixel coordinates
            px = ((corners[:, 0] - x_min) / (x_max - x_min) * width).astype(int)
            py = ((y_max - corners[:, 1]) / (y_max - y_min) * height).astype(int)

            # Draw filled polygon
            self._fill_polygon(result, px, py, float(depth + 1) / max_depth * max_depth)

    def _fill_polygon(self, image: np.ndarray, px: np.ndarray, py: np.ndarray, value: float):
        """Fill a polygon in the image using scanline algorithm."""
        height, width = image.shape

        # Clip to image bounds
        px = np.clip(px, 0, width - 1)
        py = np.clip(py, 0, height - 1)

        # Get bounding box
        min_y = max(0, int(py.min()))
        max_y = min(height - 1, int(py.max()))

        if min_y >= max_y:
            return

        # Scanline fill
        n = len(px)
        for y in range(min_y, max_y + 1):
            intersections = []

            for i in range(n):
                j = (i + 1) % n
                y1, y2 = py[i], py[j]
                x1, x2 = px[i], px[j]

                if y1 == y2:
                    continue

                if y1 > y2:
                    y1, y2 = y2, y1
                    x1, x2 = x2, x1

                if y1 <= y < y2:
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)

            intersections.sort()

            for i in range(0, len(intersections) - 1, 2):
                x_start = max(0, int(intersections[i]))
                x_end = min(width - 1, int(intersections[i + 1]))
                if x_start <= x_end:
                    image[y, x_start:x_end + 1] = value

    def set_angle(self, angle: float):
        """Set branch angle in degrees."""
        self._params['angle'] = max(20.0, min(70.0, angle))

    def get_angle(self) -> float:
        """Get current branch angle."""
        return self._params.get('angle', 45.0)

    def set_depth(self, depth: int):
        """Set recursion depth."""
        self._params['depth'] = max(5, min(15, depth))

    def get_depth(self) -> int:
        """Get current recursion depth."""
        return self._params.get('depth', 10)
