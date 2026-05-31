"""
Texture Generator Dialog - UI for fractal texture generation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QSlider, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

import numpy as np

from ..applications.texture_generator import (
    TextureGenerator, TextureType, apply_colormap_to_texture
)


class TexturePreviewWidget(QWidget):
    """Widget for displaying texture preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setMinimumSize(256, 256)
        self.setStyleSheet("background: #1a1a1a; border: 1px solid #3c3c3c;")

    def set_texture(self, rgba: np.ndarray):
        """Set the texture to display."""
        height, width = rgba.shape[:2]
        qimage = QImage(
            rgba.data.tobytes(),
            width, height,
            width * 4,
            QImage.Format.Format_RGBA8888
        )
        self._pixmap = QPixmap.fromImage(qimage)
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter
        painter = QPainter(self)
        if self._pixmap:
            # Scale to fit while maintaining aspect ratio
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        painter.end()


class TextureDialog(QDialog):
    """Dialog for generating fractal textures."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._generator = TextureGenerator()
        self._current_grayscale = None
        self._current_rgba = None

        self.setWindowTitle("Генератор фрактальних текстур")
        self.setMinimumSize(700, 550)
        self._setup_ui()
        self._generate_preview()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel - controls
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls.setFixedWidth(280)

        # Texture type
        type_group = QGroupBox("Тип текстури")
        type_layout = QVBoxLayout(type_group)

        self._type_combo = QComboBox()
        texture_types = TextureGenerator.get_texture_types()
        for tex_type, name in texture_types.items():
            self._type_combo.addItem(name, tex_type)
        self._type_combo.currentIndexChanged.connect(self._generate_preview)
        type_layout.addWidget(self._type_combo)
        controls_layout.addWidget(type_group)

        # Parameters
        param_group = QGroupBox("Параметри")
        param_layout = QVBoxLayout(param_group)

        # Main parameter slider
        param_layout.addWidget(QLabel("Інтенсивність:"))
        self._param_slider = QSlider(Qt.Orientation.Horizontal)
        self._param_slider.setRange(0, 100)
        self._param_slider.setValue(50)
        self._param_slider.valueChanged.connect(self._generate_preview)
        param_layout.addWidget(self._param_slider)

        # Seed
        seed_layout = QHBoxLayout()
        seed_layout.addWidget(QLabel("Seed:"))
        self._seed_spin = QSpinBox()
        self._seed_spin.setRange(0, 999999)
        self._seed_spin.setValue(42)
        self._seed_spin.valueChanged.connect(self._generate_preview)
        seed_layout.addWidget(self._seed_spin)

        randomize_btn = QPushButton("🎲")
        randomize_btn.setFixedWidth(30)
        randomize_btn.clicked.connect(self._randomize_seed)
        seed_layout.addWidget(randomize_btn)
        param_layout.addLayout(seed_layout)

        controls_layout.addWidget(param_group)

        # Size
        size_group = QGroupBox("Розмір")
        size_layout = QHBoxLayout(size_group)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(64, 2048)
        self._width_spin.setValue(512)
        self._width_spin.setSingleStep(64)
        size_layout.addWidget(QLabel("Ш:"))
        size_layout.addWidget(self._width_spin)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(64, 2048)
        self._height_spin.setValue(512)
        self._height_spin.setSingleStep(64)
        size_layout.addWidget(QLabel("В:"))
        size_layout.addWidget(self._height_spin)

        controls_layout.addWidget(size_group)

        # Colormap
        color_group = QGroupBox("Кольорова схема")
        color_layout = QVBoxLayout(color_group)

        self._colormap_combo = QComboBox()
        colormaps = TextureGenerator.get_colormaps()
        for cmap_id, name in colormaps.items():
            self._colormap_combo.addItem(name, cmap_id)
        self._colormap_combo.currentIndexChanged.connect(self._update_colormap)
        color_layout.addWidget(self._colormap_combo)

        controls_layout.addWidget(color_group)

        # Options
        options_group = QGroupBox("Опції")
        options_layout = QVBoxLayout(options_group)

        self._seamless_check = QCheckBox("Безшовна текстура (tileable)")
        self._seamless_check.setChecked(True)
        self._seamless_check.stateChanged.connect(self._generate_preview)
        options_layout.addWidget(self._seamless_check)

        controls_layout.addWidget(options_group)

        # Buttons
        controls_layout.addStretch()

        generate_btn = QPushButton("Згенерувати")
        generate_btn.clicked.connect(self._generate_full)
        controls_layout.addWidget(generate_btn)

        save_btn = QPushButton("Зберегти текстуру...")
        save_btn.clicked.connect(self._save_texture)
        controls_layout.addWidget(save_btn)

        save_height_btn = QPushButton("Зберегти heightmap...")
        save_height_btn.clicked.connect(self._save_heightmap)
        controls_layout.addWidget(save_height_btn)

        layout.addWidget(controls)

        # Right panel - preview
        preview_layout = QVBoxLayout()

        preview_label = QLabel("<b>Попередній перегляд</b>")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)

        self._preview = TexturePreviewWidget()
        preview_layout.addWidget(self._preview, stretch=1)

        # Info
        self._info_label = QLabel("")
        self._info_label.setStyleSheet("color: #888;")
        preview_layout.addWidget(self._info_label)

        # Application examples
        examples = QLabel(
            "<p style='color: #aaa;'><b>Застосування:</b></p>"
            "<ul style='color: #888;'>"
            "<li>Рельєф — генерація ландшафту в іграх</li>"
            "<li>Хмари — атмосферні ефекти</li>"
            "<li>Мармур — текстури матеріалів</li>"
            "<li>Клітинна — біологічні структури</li>"
            "</ul>"
        )
        examples.setWordWrap(True)
        preview_layout.addWidget(examples)

        layout.addLayout(preview_layout, stretch=1)

    def _generate_preview(self):
        """Generate preview at reduced resolution."""
        self._generator.set_size(256, 256)
        self._generator.set_seamless(self._seamless_check.isChecked())
        self._generator.set_seed(self._seed_spin.value())

        tex_type = self._type_combo.currentData()
        param = self._param_slider.value() / 100.0
        colormap = self._colormap_combo.currentData() or "terrain"

        self._current_grayscale, self._current_rgba = self._generator.generate(
            tex_type, param, colormap
        )

        self._preview.set_texture(self._current_rgba)
        self._info_label.setText("Попередній перегляд: 256x256")

    def _generate_full(self):
        """Generate full resolution texture."""
        width = self._width_spin.value()
        height = self._height_spin.value()

        self._generator.set_size(width, height)
        self._generator.set_seamless(self._seamless_check.isChecked())
        self._generator.set_seed(self._seed_spin.value())

        tex_type = self._type_combo.currentData()
        param = self._param_slider.value() / 100.0
        colormap = self._colormap_combo.currentData() or "terrain"

        self._current_grayscale, self._current_rgba = self._generator.generate(
            tex_type, param, colormap
        )

        self._preview.set_texture(self._current_rgba)
        self._info_label.setText(f"Повний розмір: {width}x{height}")

    def _update_colormap(self):
        """Update colormap on existing texture."""
        if self._current_grayscale is not None:
            colormap = self._colormap_combo.currentData() or "terrain"
            self._current_rgba = apply_colormap_to_texture(
                self._current_grayscale, colormap
            )
            self._preview.set_texture(self._current_rgba)

    def _randomize_seed(self):
        """Set random seed."""
        import random
        self._seed_spin.setValue(random.randint(0, 999999))

    def _save_texture(self):
        """Save colored texture."""
        if self._current_rgba is None:
            QMessageBox.warning(self, "Помилка", "Спочатку згенеруйте текстуру.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти текстуру", "texture.png",
            "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
        )

        if path:
            try:
                from PIL import Image
                img = Image.fromarray(self._current_rgba)
                img.save(path)
                QMessageBox.information(self, "Збережено", f"Текстуру збережено: {path}")
            except ImportError:
                # Fallback without PIL
                height, width = self._current_rgba.shape[:2]
                qimage = QImage(
                    self._current_rgba.data.tobytes(),
                    width, height, width * 4,
                    QImage.Format.Format_RGBA8888
                )
                qimage.save(path)
                QMessageBox.information(self, "Збережено", f"Текстуру збережено: {path}")

    def _save_heightmap(self):
        """Save grayscale heightmap."""
        if self._current_grayscale is None:
            QMessageBox.warning(self, "Помилка", "Спочатку згенеруйте текстуру.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти heightmap", "heightmap.png",
            "PNG (*.png);;RAW 16-bit (*.raw);;All Files (*)"
        )

        if path:
            try:
                from PIL import Image
                if path.endswith('.raw'):
                    # 16-bit raw for game engines
                    data_16bit = (self._current_grayscale * 65535).astype(np.uint16)
                    data_16bit.tofile(path)
                else:
                    # 8-bit PNG
                    data_8bit = (self._current_grayscale * 255).astype(np.uint8)
                    img = Image.fromarray(data_8bit, mode='L')
                    img.save(path)
                QMessageBox.information(self, "Збережено", f"Heightmap збережено: {path}")
            except ImportError:
                QMessageBox.warning(self, "Помилка", "Для збереження потрібна бібліотека Pillow.")
