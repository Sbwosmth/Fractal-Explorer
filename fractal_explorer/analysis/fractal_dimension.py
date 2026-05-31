"""
Fractal Dimension Calculator using box-counting method.
"""

import numpy as np
from typing import Tuple, List
import math


def compute_box_counting_dimension(
    binary_image: np.ndarray,
    min_box_size: int = 2,
    max_box_size: int = None
) -> Tuple[float, List[int], List[int], float]:
    """
    Compute the fractal dimension of a binary image using box-counting.

    The box-counting dimension D is computed from the relationship:
        N(s) ~ s^(-D)
    where N(s) is the number of boxes of size s that contain at least
    one pixel of the fractal, and s is the box size.

    Args:
        binary_image: 2D numpy array where non-zero values represent the fractal
        min_box_size: Minimum box size to use
        max_box_size: Maximum box size (defaults to min(width, height) / 4)

    Returns:
        Tuple of (dimension, box_sizes, box_counts, r_squared)
        - dimension: Estimated fractal dimension
        - box_sizes: List of box sizes used
        - box_counts: List of box counts for each size
        - r_squared: R-squared value of the linear fit (quality indicator)
    """
    height, width = binary_image.shape

    if max_box_size is None:
        max_box_size = min(width, height) // 4

    # Binarize the image
    binary = (binary_image > 0).astype(np.uint8)

    box_sizes = []
    box_counts = []

    # Use powers of 2 for box sizes
    size = min_box_size
    while size <= max_box_size:
        count = _count_boxes(binary, size)
        if count > 0:
            box_sizes.append(size)
            box_counts.append(count)
        size *= 2

    if len(box_sizes) < 3:
        # Not enough data points for reliable estimation
        return 0.0, box_sizes, box_counts, 0.0

    # Linear regression on log-log scale
    log_sizes = np.log(box_sizes)
    log_counts = np.log(box_counts)

    # D = -slope of log(N) vs log(s)
    slope, intercept, r_squared = _linear_regression(log_sizes, log_counts)
    dimension = -slope

    return dimension, box_sizes, box_counts, r_squared


def _count_boxes(binary: np.ndarray, box_size: int) -> int:
    """Count the number of boxes of given size containing fractal points."""
    height, width = binary.shape
    count = 0

    for y in range(0, height, box_size):
        for x in range(0, width, box_size):
            y_end = min(y + box_size, height)
            x_end = min(x + box_size, width)
            box = binary[y:y_end, x:x_end]
            if np.any(box):
                count += 1

    return count


def _linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    Simple linear regression.

    Returns:
        (slope, intercept, r_squared)
    """
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_xx = np.sum(x * x)
    sum_yy = np.sum(y * y)

    # Slope and intercept
    denom = n * sum_xx - sum_x * sum_x
    if abs(denom) < 1e-10:
        return 0.0, 0.0, 0.0

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    # R-squared
    ss_tot = sum_yy - (sum_y * sum_y) / n
    ss_res = sum_yy - slope * sum_xy - intercept * sum_y
    if abs(ss_tot) < 1e-10:
        r_squared = 0.0
    else:
        r_squared = 1.0 - ss_res / ss_tot

    return slope, intercept, max(0.0, min(1.0, r_squared))


def iterations_to_binary(iterations: np.ndarray, max_iter: int) -> np.ndarray:
    """
    Convert iteration data to binary boundary image.

    The fractal boundary is where the iteration count changes rapidly,
    i.e., where interior meets exterior.

    Args:
        iterations: 2D array of iteration counts
        max_iter: Maximum iterations used

    Returns:
        Binary image highlighting the fractal boundary
    """
    # Find boundary pixels using gradient magnitude
    gradient_y = np.abs(np.diff(iterations, axis=0, prepend=iterations[:1, :]))
    gradient_x = np.abs(np.diff(iterations, axis=1, prepend=iterations[:, :1]))
    gradient_mag = np.sqrt(gradient_y**2 + gradient_x**2)

    # Threshold: consider pixels with significant gradient as boundary
    threshold = np.percentile(gradient_mag[gradient_mag > 0], 50)
    binary = (gradient_mag > threshold).astype(np.uint8)

    return binary


# Theoretical fractal dimensions for comparison
KNOWN_DIMENSIONS = {
    'mandelbrot': 2.0,  # Boundary dimension is exactly 2
    'julia': 1.5,  # Varies, typically 1.3-2.0
    'sierpinski': math.log(3) / math.log(2),  # ~1.585
    'koch': math.log(4) / math.log(3),  # ~1.2619
    'barnsley_fern': 1.7,  # Approximately
    'pythagoras': 2.0,  # Area-filling
    'newton': 1.5,  # Basin boundaries, varies
}


def get_theoretical_dimension(fractal_name: str) -> float:
    """Get the theoretical/known fractal dimension for a fractal type."""
    return KNOWN_DIMENSIONS.get(fractal_name, 0.0)
