"""
Data Export Dialog - UI for exporting analysis results.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QCheckBox, QFileDialog, QMessageBox,
    QTabWidget, QWidget, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt

from ..analysis.data_export import get_exporter, AnalysisExporter


class ExportDialog(QDialog):
    """Dialog for exporting fractal analysis data."""

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self._renderer = renderer
        self._exporter = get_exporter()

        self.setWindowTitle("Експорт даних аналізу")
        self.setMinimumSize(500, 450)
        self._setup_ui()
        self._update_exporter_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "<h3>Експорт результатів аналізу</h3>"
            "<p style='color: #888;'>Збереження даних для наукових робіт та подальшого аналізу</p>"
        )
        layout.addWidget(header)

        # Tabs for different export types
        tabs = QTabWidget()

        # JSON tab
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)

        json_info = QLabel(
            "<p>JSON формат містить всі зібрані дані:</p>"
            "<ul>"
            "<li>Параметри фракталу</li>"
            "<li>Результати аналізу розмірності</li>"
            "<li>Дані бенчмарку</li>"
            "<li>Траєкторії орбіт</li>"
            "</ul>"
        )
        json_layout.addWidget(json_info)

        json_btn = QPushButton("Експортувати в JSON...")
        json_btn.clicked.connect(self._export_json)
        json_layout.addWidget(json_btn)
        json_layout.addStretch()

        tabs.addTab(json_tab, "JSON")

        # CSV tab
        csv_tab = QWidget()
        csv_layout = QVBoxLayout(csv_tab)

        csv_info = QLabel(
            "<p>CSV формат для імпорту в Excel, SPSS, R тощо:</p>"
        )
        csv_layout.addWidget(csv_info)

        self._csv_dimension = QCheckBox("Дані аналізу розмірності")
        self._csv_dimension.setChecked(True)
        csv_layout.addWidget(self._csv_dimension)

        self._csv_benchmark = QCheckBox("Дані бенчмарку")
        self._csv_benchmark.setChecked(True)
        csv_layout.addWidget(self._csv_benchmark)

        self._csv_orbit = QCheckBox("Дані орбіт")
        csv_layout.addWidget(self._csv_orbit)

        csv_btn = QPushButton("Експортувати в CSV...")
        csv_btn.clicked.connect(self._export_csv)
        csv_layout.addWidget(csv_btn)
        csv_layout.addStretch()

        tabs.addTab(csv_tab, "CSV")

        # LaTeX tab
        latex_tab = QWidget()
        latex_layout = QVBoxLayout(latex_tab)

        latex_info = QLabel(
            "<p>LaTeX таблиці для вставки в наукові статті:</p>"
        )
        latex_layout.addWidget(latex_info)

        self._latex_dimension = QCheckBox("Таблиця розмірності")
        self._latex_dimension.setChecked(True)
        latex_layout.addWidget(self._latex_dimension)

        self._latex_benchmark = QCheckBox("Таблиця бенчмарку")
        latex_layout.addWidget(self._latex_benchmark)

        latex_preview = QGroupBox("Попередній перегляд")
        preview_layout = QVBoxLayout(latex_preview)
        self._latex_preview = QTextEdit()
        self._latex_preview.setReadOnly(True)
        self._latex_preview.setMaximumHeight(150)
        self._latex_preview.setStyleSheet("font-family: monospace; font-size: 11px;")
        preview_layout.addWidget(self._latex_preview)
        latex_layout.addWidget(latex_preview)

        self._latex_dimension.stateChanged.connect(self._update_latex_preview)
        self._latex_benchmark.stateChanged.connect(self._update_latex_preview)

        latex_btn = QPushButton("Експортувати в LaTeX...")
        latex_btn.clicked.connect(self._export_latex)
        latex_layout.addWidget(latex_btn)
        latex_layout.addStretch()

        tabs.addTab(latex_tab, "LaTeX")

        layout.addWidget(tabs)

        # Current data summary
        summary_group = QGroupBox("Доступні дані для експорту")
        summary_layout = QVBoxLayout(summary_group)
        self._summary_label = QLabel("")
        self._summary_label.setStyleSheet("color: #aaa;")
        summary_layout.addWidget(self._summary_label)
        layout.addWidget(summary_group)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self._update_summary()
        self._update_latex_preview()

    def _update_exporter_data(self):
        """Update exporter with current renderer data."""
        # Set fractal info
        self._exporter.set_fractal_info(
            self._renderer.current_fractal_name,
            self._renderer.viewport.center_re,
            self._renderer.viewport.center_im,
            self._renderer.viewport.scale,
            self._renderer.get_max_iterations()
        )

        # Set render stats
        info = self._renderer.get_info()
        self._exporter.set_render_stats(
            800, 600,  # Default size
            info.get('render_time_ms', 0),
            info.get('backend', 'Unknown')
        )

    def _update_summary(self):
        """Update data summary display."""
        data = self._exporter._data
        items = []

        if 'fractal' in data:
            items.append(f"Фрактал: {data['fractal']['name']}")

        if 'dimension_analysis' in data:
            dim = data['dimension_analysis']['computed_dimension']
            items.append(f"Розмірність: D = {dim:.4f}")

        if 'benchmark' in data:
            items.append(f"Бенчмарк: {len(data['benchmark']['resolutions'])} тестів")

        if 'orbit_analysis' in data:
            items.append(f"Орбіта: {data['orbit_analysis']['num_iterations']} точок")

        if items:
            self._summary_label.setText("\n".join(items))
        else:
            self._summary_label.setText("Немає даних для експорту.\nЗапустіть аналіз розмірності або бенчмарк.")

    def _update_latex_preview(self):
        """Update LaTeX preview."""
        preview_lines = []

        if self._latex_dimension.isChecked():
            preview_lines.append("% Таблиця розмірності")
            preview_lines.append("\\begin{table}[h]")
            preview_lines.append("  \\caption{Box-counting dimension}")
            preview_lines.append("  ...")
            preview_lines.append("\\end{table}")
            preview_lines.append("")

        if self._latex_benchmark.isChecked():
            preview_lines.append("% Таблиця бенчмарку")
            preview_lines.append("\\begin{table}[h]")
            preview_lines.append("  \\caption{GPU vs CPU performance}")
            preview_lines.append("  ...")
            preview_lines.append("\\end{table}")

        self._latex_preview.setText("\n".join(preview_lines))

    def _export_json(self):
        """Export all data to JSON."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти JSON", "fractal_analysis.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if path:
            self._update_exporter_data()
            if self._exporter.export_json(path):
                QMessageBox.information(self, "Успіх", f"Дані збережено: {path}")
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося зберегти файл.")

    def _export_csv(self):
        """Export selected data to CSV files."""
        exported = []

        if self._csv_dimension.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self, "Зберегти дані розмірності", "dimension_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            if path and self._exporter.export_csv_dimension(path):
                exported.append("розмірність")

        if self._csv_benchmark.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self, "Зберегти дані бенчмарку", "benchmark_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            if path and self._exporter.export_csv_benchmark(path):
                exported.append("бенчмарк")

        if self._csv_orbit.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self, "Зберегти дані орбіти", "orbit_data.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            if path and self._exporter.export_csv_orbit(path):
                exported.append("орбіта")

        if exported:
            QMessageBox.information(
                self, "Успіх",
                f"Експортовано: {', '.join(exported)}"
            )

    def _export_latex(self):
        """Export LaTeX tables."""
        exported = []

        if self._latex_dimension.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self, "Зберегти LaTeX таблицю", "dimension_table.tex",
                "LaTeX Files (*.tex);;All Files (*)"
            )
            if path and self._exporter.export_latex_table(path, 'dimension'):
                exported.append("розмірність")

        if self._latex_benchmark.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self, "Зберегти LaTeX таблицю", "benchmark_table.tex",
                "LaTeX Files (*.tex);;All Files (*)"
            )
            if path and self._exporter.export_latex_table(path, 'benchmark'):
                exported.append("бенчмарк")

        if exported:
            QMessageBox.information(
                self, "Успіх",
                f"Експортовано LaTeX таблиці: {', '.join(exported)}"
            )


def set_dimension_data(dimension: float, r_squared: float,
                       box_sizes: list, box_counts: list,
                       theoretical: float = None):
    """Helper to set dimension data in global exporter."""
    get_exporter().set_dimension_data(
        dimension, r_squared, box_sizes, box_counts, theoretical
    )


def set_benchmark_data(resolutions: list, cpu_times: list,
                       gpu_times: list, iterations_test: dict = None):
    """Helper to set benchmark data in global exporter."""
    get_exporter().set_benchmark_data(
        resolutions, cpu_times, gpu_times, iterations_test
    )


def set_orbit_data(start_re: float, start_im: float,
                   orbit_points: list, escaped: bool,
                   fractal_type: str):
    """Helper to set orbit data in global exporter."""
    get_exporter().set_orbit_data(
        start_re, start_im, orbit_points, escaped, fractal_type
    )
