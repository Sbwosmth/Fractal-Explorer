"""
Animation type definitions for fractal animations.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, Callable


@dataclass
class AnimationState:
    """State of the animation at a given frame."""
    center_re: float
    center_im: float
    scale: float
    # Optional parameters for specific fractal types
    julia_c_re: Optional[float] = None
    julia_c_im: Optional[float] = None
    phoenix_p_re: Optional[float] = None
    phoenix_p_im: Optional[float] = None


class AnimationBase(ABC):
    """Base class for all animation types."""

    def __init__(self, duration_seconds: float, fps: int = 30):
        """
        Initialize animation.

        Args:
            duration_seconds: Total animation duration in seconds
            fps: Frames per second
        """
        self.duration = duration_seconds
        self.fps = fps
        self.total_frames = int(duration_seconds * fps)

    @abstractmethod
    def get_state(self, frame: int) -> AnimationState:
        """
        Get the animation state for a given frame.

        Args:
            frame: Frame number (0 to total_frames-1)

        Returns:
            AnimationState for this frame
        """
        pass

    def get_progress(self, frame: int) -> float:
        """Get animation progress as value from 0 to 1."""
        if self.total_frames <= 1:
            return 1.0
        return frame / (self.total_frames - 1)


class ZoomAnimation(AnimationBase):
    """
    Deep zoom animation toward a target point.

    Uses exponential interpolation for smooth zoom effect.
    """

    def __init__(self,
                 start_center_re: float,
                 start_center_im: float,
                 start_scale: float,
                 target_re: float,
                 target_im: float,
                 end_scale: float,
                 duration_seconds: float,
                 fps: int = 30,
                 ease_function: Optional[Callable[[float], float]] = None):
        """
        Initialize zoom animation.

        Args:
            start_center_re, start_center_im: Starting center coordinates
            start_scale: Starting viewport scale
            target_re, target_im: Target center coordinates to zoom into
            end_scale: Final viewport scale (smaller = more zoomed in)
            duration_seconds: Animation duration
            fps: Frames per second
            ease_function: Optional easing function (takes 0-1, returns 0-1)
        """
        super().__init__(duration_seconds, fps)
        self.start_center_re = start_center_re
        self.start_center_im = start_center_im
        self.start_scale = start_scale
        self.target_re = target_re
        self.target_im = target_im
        self.end_scale = end_scale
        self.ease_function = ease_function or self._ease_in_out_cubic

    @staticmethod
    def _ease_in_out_cubic(t: float) -> float:
        """Smooth ease-in-out cubic function."""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2

    def get_state(self, frame: int) -> AnimationState:
        """Get state for a given frame."""
        t = self.get_progress(frame)
        eased_t = self.ease_function(t)

        # Linear interpolation for center
        center_re = self.start_center_re + (self.target_re - self.start_center_re) * eased_t
        center_im = self.start_center_im + (self.target_im - self.start_center_im) * eased_t

        # Exponential interpolation for scale (smoother zoom)
        log_start = math.log(self.start_scale)
        log_end = math.log(self.end_scale)
        scale = math.exp(log_start + (log_end - log_start) * eased_t)

        return AnimationState(
            center_re=center_re,
            center_im=center_im,
            scale=scale
        )


class JuliaOrbitAnimation(AnimationBase):
    """
    Animation where the Julia c parameter moves along a path.

    Can create circular, elliptical, or custom path animations.
    """

    def __init__(self,
                 center_re: float,
                 center_im: float,
                 scale: float,
                 c_center_re: float,
                 c_center_im: float,
                 c_radius: float,
                 duration_seconds: float,
                 fps: int = 30,
                 orbits: float = 1.0,
                 ellipse_ratio: float = 1.0):
        """
        Initialize Julia orbit animation.

        Args:
            center_re, center_im: Viewport center (fixed)
            scale: Viewport scale (fixed)
            c_center_re, c_center_im: Center of the c parameter orbit
            c_radius: Radius of the c parameter orbit
            duration_seconds: Animation duration
            fps: Frames per second
            orbits: Number of complete orbits
            ellipse_ratio: Ratio for elliptical orbits (1.0 = circle)
        """
        super().__init__(duration_seconds, fps)
        self.center_re = center_re
        self.center_im = center_im
        self.scale = scale
        self.c_center_re = c_center_re
        self.c_center_im = c_center_im
        self.c_radius = c_radius
        self.orbits = orbits
        self.ellipse_ratio = ellipse_ratio

    def get_state(self, frame: int) -> AnimationState:
        """Get state for a given frame."""
        t = self.get_progress(frame)
        angle = 2 * math.pi * self.orbits * t

        c_re = self.c_center_re + self.c_radius * math.cos(angle)
        c_im = self.c_center_im + self.c_radius * self.ellipse_ratio * math.sin(angle)

        return AnimationState(
            center_re=self.center_re,
            center_im=self.center_im,
            scale=self.scale,
            julia_c_re=c_re,
            julia_c_im=c_im
        )


class MorphAnimation(AnimationBase):
    """
    Smooth transition (morph) between two viewport states.

    Can be used for smooth panning, zooming, or combined transitions.
    """

    def __init__(self,
                 start_state: AnimationState,
                 end_state: AnimationState,
                 duration_seconds: float,
                 fps: int = 30,
                 use_exponential_scale: bool = True):
        """
        Initialize morph animation.

        Args:
            start_state: Starting animation state
            end_state: Ending animation state
            duration_seconds: Animation duration
            fps: Frames per second
            use_exponential_scale: Use exponential interpolation for scale
        """
        super().__init__(duration_seconds, fps)
        self.start_state = start_state
        self.end_state = end_state
        self.use_exponential_scale = use_exponential_scale

    @staticmethod
    def _ease_in_out_sine(t: float) -> float:
        """Smooth ease-in-out sine function."""
        return -(math.cos(math.pi * t) - 1) / 2

    def _lerp(self, start: Optional[float], end: Optional[float], t: float) -> Optional[float]:
        """Linear interpolation with None handling."""
        if start is None or end is None:
            return end
        return start + (end - start) * t

    def get_state(self, frame: int) -> AnimationState:
        """Get state for a given frame."""
        t = self.get_progress(frame)
        eased_t = self._ease_in_out_sine(t)

        # Linear interpolation for center
        center_re = self._lerp(self.start_state.center_re, self.end_state.center_re, eased_t)
        center_im = self._lerp(self.start_state.center_im, self.end_state.center_im, eased_t)

        # Scale interpolation
        if self.use_exponential_scale:
            log_start = math.log(self.start_state.scale)
            log_end = math.log(self.end_state.scale)
            scale = math.exp(log_start + (log_end - log_start) * eased_t)
        else:
            scale = self._lerp(self.start_state.scale, self.end_state.scale, eased_t)

        # Optional parameter interpolation
        julia_c_re = self._lerp(self.start_state.julia_c_re, self.end_state.julia_c_re, eased_t)
        julia_c_im = self._lerp(self.start_state.julia_c_im, self.end_state.julia_c_im, eased_t)
        phoenix_p_re = self._lerp(self.start_state.phoenix_p_re, self.end_state.phoenix_p_re, eased_t)
        phoenix_p_im = self._lerp(self.start_state.phoenix_p_im, self.end_state.phoenix_p_im, eased_t)

        return AnimationState(
            center_re=center_re,
            center_im=center_im,
            scale=scale,
            julia_c_re=julia_c_re,
            julia_c_im=julia_c_im,
            phoenix_p_re=phoenix_p_re,
            phoenix_p_im=phoenix_p_im
        )


class PhoenixOrbitAnimation(AnimationBase):
    """
    Animation where the Phoenix p parameter moves along a path.
    """

    def __init__(self,
                 center_re: float,
                 center_im: float,
                 scale: float,
                 p_center_re: float,
                 p_center_im: float,
                 p_radius: float,
                 duration_seconds: float,
                 fps: int = 30,
                 orbits: float = 1.0):
        """
        Initialize Phoenix orbit animation.

        Args:
            center_re, center_im: Viewport center (fixed)
            scale: Viewport scale (fixed)
            p_center_re, p_center_im: Center of the p parameter orbit
            p_radius: Radius of the p parameter orbit
            duration_seconds: Animation duration
            fps: Frames per second
            orbits: Number of complete orbits
        """
        super().__init__(duration_seconds, fps)
        self.center_re = center_re
        self.center_im = center_im
        self.scale = scale
        self.p_center_re = p_center_re
        self.p_center_im = p_center_im
        self.p_radius = p_radius
        self.orbits = orbits

    def get_state(self, frame: int) -> AnimationState:
        """Get state for a given frame."""
        t = self.get_progress(frame)
        angle = 2 * math.pi * self.orbits * t

        p_re = self.p_center_re + self.p_radius * math.cos(angle)
        p_im = self.p_center_im + self.p_radius * math.sin(angle * 0.7)  # Lissajous-like

        return AnimationState(
            center_re=self.center_re,
            center_im=self.center_im,
            scale=self.scale,
            phoenix_p_re=p_re,
            phoenix_p_im=p_im
        )
