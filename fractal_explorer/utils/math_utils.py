"""
Mathematical utility functions.
"""

from typing import Tuple


def complex_to_pixel(re: float, im: float,
                    x_min: float, x_max: float,
                    y_min: float, y_max: float,
                    width: int, height: int) -> Tuple[int, int]:
    """
    Convert complex plane coordinates to pixel coordinates.

    Args:
        re, im: Complex coordinates
        x_min, x_max: Real axis bounds
        y_min, y_max: Imaginary axis bounds
        width, height: Image dimensions

    Returns:
        Tuple of (px, py) pixel coordinates
    """
    px = int((re - x_min) / (x_max - x_min) * width)
    py = int((y_max - im) / (y_max - y_min) * height)
    return (px, py)


def pixel_to_complex(px: int, py: int,
                    x_min: float, x_max: float,
                    y_min: float, y_max: float,
                    width: int, height: int) -> Tuple[float, float]:
    """
    Convert pixel coordinates to complex plane coordinates.

    Args:
        px, py: Pixel coordinates
        x_min, x_max: Real axis bounds
        y_min, y_max: Imaginary axis bounds
        width, height: Image dimensions

    Returns:
        Tuple of (re, im) complex coordinates
    """
    re = x_min + (x_max - x_min) * px / width
    im = y_max - (y_max - y_min) * py / height
    return (re, im)


def format_complex(re: float, im: float, precision: int = 6) -> str:
    """
    Format a complex number as a string.

    Args:
        re: Real part
        im: Imaginary part
        precision: Decimal precision

    Returns:
        Formatted string like "0.123456 + 0.789012i"
    """
    sign = '+' if im >= 0 else '-'
    return f"{re:.{precision}f} {sign} {abs(im):.{precision}f}i"


def format_scientific(value: float) -> str:
    """
    Format a number in scientific notation if appropriate.

    Args:
        value: Number to format

    Returns:
        Formatted string
    """
    if abs(value) >= 1e6 or (abs(value) < 1e-4 and value != 0):
        return f"{value:.2e}"
    return f"{value:.6f}"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to a range.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.

    Args:
        a: Start value
        b: End value
        t: Interpolation factor [0, 1]

    Returns:
        Interpolated value
    """
    return a + (b - a) * t
