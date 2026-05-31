"""
Base class for fractal implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np


@dataclass
class FractalDefaults:
    """Default parameters for a fractal type."""
    center_re: float
    center_im: float
    scale: float
    max_iterations: int


class BaseFractal(ABC):
    """Abstract base class for all fractal types."""

    # Override in subclasses
    name: str = "Base Fractal"
    defaults: FractalDefaults = FractalDefaults(0.0, 0.0, 3.0, 200)

    def __init__(self, compute_backend):
        """
        Initialize fractal with a compute backend.

        Args:
            compute_backend: ComputeBackend instance for GPU/CPU computation
        """
        self.backend = compute_backend
        self._params: Dict[str, Any] = {}

    @abstractmethod
    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """
        Compute the fractal iteration data.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            x_min, x_max: Real axis bounds
            y_min, y_max: Imaginary axis bounds
            max_iter: Maximum iterations

        Returns:
            2D numpy array of iteration counts (float32 for smooth coloring)
        """
        pass

    def get_param(self, name: str, default: Any = None) -> Any:
        """Get a fractal-specific parameter."""
        return self._params.get(name, default)

    def set_param(self, name: str, value: Any):
        """Set a fractal-specific parameter."""
        self._params[name] = value

    def get_params(self) -> Dict[str, Any]:
        """Get all fractal-specific parameters."""
        return self._params.copy()

    def set_params(self, params: Dict[str, Any]):
        """Set multiple parameters at once."""
        self._params.update(params)

    def reset_params(self):
        """Reset parameters to defaults."""
        self._params.clear()

    @classmethod
    def get_default_viewport(cls) -> tuple:
        """Get default viewport parameters (center_re, center_im, scale)."""
        return (cls.defaults.center_re, cls.defaults.center_im, cls.defaults.scale)

    @classmethod
    def get_default_iterations(cls) -> int:
        """Get default maximum iterations."""
        return cls.defaults.max_iterations

    def is_iterative(self) -> bool:
        """Return True if this fractal uses iteration-based computation."""
        return True
