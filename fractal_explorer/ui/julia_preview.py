"""
Julia set preview widget - floating overlay on canvas corner.

Shows Julia set corresponding to cursor position on Mandelbrot in real-time.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QMouseEvent

import numpy as np
from typing import Optional

from ..rendering.colormap import ColorMapper


class JuliaPreviewWidget(QWidget):
    """
    Floating Julia set preview overlay.

    Features:
    - Positioned in canvas corner (draggable)
    - Semi-transparent background
    - Real-time updates with debouncing
    - GPU acceleration when available
    """

    PREVIEW_SIZE = 180
    MARGIN = 15

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self._renderer = renderer
        self._colormap = ColorMapper()
        self._c_re = -0.4
        self._c_im = 0.6
        self._pixmap: Optional[QPixmap] = None
        self._enabled = True
        self._in_mandelbrot = True

        # Dragging state
        self._dragging = False
        self._drag_start = QPoint()

        # Debounce timer - 50ms for responsiveness
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.setInterval(50)
        self._update_timer.timeout.connect(self._render_preview)

        # Visual setup
        self.setFixedSize(self.PREVIEW_SIZE + 20, self.PREVIEW_SIZE + 70)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Initial render
        QTimer.singleShot(200, self._render_preview)

    def update_c(self, c_re: float, c_im: float):
        """Update the Julia parameter c based on cursor position."""
        if not self._enabled or not self.isVisible():
            return

        self._c_re = c_re
        self._c_im = c_im
        self._in_mandelbrot = self._quick_mandelbrot_test(c_re, c_im)

        # Request render with debounce
        self._update_timer.start()
        self.update()  # Repaint immediately to show coordinates

    def _quick_mandelbrot_test(self, c_re: float, c_im: float, max_iter: int = 30) -> bool:
        """Quick test if point is in Mandelbrot set."""
        # Cardioid check
        q = (c_re - 0.25) ** 2 + c_im ** 2
        if q * (q + (c_re - 0.25)) < 0.25 * c_im ** 2:
            return True
        # Period-2 bulb check
        if (c_re + 1) ** 2 + c_im ** 2 < 0.0625:
            return True
        # Iteration test
        zr, zi = 0.0, 0.0
        for _ in range(max_iter):
            zr_new = zr * zr - zi * zi + c_re
            zi = 2.0 * zr * zi + c_im
            zr = zr_new
            if zr * zr + zi * zi > 4.0:
                return False
        return True

    def _render_preview(self):
        """Render the Julia preview."""
        if not self.isVisible():
            return

        size = self.PREVIEW_SIZE
        max_iter = 100

        try:
            iterations = self._renderer.backend.compute_julia(
                size, size,
                -1.8, 1.8, -1.8, 1.8,
                self._c_re, self._c_im,
                max_iter
            )

            cmap_name = self._renderer.colormap.get_colormap_name()
            self._colormap.set_colormap(cmap_name)
            rgba = self._colormap.apply(iterations, max_iter)

            qimage = QImage(
                rgba.data.tobytes(),
                size, size,
                size * 4,
                QImage.Format.Format_RGBA8888
            )
            self._pixmap = QPixmap.fromImage(qimage)
            self.update()

        except Exception as e:
            print(f"Julia preview error: {e}")

    def paintEvent(self, event):
        """Draw the floating preview with info."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent background
        painter.fillRect(self.rect(), QColor(30, 30, 40, 220))
        painter.setPen(QColor(80, 80, 100))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        # Title
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(79, 195, 247))
        painter.drawText(10, 18, "Превью Жюліа")

        # Preview image
        if self._pixmap:
            painter.drawPixmap(10, 25, self._pixmap)
        else:
            painter.fillRect(10, 25, self.PREVIEW_SIZE, self.PREVIEW_SIZE, QColor(0, 0, 0))

        # Coordinates
        y = self.PREVIEW_SIZE + 40
        painter.setFont(QFont("Consolas", 9))
        painter.setPen(QColor(180, 180, 180))

        sign = '+' if self._c_im >= 0 else '-'
        coord_text = f"c = {self._c_re:.4f} {sign} {abs(self._c_im):.4f}i"
        painter.drawText(10, y, coord_text)

        # Status
        y += 16
        if self._in_mandelbrot:
            painter.setPen(QColor(76, 175, 80))
            painter.drawText(10, y, "∈ M → зв'язна")
        else:
            painter.setPen(QColor(255, 152, 0))
            painter.drawText(10, y, "∉ M → пил Кантора")

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        """Start dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle dragging."""
        if self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_start
            # Keep within parent bounds
            if self.parent():
                parent_rect = self.parent().rect()
                new_pos.setX(max(0, min(new_pos.x(), parent_rect.width() - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), parent_rect.height() - self.height())))
            self.move(new_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def set_enabled(self, enabled: bool):
        """Enable or disable the preview."""
        self._enabled = enabled
        self.setVisible(enabled)

    def sync_colormap(self):
        """Sync colormap with main renderer."""
        cmap_name = self._renderer.colormap.get_colormap_name()
        self._colormap.set_colormap(cmap_name)
        self._render_preview()

    def position_in_corner(self):
        """Position widget in top-right corner of parent."""
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() - self.width() - self.MARGIN
            y = self.MARGIN
            self.move(x, y)
