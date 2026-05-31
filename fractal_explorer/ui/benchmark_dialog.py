"""
Benchmark dialog - GPU vs CPU performance comparison.
"""

import time
import numpy as np
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont

from ..compute.backend import ComputeBackend


class BenchmarkWorker(QThread):
    """Worker thread for running benchmarks."""

    progress = pyqtSignal(int, str)
    result_ready = pyqtSignal(dict)

    def __init__(self, backend: ComputeBackend):
        super().__init__()
        self._backend = backend

    def run(self):
        results = {
            'cpu': [],
            'gpu': [],
            'resolutions': [],
            'iterations_test': {
                'cpu': [],
                'gpu': [],
                'iterations': []
            }
        }

        # Test 1: Resolution scaling (fixed iterations = 200)
        resolutions = [
            (200, 150), (400, 300), (600, 450),
            (800, 600), (1024, 768), (1280, 960),
            (1600, 1200), (1920, 1080)
        ]

        total_steps = len(resolutions) * 2 + 6 * 2
        step = 0

        for w, h in resolutions:
            results['resolutions'].append(f"{w}x{h}")

            # CPU test
            self.progress.emit(int(step / total_steps * 100),
                             f"CPU: {w}x{h}...")
            cpu_time = self._benchmark_cpu(w, h, 200)
            results['cpu'].append(cpu_time)
            step += 1

            # GPU test
            if self._backend.use_gpu:
                self.progress.emit(int(step / total_steps * 100),
                                 f"GPU: {w}x{h}...")
                gpu_time = self._benchmark_gpu(w, h, 200)
                results['gpu'].append(gpu_time)
            else:
                results['gpu'].append(None)
            step += 1

        # Test 2: Iteration scaling (fixed resolution 800x600)
        iter_values = [50, 100, 200, 500, 1000, 2000]

        for iters in iter_values:
            results['iterations_test']['iterations'].append(iters)

            self.progress.emit(int(step / total_steps * 100),
                             f"CPU: iter={iters}...")
            cpu_time = self._benchmark_cpu(800, 600, iters)
            results['iterations_test']['cpu'].append(cpu_time)
            step += 1

            if self._backend.use_gpu:
                self.progress.emit(int(step / total_steps * 100),
                                 f"GPU: iter={iters}...")
                gpu_time = self._benchmark_gpu(800, 600, iters)
                results['iterations_test']['gpu'].append(gpu_time)
            else:
                results['iterations_test']['gpu'].append(None)
            step += 1

        self.progress.emit(100, "Завершено!")
        self.result_ready.emit(results)

    def _benchmark_cpu(self, width, height, max_iter, runs=3):
        """Benchmark CPU rendering."""
        cpu = self._backend._cpu_compute
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            cpu.compute_mandelbrot(width, height, -2.5, 1.0, -1.25, 1.25, max_iter)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        return min(times)

    def _benchmark_gpu(self, width, height, max_iter, runs=3):
        """Benchmark GPU rendering."""
        if not self._backend.use_gpu or self._backend._gpu_compute is None:
            return None
        gpu = self._backend._gpu_compute
        times = []
        for _ in range(runs):
            try:
                import cupy as cp
                cp.cuda.Stream.null.synchronize()
                start = time.perf_counter()
                result = gpu.compute_mandelbrot(
                    width, height, -2.5, 1.0, -1.25, 1.25, max_iter
                )
                cp.cuda.Stream.null.synchronize()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            except Exception:
                return None
        return min(times) if times else None


class BenchmarkChart(QWidget):
    """Simple bar chart widget for benchmark results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._title = ""
        self.setMinimumHeight(250)

    def set_data(self, labels, cpu_times, gpu_times, title=""):
        """Set chart data."""
        self._labels = labels
        self._cpu_times = cpu_times
        self._gpu_times = gpu_times
        self._title = title
        self.update()

    def paintEvent(self, event):
        if not hasattr(self, '_labels') or self._labels is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = 70
        margin_right = 20
        margin_top = 35
        margin_bottom = 50

        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Background
        painter.fillRect(0, 0, w, h, QColor(30, 30, 30))

        # Title
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(margin_left, 20, self._title)

        # Find max value
        all_times = [t for t in self._cpu_times if t is not None]
        all_times += [t for t in self._gpu_times if t is not None]
        if not all_times:
            return
        max_time = max(all_times) * 1.15

        n = len(self._labels)
        bar_group_width = chart_w / n
        bar_width = bar_group_width * 0.35

        # Draw axes
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(margin_left, margin_top, margin_left, margin_top + chart_h)
        painter.drawLine(margin_left, margin_top + chart_h,
                        margin_left + chart_w, margin_top + chart_h)

        # Y-axis labels
        painter.setFont(QFont("Consolas", 8))
        for i in range(5):
            val = max_time * i / 4
            y_pos = margin_top + chart_h - (chart_h * i / 4)
            painter.setPen(QColor(120, 120, 120))
            painter.drawText(5, int(y_pos + 4), f"{val:.1f} мс")
            painter.setPen(QPen(QColor(50, 50, 50), 1, Qt.PenStyle.DashLine))
            painter.drawLine(margin_left, int(y_pos),
                           margin_left + chart_w, int(y_pos))

        # Draw bars
        for i in range(n):
            x_base = margin_left + i * bar_group_width + bar_group_width * 0.1

            # CPU bar
            cpu_time = self._cpu_times[i]
            if cpu_time is not None:
                bar_h = (cpu_time / max_time) * chart_h
                y = margin_top + chart_h - bar_h
                painter.fillRect(int(x_base), int(y),
                               int(bar_width), int(bar_h),
                               QColor(66, 133, 244))

            # GPU bar
            gpu_time = self._gpu_times[i]
            if gpu_time is not None:
                bar_h = (gpu_time / max_time) * chart_h
                y = margin_top + chart_h - bar_h
                painter.fillRect(int(x_base + bar_width + 2), int(y),
                               int(bar_width), int(bar_h),
                               QColor(52, 199, 89))

            # X-axis label
            painter.setPen(QColor(180, 180, 180))
            painter.setFont(QFont("Consolas", 7))
            label_x = int(x_base + bar_width * 0.5)
            painter.save()
            painter.translate(label_x, margin_top + chart_h + 8)
            painter.rotate(35)
            painter.drawText(0, 0, self._labels[i])
            painter.restore()

        # Legend
        legend_y = margin_top + 5
        legend_x = margin_left + chart_w - 130
        painter.fillRect(legend_x - 5, legend_y - 5, 135, 40, QColor(40, 40, 40, 200))
        painter.fillRect(legend_x, legend_y, 12, 12, QColor(66, 133, 244))
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(legend_x + 16, legend_y + 11, "CPU")

        painter.fillRect(legend_x, legend_y + 18, 12, 12, QColor(52, 199, 89))
        painter.drawText(legend_x + 16, legend_y + 29, "GPU")

        painter.end()


class BenchmarkDialog(QDialog):
    """Dialog for running and displaying GPU vs CPU benchmarks."""

    def __init__(self, backend: ComputeBackend, parent=None):
        super().__init__(parent)
        self._backend = backend
        self._worker = None
        self.setWindowTitle("Бенчмарк GPU vs CPU")
        self.setMinimumSize(800, 650)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            f"<h3>Порівняння продуктивності</h3>"
            f"<p>Бекенд: {self._backend.get_status()}</p>"
        )
        layout.addWidget(header)

        # Progress
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        # Charts area
        charts_layout = QHBoxLayout()

        self._res_chart = BenchmarkChart()
        self._iter_chart = BenchmarkChart()

        res_group = QGroupBox("Залежність від роздільної здатності")
        res_layout = QVBoxLayout(res_group)
        res_layout.addWidget(self._res_chart)
        charts_layout.addWidget(res_group)

        iter_group = QGroupBox("Залежність від кількості ітерацій")
        iter_layout = QVBoxLayout(iter_group)
        iter_layout.addWidget(self._iter_chart)
        charts_layout.addWidget(iter_group)

        layout.addLayout(charts_layout)

        # Results table
        self._table = QTableWidget()
        self._table.setMaximumHeight(200)
        self._table.setVisible(False)
        layout.addWidget(self._table)

        # Buttons
        btn_layout = QHBoxLayout()
        self._run_btn = QPushButton("Запустити бенчмарк")
        self._run_btn.clicked.connect(self._run_benchmark)
        btn_layout.addWidget(self._run_btn)

        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _run_benchmark(self):
        self._run_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._table.setVisible(False)

        self._worker = BenchmarkWorker(self._backend)
        self._worker.progress.connect(self._on_progress)
        self._worker.result_ready.connect(self._on_results)
        self._worker.finished.connect(lambda: self._run_btn.setEnabled(True))
        self._worker.start()

    def _on_progress(self, value: int, message: str):
        self._progress.setValue(value)
        self._status_label.setText(message)

    def _on_results(self, results: dict):
        self._progress.setVisible(False)
        self._status_label.setText("Бенчмарк завершено!")

        # Resolution chart
        self._res_chart.set_data(
            results['resolutions'],
            results['cpu'],
            results['gpu'],
            "Час рендерингу (мс) — Мандельброт, 200 ітерацій"
        )

        # Iterations chart
        iter_labels = [str(i) for i in results['iterations_test']['iterations']]
        self._iter_chart.set_data(
            iter_labels,
            results['iterations_test']['cpu'],
            results['iterations_test']['gpu'],
            "Час рендерингу (мс) — Мандельброт, 800x600"
        )

        # Results table
        self._setup_results_table(results)
        self._table.setVisible(True)

    def _setup_results_table(self, results: dict):
        resolutions = results['resolutions']
        cpu_times = results['cpu']
        gpu_times = results['gpu']

        n = len(resolutions)
        has_gpu = any(t is not None for t in gpu_times)

        cols = 4 if has_gpu else 2
        self._table.setColumnCount(cols)
        self._table.setRowCount(n)

        headers = ["Роздільна здатність", "CPU (мс)"]
        if has_gpu:
            headers.extend(["GPU (мс)", "Прискорення"])
        self._table.setHorizontalHeaderLabels(headers)

        for i in range(n):
            self._table.setItem(i, 0, QTableWidgetItem(resolutions[i]))
            self._table.setItem(i, 1, QTableWidgetItem(f"{cpu_times[i]:.2f}"))

            if has_gpu and gpu_times[i] is not None:
                self._table.setItem(i, 2, QTableWidgetItem(f"{gpu_times[i]:.2f}"))
                speedup = cpu_times[i] / gpu_times[i] if gpu_times[i] > 0 else 0
                item = QTableWidgetItem(f"{speedup:.1f}x")
                if speedup > 10:
                    item.setForeground(QColor(52, 199, 89))
                elif speedup > 5:
                    item.setForeground(QColor(255, 204, 0))
                self._table.setItem(i, 3, item)

        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
