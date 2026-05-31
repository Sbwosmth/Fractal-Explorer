"""
Colormap handling for fractal visualization.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class ColorMapper:
    """
    Manages colormaps for fractal rendering.

    Uses matplotlib colormaps for professional color palettes.
    """

    # Available colormap names (ordered by quality for fractals)
    # Best perceptually uniform and cyclic colormaps first
    COLORMAPS = [
        # Cyclic - perfect for infinite zoom illusion
        "twilight",
        "twilight_shifted",
        "hsv",
        # Perceptually uniform - scientific quality
        "viridis",
        "plasma",
        "magma",
        "inferno",
        "cividis",
        # High contrast artistic
        "turbo",
        "cubehelix",
        # Classic
        "hot",
        "copper",
        "ocean",
        "terrain",
    ]

    def __init__(self, colormap_name: str = "twilight"):
        """
        Initialize the color mapper.

        Args:
            colormap_name: Name of the colormap to use
        """
        self._cmap_name = colormap_name
        self._lut: Optional[np.ndarray] = None
        self._lut_cache: Dict[str, np.ndarray] = {}
        self._load_colormap(colormap_name)

    def _load_colormap(self, name: str):
        """Load a colormap and create lookup table."""
        if name in self._lut_cache:
            self._lut = self._lut_cache[name]
            self._cmap_name = name
            return

        try:
            import matplotlib.pyplot as plt
            cmap = plt.get_cmap(name)
            # Create 256-entry LUT (RGBA)
            self._lut = (cmap(np.linspace(0, 1, 256)) * 255).astype(np.uint8)
        except ImportError:
            # Fallback to built-in gradient if matplotlib unavailable
            self._lut = self._create_fallback_lut(name)

        self._lut_cache[name] = self._lut
        self._cmap_name = name

    def _create_fallback_lut(self, name: str) -> np.ndarray:
        """Create a fallback LUT without matplotlib."""
        lut = np.zeros((256, 4), dtype=np.uint8)

        if name == "hot":
            for i in range(256):
                t = i / 255.0
                r = min(1.0, t * 3)
                g = max(0, min(1.0, t * 3 - 1))
                b = max(0, t * 3 - 2)
                lut[i] = [int(r*255), int(g*255), int(b*255), 255]
        elif name == "cool":
            for i in range(256):
                t = i / 255.0
                lut[i] = [int(t*255), int((1-t)*255), 255, 255]
        else:
            # Default: grayscale
            for i in range(256):
                lut[i] = [i, i, i, 255]

        return lut

    def set_colormap(self, name: str):
        """Change the active colormap."""
        if name not in self.COLORMAPS:
            name = "twilight"
        self._load_colormap(name)

    def get_colormap_name(self) -> str:
        """Get the current colormap name."""
        return self._cmap_name

    def get_lut(self) -> np.ndarray:
        """Get the current lookup table (256x4 RGBA)."""
        return self._lut

    def apply(self, iterations: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Apply colormap to iteration data with smooth coloring.

        Args:
            iterations: 2D array of iteration counts (float32)
            max_iter: Maximum iterations used

        Returns:
            3D RGBA array (height, width, 4) uint8
        """
        # Use log-periodic coloring for smoother gradients
        # This creates repeating color cycles at different zoom levels
        # giving the illusion of infinite detail

        # Mask for points in the set (iterations == max_iter)
        in_set = iterations >= max_iter

        # Smooth coloring: use log of iterations for better gradient
        # Add small epsilon to avoid log(0)
        smooth_iter = np.where(
            in_set,
            0.0,
            np.log(iterations + 1.0) / np.log(max_iter + 1.0)
        )

        # Apply color cycling for zoom effect (repeats every ~50 iterations visible)
        # This creates banding that looks smooth at any zoom level
        cyclic_factor = 3.0  # Number of color cycles
        cyclic = np.mod(smooth_iter * cyclic_factor, 1.0)

        # Map to LUT indices [0, 255]
        indices = (cyclic * 255).astype(np.uint8)

        # Apply lookup table
        rgba = self._lut[indices].copy()

        # Points in the set are black
        rgba[in_set] = [0, 0, 0, 255]

        return rgba

    def apply_newton(self, data: np.ndarray, max_iter: int) -> np.ndarray:
        """
        Apply coloring for Newton fractal using selected colormap.

        Newton fractal data encodes both root (integer part) and
        iteration count (fractional part).

        Args:
            data: 2D array with root + iterations/max_iter
            max_iter: Maximum iterations

        Returns:
            3D RGBA array
        """
        height, width = data.shape
        rgba = np.zeros((height, width, 4), dtype=np.uint8)

        # Extract root and iteration info
        roots = np.floor(data).astype(int)
        iter_frac = data - roots

        # Use colormap for each root, offset by 1/3 of the colormap
        # This creates distinct but harmonious colors from the selected palette
        for root_id in range(4):
            mask = (roots == root_id)
            if not np.any(mask):
                continue

            if root_id == 0:
                # No convergence - dark
                rgba[mask] = [20, 20, 25, 255]
            else:
                # Map each root to a different section of the colormap
                # Root 1 -> 0-85, Root 2 -> 85-170, Root 3 -> 170-255
                base_index = (root_id - 1) * 85

                # Vary within that section based on iteration count
                iter_vals = iter_frac[mask]
                # Use log scale for smoother gradients
                brightness = np.power(1.0 - iter_vals, 0.6)
                indices = (base_index + brightness * 84).astype(np.uint8)

                rgba[mask] = self._lut[indices]

        return rgba

    def apply_tree(self, data: np.ndarray, max_depth: int) -> np.ndarray:
        """
        Apply coloring for Pythagoras tree using selected colormap.

        Args:
            data: 2D array with depth values
            max_depth: Maximum depth (actually used as max_depth parameter)

        Returns:
            3D RGBA array
        """
        height, width = data.shape
        rgba = np.zeros((height, width, 4), dtype=np.uint8)

        # Background
        rgba[:, :, 3] = 255  # Full alpha

        # Color squares by depth using the selected colormap
        mask = data > 0

        # Normalize depth
        # Use actual depth values from the tree (1 to max_depth)
        actual_max = max(data.max(), 1)
        normalized = np.clip(data / actual_max, 0, 1)

        # Apply colormap to tree pixels
        indices = (normalized * 255).astype(np.uint8)
        rgba[mask] = self._lut[indices[mask]]

        # Dark background
        bg_mask = ~mask
        rgba[bg_mask] = [15, 18, 25, 255]

        return rgba

    def apply_ifs(self, density: np.ndarray) -> np.ndarray:
        """
        Apply coloring for IFS/density-based fractals.

        Args:
            density: 2D array of density values (already 0-255 normalized)

        Returns:
            3D RGBA array
        """
        height, width = density.shape
        rgba = np.zeros((height, width, 4), dtype=np.uint8)

        # Background
        rgba[:, :, 3] = 255

        # Use density as colormap index
        indices = np.clip(density, 0, 255).astype(np.uint8)
        rgba = self._lut[indices].copy()

        # Dark background for zero-density areas
        bg_mask = density < 1.0
        rgba[bg_mask] = [15, 18, 25, 255]

        return rgba

    def get_preview(self, width: int = 256, height: int = 20) -> np.ndarray:
        """
        Generate a colormap preview image.

        Args:
            width: Preview width
            height: Preview height

        Returns:
            RGBA array of the preview
        """
        gradient = np.linspace(0, 255, width).astype(np.uint8)
        gradient = np.tile(gradient, (height, 1))
        return self._lut[gradient]

    @classmethod
    def get_available_colormaps(cls) -> List[str]:
        """Get list of available colormap names."""
        return cls.COLORMAPS.copy()


class OrbitTrapColorMapper:
    """
    Orbit trap coloring for fractals.

    Colors pixels based on minimum distance from orbit to trap objects
    instead of iteration count.
    """

    # Available trap types
    TRAP_TYPES = ["point", "circle", "cross", "line"]

    def __init__(self, trap_type: str = "point", colormap_name: str = "twilight"):
        """
        Initialize orbit trap color mapper.

        Args:
            trap_type: Type of trap ("point", "circle", "cross", "line")
            colormap_name: Colormap name for coloring
        """
        self._trap_type = trap_type
        self._color_mapper = ColorMapper(colormap_name)

        # Trap parameters
        self._trap_center_re = 0.0
        self._trap_center_im = 0.0
        self._trap_radius = 0.5  # For circle trap

    def set_trap_type(self, trap_type: str):
        """Set the trap type."""
        if trap_type in self.TRAP_TYPES:
            self._trap_type = trap_type

    def get_trap_type(self) -> str:
        """Get current trap type."""
        return self._trap_type

    def set_trap_center(self, re: float, im: float):
        """Set trap center position."""
        self._trap_center_re = re
        self._trap_center_im = im

    def set_trap_radius(self, radius: float):
        """Set trap radius (for circle trap)."""
        self._trap_radius = max(0.01, radius)

    def set_colormap(self, name: str):
        """Set the colormap."""
        self._color_mapper.set_colormap(name)

    def _distance_point(self, z_re: float, z_im: float) -> float:
        """Distance from z to point trap."""
        dr = z_re - self._trap_center_re
        di = z_im - self._trap_center_im
        return np.sqrt(dr * dr + di * di)

    def _distance_circle(self, z_re: float, z_im: float) -> float:
        """Distance from z to circle trap (distance to circle edge)."""
        dr = z_re - self._trap_center_re
        di = z_im - self._trap_center_im
        dist_to_center = np.sqrt(dr * dr + di * di)
        return np.abs(dist_to_center - self._trap_radius)

    def _distance_cross(self, z_re: float, z_im: float) -> float:
        """Distance from z to cross trap (vertical + horizontal lines through center)."""
        dist_to_vertical = np.abs(z_re - self._trap_center_re)
        dist_to_horizontal = np.abs(z_im - self._trap_center_im)
        return np.minimum(dist_to_vertical, dist_to_horizontal)

    def _distance_line(self, z_re: float, z_im: float) -> float:
        """Distance from z to horizontal line trap."""
        return np.abs(z_im - self._trap_center_im)

    def compute_orbit_trap_data(self,
                                 width: int, height: int,
                                 x_min: float, x_max: float,
                                 y_min: float, y_max: float,
                                 max_iter: int,
                                 fractal_type: str = "mandelbrot",
                                 c_re: float = 0.0, c_im: float = 0.0) -> np.ndarray:
        """
        Compute minimum orbit distances to trap.

        Args:
            width, height: Output dimensions
            x_min, x_max, y_min, y_max: Viewport bounds
            max_iter: Maximum iterations
            fractal_type: "mandelbrot" or "julia"
            c_re, c_im: Julia constant (for Julia set)

        Returns:
            2D array of minimum distances (float32)
        """
        result = np.full((height, width), np.inf, dtype=np.float32)

        # Select distance function
        if self._trap_type == "point":
            dist_func = self._distance_point
        elif self._trap_type == "circle":
            dist_func = self._distance_circle
        elif self._trap_type == "cross":
            dist_func = self._distance_cross
        else:  # line
            dist_func = self._distance_line

        # Generate coordinate grids
        x_coords = np.linspace(x_min, x_max, width)
        y_coords = np.linspace(y_max, y_min, height)  # Flip Y

        for py in range(height):
            for px in range(width):
                if fractal_type == "julia":
                    z_re = x_coords[px]
                    z_im = y_coords[py]
                    cr, ci = c_re, c_im
                else:  # mandelbrot
                    z_re, z_im = 0.0, 0.0
                    cr = x_coords[px]
                    ci = y_coords[py]

                min_dist = np.inf

                for _ in range(max_iter):
                    # z = z^2 + c
                    z_re_new = z_re * z_re - z_im * z_im + cr
                    z_im = 2.0 * z_re * z_im + ci
                    z_re = z_re_new

                    if z_re * z_re + z_im * z_im > 4.0:
                        break

                    # Calculate distance to trap
                    d = dist_func(z_re, z_im)
                    if d < min_dist:
                        min_dist = d

                result[py, px] = min_dist

        return result

    def apply(self, distances: np.ndarray, max_distance: float = 2.0) -> np.ndarray:
        """
        Apply coloring based on orbit trap distances.

        Args:
            distances: 2D array of minimum distances
            max_distance: Maximum distance for normalization

        Returns:
            3D RGBA array
        """
        # Normalize distances
        normalized = np.clip(distances / max_distance, 0, 1)

        # Apply log scaling for better contrast
        normalized = np.log(normalized + 0.01) / np.log(1.01)
        normalized = 1.0 - np.clip(normalized, 0, 1)

        # Map to colormap
        lut = self._color_mapper.get_lut()
        indices = (normalized * 255).astype(np.uint8)

        return lut[indices]

    @classmethod
    def get_available_trap_types(cls) -> List[str]:
        """Get list of available trap types."""
        return cls.TRAP_TYPES.copy()
