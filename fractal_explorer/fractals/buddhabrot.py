"""
Buddhabrot fractal - alternative Mandelbrot visualization.

ЩО ТАКЕ БУДДАБРОТ?
==================
Буддаброт — це НЕ звичайний фрактал і НЕ туманність!

Як працює звичайний Мандельброт:
- Для кожної точки c перевіряємо, чи втікає послідовність z = z² + c
- Колір = кількість ітерацій до втечі
- Точки всередині множини — чорні

Як працює Буддаброт:
- Беремо ТІЛЬКИ точки, які ВТІКАЮТЬ (не в множині!)
- Для кожної такої точки малюємо ВСЮ її орбіту (траєкторію)
- Рахуємо, скільки орбіт проходить через кожен піксель
- Яскравість = густота орбіт

Результат нагадує фігуру Будди в медитації — звідси назва.
Це як "рентген" множини Мандельброта, що показує приховану структуру.

Відкрито Меліндою Грін у 1993 році.
"""

import numpy as np
from .base import BaseFractal, FractalDefaults


class BuddhabrotFractal(BaseFractal):
    """
    Buddhabrot rendering of the Mandelbrot set.

    Instead of coloring by escape iteration, traces the orbits of
    ESCAPING points and accumulates a density map of visited locations.
    The result resembles a meditating Buddha figure.

    Key insight: We trace orbits ONLY for points OUTSIDE the Mandelbrot set.
    Then we count how many times each pixel is visited by these orbits.
    High density = bright, low density = dark.

    Discovered by Melinda Green in 1993.
    """

    name = "Buddhabrot"
    defaults = FractalDefaults(
        center_re=-0.3,
        center_im=0.0,
        scale=3.5,
        max_iterations=200
    )

    def __init__(self, compute_backend):
        super().__init__(compute_backend)
        self._params['num_samples'] = 500000

    def is_iterative(self) -> bool:
        return False

    def compute(self, width: int, height: int,
               x_min: float, x_max: float,
               y_min: float, y_max: float,
               max_iter: int) -> np.ndarray:
        """Compute Buddhabrot density map."""
        num_samples = self._params.get('num_samples', 500000)
        return _compute_buddhabrot(
            width, height, x_min, x_max, y_min, y_max,
            max_iter, num_samples
        )


def _compute_buddhabrot(width, height, x_min, x_max, y_min, y_max,
                        max_iter, num_samples):
    """Compute Buddhabrot density map using random sampling."""
    result = np.zeros((height, width), dtype=np.float32)

    rng = np.random.default_rng(42)

    # Sample random points in the complex plane
    c_re = rng.uniform(x_min, x_max, num_samples).astype(np.float64)
    c_im = rng.uniform(y_min, y_max, num_samples).astype(np.float64)

    for s in range(num_samples):
        cr, ci = c_re[s], c_im[s]

        # Quick cardioid/bulb check to skip points inside the set
        q = (cr - 0.25) ** 2 + ci ** 2
        if q * (q + (cr - 0.25)) < 0.25 * ci ** 2:
            continue
        if (cr + 1) ** 2 + ci ** 2 < 0.0625:
            continue

        # First pass: check if point escapes
        zr, zi = 0.0, 0.0
        escaped = False
        for i in range(max_iter):
            zr_new = zr * zr - zi * zi + cr
            zi = 2.0 * zr * zi + ci
            zr = zr_new
            if zr * zr + zi * zi > 4.0:
                escaped = True
                break

        if not escaped:
            continue

        # Second pass: trace orbit and accumulate
        zr, zi = 0.0, 0.0
        for i in range(max_iter):
            zr_new = zr * zr - zi * zi + cr
            zi = 2.0 * zr * zi + ci
            zr = zr_new

            if zr * zr + zi * zi > 4.0:
                break

            # Map orbit point to pixel
            px = int((zr - x_min) / (x_max - x_min) * width)
            py = int((y_max - zi) / (y_max - y_min) * height)

            if 0 <= px < width and 0 <= py < height:
                result[py, px] += 1.0

    # Log-scale normalization
    result = np.log1p(result)
    max_val = result.max()
    if max_val > 0:
        result = result / max_val * 255.0

    return result
