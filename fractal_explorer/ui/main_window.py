"""
Main application window.
"""

import math

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from .control_panel import ControlPanel
from .fractal_canvas import FractalCanvas
from .info_bar import InfoBar
from .animation_panel import AnimationPanel
from .julia_preview import JuliaPreviewWidget
from .orbit_viewer import OrbitOverlay
from ..rendering.renderer import FractalRenderer
from ..utils.export import export_image


class MainWindow(QMainWindow):
    """
    Main application window for Fractal Explorer.
    """

    def __init__(self):
        super().__init__()

        self._renderer = FractalRenderer()

        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animation_step)
        self._animation_angle = 0.0
        self._animation_speed = 0.03
        self._animation_radius = 0.7885
        self._animation_zoom_factor = 1.008
        self._animation_frame = 0

        self._color_cycling_active = False
        self._color_cycle_offset = 0.0
        self._color_cycle_timer = QTimer(self)
        self._color_cycle_timer.timeout.connect(self._color_cycle_step)

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._load_styles()

        self.setWindowTitle("Дослідник Фракталів")
        self.setMinimumSize(1024, 768)
        self.resize(1400, 900)

        self._update_backend_info()

    def _setup_ui(self):
        """Setup the main window UI."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Left control panel with vertical scroll
        self._control_panel = ControlPanel()

        self._control_scroll = QScrollArea()
        self._control_scroll.setWidget(self._control_panel)
        self._control_scroll.setWidgetResizable(False)
        self._control_scroll.setFixedWidth(270)
        self._control_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._control_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        content_layout.addWidget(self._control_scroll)

        self._canvas = FractalCanvas(self._renderer)
        content_layout.addWidget(self._canvas, stretch=1)

        self._orbit_overlay = OrbitOverlay(self._canvas)

        self._julia_preview = JuliaPreviewWidget(self._renderer, self._canvas)
        self._julia_preview.setVisible(False)

        self._animation_panel = AnimationPanel(self._renderer)
        self._animation_panel.setVisible(False)
        content_layout.addWidget(self._animation_panel)

        main_layout.addWidget(content, stretch=1)

        self._info_bar = InfoBar()
        main_layout.addWidget(self._info_bar)

    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Файл")

        save_action = QAction("&Зберегти зображення...", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("В&ихід", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("&Вигляд")

        reset_action = QAction("&Скинути вигляд", self)
        reset_action.setShortcut(QKeySequence("R"))
        reset_action.triggered.connect(self._on_reset)
        view_menu.addAction(reset_action)

        view_menu.addSeparator()

        self._anim_panel_action = QAction("&Панель анімації", self)
        self._anim_panel_action.setShortcut(QKeySequence("A"))
        self._anim_panel_action.setCheckable(True)
        self._anim_panel_action.triggered.connect(self._toggle_animation_panel)
        view_menu.addAction(self._anim_panel_action)

        analysis_menu = menubar.addMenu("&Аналіз")

        dimension_action = QAction("Фрактальна &розмірність...", self)
        dimension_action.setShortcut(QKeySequence("D"))
        dimension_action.triggered.connect(self._show_dimension_dialog)
        analysis_menu.addAction(dimension_action)

        benchmark_action = QAction("&Бенчмарк GPU/CPU...", self)
        benchmark_action.setShortcut(QKeySequence("B"))
        benchmark_action.triggered.connect(self._show_benchmark_dialog)
        analysis_menu.addAction(benchmark_action)

        analysis_menu.addSeparator()

        self._orbit_action = QAction("&Візуалізація орбіт", self)
        self._orbit_action.setShortcut(QKeySequence("O"))
        self._orbit_action.setCheckable(True)
        self._orbit_action.triggered.connect(self._toggle_orbit_mode)
        analysis_menu.addAction(self._orbit_action)

        self._julia_preview_action = QAction("Прев'ю &Жюліа", self)
        self._julia_preview_action.setShortcut(QKeySequence("J"))
        self._julia_preview_action.setCheckable(True)
        self._julia_preview_action.triggered.connect(self._toggle_julia_preview)
        analysis_menu.addAction(self._julia_preview_action)

        analysis_menu.addSeparator()

        self._color_cycle_action = QAction("&Циклічна анімація кольору", self)
        self._color_cycle_action.setShortcut(QKeySequence("C"))
        self._color_cycle_action.setCheckable(True)
        self._color_cycle_action.triggered.connect(self._toggle_color_cycling)
        analysis_menu.addAction(self._color_cycle_action)

        analysis_menu.addSeparator()

        export_action = QAction("&Експорт даних аналізу...", self)
        export_action.setShortcut(QKeySequence("E"))
        export_action.triggered.connect(self._show_export_dialog)
        analysis_menu.addAction(export_action)

        apps_menu = menubar.addMenu("&Застосування")

        texture_action = QAction("&Генератор текстур...", self)
        texture_action.setShortcut(QKeySequence("T"))
        texture_action.triggered.connect(self._show_texture_generator)
        apps_menu.addAction(texture_action)

        apps_menu.addSeparator()

        demo_action = QAction("&Демонстраційні тури...", self)
        demo_action.setShortcut(QKeySequence("F5"))
        demo_action.triggered.connect(self._show_demo_tours)
        apps_menu.addAction(demo_action)

        help_menu = menubar.addMenu("&Довідка")

        shortcuts_action = QAction("&Клавіатурні скорочення", self)
        shortcuts_action.setShortcut(QKeySequence("F1"))
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)

        math_action = QAction("&Математика фракталів", self)
        math_action.triggered.connect(self._show_math_help)
        help_menu.addAction(math_action)

        help_menu.addSeparator()

        about_action = QAction("&Про програму", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        """Connect UI signals."""
        self._control_panel.fractal_changed.connect(self._on_fractal_changed)
        self._control_panel.iterations_changed.connect(self._on_iterations_changed)
        self._control_panel.colormap_changed.connect(self._on_colormap_changed)
        self._control_panel.julia_c_changed.connect(self._on_julia_c_changed)
        self._control_panel.tree_params_changed.connect(self._on_tree_params_changed)
        self._control_panel.phoenix_p_changed.connect(self._on_phoenix_p_changed)
        self._control_panel.reset_requested.connect(self._on_reset)
        self._control_panel.save_requested.connect(self._on_save)
        self._control_panel.animation_toggled.connect(self._on_animation_toggled)

        self._canvas.cursor_moved.connect(self._info_bar.update_cursor)
        self._canvas.cursor_moved.connect(self._on_cursor_moved)
        self._canvas.render_complete.connect(self._on_render_complete)

    def _load_styles(self):
        """Load stylesheet."""
        try:
            import importlib.resources as pkg_resources
            from .. import resources

            style_path = pkg_resources.files(resources) / "styles.qss"

            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            self.setStyleSheet(self._get_default_style())

    def _get_default_style(self) -> str:
        """Get default dark theme stylesheet."""
        return """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }

            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background-color: #3c3c3c;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QGroupBox {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #ffffff;
            }

            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1177bb;
            }

            QPushButton:pressed {
                background-color: #0d5289;
            }

            QPushButton:checked {
                background-color: #cc6633;
            }

            QSlider::groove:horizontal {
                border: 1px solid #3c3c3c;
                height: 6px;
                background: #2d2d2d;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #0e639c;
                border: none;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }

            QSlider::handle:horizontal:hover {
                background: #1177bb;
            }

            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px 10px;
                color: #cccccc;
            }

            QComboBox:hover {
                border-color: #0e639c;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                selection-background-color: #0e639c;
            }

            QSpinBox, QDoubleSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
                color: #cccccc;
            }

            QSpinBox:hover, QDoubleSpinBox:hover {
                border-color: #0e639c;
            }

            QRadioButton {
                spacing: 8px;
                color: #cccccc;
            }

            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }

            QRadioButton::indicator:unchecked {
                border: 2px solid #3c3c3c;
                border-radius: 9px;
                background: #2d2d2d;
            }

            QRadioButton::indicator:checked {
                border: 2px solid #0e639c;
                border-radius: 9px;
                background: #0e639c;
            }

            QMenuBar {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3c3c3c;
            }

            QMenuBar::item {
                padding: 5px 10px;
            }

            QMenuBar::item:selected {
                background-color: #3c3c3c;
            }

            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
            }

            QMenu::item {
                padding: 5px 30px 5px 20px;
            }

            QMenu::item:selected {
                background-color: #0e639c;
            }
        """

    def _on_fractal_changed(self, name: str):
        """Handle fractal type change."""
        self._control_panel.stop_animation()
        self._renderer.set_fractal_type(name)

        if name == "julia":
            c_re, c_im = self._renderer.get_julia_c()
            self._control_panel.set_julia_c(c_re, c_im)
        elif name == "pythagoras":
            angle, depth = self._renderer.get_tree_params()
            self._control_panel.set_tree_params(angle, depth)
        elif name == "phoenix":
            p_re, p_im = self._renderer.get_phoenix_p()
            self._control_panel.set_phoenix_p(p_re, p_im)

        self._control_panel.set_iterations(self._renderer.get_max_iterations())
        self._canvas.request_render(immediate=True)

    def _on_iterations_changed(self, value: int):
        """Handle iterations change."""
        self._renderer.set_max_iterations(value)
        self._canvas.request_render(immediate=True)

    def _on_colormap_changed(self, name: str):
        """Handle colormap change."""
        self._renderer.set_colormap(name)
        self._canvas.request_render(immediate=True)

    def _on_julia_c_changed(self, c_re: float, c_im: float):
        """Handle Julia c parameter change."""
        self._renderer.set_julia_c(c_re, c_im)
        self._canvas.request_render(immediate=True)

    def _on_tree_params_changed(self, angle: float, depth: int):
        """Handle tree parameter change."""
        self._renderer.set_tree_params(angle, depth)
        self._canvas.request_render(immediate=True)

    def _on_phoenix_p_changed(self, p_re: float, p_im: float):
        """Handle Phoenix p parameter change."""
        self._renderer.set_phoenix_p(p_re, p_im)
        self._canvas.request_render(immediate=True)

    def _on_reset(self):
        """Handle reset view."""
        self._control_panel.stop_animation()
        self._renderer.reset_view()
        self._control_panel.set_iterations(self._renderer.get_max_iterations())
        self._canvas.request_render(immediate=True)

    def _on_save(self):
        """Handle save image."""
        rgba = self._canvas.get_current_rgba()

        if rgba is None:
            QMessageBox.warning(
                self,
                "Помилка збереження",
                "Немає зображення для збереження. Зачекайте завершення рендерингу."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти зображення фракталу",
            "fractal.png",
            "PNG зображення (*.png);;JPEG зображення (*.jpg);;Всі файли (*)"
        )

        if file_path:
            try:
                export_image(rgba, file_path)
                QMessageBox.information(
                    self,
                    "Збереження завершено",
                    f"Зображення збережено:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Помилка збереження",
                    f"Не вдалося зберегти зображення:\n{str(e)}"
                )

    def _on_animation_toggled(self, running: bool):
        """Handle animation toggle."""
        if running:
            self._animation_angle = 0.0
            self._animation_frame = 0
            self._canvas.set_animation_mode(True)
            self._animation_timer.start(16)
        else:
            self._animation_timer.stop()
            self._canvas.set_animation_mode(False)
            self._canvas.request_render(immediate=True)

    def _animation_step(self):
        """Perform one animation step with smooth infinite zoom illusion."""
        fractal_name = self._renderer.current_fractal_name
        self._animation_frame += 1

        if fractal_name == "julia":
            self._animation_angle += self._animation_speed

            radius_mod = self._animation_radius * (
                1.0 + 0.05 * math.sin(self._animation_angle * 2)
            )

            c_re = radius_mod * math.cos(self._animation_angle)
            c_im = radius_mod * math.sin(self._animation_angle)

            self._renderer.set_julia_c(c_re, c_im)

            if self._animation_frame % 5 == 0:
                self._control_panel.set_julia_c(c_re, c_im)

        elif fractal_name == "mandelbrot":
            target_re = -0.74364388703
            target_im = 0.13182590421

            blend = 0.015
            self._renderer.viewport.center_re += (
                target_re - self._renderer.viewport.center_re
            ) * blend
            self._renderer.viewport.center_im += (
                target_im - self._renderer.viewport.center_im
            ) * blend

            self._renderer.viewport.scale *= 1.0 / self._animation_zoom_factor

            if self._renderer.viewport.scale < 1e-13:
                self._renderer.viewport.scale = 3.5
                self._renderer.viewport.center_re = -0.5
                self._renderer.viewport.center_im = 0.0

        elif fractal_name == "newton":
            self._animation_angle += self._animation_speed * 0.7

            spiral_t = self._animation_angle * 0.5
            radius = 0.25 + 0.15 * math.sin(spiral_t * 1.5)

            self._renderer.viewport.center_re = radius * math.cos(self._animation_angle)
            self._renderer.viewport.center_im = radius * math.sin(self._animation_angle)

            zoom_pulse = 2.2 + 0.8 * math.sin(self._animation_angle * 0.8)
            self._renderer.viewport.scale = zoom_pulse

        elif fractal_name == "pythagoras":
            self._animation_frame += 1

            angle_deg = self._renderer.get_tree_params()[0]
            angle_rad = math.radians(angle_deg)

            _branch_scale = math.cos(angle_rad)

            zoom_factor = 1.012
            current_scale = self._renderer.viewport.scale
            new_scale = current_scale / zoom_factor

            t = self._animation_frame * 0.008

            target_x = -0.3 * math.sin(t * 0.5)
            target_y = 1.0 + t * 0.5

            blend = 0.02
            self._renderer.viewport.center_re += (
                target_x - self._renderer.viewport.center_re
            ) * blend
            self._renderer.viewport.center_im += (
                target_y - self._renderer.viewport.center_im
            ) * blend
            self._renderer.viewport.scale = new_scale

            if new_scale < 0.05:
                self._renderer.viewport.reset(0, 0.8, 4.5)
                self._animation_frame = 0

        elif fractal_name == "burning_ship":
            target_re = -1.762
            target_im = -0.028

            blend = 0.015
            self._renderer.viewport.center_re += (
                target_re - self._renderer.viewport.center_re
            ) * blend
            self._renderer.viewport.center_im += (
                target_im - self._renderer.viewport.center_im
            ) * blend

            self._renderer.viewport.scale *= 1.0 / self._animation_zoom_factor

            if self._renderer.viewport.scale < 1e-13:
                self._renderer.viewport.scale = 3.5
                self._renderer.viewport.center_re = -0.4
                self._renderer.viewport.center_im = -0.5

        elif fractal_name == "tricorn":
            self._animation_angle += self._animation_speed * 0.5

            target_re = -1.0
            target_im = 0.0

            blend = 0.01
            self._renderer.viewport.center_re += (
                target_re - self._renderer.viewport.center_re
            ) * blend
            self._renderer.viewport.center_im += (
                target_im - self._renderer.viewport.center_im
            ) * blend

            self._renderer.viewport.scale *= 1.0 / self._animation_zoom_factor

            if self._renderer.viewport.scale < 1e-13:
                self._renderer.viewport.scale = 3.5
                self._renderer.viewport.center_re = -0.3
                self._renderer.viewport.center_im = 0.0

        elif fractal_name == "phoenix":
            self._animation_angle += self._animation_speed

            base_re = 0.5667
            base_im = -0.5
            radius = 0.15

            p_re = base_re + radius * math.cos(self._animation_angle)
            p_im = base_im + radius * math.sin(self._animation_angle * 0.7)

            self._renderer.set_phoenix_p(p_re, p_im)

            if self._animation_frame % 5 == 0:
                self._control_panel.set_phoenix_p(p_re, p_im)

        self._canvas.request_render(immediate=True)

    def _on_render_complete(self, info: dict):
        """Handle render completion."""
        self._info_bar.update_all(info)
        self._update_backend_info()

    def _update_backend_info(self):
        """Update info bar with detailed backend status."""
        status = self._renderer.backend.get_status()
        detailed = self._renderer.backend.get_detailed_status()
        self._info_bar.update_backend_detailed(status, detailed)

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "Про Дослідник Фракталів",
            "<h2>Дослідник Фракталів v3.0</h2>"
            "<p>Інтерактивна візуалізація та аналіз фракталів</p>"
            "<hr>"
            "<p><b>11 типів фракталів:</b> Мандельброт, Жюліа, Ньютон, "
            "Піфагор, Палаючий Корабель, Трикорн, Фенікс, "
            "Папороть Барнслі, Серпінський, Коха, Буддаброт</p>"
            "<hr>"
            "<p><b>Клавіатурні скорочення:</b></p>"
            "<table>"
            "<tr><td><b>Колесо миші</b></td><td>— масштабування</td></tr>"
            "<tr><td><b>ЛКМ + тягнути</b></td><td>— переміщення</td></tr>"
            "<tr><td><b>Подвійний клік</b></td><td>— центрувати + zoom</td></tr>"
            "<tr><td><b>R</b></td><td>— скинути вигляд</td></tr>"
            "<tr><td><b>J</b></td><td>— превью Жюліа</td></tr>"
            "<tr><td><b>O</b></td><td>— візуалізація орбіт</td></tr>"
            "<tr><td><b>C</b></td><td>— циклічна анімація</td></tr>"
            "<tr><td><b>D</b></td><td>— розмірність</td></tr>"
            "<tr><td><b>B</b></td><td>— бенчмарк</td></tr>"
            "<tr><td><b>A</b></td><td>— панель анімації</td></tr>"
            "<tr><td><b>Ctrl+S</b></td><td>— зберегти</td></tr>"
            "</table>"
            "<hr>"
            "<p><b>GPU:</b> CUDA (CuPy) | <b>CPU:</b> Numba JIT</p>"
        )

    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        QMessageBox.information(
            self,
            "Клавіатурні скорочення",
            "<style>td { padding: 4px 12px; }</style>"
            "<h3>Навігація</h3>"
            "<table>"
            "<tr><td><b>Колесо миші</b></td><td>Масштабування (zoom in/out)</td></tr>"
            "<tr><td><b>ЛКМ + тягнути</b></td><td>Переміщення (pan)</td></tr>"
            "<tr><td><b>Подвійний клік</b></td><td>Центрувати та збільшити</td></tr>"
            "<tr><td><b>R</b></td><td>Скинути вигляд до початкового</td></tr>"
            "</table>"
            "<h3>Аналіз</h3>"
            "<table>"
            "<tr><td><b>J</b></td><td>Превью Жюліа (тільки для Мандельброта)</td></tr>"
            "<tr><td><b>O</b></td><td>Візуалізація орбіт (клік = показати орбіту)</td></tr>"
            "<tr><td><b>D</b></td><td>Обчислити фрактальну розмірність</td></tr>"
            "<tr><td><b>B</b></td><td>Бенчмарк GPU vs CPU</td></tr>"
            "<tr><td><b>C</b></td><td>Циклічна анімація кольору</td></tr>"
            "</table>"
            "<h3>Інше</h3>"
            "<table>"
            "<tr><td><b>A</b></td><td>Панель анімації</td></tr>"
            "<tr><td><b>T</b></td><td>Генератор текстур</td></tr>"
            "<tr><td><b>E</b></td><td>Експорт даних аналізу</td></tr>"
            "<tr><td><b>F5</b></td><td>Демонстраційні тури</td></tr>"
            "<tr><td><b>Ctrl+S</b></td><td>Зберегти зображення</td></tr>"
            "<tr><td><b>F1</b></td><td>Ця довідка</td></tr>"
            "</table>"
        )

    def _show_math_help(self):
        """Show mathematical descriptions of fractals."""
        from .math_help_dialog import MathHelpDialog

        dialog = MathHelpDialog(self)
        dialog.exec()

    def _toggle_animation_panel(self, checked: bool):
        """Toggle animation panel visibility."""
        self._animation_panel.setVisible(checked)

    def _on_cursor_moved(self, re: float, im: float):
        """Handle cursor movement for Julia preview."""
        if self._julia_preview.isVisible() and self._renderer.current_fractal_name == "mandelbrot":
            self._julia_preview.update_c(re, im)

    def _toggle_julia_preview(self, checked: bool):
        """Toggle Julia preview overlay."""
        show = checked and self._renderer.current_fractal_name == "mandelbrot"
        self._julia_preview.setVisible(show)

        if show:
            self._julia_preview.position_in_corner()
            self._julia_preview.sync_colormap()
            self._julia_preview.raise_()

    def _toggle_orbit_mode(self, checked: bool):
        """Toggle orbit visualization mode."""
        if checked:
            self._orbit_overlay.setGeometry(
                0,
                0,
                self._canvas.width(),
                self._canvas.height()
            )
            self._orbit_overlay.raise_()

            aspect_ratio = self._canvas.width() / max(1, self._canvas.height())
            x_min, x_max, y_min, y_max = self._renderer.viewport.get_bounds(aspect_ratio)
            self._orbit_overlay.set_viewport(x_min, x_max, y_min, y_max)

            c_re, c_im = 0.0, 0.0
            p_re, p_im = 0.0, 0.0

            if self._renderer.current_fractal_name == "julia":
                c_re, c_im = self._renderer.get_julia_c()
            elif self._renderer.current_fractal_name == "phoenix":
                p_re, p_im = self._renderer.get_phoenix_p()

            self._orbit_overlay.set_fractal_params(
                self._renderer.current_fractal_name,
                self._renderer.get_max_iterations(),
                c_re,
                c_im,
                p_re,
                p_im
            )

        self._orbit_overlay.set_active(checked)

    def _toggle_color_cycling(self, checked: bool):
        """Toggle color cycling animation."""
        self._color_cycling_active = checked

        if checked:
            self._color_cycle_timer.start(33)
        else:
            self._color_cycle_timer.stop()
            self._canvas.request_render(immediate=True)

    def _color_cycle_step(self):
        """Perform one step of color cycling animation."""
        self._color_cycle_offset += 0.02

        if self._color_cycle_offset > 1.0:
            self._color_cycle_offset -= 1.0

        self._canvas.apply_color_shift(self._color_cycle_offset)

    def _show_dimension_dialog(self):
        """Show fractal dimension calculation dialog."""
        iterations = self._renderer.get_last_iterations()

        if iterations is None:
            QMessageBox.warning(
                self,
                "Помилка",
                "Немає даних для аналізу. Спочатку відрендеріть фрактал."
            )
            return

        from .dimension_dialog import DimensionDialog

        dialog = DimensionDialog(
            iterations,
            self._renderer.get_max_iterations(),
            self._renderer.current_fractal_name,
            self
        )
        dialog.exec()

    def _show_benchmark_dialog(self):
        """Show GPU vs CPU benchmark dialog."""
        from .benchmark_dialog import BenchmarkDialog

        dialog = BenchmarkDialog(self._renderer.backend, self)
        dialog.exec()

    def _show_export_dialog(self):
        """Show data export dialog."""
        from .export_dialog import ExportDialog

        dialog = ExportDialog(self._renderer, self)
        dialog.exec()

    def _show_texture_generator(self):
        """Show texture generator dialog."""
        from .texture_dialog import TextureDialog

        dialog = TextureDialog(self)
        dialog.exec()

    def _show_demo_tours(self):
        """Show demo tours dialog."""
        from .demo_tour import DemoTourDialog

        dialog = DemoTourDialog(self._renderer, self._canvas, self)
        dialog.exec()

        self._canvas.request_render(immediate=True)

    def showEvent(self, event):
        """Handle window show - initialize overlay size."""
        super().showEvent(event)

        if hasattr(self, "_orbit_overlay") and hasattr(self, "_canvas"):
            QTimer.singleShot(100, self._size_orbit_overlay)

    def _size_orbit_overlay(self):
        """Size orbit overlay to match canvas."""
        if hasattr(self, "_orbit_overlay") and hasattr(self, "_canvas"):
            self._orbit_overlay.setGeometry(
                0,
                0,
                self._canvas.width(),
                self._canvas.height()
            )

        if hasattr(self, "_julia_preview") and self._julia_preview.isVisible():
            self._julia_preview.position_in_corner()

    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        self._size_orbit_overlay()

    def closeEvent(self, event):
        """Handle window close."""
        self._animation_timer.stop()
        self._color_cycle_timer.stop()
        self._animation_panel.stop_rendering()
        event.accept()