"""Fractal implementations."""

from .base import BaseFractal
from .mandelbrot import MandelbrotFractal
from .julia import JuliaFractal
from .newton import NewtonFractal
from .pythagoras_tree import PythagorasTreeFractal
from .burning_ship import BurningShipFractal
from .tricorn import TricornFractal
from .phoenix import PhoenixFractal
from .barnsley_fern import BarnsleyFernFractal
from .sierpinski import SierpinskiFractal
from .koch import KochSnowflakeFractal
from .buddhabrot import BuddhabrotFractal

__all__ = [
    'BaseFractal',
    'MandelbrotFractal',
    'JuliaFractal',
    'NewtonFractal',
    'PythagorasTreeFractal',
    'BurningShipFractal',
    'TricornFractal',
    'PhoenixFractal',
    'BarnsleyFernFractal',
    'SierpinskiFractal',
    'KochSnowflakeFractal',
    'BuddhabrotFractal',
]
