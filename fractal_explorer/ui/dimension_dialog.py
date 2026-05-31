"""
Fractal Dimension calculation dialog with visualization.
"""

import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush

from ..analysis.fractal_dimension import (
    compute_box_counting_dimension,
    iterations_to_binary,
    get_theoretical_dimension
)


class DimensionWorker(QThread):
    """Worker thread for fractal dimension calculation."""

    progress = pyqtSignal(int, str)
    result_ready = pyqtSignal(dict)

    def __init__(self, iterations: np.ndarray, max_iter: int, fractal_name: str):
        super().__init__()
        self._iterations = iterations
        self._max_iter = max_iter
        self._fractal_name = fractal_name

    def run(self):
        self.progress.emit(10, "Конвертація в бінарне зображення...")

        # Convert to binary boundary image
        binary = iterations_to_binary(self._iterations, self._max_iter)

        self.progress.emit(40, "Обчислення розмірності...")

        # Compute dimension
        dimension, box_sizes, box_counts, r_squared = compute_box_counting_dimension(
            binary, min_box_size=2
        )

        self.progress.emit(90, "Завершення...")

        # Get theoretical value
        theoretical = get_theoretical_dimension(self._fractal_name)

        result = {
            'dimension': dimension,
            'box_sizes': box_sizes,
            'box_counts': box_counts,
            'r_squared': r_squared,
            'theoretical': theoretical,
            'fractal_name': self._fractal_name
        }

        self.progress.emit(100, "Готово!")
        self.result_ready.emit(result)


class LogLogPlot(QWidget):
    """Widget for displaying log-log plot of box counting data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)

    def set_data(self, box_sizes, box_counts, dimension, r_squared):
        self._box_sizes = box_sizes
        self._box_counts = box_counts
        self._dimension = dimension
        self._r_squared = r_squared
        self.update()

    def paintEvent(self, event):
        if not hasattr(self, '_box_sizes') or not self._box_sizes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = 70
        margin_right = 30
        margin_top = 40
        margin_bottom = 50

        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Background
        painter.fillRect(0, 0, w, h, QColor(30, 30, 30))

        # Title
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(margin_left, 20, "Залежність log(N) від log(1/s)")

        # Compute log values
        log_sizes = np.log(self._box_sizes)
        log_counts = np.log(self._box_counts)

        # Invert log_sizes for log(1/s)
        log_inv_sizes = -log_sizes

        # Data ranges
        x_min, x_max = log_inv_sizes.min(), log_inv_sizes.max()
        y_min, y_max = log_counts.min(), log_counts.max()

        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
        y_min -= y_range * 0.1
        y_max += y_range * 0.1

        def to_screen(lx, ly):
            sx = margin_left + (lx - x_min) / (x_max - x_min) * chart_w
            sy = margin_top + chart_h - (ly - y_min) / (y_max - y_min) * chart_h
            return int(sx), int(sy)

        # Draw axes
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(margin_left, margin_top,
                        margin_left, margin_top + chart_h)
        painter.drawLine(margin_left, margin_top + chart_h,
                        margin_left + chart_w, margin_top + chart_h)

        # Axis labels
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(180, 180, 180))
        painter.drawText(w // 2 - 40, h - 5, "log(1/s)")
        painter.save()
        painter.translate(15, h // 2 + 30)
        painter.rotate(-90)
        painter.drawText(0, 0, "log(N)")
        painter.restore()

        # Draw grid and tick labels
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor(80, 80, 80))

        # Y-axis ticks
        for i in range(5):
            y_val = y_min + (y_max - y_min) * i / 4
            _, sy = to_screen(x_min, y_val)
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(5, sy + 4, f"{y_val:.1f}")
            painter.setPen(QPen(QColor(50, 50, 50), 1, Qt.PenStyle.DashLine))
            painter.drawLine(margin_left, sy, margin_left + chart_w, sy)

        # X-axis ticks
        for i in range(5):
            x_val = x_min + (x_max - x_min) * i / 4
            sx, _ = to_screen(x_val, y_min)
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(sx - 15, margin_top + chart_h + 15, f"{x_val:.1f}")

        # Draw regression line
        x_line = np.linspace(x_min, x_max, 100)
        # D = slope, so: log(N) = D * log(1/s) + intercept
        # Use first point to find intercept
        intercept = log_counts[0] - self._dimension * log_inv_sizes[0]
        y_line = self._dimension * x_line + intercept

        painter.setPen(QPen(QColor(255, 100, 100, 150), 2))
        for i in range(len(x_line) - 1):
            sx1, sy1 = to_screen(x_line[i], y_line[i])
            sx2, sy2 = to_screen(x_line[i + 1], y_line[i + 1])
            painter.drawLine(sx1, sy1, sx2, sy2)

        # Draw data points
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QBrush(QColor(66, 133, 244)))
        for lx, ly in zip(log_inv_sizes, log_counts):
            sx, sy = to_screen(lx, ly)
            painter.drawEllipse(sx - 5, sy - 5, 10, 10)

        # Legend
        painter.setFont(QFont("Segoe UI", 9))
        legend_x = margin_left + 10
        legend_y = margin_top + 20
        painter.fillRect(legend_x - 5, legend_y - 15, 180, 45, QColor(40, 40, 40, 220))

        painter.setPen(QColor(255, 100, 100))
        painter.drawText(legend_x, legend_y, f"D = {self._dimension:.4f}")
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(legend_x, legend_y + 18, f"R² = {self._r_squared:.4f}")

        painter.end()


class DimensionDialog(QDialog):
    """Dialog for computing and displaying fractal dimension."""

    def __init__(self, iterations: np.ndarray, max_iter: int,
                 fractal_name: str, parent=None):
        super().__init__(parent)
        self._iterations = iterations
        self._max_iter = max_iter
        self._fractal_name = fractal_name
        self._worker = None

        self.setWindowTitle("Фрактальна розмірність")
        self.setMinimumSize(550, 500)
        self._setup_ui()

        # Start computation
        self._compute()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "<h3>Обчислення фрактальної розмірності</h3>"
            "<p>Метод: Box-counting (підрахунок комірок)</p>"
        )
        layout.addWidget(header)

        # Progress
        self._progress = QProgressBar()
        layout.addWidget(self._progress)

        self._status = QLabel("Обчислення...")
        layout.addWidget(self._status)

        # Results group
        results_group = QGroupBox("Результати")
        results_layout = QVBoxLayout(results_group)

        self._dim_label = QLabel("")
        self._dim_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(self._dim_label)

        self._theoretical_label = QLabel("")
        results_layout.addWidget(self._theoretical_label)

        self._quality_label = QLabel("")
        results_layout.addWidget(self._quality_label)

        layout.addWidget(results_group)

        # Plot
        self._plot = LogLogPlot()
        layout.addWidget(self._plot)

        # Explanation
        explanation = QLabel(
            "<p style='color: #aaa;'>"
            "Фрактальна розмірність D визначається зі співвідношення N(s) ~ s<sup>-D</sup>, "
            "де N(s) — кількість комірок розміру s, що містять фрактал. "
            "Нахил прямої на графіку log(N) vs log(1/s) дорівнює D."
            "</p>"
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # Buttons
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _compute(self):
        self._worker = DimensionWorker(
            self._iterations, self._max_iter, self._fractal_name
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.result_ready.connect(self._on_results)
        self._worker.start()

    def _on_progress(self, value: int, message: str):
        self._progress.setValue(value)
        self._status.setText(message)

    def _on_results(self, results: dict):
        self._progress.setVisible(False)
        self._status.setText("Обчислення завершено")

        dim = results['dimension']
        theoretical = results['theoretical']
        r_squared = results['r_squared']

        self._dim_label.setText(f"Обчислена розмірність: D = {dim:.4f}")

        if theoretical > 0:
            error = abs(dim - theoretical) / theoretical * 100
            self._theoretical_label.setText(
                f"Теоретичне значення: D = {theoretical:.4f} "
                f"(похибка: {error:.1f}%)"
            )
        else:
            self._theoretical_label.setText("Теоретичне значення: невідомо")

        quality = "Відмінна" if r_squared > 0.99 else \
                  "Хороша" if r_squared > 0.95 else \
                  "Задовільна" if r_squared > 0.9 else "Низька"
        color = "#52c759" if r_squared > 0.95 else "#ffcc00" if r_squared > 0.9 else "#ff6666"
        self._quality_label.setText(
            f"Якість апроксимації: R² = {r_squared:.4f} "
            f"(<span style='color: {color};'>{quality}</span>)"
        )

        # Update plot
        if results['box_sizes']:
            self._plot.set_data(
                results['box_sizes'],
                results['box_counts'],
                dim,
                r_squared
            )
