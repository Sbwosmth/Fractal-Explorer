"""
Fractal display canvas widget.
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import (
    QImage, QPixmap, QPainter, QMouseEvent, QWheelEvent,
    QResizeEvent, QPaintEvent
)

import numpy as np
from typing import Optional

from ..rendering.renderer import FractalRenderer


class FractalCanvas(QWidget):
    """
    Canvas widget for displaying and interacting with fractals.

    Handles:
    - Mouse wheel zoom
    - Click and drag panning
    - Double-click center and zoom
    - Cursor position tracking
    - Resize handling with debounced re-render
    """

    # Signals
    cursor_moved = pyqtSignal(float, float)  # Complex coordinates
    render_complete = pyqtSignal(dict)  # Render info

    # Zoom factor for mouse wheel
    ZOOM_FACTOR = 1.5

    def __init__(self, renderer: FractalRenderer, parent=None):
        super().__init__(parent)

        self._renderer = renderer
        self._image: Optional[QImage] = None
        self._pixmap: Optional[QPixmap] = None

        # Mouse state
        self._dragging = False
        self._last_mouse_pos: Optional[QPoint] = None

        # Render debounce timer
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._do_render)

        # Animation mode - uses lower resolution for smooth playback
        self._animation_mode = False
        self._animation_scale = 0.5  # Render at 50% resolution during animation

        # Cache for RGBA data
        self._current_rgba: Optional[np.ndarray] = None

        # Setup widget
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)

        # Initial render
        QTimer.singleShot(100, self._do_render)

    def _do_render(self):
        """Perform the actual rendering."""
        display_width = self.width()
        display_height = self.height()

        if display_width <= 0 or display_height <= 0:
            return

        # Use lower resolution during animation for smooth playback
        if self._animation_mode:
            render_width = int(display_width * self._animation_scale)
            render_height = int(display_height * self._animation_scale)
        else:
            render_width = display_width
            render_height = display_height

        # Render fractal
        rgba, render_time = self._renderer.render(render_width, render_height)
        self._current_rgba = rgba

        # Convert to QImage
        self._image = QImage(
            rgba.data.tobytes(),
            render_width, render_height,
            render_width * 4,
            QImage.Format.Format_RGBA8888
        )

        # Scale up if in animation mode
        if self._animation_mode and (render_width != display_width or render_height != display_height):
            self._pixmap = QPixmap.fromImage(self._image).scaled(
                display_width, display_height,
                aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
        else:
            self._pixmap = QPixmap.fromImage(self._image)

        # Emit info
        info = self._renderer.get_info()
        self.render_complete.emit(info)

        # Request repaint
        self.update()

    def request_render(self, immediate: bool = False):
        """
        Request a render, optionally with debouncing.

        Args:
            immediate: If True, render immediately; otherwise debounce
        """
        if immediate:
            self._render_timer.stop()
            self._do_render()
        else:
            # Debounce renders to avoid excessive computation
            self._render_timer.start(50)

    def paintEvent(self, event: QPaintEvent):
        """Paint the fractal image."""
        painter = QPainter(self)

        if self._pixmap:
            painter.drawPixmap(0, 0, self._pixmap)
        else:
            # Draw placeholder
            painter.fillRect(self.rect(), Qt.GlobalColor.black)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Loading..."
            )

        painter.end()

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize with debounced re-render."""
        super().resizeEvent(event)
        self.request_render(immediate=False)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel zoom."""
        # Get zoom direction
        delta = event.angleDelta().y()
        if delta == 0:
            return

        factor = self.ZOOM_FACTOR if delta > 0 else 1.0 / self.ZOOM_FACTOR

        # Get mouse position
        pos = event.position()
        mouse_x = int(pos.x())
        mouse_y = int(pos.y())

        # Zoom
        self._renderer.zoom(
            factor,
            mouse_x, mouse_y,
            self.width(), self.height()
        )

        self.request_render(immediate=True)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning and orbit visualization."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if orbit overlay is active (traverse up to main window)
            parent = self.parent()
            while parent:
                if hasattr(parent, '_orbit_overlay') and parent._orbit_overlay.is_active():
                    # Compute orbit at click position
                    pos = event.pos()
                    re, im = self._renderer.get_complex_coords(
                        pos.x(), pos.y(),
                        self.width(), self.height()
                    )
                    # Update viewport bounds for overlay
                    aspect_ratio = self.width() / max(1, self.height())
                    x_min, x_max, y_min, y_max = self._renderer.viewport.get_bounds(aspect_ratio)
                    parent._orbit_overlay.set_viewport(x_min, x_max, y_min, y_max)
                    parent._orbit_overlay.compute_orbit(re, im)
                    return
                parent = parent.parent()

            self._dragging = True
            self._last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._last_mouse_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning and cursor tracking."""
        pos = event.pos()

        # Update cursor position display
        re, im = self._renderer.get_complex_coords(
            pos.x(), pos.y(),
            self.width(), self.height()
        )
        self.cursor_moved.emit(re, im)

        # Handle panning
        if self._dragging and self._last_mouse_pos:
            dx = pos.x() - self._last_mouse_pos.x()
            dy = pos.y() - self._last_mouse_pos.y()

            if dx != 0 or dy != 0:
                self._renderer.pan(dx, dy, self.width(), self.height())
                self._last_mouse_pos = pos
                self.request_render(immediate=True)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double-click to center and zoom."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()

            # Get complex coordinates of click position
            re, im = self._renderer.get_complex_coords(
                pos.x(), pos.y(),
                self.width(), self.height()
            )

            # Center on this point and zoom in
            self._renderer.viewport.center_re = re
            self._renderer.viewport.center_im = im
            self._renderer.zoom(self.ZOOM_FACTOR)

            self.request_render(immediate=True)

    def get_current_image(self) -> Optional[QImage]:
        """Get the current rendered image."""
        return self._image

    def get_current_rgba(self) -> Optional[np.ndarray]:
        """Get current image as numpy RGBA array."""
        if self._current_rgba is None:
            return None
        return self._current_rgba.copy()

    def set_animation_mode(self, enabled: bool):
        """
        Enable or disable animation mode.

        In animation mode, rendering is done at lower resolution
        for smoother playback on fast-changing frames.
        """
        self._animation_mode = enabled

    def apply_color_shift(self, offset: float):
        """
        Apply color palette shift for color cycling animation.
        Reapplies colormap with shifted indices - fast vectorized operation.

        Args:
            offset: Color offset (0.0 to 1.0)
        """
        iterations = self._renderer.get_last_iterations()
        if iterations is None:
            return

        # Get shifted colormap and reapply
        max_iter = self._renderer.get_max_iterations()
        lut = self._renderer.colormap.get_lut()
        shift = int(offset * 256) % 256
        shifted_lut = np.roll(lut, shift, axis=0)

        # Vectorized colormap application
        normalized = np.clip(iterations / max_iter, 0, 1)
        indices = (normalized * 255).astype(np.uint8)
        rgba = shifted_lut[indices]

        # Set black for points in the set (max iterations)
        in_set = iterations >= max_iter
        rgba[in_set] = [0, 0, 0, 255]

        height, width = rgba.shape[:2]
        self._image = QImage(
            rgba.data.tobytes(),
            width, height,
            width * 4,
            QImage.Format.Format_RGBA8888
        )
        self._pixmap = QPixmap.fromImage(self._image)
        self.update()
