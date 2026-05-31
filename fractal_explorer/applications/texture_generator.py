"""
Fractal Texture Generator - practical application for computer graphics.

Generates seamless tileable textures using fractal algorithms for:
- Terrain heightmaps
- Cloud/smoke effects
- Marble/stone patterns
- Organic textures (wood, bark)
- Abstract artistic patterns
"""

import numpy as np
from typing import Tuple, Optional
from enum import Enum


class TextureType(Enum):
    """Available texture types."""
    TERRAIN = "terrain"
    CLOUDS = "clouds"
    MARBLE = "marble"
    PLASMA = "plasma"
    WOOD = "wood"
    TURBULENCE = "turbulence"
    CELLULAR = "cellular"


def generate_perlin_noise(width: int, height: int,
                          octaves: int = 6,
                          persistence: float = 0.5,
                          seed: int = 42) -> np.ndarray:
    """
    Generate Perlin-like noise using fractal Brownian motion (fBm).

    This is the foundation for most natural-looking textures.

    Args:
        width, height: Output dimensions
        octaves: Number of noise layers (detail levels)
        persistence: How much each octave contributes (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        2D array of noise values normalized to [0, 1]
    """
    rng = np.random.default_rng(seed)
    result = np.zeros((height, width), dtype=np.float64)

    amplitude = 1.0
    total_amplitude = 0.0
    frequency = 1.0

    for octave in range(octaves):
        # Generate base noise at this frequency
        noise_width = max(2, int(width * frequency / 16))
        noise_height = max(2, int(height * frequency / 16))

        # Random gradient grid
        noise = rng.random((noise_height, noise_width))

        # Bicubic interpolation to full size
        from scipy.ndimage import zoom
        try:
            scale_y = height / noise_height
            scale_x = width / noise_width
            interpolated = zoom(noise, (scale_y, scale_x), order=3)

            # Ensure correct size
            interpolated = interpolated[:height, :width]
        except ImportError:
            # Fallback to simple interpolation
            interpolated = _bilinear_interpolate(noise, width, height)

        result += interpolated * amplitude
        total_amplitude += amplitude

        amplitude *= persistence
        frequency *= 2.0

    # Normalize to [0, 1]
    result /= total_amplitude
    return np.clip(result, 0, 1)


def _bilinear_interpolate(data: np.ndarray, width: int, height: int) -> np.ndarray:
    """Simple bilinear interpolation fallback."""
    src_h, src_w = data.shape
    result = np.zeros((height, width), dtype=np.float64)

    for y in range(height):
        for x in range(width):
            src_x = x * (src_w - 1) / max(1, width - 1)
            src_y = y * (src_h - 1) / max(1, height - 1)

            x0, y0 = int(src_x), int(src_y)
            x1, y1 = min(x0 + 1, src_w - 1), min(y0 + 1, src_h - 1)

            fx, fy = src_x - x0, src_y - y0

            result[y, x] = (
                data[y0, x0] * (1 - fx) * (1 - fy) +
                data[y0, x1] * fx * (1 - fy) +
                data[y1, x0] * (1 - fx) * fy +
                data[y1, x1] * fx * fy
            )

    return result


def generate_terrain_heightmap(width: int, height: int,
                                roughness: float = 0.5,
                                seed: int = 42) -> np.ndarray:
    """
    Generate a terrain heightmap using fractal noise.

    Args:
        width, height: Output dimensions
        roughness: Terrain roughness (0=smooth, 1=rough)
        seed: Random seed

    Returns:
        2D heightmap normalized to [0, 1]
    """
    octaves = int(4 + roughness * 4)
    persistence = 0.4 + roughness * 0.2

    heightmap = generate_perlin_noise(width, height, octaves, persistence, seed)

    # Apply power curve for more realistic terrain distribution
    heightmap = np.power(heightmap, 1.0 + roughness * 0.5)

    return heightmap


def generate_cloud_texture(width: int, height: int,
                           density: float = 0.5,
                           seed: int = 42) -> np.ndarray:
    """
    Generate cloud/smoke texture.

    Args:
        width, height: Output dimensions
        density: Cloud density (0=sparse, 1=dense)
        seed: Random seed

    Returns:
        2D texture with alpha-like cloud values [0, 1]
    """
    noise = generate_perlin_noise(width, height, octaves=5,
                                  persistence=0.6, seed=seed)

    # Threshold and smooth for cloud-like appearance
    threshold = 0.3 + (1.0 - density) * 0.3
    clouds = np.clip((noise - threshold) / (1.0 - threshold), 0, 1)

    # Soften edges
    clouds = np.power(clouds, 0.7)

    return clouds


def generate_marble_texture(width: int, height: int,
                            vein_scale: float = 3.0,
                            turbulence: float = 0.5,
                            seed: int = 42) -> np.ndarray:
    """
    Generate marble texture using turbulent sine waves.

    Args:
        width, height: Output dimensions
        vein_scale: Scale of marble veins
        turbulence: Amount of vein distortion
        seed: Random seed

    Returns:
        2D marble texture [0, 1]
    """
    # Base coordinates
    x = np.linspace(0, vein_scale * np.pi, width)
    y = np.linspace(0, vein_scale * np.pi, height)
    X, Y = np.meshgrid(x, y)

    # Turbulence from fractal noise
    noise = generate_perlin_noise(width, height, octaves=4,
                                  persistence=0.5, seed=seed)

    # Distort coordinates with turbulence
    turb_strength = turbulence * 5.0
    marble = np.sin(X + turb_strength * noise)

    # Normalize to [0, 1]
    marble = (marble + 1) / 2

    return marble


def generate_plasma_texture(width: int, height: int,
                            complexity: float = 0.5,
                            seed: int = 42) -> np.ndarray:
    """
    Generate plasma/abstract texture using multiple overlapping sine waves.

    Args:
        width, height: Output dimensions
        complexity: Pattern complexity (0=simple, 1=complex)
        seed: Random seed

    Returns:
        2D plasma texture [0, 1]
    """
    rng = np.random.default_rng(seed)

    x = np.linspace(0, 4 * np.pi, width)
    y = np.linspace(0, 4 * np.pi, height)
    X, Y = np.meshgrid(x, y)

    result = np.zeros((height, width), dtype=np.float64)

    num_waves = int(3 + complexity * 5)
    for _ in range(num_waves):
        freq_x = rng.uniform(0.5, 2.0)
        freq_y = rng.uniform(0.5, 2.0)
        phase = rng.uniform(0, 2 * np.pi)

        result += np.sin(freq_x * X + freq_y * Y + phase)

    # Normalize
    result = (result - result.min()) / (result.max() - result.min() + 1e-10)

    return result


def generate_wood_texture(width: int, height: int,
                          ring_count: int = 10,
                          turbulence: float = 0.3,
                          seed: int = 42) -> np.ndarray:
    """
    Generate wood grain texture.

    Args:
        width, height: Output dimensions
        ring_count: Number of wood rings
        turbulence: Ring distortion amount
        seed: Random seed

    Returns:
        2D wood texture [0, 1]
    """
    # Distance from center
    cx, cy = width / 2, height / 2
    x = np.arange(width) - cx
    y = np.arange(height) - cy
    X, Y = np.meshgrid(x, y)

    dist = np.sqrt(X**2 + Y**2)

    # Add turbulence
    noise = generate_perlin_noise(width, height, octaves=3,
                                  persistence=0.5, seed=seed)
    dist += noise * turbulence * width * 0.1

    # Create rings
    wood = np.sin(dist * ring_count * 2 * np.pi / max(width, height))

    # Normalize
    wood = (wood + 1) / 2

    return wood


def generate_turbulence_texture(width: int, height: int,
                                 intensity: float = 0.5,
                                 seed: int = 42) -> np.ndarray:
    """
    Generate pure turbulence texture (absolute value of noise).

    Args:
        width, height: Output dimensions
        intensity: Turbulence intensity
        seed: Random seed

    Returns:
        2D turbulence texture [0, 1]
    """
    octaves = int(4 + intensity * 4)

    result = np.zeros((height, width), dtype=np.float64)
    amplitude = 1.0
    total = 0.0

    for i in range(octaves):
        noise = generate_perlin_noise(width, height, octaves=1,
                                      persistence=0.5, seed=seed + i)
        # Use absolute value for turbulence effect
        result += np.abs(noise - 0.5) * 2 * amplitude
        total += amplitude
        amplitude *= 0.5

    return result / total


def generate_cellular_texture(width: int, height: int,
                               cell_count: int = 20,
                               seed: int = 42) -> np.ndarray:
    """
    Generate cellular/Voronoi-like texture.

    Args:
        width, height: Output dimensions
        cell_count: Approximate number of cells
        seed: Random seed

    Returns:
        2D cellular texture [0, 1]
    """
    rng = np.random.default_rng(seed)

    # Generate random cell centers
    num_points = cell_count
    points_x = rng.uniform(0, width, num_points)
    points_y = rng.uniform(0, height, num_points)

    # For each pixel, find distance to nearest point
    result = np.zeros((height, width), dtype=np.float64)

    for y in range(height):
        for x in range(width):
            min_dist = float('inf')
            for px, py in zip(points_x, points_y):
                dist = np.sqrt((x - px)**2 + (y - py)**2)
                if dist < min_dist:
                    min_dist = dist
            result[y, x] = min_dist

    # Normalize
    result = result / result.max()

    return result


def apply_colormap_to_texture(texture: np.ndarray,
                              colormap: str = "terrain") -> np.ndarray:
    """
    Apply a colormap to a grayscale texture.

    Args:
        texture: 2D grayscale texture [0, 1]
        colormap: Matplotlib colormap name

    Returns:
        3D RGBA texture array
    """
    try:
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap(colormap)
        rgba = (cmap(texture) * 255).astype(np.uint8)
        return rgba
    except ImportError:
        # Fallback: grayscale
        height, width = texture.shape
        rgba = np.zeros((height, width, 4), dtype=np.uint8)
        gray = (texture * 255).astype(np.uint8)
        rgba[:, :, 0] = gray
        rgba[:, :, 1] = gray
        rgba[:, :, 2] = gray
        rgba[:, :, 3] = 255
        return rgba


def make_seamless(texture: np.ndarray, blend_width: int = None) -> np.ndarray:
    """
    Make a texture seamlessly tileable.

    Args:
        texture: 2D texture array
        blend_width: Width of blending region (default: 1/4 of size)

    Returns:
        Seamlessly tileable texture
    """
    height, width = texture.shape[:2]
    if blend_width is None:
        blend_width = min(width, height) // 4

    result = texture.copy()

    # Blend horizontal edges
    for i in range(blend_width):
        t = i / blend_width
        weight = 0.5 * (1 - np.cos(t * np.pi))

        # Left-right blend
        result[:, i] = texture[:, i] * (1 - weight) + texture[:, width - blend_width + i] * weight
        result[:, width - blend_width + i] = texture[:, width - blend_width + i] * (1 - weight) + texture[:, i] * weight

    # Blend vertical edges
    for i in range(blend_width):
        t = i / blend_width
        weight = 0.5 * (1 - np.cos(t * np.pi))

        # Top-bottom blend
        result[i, :] = result[i, :] * (1 - weight) + result[height - blend_width + i, :] * weight
        result[height - blend_width + i, :] = result[height - blend_width + i, :] * (1 - weight) + result[i, :] * weight

    return result


class TextureGenerator:
    """
    High-level texture generator class for UI integration.
    """

    TEXTURE_TYPES = {
        TextureType.TERRAIN: ("Рельєф місцевості", generate_terrain_heightmap),
        TextureType.CLOUDS: ("Хмари / Дим", generate_cloud_texture),
        TextureType.MARBLE: ("Мармур", generate_marble_texture),
        TextureType.PLASMA: ("Плазма", generate_plasma_texture),
        TextureType.WOOD: ("Дерево", generate_wood_texture),
        TextureType.TURBULENCE: ("Турбулентність", generate_turbulence_texture),
        TextureType.CELLULAR: ("Клітинна структура", generate_cellular_texture),
    }

    COLORMAPS = {
        "terrain": "Рельєф",
        "ocean": "Океан",
        "hot": "Жар",
        "copper": "Мідь",
        "bone": "Кістка",
        "gray": "Сірий",
        "viridis": "Viridis",
        "plasma": "Плазма",
    }

    def __init__(self):
        self._seed = 42
        self._width = 512
        self._height = 512
        self._seamless = True

    def set_seed(self, seed: int):
        self._seed = seed

    def set_size(self, width: int, height: int):
        self._width = width
        self._height = height

    def set_seamless(self, seamless: bool):
        self._seamless = seamless

    def generate(self, texture_type: TextureType,
                 param: float = 0.5,
                 colormap: str = "terrain") -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a texture.

        Args:
            texture_type: Type of texture to generate
            param: Type-specific parameter (0.0-1.0)
            colormap: Colormap to apply

        Returns:
            Tuple of (grayscale_texture, rgba_texture)
        """
        _, generator_func = self.TEXTURE_TYPES[texture_type]

        # Generate grayscale texture
        if texture_type == TextureType.TERRAIN:
            grayscale = generator_func(self._width, self._height, param, self._seed)
        elif texture_type == TextureType.CLOUDS:
            grayscale = generator_func(self._width, self._height, param, self._seed)
        elif texture_type == TextureType.MARBLE:
            grayscale = generator_func(self._width, self._height, 3.0, param, self._seed)
        elif texture_type == TextureType.PLASMA:
            grayscale = generator_func(self._width, self._height, param, self._seed)
        elif texture_type == TextureType.WOOD:
            grayscale = generator_func(self._width, self._height, int(5 + param * 15), param * 0.5, self._seed)
        elif texture_type == TextureType.TURBULENCE:
            grayscale = generator_func(self._width, self._height, param, self._seed)
        elif texture_type == TextureType.CELLULAR:
            grayscale = generator_func(self._width, self._height, int(10 + param * 40), self._seed)
        else:
            grayscale = np.zeros((self._height, self._width))

        # Make seamless if requested
        if self._seamless:
            grayscale = make_seamless(grayscale)

        # Apply colormap
        rgba = apply_colormap_to_texture(grayscale, colormap)

        return grayscale, rgba

    @classmethod
    def get_texture_types(cls) -> dict:
        """Get available texture types with Ukrainian names."""
        return {t: name for t, (name, _) in cls.TEXTURE_TYPES.items()}

    @classmethod
    def get_colormaps(cls) -> dict:
        """Get available colormaps with Ukrainian names."""
        return cls.COLORMAPS
