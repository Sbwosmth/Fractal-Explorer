"""
Information bar widget displaying fractal state.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class InfoBar(QWidget):
    """
    Information bar showing current fractal state.

    Displays:
    - Current coordinates (Re, Im)
    - Zoom level
    - Render time
    - Cursor position in complex plane
    - Compute backend status
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gpu_tooltip = ""
        self._setup_ui()

    def _setup_ui(self):
        """Setup the info bar layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)

        # Create info labels
        self._center_label = QLabel("Центр: (0.000, 0.000)")
        self._zoom_label = QLabel("Масштаб: 1.00x")
        self._render_time_label = QLabel("Рендер: 0 мс")
        self._cursor_label = QLabel("Курсор: (0.000, 0.000)")
        self._backend_label = QLabel("Обчислення: CPU")

        # Add separator style
        for label in [self._center_label, self._zoom_label,
                      self._render_time_label, self._cursor_label]:
            layout.addWidget(label)
            layout.addWidget(self._create_separator())

        layout.addWidget(self._backend_label)
        layout.addStretch()

        # Style
        self.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

    def _create_separator(self) -> QFrame:
        """Create a vertical separator."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("color: #555555;")
        return separator

    def update_center(self, re: float, im: float):
        """Update center coordinates display."""
        sign = '+' if im >= 0 else '-'
        self._center_label.setText(f"Центр: ({re:.6f}, {sign}{abs(im):.6f}i)")

    def update_zoom(self, zoom_str: str):
        """Update zoom level display."""
        self._zoom_label.setText(f"Масштаб: {zoom_str}")

    def update_render_time(self, time_ms: float):
        """Update render time display."""
        if time_ms < 1:
            self._render_time_label.setText(f"Рендер: <1 мс")
        elif time_ms < 1000:
            self._render_time_label.setText(f"Рендер: {time_ms:.1f} мс")
        else:
            self._render_time_label.setText(f"Рендер: {time_ms/1000:.2f} с")

    def update_cursor(self, re: float, im: float):
        """Update cursor position display."""
        sign = '+' if im >= 0 else '-'
        self._cursor_label.setText(f"Курсор: ({re:.6f}, {sign}{abs(im):.6f}i)")

    def update_backend(self, status: str):
        """Update backend status display."""
        self._backend_label.setText(f"Обчислення: {status}")

    def update_backend_detailed(self, status: str, detailed_info: dict):
        """Update backend status with detailed tooltip."""
        is_gpu = detailed_info.get('use_gpu', False)
        reason = detailed_info.get('gpu_reason', '')

        if is_gpu:
            self._backend_label.setText(f"<span style='color: #4caf50;'>GPU: {detailed_info.get('device_name', 'Unknown')}</span>")
            self._backend_label.setStyleSheet("color: #4caf50; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;")
            tooltip = f"Прискорення GPU активне!\n{reason}"
        else:
            self._backend_label.setText(f"CPU: {detailed_info.get('device_name', 'Numba JIT')}")
            self._backend_label.setStyleSheet("color: #ff9800; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;")
            tooltip = f"GPU недоступний.\n{reason}\n\nДля GPU потрібно:\n1. NVIDIA GPU з CUDA\n2. pip install cupy-cuda12x"

        self._backend_label.setToolTip(tooltip)

    def update_all(self, info: dict):
        """Update all fields from an info dictionary."""
        if 'center_re' in info and 'center_im' in info:
            self.update_center(info['center_re'], info['center_im'])
        if 'zoom' in info:
            self.update_zoom(info['zoom'])
        if 'render_time_ms' in info:
            self.update_render_time(info['render_time_ms'])
        if 'backend' in info:
            self.update_backend(info['backend'])
