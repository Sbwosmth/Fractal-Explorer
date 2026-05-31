"""
Animation control panel for creating and exporting fractal animations.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot

from ..animation import (
    AnimationEngine, ZoomAnimation, JuliaOrbitAnimation,
    MorphAnimation, AnimationState
)
from ..animation.animation_types import PhoenixOrbitAnimation
from ..animation.video_encoder import check_ffmpeg_available


class AnimationWorker(QThread):
    """Background worker for animation rendering."""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, engine, animation, width, height, output_path, format, keep_frames=False):
        super().__init__()
        self.engine = engine
        self.animation = animation
        self.width = width
        self.height = height
        self.output_path = output_path
        self.format = format
        self.keep_frames = keep_frames

    def run(self):
        """Run animation rendering in background."""
        def progress_callback(current, total, message):
            self.progress.emit(current, total, message)

        try:
            success = self.engine.render_animation(
                self.animation,
                self.width,
                self.height,
                self.output_path,
                self.format,
                progress_callback,
                self.keep_frames
            )

            if success:
                self.finished.emit(True, f"Анімацію збережено: {self.output_path}")
            elif self.engine.is_cancelled():
                self.finished.emit(False, "Анімацію скасовано")
            else:
                self.finished.emit(False, "Помилка рендерингу анімації")

        except Exception as e:
            self.finished.emit(False, f"Помилка: {str(e)}")

    def cancel(self):
        """Cancel rendering."""
        self.engine.cancel()


class AnimationPanel(QWidget):
    """
    Panel for configuring and exporting fractal animations.
    """

    animation_started = pyqtSignal()
    animation_finished = pyqtSignal()

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.engine = AnimationEngine(renderer)
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the animation panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Експорт анімації")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Animation type selection
        layout.addWidget(self._create_type_group())

        # Parameters
        layout.addWidget(self._create_params_group())

        # Output settings
        layout.addWidget(self._create_output_group())

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._status_label = QLabel("")
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        # Buttons
        layout.addWidget(self._create_buttons())

        # FFmpeg status
        self._ffmpeg_label = QLabel()
        self._update_ffmpeg_status()
        layout.addWidget(self._ffmpeg_label)

        layout.addStretch()

        self.setFixedWidth(280)

    def _create_type_group(self) -> QGroupBox:
        """Create animation type selection group."""
        group = QGroupBox("Тип анімації")
        layout = QVBoxLayout(group)

        self._type_combo = QComboBox()
        self._type_combo.addItems([
            "Зум до точки",
            "Орбіта Жюліа",
            "Орбіта Фенікса",
            "Морфінг"
        ])
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addWidget(self._type_combo)

        return group

    def _create_params_group(self) -> QGroupBox:
        """Create animation parameters group."""
        group = QGroupBox("Параметри")
        layout = QVBoxLayout(group)

        # Duration
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("Тривалість (с):"))
        self._duration_spin = QDoubleSpinBox()
        self._duration_spin.setRange(1.0, 120.0)
        self._duration_spin.setValue(10.0)
        self._duration_spin.setSingleStep(1.0)
        dur_layout.addWidget(self._duration_spin)
        layout.addLayout(dur_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Кадрів/сек:"))
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(15, 60)
        self._fps_spin.setValue(30)
        fps_layout.addWidget(self._fps_spin)
        layout.addLayout(fps_layout)

        # Resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Роздільність:"))
        self._resolution_combo = QComboBox()
        self._resolution_combo.addItems([
            "640x480",
            "800x600",
            "1280x720 (HD)",
            "1920x1080 (Full HD)",
            "2560x1440 (2K)",
            "3840x2160 (4K)"
        ])
        self._resolution_combo.setCurrentText("1280x720 (HD)")
        res_layout.addWidget(self._resolution_combo)
        layout.addLayout(res_layout)

        # Zoom depth (for zoom animation)
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Глибина зуму:"))
        self._zoom_depth_spin = QSpinBox()
        self._zoom_depth_spin.setRange(2, 15)
        self._zoom_depth_spin.setValue(10)
        self._zoom_depth_spin.setToolTip("Показник степеня глибини зуму (10^N)")
        zoom_layout.addWidget(self._zoom_depth_spin)
        self._zoom_layout_widget = QWidget()
        self._zoom_layout_widget.setLayout(zoom_layout)
        layout.addWidget(self._zoom_layout_widget)

        return group

    def _create_output_group(self) -> QGroupBox:
        """Create output settings group."""
        group = QGroupBox("Вивід")
        layout = QVBoxLayout(group)

        # Format
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Формат:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["MP4", "GIF", "PNG послідовність"])
        fmt_layout.addWidget(self._format_combo)
        layout.addLayout(fmt_layout)

        # Keep frames checkbox
        self._keep_frames_check = QCheckBox("Зберегти PNG кадри")
        self._keep_frames_check.setChecked(False)
        layout.addWidget(self._keep_frames_check)

        return group

    def _create_buttons(self) -> QWidget:
        """Create action buttons."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Render button
        self._render_btn = QPushButton("Створити анімацію")
        self._render_btn.clicked.connect(self._on_render_clicked)
        layout.addWidget(self._render_btn)

        # Cancel button
        self._cancel_btn = QPushButton("Скасувати")
        self._cancel_btn.clicked.connect(self._on_cancel_clicked)
        self._cancel_btn.setVisible(False)
        layout.addWidget(self._cancel_btn)

        return widget

    def _update_ffmpeg_status(self):
        """Update FFmpeg availability status."""
        available, version = check_ffmpeg_available()
        if available:
            self._ffmpeg_label.setText("FFmpeg: доступний")
            self._ffmpeg_label.setStyleSheet("color: #4a4;")
        else:
            self._ffmpeg_label.setText("FFmpeg: не знайдено (тільки PNG)")
            self._ffmpeg_label.setStyleSheet("color: #a44;")
            # Disable video formats if FFmpeg not available
            self._format_combo.setCurrentText("PNG послідовність")

    def _on_type_changed(self, type_name: str):
        """Handle animation type change."""
        # Show/hide zoom depth based on type
        is_zoom = type_name == "Зум до точки"
        self._zoom_layout_widget.setVisible(is_zoom)

    def _get_resolution(self) -> tuple:
        """Get selected resolution as (width, height)."""
        text = self._resolution_combo.currentText()
        # Parse resolution from text like "1280x720 (HD)"
        res_part = text.split(" ")[0]
        w, h = res_part.split("x")
        return int(w), int(h)

    def _create_animation(self):
        """Create animation based on current settings."""
        duration = self._duration_spin.value()
        fps = self._fps_spin.value()
        anim_type = self._type_combo.currentText()

        # Get current viewport state
        viewport = self.renderer.viewport
        fractal_name = self.renderer.current_fractal_name

        if anim_type == "Зум до точки":
            # Create zoom animation toward current center
            zoom_depth = self._zoom_depth_spin.value()
            target_scale = viewport.scale / (10 ** zoom_depth)

            return ZoomAnimation(
                start_center_re=viewport.center_re,
                start_center_im=viewport.center_im,
                start_scale=viewport.scale,
                target_re=viewport.center_re,
                target_im=viewport.center_im,
                end_scale=target_scale,
                duration_seconds=duration,
                fps=fps
            )

        elif anim_type == "Орбіта Жюліа":
            if fractal_name != 'julia':
                QMessageBox.warning(
                    self, "Увага",
                    "Орбіта Жюліа працює тільки для множини Жюліа.\n"
                    "Переключіться на фрактал Жюліа."
                )
                return None

            c_re, c_im = self.renderer.get_julia_c()
            return JuliaOrbitAnimation(
                center_re=viewport.center_re,
                center_im=viewport.center_im,
                scale=viewport.scale,
                c_center_re=0.0,
                c_center_im=0.0,
                c_radius=0.7885,
                duration_seconds=duration,
                fps=fps,
                orbits=1.0
            )

        elif anim_type == "Орбіта Фенікса":
            if fractal_name != 'phoenix':
                QMessageBox.warning(
                    self, "Увага",
                    "Орбіта Фенікса працює тільки для фракталу Фенікс.\n"
                    "Переключіться на фрактал Фенікс."
                )
                return None

            return PhoenixOrbitAnimation(
                center_re=viewport.center_re,
                center_im=viewport.center_im,
                scale=viewport.scale,
                p_center_re=0.5667,
                p_center_im=-0.5,
                p_radius=0.15,
                duration_seconds=duration,
                fps=fps,
                orbits=1.0
            )

        elif anim_type == "Морфінг":
            # Create morph from current state to zoomed-in state
            start_state = AnimationState(
                center_re=viewport.center_re,
                center_im=viewport.center_im,
                scale=viewport.scale
            )
            end_state = AnimationState(
                center_re=viewport.center_re,
                center_im=viewport.center_im,
                scale=viewport.scale / 100  # Zoom in 100x
            )
            return MorphAnimation(
                start_state=start_state,
                end_state=end_state,
                duration_seconds=duration,
                fps=fps
            )

        return None

    def _on_render_clicked(self):
        """Handle render button click."""
        animation = self._create_animation()
        if animation is None:
            return

        # Get output settings
        format_text = self._format_combo.currentText()
        if format_text == "MP4":
            ext = "mp4"
            filter_str = "MP4 відео (*.mp4)"
        elif format_text == "GIF":
            ext = "gif"
            filter_str = "GIF анімація (*.gif)"
        else:
            ext = None
            filter_str = "PNG зображення (*.png)"

        # Check FFmpeg for video formats
        if ext in ("mp4", "gif") and not self.engine.ffmpeg_available:
            QMessageBox.warning(
                self, "FFmpeg не знайдено",
                "Для створення відео потрібен FFmpeg.\n"
                "Встановіть FFmpeg або оберіть PNG послідовність."
            )
            return

        # Get output path
        if ext:
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Зберегти анімацію",
                f"fractal_animation.{ext}",
                filter_str
            )
        else:
            output_path = QFileDialog.getExistingDirectory(
                self,
                "Обрати папку для кадрів"
            )

        if not output_path:
            return

        # Get resolution
        width, height = self._get_resolution()

        # Start rendering
        self._render_btn.setVisible(False)
        self._cancel_btn.setVisible(True)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_label.setVisible(True)
        self._status_label.setText("Підготовка...")

        self.animation_started.emit()

        if ext:
            # Video output
            self._worker = AnimationWorker(
                self.engine,
                animation,
                width, height,
                output_path,
                ext,
                self._keep_frames_check.isChecked()
            )
        else:
            # PNG sequence - use frames-only mode
            self._worker = AnimationWorker(
                self.engine,
                animation,
                width, height,
                os.path.join(output_path, "frame.png"),  # Will be handled specially
                "png",
                True  # Keep frames
            )

        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        if self._worker:
            self._worker.cancel()
            self._status_label.setText("Скасування...")

    @pyqtSlot(int, int, str)
    def _on_progress(self, current: int, total: int, message: str):
        """Handle progress update."""
        if total > 0:
            self._progress_bar.setMaximum(total)
            self._progress_bar.setValue(current)
        self._status_label.setText(message)

    @pyqtSlot(bool, str)
    def _on_finished(self, success: bool, message: str):
        """Handle rendering finished."""
        self._render_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setVisible(False)
        self._status_label.setText(message)

        self.animation_finished.emit()

        if success:
            QMessageBox.information(self, "Готово", message)
        elif "скасовано" not in message.lower():
            QMessageBox.warning(self, "Помилка", message)

        self._worker = None

    def stop_rendering(self):
        """Stop any ongoing rendering."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
