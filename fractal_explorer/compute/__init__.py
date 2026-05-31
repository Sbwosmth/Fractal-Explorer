"""Compute backends for fractal calculations."""

from .backend import ComputeBackend
from .cpu_fallback import CPUCompute

__all__ = ['ComputeBackend', 'CPUCompute']
