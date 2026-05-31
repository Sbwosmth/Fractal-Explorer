"""
Control panel widget for fractal parameters.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QRadioButton, QButtonGroup, QSlider, QLabel,
    QComboBox, QPushButton, QDoubleSpinBox, QSpinBox,
    QSizePolicy, QAbstractSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

from ..rendering.colormap import ColorMapper


class NoWheelSlider(QSlider):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class ControlPanel(QWidget):
    FRACTAL_DESCRIPTIONS = {
        'mandelbrot': (
            "Множина Мандельброта",
            "Найвідоміший фрактал. Для кожної точки c виконується "
            "ітерація z = z² + c. Чорні області — точки, де "
            "послідовність не втікає в нескінченність."
        ),
        'julia': (
            "Множина Жюліа",
            "Споріднена з Мандельбротом. Формула та сама: "
            "z = z² + c, але параметр c фіксований."
        ),
        'newton': (
            "Фрактал Ньютона",
            "Візуалізація методу Ньютона для знаходження коренів "
            "рівняння z³ = 1."
        ),
        'pythagoras': (
            "Дерево Піфагора",
            "Геометричний фрактал. Кожен квадрат породжує "
            "два менших квадрати."
        ),
        'burning_ship': (
            "Палаючий Корабель",
            "Варіант Мандельброта з абсолютними значеннями."
        ),
        'tricorn': (
            "Трикорн",
            "Модифікація Мандельброта з комплексним спряженням."
        ),
        'phoenix': (
            "Фенікс",
            "Ітерація використовує попереднє значення. "
            "Створює вигнуті органічні форми."
        ),
        'barnsley_fern': (
            "Папороть Барнслі",
            "IFS-фрактал, схожий на природну папороть."
        ),
        'sierpinski': (
            "Трикутник Серпінського",
            "Класичний самоподібний трикутний фрактал."
        ),
        'koch': (
            "Сніжинка Коха",
            "Фрактал, у якому кожен відрізок замінюється "
            "на чотири менших."
        ),
        'buddhabrot': (
            "Буддаброт",
            "Карта густини орбіт множини Мандельброта."
        ),
    }

    fractal_changed = pyqtSignal(str)
    iterations_changed = pyqtSignal(int)
    colormap_changed = pyqtSignal(str)
    julia_c_changed = pyqtSignal(float, float)
    tree_params_changed = pyqtSignal(float, int)
    phoenix_p_changed = pyqtSignal(float, float)
    reset_requested = pyqtSignal()
    save_requested = pyqtSignal()
    animation_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color_mapper = ColorMapper()
        self._animation_running = False
        self._setup_ui()

    def _section(self, title: str):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setObjectName("panelSection")
        frame.setStyleSheet("""
            QFrame#panelSection {
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                background-color: #1e1e1e;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        layout.addWidget(title_label)

        return frame, layout

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(10, 10, 10, 20)

        self._fractal_group = self._create_fractal_group()
        layout.addWidget(self._fractal_group)

        self._info_group = self._create_info_group()
        layout.addWidget(self._info_group)

        self._iter_group = self._create_iterations_group()
        layout.addWidget(self._iter_group)

        self._julia_group = self._create_julia_group()
        layout.addWidget(self._julia_group)
        self._julia_group.hide()

        self._tree_group = self._create_tree_group()
        layout.addWidget(self._tree_group)
        self._tree_group.hide()

        self._phoenix_group = self._create_phoenix_group()
        layout.addWidget(self._phoenix_group)
        self._phoenix_group.hide()

        self._colormap_group = self._create_colormap_group()
        layout.addWidget(self._colormap_group)

        self._buttons_widget = self._create_action_buttons()
        layout.addWidget(self._buttons_widget)

        layout.addStretch()

        self.setFixedWidth(260)
        self.setMinimumHeight(1250)

    def _create_fractal_group(self):
        frame, layout = self._section("Тип фракталу")

        self._fractal_buttons = QButtonGroup(self)

        fractals = [
            ('mandelbrot', "Множина Мандельброта"),
            ('julia', "Множина Жюліа"),
            ('newton', "Фрактал Ньютона"),
            ('pythagoras', "Дерево Піфагора"),
            ('burning_ship', "Палаючий Корабель"),
            ('tricorn', "Трикорн"),
            ('phoenix', "Фенікс"),
            ('barnsley_fern', "Папороть Барнслі"),
            ('sierpinski', "Трикутник Серпінського"),
            ('koch', "Сніжинка Коха"),
            ('buddhabrot', "Буддаброт"),
        ]

        for i, (name, label) in enumerate(fractals):
            radio = QRadioButton(label)
            radio.setProperty('fractal_name', name)
            radio.setFixedHeight(26)

            self._fractal_buttons.addButton(radio, i)
            layout.addWidget(radio)

            if name == 'mandelbrot':
                radio.setChecked(True)

        self._fractal_buttons.buttonClicked.connect(self._on_fractal_changed)

        return frame

    def _create_info_group(self):
        frame, layout = self._section("Що це?")

        self._info_title = QLabel("<b>Множина Мандельброта</b>")
        self._info_title.setWordWrap(True)
        self._info_title.setStyleSheet("""
            color: #4fc3f7;
            font-size: 12px;
            border: none;
            background: transparent;
        """)
        layout.addWidget(self._info_title)

        self._info_text = QLabel(self.FRACTAL_DESCRIPTIONS['mandelbrot'][1])
        self._info_text.setWordWrap(True)
        self._info_text.setStyleSheet("""
            color: #bbbbbb;
            font-size: 10px;
            border: none;
            background: transparent;
        """)
        layout.addWidget(self._info_text)

        frame.setMinimumHeight(150)
        return frame

    def _create_iterations_group(self):
        frame, layout = self._section("Ітерації")

        self._iter_slider = NoWheelSlider(Qt.Orientation.Horizontal)
        self._iter_slider.setRange(50, 2000)
        self._iter_slider.setValue(200)
        self._iter_slider.valueChanged.connect(self._on_iterations_changed)

        self._iter_label = QLabel("200")
        self._iter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._iter_label.setStyleSheet("border: none; background: transparent;")

        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(8)

        min_label = QLabel("50")
        max_label = QLabel("2000")
        min_label.setStyleSheet("border: none; background: transparent;")
        max_label.setStyleSheet("border: none; background: transparent;")

        slider_layout.addWidget(min_label)
        slider_layout.addWidget(self._iter_slider)
        slider_layout.addWidget(max_label)

        layout.addLayout(slider_layout)
        layout.addWidget(self._iter_label)

        frame.setMinimumHeight(110)
        return frame

    def _create_julia_group(self):
        frame, layout = self._section("Параметри Жюліа")

        self._julia_preset = NoWheelComboBox()
        self._julia_preset.addItems([
            "Кролик", "Дракон", "Спіраль", "Дендрит",
            "Галактика", "Перо", "Власний"
        ])
        self._julia_preset.setCurrentText("Спіраль")
        self._julia_preset.currentTextChanged.connect(self._on_julia_preset_changed)

        self._julia_re_spin = NoWheelDoubleSpinBox()
        self._julia_re_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._julia_re_spin.setRange(-2.0, 2.0)
        self._julia_re_spin.setSingleStep(0.001)
        self._julia_re_spin.setDecimals(4)
        self._julia_re_spin.setValue(-0.4)
        self._julia_re_spin.valueChanged.connect(self._on_julia_c_changed)

        self._julia_im_spin = NoWheelDoubleSpinBox()
        self._julia_im_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._julia_im_spin.setRange(-2.0, 2.0)
        self._julia_im_spin.setSingleStep(0.001)
        self._julia_im_spin.setDecimals(4)
        self._julia_im_spin.setValue(0.6)
        self._julia_im_spin.valueChanged.connect(self._on_julia_c_changed)

        self._add_row(layout, "Шаблон:", self._julia_preset)
        self._add_row(layout, "Re(c):", self._julia_re_spin)
        self._add_row(layout, "Im(c):", self._julia_im_spin)

        frame.setMinimumHeight(180)
        return frame

    def _create_tree_group(self):
        frame, layout = self._section("Параметри дерева")

        self._tree_angle_spin = NoWheelSpinBox()
        self._tree_angle_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._tree_angle_spin.setRange(20, 70)
        self._tree_angle_spin.setValue(45)
        self._tree_angle_spin.setSuffix("°")
        self._tree_angle_spin.valueChanged.connect(self._on_tree_params_changed)

        self._tree_depth_spin = NoWheelSpinBox()
        self._tree_depth_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._tree_depth_spin.setRange(5, 15)
        self._tree_depth_spin.setValue(10)
        self._tree_depth_spin.valueChanged.connect(self._on_tree_params_changed)

        self._add_row(layout, "Кут:", self._tree_angle_spin)
        self._add_row(layout, "Глибина:", self._tree_depth_spin)

        frame.setMinimumHeight(140)
        return frame

    def _create_phoenix_group(self):
        frame, layout = self._section("Параметри Фенікса")

        self._phoenix_preset = NoWheelComboBox()
        self._phoenix_preset.addItems([
            "Класичний", "Полум'я", "Перо",
            "Спіраль", "Дракон", "Власний"
        ])
        self._phoenix_preset.setCurrentText("Класичний")
        self._phoenix_preset.currentTextChanged.connect(self._on_phoenix_preset_changed)

        self._phoenix_re_spin = NoWheelDoubleSpinBox()
        self._phoenix_re_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._phoenix_re_spin.setRange(-2.0, 2.0)
        self._phoenix_re_spin.setSingleStep(0.001)
        self._phoenix_re_spin.setDecimals(4)
        self._phoenix_re_spin.setValue(0.5667)
        self._phoenix_re_spin.valueChanged.connect(self._on_phoenix_p_changed)

        self._phoenix_im_spin = NoWheelDoubleSpinBox()
        self._phoenix_im_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._phoenix_im_spin.setRange(-2.0, 2.0)
        self._phoenix_im_spin.setSingleStep(0.001)
        self._phoenix_im_spin.setDecimals(4)
        self._phoenix_im_spin.setValue(-0.5)
        self._phoenix_im_spin.valueChanged.connect(self._on_phoenix_p_changed)

        self._add_row(layout, "Шаблон:", self._phoenix_preset)
        self._add_row(layout, "Re(p):", self._phoenix_re_spin)
        self._add_row(layout, "Im(p):", self._phoenix_im_spin)

        frame.setMinimumHeight(190)
        return frame

    def _create_colormap_group(self):
        frame, layout = self._section("Кольорова схема")

        self._colormap_combo = NoWheelComboBox()
        self._colormap_combo.addItems(ColorMapper.get_available_colormaps())
        self._colormap_combo.setCurrentText("twilight")
        self._colormap_combo.currentTextChanged.connect(self._on_colormap_changed)

        layout.addWidget(self._colormap_combo)

        self._colormap_preview = QLabel()
        self._colormap_preview.setFixedHeight(24)
        self._colormap_preview.setStyleSheet("border: 1px solid #555;")
        layout.addWidget(self._colormap_preview)

        self._update_colormap_preview("twilight")

        frame.setMinimumHeight(130)
        return frame

    def _create_action_buttons(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._reset_btn = QPushButton("Скинути вигляд")
        self._reset_btn.setMinimumHeight(42)
        self._reset_btn.clicked.connect(self.reset_requested.emit)
        layout.addWidget(self._reset_btn)

        self._save_btn = QPushButton("Зберегти зображення")
        self._save_btn.setMinimumHeight(42)
        self._save_btn.clicked.connect(self.save_requested.emit)
        layout.addWidget(self._save_btn)

        self._anim_btn = QPushButton("Запустити анімацію")
        self._anim_btn.setMinimumHeight(42)
        self._anim_btn.setCheckable(True)
        self._anim_btn.clicked.connect(self._on_animation_toggled)
        layout.addWidget(self._anim_btn)

        widget.setMinimumHeight(150)
        return widget

    def _add_row(self, parent_layout: QVBoxLayout, text: str, widget: QWidget):
        row = QHBoxLayout()
        row.setSpacing(8)

        label = QLabel(text)
        label.setFixedWidth(65)
        label.setStyleSheet("border: none; background: transparent;")

        widget.setMinimumHeight(34)
        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        row.addWidget(label)
        row.addWidget(widget)
        parent_layout.addLayout(row)

    def _update_fractal_info(self, fractal_name: str):
        if fractal_name in self.FRACTAL_DESCRIPTIONS:
            title, desc = self.FRACTAL_DESCRIPTIONS[fractal_name]
            self._info_title.setText(f"<b>{title}</b>")
            self._info_text.setText(desc)

    def _update_colormap_preview(self, name: str):
        self._color_mapper.set_colormap(name)
        preview = self._color_mapper.get_preview(220, 24)

        height, width = preview.shape[:2]
        qimage = QImage(
            preview.data.tobytes(),
            width,
            height,
            width * 4,
            QImage.Format.Format_RGBA8888
        )

        pixmap = QPixmap.fromImage(qimage)
        self._colormap_preview.setPixmap(pixmap)

    def _on_fractal_changed(self, button: QRadioButton):
        name = button.property('fractal_name')
        self.fractal_changed.emit(name)
        self._update_fractal_info(name)

        self._julia_group.setVisible(name == 'julia')
        self._tree_group.setVisible(name == 'pythagoras')
        self._phoenix_group.setVisible(name == 'phoenix')

        ifs_fractals = {
            'pythagoras',
            'barnsley_fern',
            'sierpinski',
            'koch',
            'buddhabrot'
        }
        self._iter_group.setVisible(name not in ifs_fractals)

        iterative_fractals = {
            'mandelbrot',
            'julia',
            'newton',
            'burning_ship',
            'tricorn',
            'phoenix'
        }
        self._anim_btn.setVisible(name in iterative_fractals)

    def _on_iterations_changed(self, value: int):
        self._iter_label.setText(str(value))
        self.iterations_changed.emit(value)

    def _on_colormap_changed(self, name: str):
        self._update_colormap_preview(name)
        self.colormap_changed.emit(name)

    def _on_julia_preset_changed(self, preset: str):
        preset_map = {
            "Кролик": "Rabbit",
            "Дракон": "Dragon",
            "Спіраль": "Spiral",
            "Дендрит": "Dendrite",
            "Галактика": "Galaxy",
            "Перо": "Feather",
            "Власний": "Custom",
        }

        eng_preset = preset_map.get(preset, preset)

        from ..fractals.julia import JuliaFractal

        if eng_preset in JuliaFractal.PRESETS:
            c_re, c_im = JuliaFractal.PRESETS[eng_preset]

            self._julia_re_spin.blockSignals(True)
            self._julia_im_spin.blockSignals(True)

            self._julia_re_spin.setValue(c_re)
            self._julia_im_spin.setValue(c_im)

            self._julia_re_spin.blockSignals(False)
            self._julia_im_spin.blockSignals(False)

            self.julia_c_changed.emit(c_re, c_im)

    def _on_julia_c_changed(self):
        c_re = self._julia_re_spin.value()
        c_im = self._julia_im_spin.value()

        self._julia_preset.blockSignals(True)
        self._julia_preset.setCurrentText("Власний")
        self._julia_preset.blockSignals(False)

        self.julia_c_changed.emit(c_re, c_im)

    def _on_tree_params_changed(self):
        angle = float(self._tree_angle_spin.value())
        depth = self._tree_depth_spin.value()
        self.tree_params_changed.emit(angle, depth)

    def _on_phoenix_preset_changed(self, preset: str):
        preset_map = {
            "Класичний": "Classic",
            "Полум'я": "Flame",
            "Перо": "Feather",
            "Спіраль": "Spiral",
            "Дракон": "Dragon",
            "Власний": "Custom",
        }

        eng_preset = preset_map.get(preset, preset)

        from ..fractals.phoenix import PhoenixFractal

        if eng_preset in PhoenixFractal.PRESETS:
            p_re, p_im = PhoenixFractal.PRESETS[eng_preset]

            self._phoenix_re_spin.blockSignals(True)
            self._phoenix_im_spin.blockSignals(True)

            self._phoenix_re_spin.setValue(p_re)
            self._phoenix_im_spin.setValue(p_im)

            self._phoenix_re_spin.blockSignals(False)
            self._phoenix_im_spin.blockSignals(False)

            self.phoenix_p_changed.emit(p_re, p_im)

    def _on_phoenix_p_changed(self):
        p_re = self._phoenix_re_spin.value()
        p_im = self._phoenix_im_spin.value()

        self._phoenix_preset.blockSignals(True)
        self._phoenix_preset.setCurrentText("Власний")
        self._phoenix_preset.blockSignals(False)

        self.phoenix_p_changed.emit(p_re, p_im)

    def _on_animation_toggled(self, checked: bool):
        self._animation_running = checked
        self._anim_btn.setText(
            "Зупинити анімацію" if checked else "Запустити анімацію"
        )
        self.animation_toggled.emit(checked)

    def set_iterations(self, value: int):
        self._iter_slider.setValue(value)

    def set_julia_c(self, c_re: float, c_im: float):
        self._julia_re_spin.blockSignals(True)
        self._julia_im_spin.blockSignals(True)

        self._julia_re_spin.setValue(c_re)
        self._julia_im_spin.setValue(c_im)

        self._julia_re_spin.blockSignals(False)
        self._julia_im_spin.blockSignals(False)

    def set_tree_params(self, angle: float, depth: int):
        self._tree_angle_spin.blockSignals(True)
        self._tree_depth_spin.blockSignals(True)

        self._tree_angle_spin.setValue(int(angle))
        self._tree_depth_spin.setValue(depth)

        self._tree_angle_spin.blockSignals(False)
        self._tree_depth_spin.blockSignals(False)

    def set_phoenix_p(self, p_re: float, p_im: float):
        self._phoenix_re_spin.blockSignals(True)
        self._phoenix_im_spin.blockSignals(True)

        self._phoenix_re_spin.setValue(p_re)
        self._phoenix_im_spin.setValue(p_im)

        self._phoenix_im_spin.blockSignals(False)
        self._phoenix_re_spin.blockSignals(False)

    def stop_animation(self):
        if self._animation_running:
            self._anim_btn.setChecked(False)
            self._on_animation_toggled(False)