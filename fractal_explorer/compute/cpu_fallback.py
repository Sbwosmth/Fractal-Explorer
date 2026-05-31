"""
CPU fallback implementations using Numba for JIT compilation.
"""

import numpy as np
from numba import njit, prange


@njit(parallel=True, fastmath=True)
def compute_mandelbrot_cpu(width: int, height: int,
                           x_min: float, x_max: float,
                           y_min: float, y_max: float,
                           max_iter: int) -> np.ndarray:
    """Compute Mandelbrot set on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            x0 = x_min + (x_max - x_min) * px / width
            y0 = y_max - (y_max - y_min) * py / height  # Flip Y

            x, y = 0.0, 0.0
            iteration = 0

            while x*x + y*y <= 4.0 and iteration < max_iter:
                x_new = x*x - y*y + x0
                y = 2.0*x*y + y0
                x = x_new
                iteration += 1

            # Smooth coloring
            smooth_iter = float(iteration)
            if iteration < max_iter:
                log_zn = np.log(x*x + y*y) / 2.0
                nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
                smooth_iter = iteration + 1.0 - nu

            result[py, px] = smooth_iter

    return result


@njit(parallel=True, fastmath=True)
def compute_julia_cpu(width: int, height: int,
                      x_min: float, x_max: float,
                      y_min: float, y_max: float,
                      c_re: float, c_im: float,
                      max_iter: int) -> np.ndarray:
    """Compute Julia set on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            x = x_min + (x_max - x_min) * px / width
            y = y_max - (y_max - y_min) * py / height

            iteration = 0

            while x*x + y*y <= 4.0 and iteration < max_iter:
                x_new = x*x - y*y + c_re
                y = 2.0*x*y + c_im
                x = x_new
                iteration += 1

            # Smooth coloring
            smooth_iter = float(iteration)
            if iteration < max_iter:
                log_zn = np.log(x*x + y*y) / 2.0
                nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
                smooth_iter = iteration + 1.0 - nu

            result[py, px] = smooth_iter

    return result


@njit(parallel=True, fastmath=True)
def compute_burning_ship_cpu(width: int, height: int,
                              x_min: float, x_max: float,
                              y_min: float, y_max: float,
                              max_iter: int) -> np.ndarray:
    """Compute Burning Ship fractal on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            x0 = x_min + (x_max - x_min) * px / width
            y0 = y_max - (y_max - y_min) * py / height  # Flip Y

            x, y = 0.0, 0.0
            iteration = 0

            while x*x + y*y <= 4.0 and iteration < max_iter:
                # Take absolute values before squaring
                x_new = x*x - y*y + x0
                y = abs(2.0*x*y) + y0
                x = abs(x_new)
                iteration += 1

            # Smooth coloring
            smooth_iter = float(iteration)
            if iteration < max_iter:
                log_zn = np.log(x*x + y*y) / 2.0
                nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
                smooth_iter = iteration + 1.0 - nu

            result[py, px] = smooth_iter

    return result


@njit(parallel=True, fastmath=True)
def compute_tricorn_cpu(width: int, height: int,
                        x_min: float, x_max: float,
                        y_min: float, y_max: float,
                        max_iter: int) -> np.ndarray:
    """Compute Tricorn (Mandelbar) fractal on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            x0 = x_min + (x_max - x_min) * px / width
            y0 = y_max - (y_max - y_min) * py / height

            x, y = 0.0, 0.0
            iteration = 0

            while x*x + y*y <= 4.0 and iteration < max_iter:
                # Use conjugate: (x - iy)^2 + c
                x_new = x*x - y*y + x0
                y = -2.0*x*y + y0  # Negated for conjugate
                x = x_new
                iteration += 1

            # Smooth coloring
            smooth_iter = float(iteration)
            if iteration < max_iter:
                log_zn = np.log(x*x + y*y) / 2.0
                nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
                smooth_iter = iteration + 1.0 - nu

            result[py, px] = smooth_iter

    return result


@njit(parallel=True, fastmath=True)
def compute_phoenix_cpu(width: int, height: int,
                        x_min: float, x_max: float,
                        y_min: float, y_max: float,
                        p_re: float, p_im: float,
                        max_iter: int) -> np.ndarray:
    """Compute Phoenix fractal on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            # For Phoenix, the starting point is the pixel coordinate
            x = x_min + (x_max - x_min) * px / width
            y = y_max - (y_max - y_min) * py / height

            # z(n+1) = z(n)^2 + p_re + p_im * z(n-1)
            prev_x, prev_y = 0.0, 0.0
            iteration = 0

            while x*x + y*y <= 4.0 and iteration < max_iter:
                x_new = x*x - y*y + p_re + p_im * prev_x
                y_new = 2.0*x*y + p_im * prev_y
                prev_x = x
                prev_y = y
                x = x_new
                y = y_new
                iteration += 1

            # Smooth coloring
            smooth_iter = float(iteration)
            if iteration < max_iter:
                log_zn = np.log(x*x + y*y) / 2.0
                nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
                smooth_iter = iteration + 1.0 - nu

            result[py, px] = smooth_iter

    return result


@njit(parallel=True, fastmath=True)
def compute_newton_cpu(width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       max_iter: int,
                       tolerance: float = 1e-6) -> np.ndarray:
    """Compute Newton fractal on CPU with Numba acceleration."""
    result = np.empty((height, width), dtype=np.float32)

    # Roots of z^3 - 1 = 0
    root1_r, root1_i = 1.0, 0.0
    root2_r, root2_i = -0.5, 0.86602540378
    root3_r, root3_i = -0.5, -0.86602540378

    tol2 = tolerance * tolerance

    for py in prange(height):
        for px in range(width):
            zr = x_min + (x_max - x_min) * px / width
            zi = y_max - (y_max - y_min) * py / height

            iteration = 0
            root = 0

            while iteration < max_iter:
                zr2 = zr * zr
                zi2 = zi * zi

                # z^3
                zr3 = zr * zr2 - 3.0 * zr * zi2
                zi3 = 3.0 * zr2 * zi - zi * zi2

                # 3z^2 (denominator)
                denom_r = 3.0 * (zr2 - zi2)
                denom_i = 6.0 * zr * zi
                denom_mag2 = denom_r * denom_r + denom_i * denom_i

                if denom_mag2 < 1e-20:
                    break

                # (z^3 - 1) / (3z^2)
                num_r = zr3 - 1.0
                num_i = zi3

                div_r = (num_r * denom_r + num_i * denom_i) / denom_mag2
                div_i = (num_i * denom_r - num_r * denom_i) / denom_mag2

                zr = zr - div_r
                zi = zi - div_i

                # Check convergence to roots
                d1 = (zr - root1_r)**2 + (zi - root1_i)**2
                d2 = (zr - root2_r)**2 + (zi - root2_i)**2
                d3 = (zr - root3_r)**2 + (zi - root3_i)**2

                if d1 < tol2:
                    root = 1
                    break
                if d2 < tol2:
                    root = 2
                    break
                if d3 < tol2:
                    root = 3
                    break

                iteration += 1

            # Combine root and iteration for coloring
            value = float(root) + float(iteration) / float(max_iter)
            result[py, px] = value

    return result


@njit(parallel=True, fastmath=True)
def compute_orbit_trap_cpu(width: int, height: int,
                            x_min: float, x_max: float,
                            y_min: float, y_max: float,
                            trap_re: float, trap_im: float,
                            trap_radius: float,
                            trap_type: int,  # 0=point, 1=circle, 2=cross, 3=line
                            max_iter: int,
                            is_julia: bool = False,
                            c_re: float = 0.0, c_im: float = 0.0) -> np.ndarray:
    """
    Compute orbit trap minimum distances.

    trap_type: 0=point, 1=circle, 2=cross, 3=line
    """
    result = np.full((height, width), np.inf, dtype=np.float32)

    for py in prange(height):
        for px in range(width):
            if is_julia:
                z_re = x_min + (x_max - x_min) * px / width
                z_im = y_max - (y_max - y_min) * py / height
                cr, ci = c_re, c_im
            else:
                z_re, z_im = 0.0, 0.0
                cr = x_min + (x_max - x_min) * px / width
                ci = y_max - (y_max - y_min) * py / height

            min_dist = 1e10

            for _ in range(max_iter):
                # z = z^2 + c
                z_re_new = z_re * z_re - z_im * z_im + cr
                z_im = 2.0 * z_re * z_im + ci
                z_re = z_re_new

                if z_re * z_re + z_im * z_im > 4.0:
                    break

                # Calculate distance to trap
                dr = z_re - trap_re
                di = z_im - trap_im

                if trap_type == 0:  # point
                    d = np.sqrt(dr * dr + di * di)
                elif trap_type == 1:  # circle
                    dist_to_center = np.sqrt(dr * dr + di * di)
                    d = abs(dist_to_center - trap_radius)
                elif trap_type == 2:  # cross
                    d = min(abs(dr), abs(di))
                else:  # line
                    d = abs(di)

                if d < min_dist:
                    min_dist = d

            result[py, px] = min_dist

    return result


class CPUCompute:
    """CPU-based fractal computation using Numba."""

    def __init__(self):
        self.device_name = "CPU (Numba JIT)"
        # Warm up JIT compilation
        self._warmup()

    def _warmup(self):
        """Warm up JIT compilation with small arrays."""
        compute_mandelbrot_cpu(10, 10, -2, 1, -1.5, 1.5, 10)
        compute_julia_cpu(10, 10, -2, 2, -2, 2, -0.4, 0.6, 10)
        compute_newton_cpu(10, 10, -2, 2, -2, 2, 10)
        compute_burning_ship_cpu(10, 10, -2, 1, -1.5, 1.5, 10)
        compute_tricorn_cpu(10, 10, -2, 1, -1.5, 1.5, 10)
        compute_phoenix_cpu(10, 10, -2, 2, -2, 2, 0.5667, -0.5, 10)
        compute_orbit_trap_cpu(10, 10, -2, 2, -2, 2, 0.0, 0.0, 0.5, 0, 10, False, 0.0, 0.0)

    @staticmethod
    def compute_mandelbrot(width: int, height: int,
                          x_min: float, x_max: float,
                          y_min: float, y_max: float,
                          max_iter: int) -> np.ndarray:
        """Compute Mandelbrot set on CPU."""
        return compute_mandelbrot_cpu(width, height, x_min, x_max, y_min, y_max, max_iter)

    @staticmethod
    def compute_julia(width: int, height: int,
                     x_min: float, x_max: float,
                     y_min: float, y_max: float,
                     c_re: float, c_im: float,
                     max_iter: int) -> np.ndarray:
        """Compute Julia set on CPU."""
        return compute_julia_cpu(width, height, x_min, x_max, y_min, y_max, c_re, c_im, max_iter)

    @staticmethod
    def compute_newton(width: int, height: int,
                      x_min: float, x_max: float,
                      y_min: float, y_max: float,
                      max_iter: int,
                      tolerance: float = 1e-6) -> np.ndarray:
        """Compute Newton fractal on CPU."""
        return compute_newton_cpu(width, height, x_min, x_max, y_min, y_max, max_iter, tolerance)

    @staticmethod
    def compute_burning_ship(width: int, height: int,
                             x_min: float, x_max: float,
                             y_min: float, y_max: float,
                             max_iter: int) -> np.ndarray:
        """Compute Burning Ship fractal on CPU."""
        return compute_burning_ship_cpu(width, height, x_min, x_max, y_min, y_max, max_iter)

    @staticmethod
    def compute_tricorn(width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       max_iter: int) -> np.ndarray:
        """Compute Tricorn fractal on CPU."""
        return compute_tricorn_cpu(width, height, x_min, x_max, y_min, y_max, max_iter)

    @staticmethod
    def compute_phoenix(width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       p_re: float, p_im: float,
                       max_iter: int) -> np.ndarray:
        """Compute Phoenix fractal on CPU."""
        return compute_phoenix_cpu(width, height, x_min, x_max, y_min, y_max, p_re, p_im, max_iter)

    @staticmethod
    def compute_orbit_trap(width: int, height: int,
                           x_min: float, x_max: float,
                           y_min: float, y_max: float,
                           trap_re: float, trap_im: float,
                           trap_radius: float,
                           trap_type: int,
                           max_iter: int,
                           is_julia: bool = False,
                           c_re: float = 0.0, c_im: float = 0.0) -> np.ndarray:
        """Compute orbit trap distances on CPU."""
        return compute_orbit_trap_cpu(
            width, height, x_min, x_max, y_min, y_max,
            trap_re, trap_im, trap_radius, trap_type, max_iter,
            is_julia, c_re, c_im
        )

    @staticmethod
    def to_numpy(array: np.ndarray) -> np.ndarray:
        """Return array as-is (already numpy)."""
        return array

    @staticmethod
    def apply_colormap(iterations: np.ndarray, colormap_lut: np.ndarray, max_iter: int) -> np.ndarray:
        """Apply colormap on CPU."""
        normalized = np.clip(iterations / max_iter, 0, 1)
        indices = (normalized * 255).astype(np.uint8)
        rgba = colormap_lut[indices]
        return rgba
