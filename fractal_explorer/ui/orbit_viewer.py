"""
Orbit visualization - shows iteration trajectory for a clicked point.

WHAT IS AN ORBIT?
In fractal mathematics, an "orbit" is the sequence of values z₀, z₁, z₂, ...
produced by repeatedly applying the iteration formula.

For Mandelbrot: z_{n+1} = z_n² + c
Starting from z₀ = 0, the orbit shows where each iteration "lands".

- If the orbit stays bounded (near origin) → point is IN the set (black)
- If the orbit escapes to infinity → point is OUTSIDE the set (colored)

This visualization helps understand WHY some points are in the set and others aren't.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QBrush, QFont, QMouseEvent

import numpy as np
from typing import List, Tuple, Optional


class OrbitOverlay(QWidget):
    """
    Transparent overlay that draws iteration orbits on the fractal canvas.

    When active, clicking a point shows the trajectory z₀ → z₁ → z₂ → ...
    of the fractal iteration. This demonstrates the core concept of
    escape-time fractals.
    """

    MAX_ORBIT_POINTS = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setMouseTracking(True)

        self._orbit_points: List[Tuple[float, float]] = []
        self._escaped = False
        self._active = False
        self._fractal_type = 'mandelbrot'
        self._max_iter = 200
        self._click_point = (0.0, 0.0)  # Original click coordinates

        # Viewport mapping parameters
        self._x_min = -2.0
        self._x_max = 1.0
        self._y_min = -1.5
        self._y_max = 1.5

        # Fractal parameters
        self._c_re = -0.4
        self._c_im = 0.6
        self._p_re = 0.5667
        self._p_im = -0.5

    def set_active(self, active: bool):
        """Enable/disable orbit visualization mode."""
        self._active = active
        # Toggle mouse event handling
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not active)
        if not active:
            self._orbit_points = []
        self.update()

    def is_active(self) -> bool:
        return self._active

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click to compute orbit at that point."""
        if not self._active:
            event.ignore()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # Convert pixel to complex coordinates
            pos = event.pos()
            re = self._x_min + (self._x_max - self._x_min) * pos.x() / self.width()
            im = self._y_max - (self._y_max - self._y_min) * pos.y() / self.height()
            self.compute_orbit(re, im)
            event.accept()
        else:
            event.ignore()

    def set_viewport(self, x_min: float, x_max: float,
                     y_min: float, y_max: float):
        """Update viewport bounds for coordinate mapping."""
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

    def set_fractal_params(self, fractal_type: str, max_iter: int,
                           c_re: float = 0.0, c_im: float = 0.0,
                           p_re: float = 0.0, p_im: float = 0.0):
        """Set fractal parameters for orbit computation."""
        self._fractal_type = fractal_type
        self._max_iter = max_iter
        self._c_re = c_re
        self._c_im = c_im
        self._p_re = p_re
        self._p_im = p_im

    def compute_orbit(self, click_re: float, click_im: float):
        """Compute the orbit for a given point in the complex plane."""
        self._orbit_points = []
        self._escaped = False
        self._click_point = (click_re, click_im)

        if self._fractal_type == 'mandelbrot':
            self._compute_mandelbrot_orbit(click_re, click_im)
        elif self._fractal_type == 'julia':
            self._compute_julia_orbit(click_re, click_im)
        elif self._fractal_type == 'burning_ship':
            self._compute_burning_ship_orbit(click_re, click_im)
        elif self._fractal_type == 'tricorn':
            self._compute_tricorn_orbit(click_re, click_im)
        elif self._fractal_type == 'phoenix':
            self._compute_phoenix_orbit(click_re, click_im)
        else:
            return

        self.update()

    def _compute_mandelbrot_orbit(self, c_re: float, c_im: float):
        """Mandelbrot: z_{n+1} = z_n² + c, starting from z₀ = 0"""
        zr, zi = 0.0, 0.0
        self._orbit_points.append((zr, zi))

        for _ in range(min(self._max_iter, self.MAX_ORBIT_POINTS)):
            zr_new = zr * zr - zi * zi + c_re
            zi = 2.0 * zr * zi + c_im
            zr = zr_new
            self._orbit_points.append((zr, zi))

            if zr * zr + zi * zi > 100.0:
                self._escaped = True
                break

    def _compute_julia_orbit(self, z_re: float, z_im: float):
        """Julia: z_{n+1} = z_n² + c, starting from z₀ = click point"""
        zr, zi = z_re, z_im
        self._orbit_points.append((zr, zi))

        for _ in range(min(self._max_iter, self.MAX_ORBIT_POINTS)):
            zr_new = zr * zr - zi * zi + self._c_re
            zi = 2.0 * zr * zi + self._c_im
            zr = zr_new
            self._orbit_points.append((zr, zi))

            if zr * zr + zi * zi > 100.0:
                self._escaped = True
                break

    def _compute_burning_ship_orbit(self, c_re: float, c_im: float):
        zr, zi = 0.0, 0.0
        self._orbit_points.append((zr, zi))

        for _ in range(min(self._max_iter, self.MAX_ORBIT_POINTS)):
            zr_new = zr * zr - zi * zi + c_re
            zi = abs(2.0 * zr * zi) + c_im
            zr = abs(zr_new)
            self._orbit_points.append((zr, zi))

            if zr * zr + zi * zi > 100.0:
                self._escaped = True
                break

    def _compute_tricorn_orbit(self, c_re: float, c_im: float):
        zr, zi = 0.0, 0.0
        self._orbit_points.append((zr, zi))

        for _ in range(min(self._max_iter, self.MAX_ORBIT_POINTS)):
            zr_new = zr * zr - zi * zi + c_re
            zi = -2.0 * zr * zi + c_im
            zr = zr_new
            self._orbit_points.append((zr, zi))

            if zr * zr + zi * zi > 100.0:
                self._escaped = True
                break

    def _compute_phoenix_orbit(self, z_re: float, z_im: float):
        zr, zi = z_re, z_im
        prev_zr, prev_zi = 0.0, 0.0
        self._orbit_points.append((zr, zi))

        for _ in range(min(self._max_iter, self.MAX_ORBIT_POINTS)):
            zr_new = zr * zr - zi * zi + self._p_re + self._p_im * prev_zr
            zi_new = 2.0 * zr * zi + self._p_im * prev_zi
            prev_zr, prev_zi = zr, zi
            zr, zi = zr_new, zi_new
            self._orbit_points.append((zr, zi))

            if zr * zr + zi * zi > 100.0:
                self._escaped = True
                break

    def _complex_to_pixel(self, re: float, im: float) -> QPointF:
        """Convert complex plane coordinates to widget pixel coordinates."""
        w = self.width()
        h = self.height()
        px = (re - self._x_min) / (self._x_max - self._x_min) * w
        py = (self._y_max - im) / (self._y_max - self._y_min) * h
        return QPointF(px, py)

    def paintEvent(self, event):
        """Draw the orbit visualization with explanatory information."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Always draw instructions when active
        if self._active:
            self._draw_instructions(painter)

        if not self._active or len(self._orbit_points) < 2:
            painter.end()
            return

        n = len(self._orbit_points)

        # Draw escape radius circle (|z| = 2)
        self._draw_escape_circle(painter)

        # Draw connecting lines with gradient
        for i in range(n - 1):
            t = i / max(1, n - 1)
            alpha = max(40, int(220 * (1.0 - t * 0.7)))

            if self._escaped:
                color = QColor(255, int(100 + 155 * (1 - t)), 50, alpha)
            else:
                color = QColor(50, int(150 + 105 * (1 - t)), 255, alpha)

            pen = QPen(color, max(1.0, 3.0 - t * 2.0))
            painter.setPen(pen)

            p1 = self._complex_to_pixel(*self._orbit_points[i])
            p2 = self._complex_to_pixel(*self._orbit_points[i + 1])
            painter.drawLine(p1, p2)

        # Draw points with labels for key iterations
        for i, (re, im) in enumerate(self._orbit_points):
            t = i / max(1, n - 1)
            pt = self._complex_to_pixel(re, im)

            # Starting point z₀
            if i == 0:
                painter.setBrush(QBrush(QColor(0, 255, 0, 220)))
                painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
                painter.drawEllipse(pt, 8, 8)
                # Label
                painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(int(pt.x()) + 12, int(pt.y()) + 5, "z₀ (старт)")

            elif i == n - 1:
                # Last point
                if self._escaped:
                    painter.setBrush(QBrush(QColor(255, 50, 50, 220)))
                    label = f"z_{i} (втекла!)"
                else:
                    painter.setBrush(QBrush(QColor(50, 150, 255, 220)))
                    label = f"z_{i} (в множині)"
                painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
                painter.drawEllipse(pt, 7, 7)
                painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(int(pt.x()) + 10, int(pt.y()) + 5, label)

            elif i <= 5 or i == n // 2:
                # Show first few iterations and middle
                radius = max(2.0, 4.0 - t * 2.5)
                alpha = max(80, int(220 * (1.0 - t * 0.5)))
                painter.setBrush(QBrush(QColor(255, 255, 255, alpha)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pt, radius, radius)

                if i <= 3:
                    painter.setFont(QFont("Arial", 8))
                    painter.setPen(QColor(200, 200, 200, 200))
                    painter.drawText(int(pt.x()) + 6, int(pt.y()) - 3, f"z_{i}")
            else:
                radius = max(1.5, 3.0 - t * 2.0)
                alpha = max(60, int(180 * (1.0 - t * 0.6)))
                painter.setBrush(QBrush(QColor(255, 255, 255, alpha)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pt, radius, radius)

        # Draw info panel
        self._draw_info_panel(painter, n)

        painter.end()

    def _draw_escape_circle(self, painter: QPainter):
        """Draw the escape radius circle |z| = 2."""
        center = self._complex_to_pixel(0, 0)
        # Calculate radius in pixels
        edge = self._complex_to_pixel(2, 0)
        radius = abs(edge.x() - center.x())

        if radius > 10 and radius < self.width() * 2:
            painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius, radius)

            # Label
            painter.setFont(QFont("Arial", 8))
            painter.setPen(QColor(255, 255, 255, 100))
            label_pt = self._complex_to_pixel(2.1, 0.1)
            painter.drawText(int(label_pt.x()), int(label_pt.y()), "|z|=2 (межа втечі)")

    def _draw_instructions(self, painter: QPainter):
        """Draw usage instructions."""
        if len(self._orbit_points) > 0:
            return

        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor(255, 255, 255, 200))

        text = "Клікніть на будь-яку точку, щоб побачити її орбіту (траєкторію ітерацій)"
        rect = painter.fontMetrics().boundingRect(text)

        x = (self.width() - rect.width()) // 2
        y = 30

        # Background
        painter.fillRect(x - 10, y - 20, rect.width() + 20, rect.height() + 15,
                        QColor(0, 0, 0, 150))
        painter.drawText(x, y, text)

    def _draw_info_panel(self, painter: QPainter, n: int):
        """Draw explanation panel."""
        panel_x = 10
        panel_y = self.height() - 180
        panel_w = 320
        panel_h = 170

        # Background
        painter.fillRect(panel_x, panel_y, panel_w, panel_h, QColor(20, 20, 30, 230))
        painter.setPen(QPen(QColor(100, 100, 120), 1))
        painter.drawRect(panel_x, panel_y, panel_w, panel_h)

        # Title
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(panel_x + 10, panel_y + 22, "Що таке орбіта?")

        # Explanation
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(200, 200, 200))

        lines = [
            "Орбіта — це послідовність z₀ → z₁ → z₂ → ...",
            f"Формула: z_{{n+1}} = z_n² + c",
            "",
            f"Точка c = ({self._click_point[0]:.4f}, {self._click_point[1]:.4f})",
            f"Кількість ітерацій: {n}",
            "",
        ]

        if self._escaped:
            lines.append("Результат: ВТЕКЛА (точка НЕ в множині)")
            lines.append("Орбіта вийшла за межу |z| > 2")
            result_color = QColor(255, 100, 100)
        else:
            lines.append("Результат: В МНОЖИНІ (чорна точка)")
            lines.append("Орбіта залишилась обмеженою")
            result_color = QColor(100, 200, 255)

        y = panel_y + 40
        for i, line in enumerate(lines):
            if i >= 6:
                painter.setPen(result_color)
                painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(panel_x + 10, y, line)
            y += 16
