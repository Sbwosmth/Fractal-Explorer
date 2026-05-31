"""
Compute backend with automatic GPU/CPU selection.
"""

import numpy as np
from typing import Optional


class ComputeBackend:
    """
    Compute backend that automatically selects GPU or CPU.

    Tries to use GPU (CuPy/CUDA) first, falls back to CPU (Numba) if unavailable.
    """

    def __init__(self):
        self.use_gpu = False
        self.device_name = "CPU"
        self._gpu_compute = None
        self._cpu_compute = None
        self._gpu_status_reason = ""

        # Try to initialize GPU backend
        try:
            from .gpu_kernels import GPUCompute, GPU_AVAILABLE
            if GPU_AVAILABLE:
                self._gpu_compute = GPUCompute()
                # Test that GPU actually works by doing a simple computation
                import cupy as cp
                test_arr = cp.array([1, 2, 3])
                _ = cp.asnumpy(test_arr * 2)
                self.use_gpu = True
                self.device_name = f"GPU ({self._gpu_compute.device_name})"
                self._gpu_status_reason = "CUDA прискорення активне!"
            else:
                self._gpu_status_reason = "CuPy не встановлено (pip install cupy-cuda12x)"
        except ImportError as e:
            self._gpu_status_reason = f"CuPy не знайдено: pip install cupy-cuda12x"
        except RuntimeError as e:
            error_msg = str(e)
            if 'nvrtc' in error_msg.lower() or 'dll' in error_msg.lower():
                self._gpu_status_reason = (
                    "CUDA 12 бібліотеки не знайдено!\n"
                    "Встановіть CUDA Toolkit 12.x з nvidia.com/cuda-downloads"
                )
            else:
                self._gpu_status_reason = f"GPU помилка: {error_msg[:80]}"
        except Exception as e:
            self._gpu_status_reason = f"GPU помилка: {str(e)[:80]}"

        # Always initialize CPU backend as fallback
        from .cpu_fallback import CPUCompute
        self._cpu_compute = CPUCompute()

        if not self.use_gpu:
            self.device_name = self._cpu_compute.device_name

    @property
    def compute(self):
        """Get the active compute implementation."""
        if self.use_gpu and self._gpu_compute is not None:
            return self._gpu_compute
        return self._cpu_compute

    def set_gpu_mode(self, enabled: bool):
        """Manually enable or disable GPU mode."""
        if enabled and self._gpu_compute is not None:
            self.use_gpu = True
            self.device_name = f"GPU ({self._gpu_compute.device_name})"
        else:
            self.use_gpu = False
            self.device_name = self._cpu_compute.device_name

    def compute_mandelbrot(self, width: int, height: int,
                          x_min: float, x_max: float,
                          y_min: float, y_max: float,
                          max_iter: int) -> np.ndarray:
        """Compute Mandelbrot set."""
        result = self.compute.compute_mandelbrot(
            width, height, x_min, x_max, y_min, y_max, max_iter
        )
        return self.compute.to_numpy(result)

    def compute_julia(self, width: int, height: int,
                     x_min: float, x_max: float,
                     y_min: float, y_max: float,
                     c_re: float, c_im: float,
                     max_iter: int) -> np.ndarray:
        """Compute Julia set."""
        result = self.compute.compute_julia(
            width, height, x_min, x_max, y_min, y_max, c_re, c_im, max_iter
        )
        return self.compute.to_numpy(result)

    def compute_newton(self, width: int, height: int,
                      x_min: float, x_max: float,
                      y_min: float, y_max: float,
                      max_iter: int,
                      tolerance: float = 1e-6) -> np.ndarray:
        """Compute Newton fractal."""
        result = self.compute.compute_newton(
            width, height, x_min, x_max, y_min, y_max, max_iter, tolerance
        )
        return self.compute.to_numpy(result)

    def compute_burning_ship(self, width: int, height: int,
                             x_min: float, x_max: float,
                             y_min: float, y_max: float,
                             max_iter: int) -> np.ndarray:
        """Compute Burning Ship fractal."""
        result = self.compute.compute_burning_ship(
            width, height, x_min, x_max, y_min, y_max, max_iter
        )
        return self.compute.to_numpy(result)

    def compute_tricorn(self, width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       max_iter: int) -> np.ndarray:
        """Compute Tricorn fractal."""
        result = self.compute.compute_tricorn(
            width, height, x_min, x_max, y_min, y_max, max_iter
        )
        return self.compute.to_numpy(result)

    def compute_phoenix(self, width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       p_re: float, p_im: float,
                       max_iter: int) -> np.ndarray:
        """Compute Phoenix fractal."""
        result = self.compute.compute_phoenix(
            width, height, x_min, x_max, y_min, y_max, p_re, p_im, max_iter
        )
        return self.compute.to_numpy(result)

    def apply_colormap(self, iterations: np.ndarray,
                      colormap_lut: np.ndarray,
                      max_iter: int) -> np.ndarray:
        """Apply colormap to iteration data."""
        if self.use_gpu and self._gpu_compute is not None:
            try:
                import cupy as cp
                iterations_gpu = cp.asarray(iterations)
                colormap_lut_gpu = cp.asarray(colormap_lut)
                return self._gpu_compute.apply_colormap(
                    iterations_gpu, colormap_lut_gpu, max_iter
                )
            except Exception:
                pass

        return self._cpu_compute.apply_colormap(iterations, colormap_lut, max_iter)

    def get_status(self) -> str:
        """Get human-readable status string."""
        mode = "GPU" if self.use_gpu else "CPU"
        return f"{mode}: {self.device_name}"

    def get_detailed_status(self) -> dict:
        """Get detailed status information about compute backend."""
        return {
            'use_gpu': self.use_gpu,
            'device_name': self.device_name,
            'gpu_reason': self._gpu_status_reason,
            'gpu_available': self._gpu_compute is not None,
        }

    def is_gpu_available(self) -> bool:
        """Check if GPU backend is available."""
        return self._gpu_compute is not None
