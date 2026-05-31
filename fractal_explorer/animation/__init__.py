"""Animation module for Fractal Explorer."""

from .animation_types import (
    AnimationBase, AnimationState,
    ZoomAnimation, JuliaOrbitAnimation, MorphAnimation, PhoenixOrbitAnimation
)
from .animation_engine import AnimationEngine
from .frame_exporter import FrameExporter
from .video_encoder import VideoEncoder

__all__ = [
    'AnimationBase',
    'AnimationState',
    'ZoomAnimation',
    'JuliaOrbitAnimation',
    'MorphAnimation',
    'PhoenixOrbitAnimation',
    'AnimationEngine',
    'FrameExporter',
    'VideoEncoder',
]
