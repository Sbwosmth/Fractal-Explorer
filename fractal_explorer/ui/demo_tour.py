"""
Demo Tour System - automated presentations of fractal features.

Provides guided tours through interesting fractal locations and features
for educational presentations and demonstrations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QProgressBar,
    QTextBrowser, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from dataclasses import dataclass
from typing import List, Callable, Optional
import math


@dataclass
class TourStop:
    """Single stop in a demo tour."""
    name: str
    description: str
    fractal_type: str
    center_re: float
    center_im: float
    scale: float
    iterations: int
    duration_ms: int = 3000
    colormap: str = "twilight"
    # Optional parameters
    julia_c: tuple = None  # (c_re, c_im) for Julia
    phoenix_p: tuple = None  # (p_re, p_im) for Phoenix


class DemoTour:
    """A collection of tour stops forming a complete demonstration."""

    def __init__(self, name: str, description: str, stops: List[TourStop]):
        self.name = name
        self.description = description
        self.stops = stops


# Predefined tours
TOURS = {
    'mandelbrot_deep_zoom': DemoTour(
        name="Глибокий зум Мандельброта",
        description="Подорож у нескінченну глибину множини Мандельброта через найцікавіші локації.",
        stops=[
            TourStop("Загальний вигляд", "Класична форма множини Мандельброта з кардіоїдом та головною цибулиною.",
                     "mandelbrot", -0.5, 0.0, 3.5, 200),
            TourStop("Долина морських коників", "Область з характерними спіральними структурами.",
                     "mandelbrot", -0.747, 0.1, 0.05, 300),
            TourStop("Долина слонів", "Структури, що нагадують слонів у ряд.",
                     "mandelbrot", 0.275, 0.0, 0.01, 400),
            TourStop("Подвійна спіраль", "Глибока спіральна структура з самоподібністю.",
                     "mandelbrot", -0.7435669, 0.1314023, 0.0001, 500),
            TourStop("Мінібрoт", "Мініатюрна копія всього Мандельброта на глибині.",
                     "mandelbrot", -0.74364388703, 0.13182590421, 0.00000001, 800),
            TourStop("Ультраглибокий зум", "Максимальна глибина візуалізації.",
                     "mandelbrot", -0.743643887037, 0.131825904205, 0.0000000001, 1000),
        ]
    ),

    'julia_gallery': DemoTour(
        name="Галерея множин Жюліа",
        description="Огляд найкрасивіших множин Жюліа з різними параметрами c.",
        stops=[
            TourStop("Кролик Дуаді", "Класична форма, що нагадує кролика з вухами.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(-0.123, 0.745)),
            TourStop("Дракон", "Драконоподібна форма з детальними краями.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(-0.8, 0.156)),
            TourStop("Дендрит", "Деревоподібна структура на межі зв'язності.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(0.0, 1.0)),
            TourStop("Галактика", "Спіральна структура, що нагадує галактику.",
                     "julia", 0.0, 0.0, 3.5, 300, julia_c=(-0.7269, 0.1889)),
            TourStop("Перо", "Ніжна пероподібна форма.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(-0.194, 0.6557)),
            TourStop("Спіраль", "Класична спіральна множина Жюліа.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(-0.4, 0.6)),
        ]
    ),

    'fractal_types': DemoTour(
        name="Типи фракталів",
        description="Огляд всіх типів фракталів, реалізованих у програмі.",
        stops=[
            TourStop("Мандельброт", "Найвідоміший фрактал. z² + c з z₀ = 0.",
                     "mandelbrot", -0.5, 0.0, 3.5, 200, colormap="twilight"),
            TourStop("Жюліа", "Споріднена множина. z² + c з фіксованим c.",
                     "julia", 0.0, 0.0, 3.5, 200, colormap="plasma", julia_c=(-0.4, 0.6)),
            TourStop("Ньютон", "Басейни притягання методу Ньютона для z³-1=0.",
                     "newton", 0.0, 0.0, 3.0, 50, colormap="viridis"),
            TourStop("Палаючий корабель", "Варіація Мандельброта з |Re|, |Im|.",
                     "burning_ship", -0.4, -0.5, 3.5, 200, colormap="hot"),
            TourStop("Трикорн", "Антиголоморфний аналог Мандельброта.",
                     "tricorn", -0.3, 0.0, 3.5, 200, colormap="magma"),
            TourStop("Фенікс", "Фрактал з пам'яттю попереднього кроку.",
                     "phoenix", 0.0, 0.0, 3.5, 200, colormap="inferno", phoenix_p=(0.5667, -0.5)),
            TourStop("Дерево Піфагора", "Геометричний фрактал на теоремі Піфагора.",
                     "pythagoras", 0.0, 0.8, 4.5, 10, colormap="viridis"),
            TourStop("Трикутник Серпінського", "IFS-фрактал методом хаосу.",
                     "sierpinski", 0.5, 0.33, 1.4, 500000, colormap="plasma"),
            TourStop("Папороть Барнслі", "Класичний IFS з 4 афінних перетворень.",
                     "barnsley_fern", 0.0, 5.0, 12.0, 500000, colormap="viridis"),
            TourStop("Сніжинка Коха", "L-система з нескінченним периметром.",
                     "koch", 0.0, 0.0, 3.5, 5, colormap="twilight"),
            TourStop("Буддаброт", "Альтернативна візуалізація Мандельброта.",
                     "buddhabrot", -0.3, 0.0, 3.5, 200, colormap="hot"),
        ]
    ),

    'scientific_concepts': DemoTour(
        name="Наукові концепції",
        description="Демонстрація ключових математичних понять через фрактали.",
        stops=[
            TourStop("Самоподібність", "Зменшені копії цілого всередині фракталу.",
                     "mandelbrot", -0.74364, 0.13183, 0.00001, 600, colormap="twilight"),
            TourStop("Чутливість до початкових умов", "Малі зміни → великі наслідки (хаос).",
                     "mandelbrot", -0.7436438870371, 0.1318259042, 0.000000001, 1000),
            TourStop("Фрактальна границя", "Границя Мандельброта має розмірність D=2.",
                     "mandelbrot", -0.745, 0.113, 0.001, 500),
            TourStop("Зв'язок Мандельброт-Жюліа", "Кожна точка Мандельброта → окрема Жюліа.",
                     "julia", 0.0, 0.0, 3.5, 200, julia_c=(-0.745, 0.113)),
            TourStop("Басейни притягання", "Хаотична межа між областями збіжності.",
                     "newton", 0.0, 0.0, 2.0, 100, colormap="twilight"),
            TourStop("Розмірність Хаусдорфа", "D = log(3)/log(2) ≈ 1.585 для Серпінського.",
                     "sierpinski", 0.5, 0.33, 1.4, 500000, colormap="plasma"),
        ]
    ),
}


class TourPlayer:
    """
    Plays a demo tour with animations and transitions.
    """

    # Signals would normally be here, but we'll use callbacks
    def __init__(self, renderer, canvas):
        self._renderer = renderer
        self._canvas = canvas
        self._current_tour: Optional[DemoTour] = None
        self._current_stop_index = 0
        self._is_playing = False
        self._timer = QTimer()
        self._timer.timeout.connect(self._next_stop)

        # Callbacks
        self.on_stop_changed: Optional[Callable[[int, TourStop], None]] = None
        self.on_tour_finished: Optional[Callable[[], None]] = None

    def load_tour(self, tour_id: str):
        """Load a tour by ID."""
        if tour_id in TOURS:
            self._current_tour = TOURS[tour_id]
            self._current_stop_index = 0
            return True
        return False

    def start(self):
        """Start playing the tour."""
        if not self._current_tour:
            return

        self._is_playing = True
        self._current_stop_index = 0
        self._apply_current_stop()

    def stop(self):
        """Stop the tour."""
        self._is_playing = False
        self._timer.stop()

    def pause(self):
        """Pause the tour."""
        self._timer.stop()

    def resume(self):
        """Resume the tour."""
        if self._is_playing and self._current_tour:
            stop = self._current_tour.stops[self._current_stop_index]
            self._timer.start(stop.duration_ms)

    def next(self):
        """Go to next stop."""
        if self._current_tour and self._current_stop_index < len(self._current_tour.stops) - 1:
            self._current_stop_index += 1
            self._apply_current_stop()

    def previous(self):
        """Go to previous stop."""
        if self._current_tour and self._current_stop_index > 0:
            self._current_stop_index -= 1
            self._apply_current_stop()

    def go_to_stop(self, index: int):
        """Go to specific stop."""
        if self._current_tour and 0 <= index < len(self._current_tour.stops):
            self._current_stop_index = index
            self._apply_current_stop()

    def _apply_current_stop(self):
        """Apply the current tour stop to the renderer."""
        if not self._current_tour:
            return

        stop = self._current_tour.stops[self._current_stop_index]

        # Set fractal type
        self._renderer.set_fractal_type(stop.fractal_type)

        # Set viewport
        self._renderer.viewport.center_re = stop.center_re
        self._renderer.viewport.center_im = stop.center_im
        self._renderer.viewport.scale = stop.scale

        # Set iterations
        self._renderer.set_max_iterations(stop.iterations)

        # Set colormap
        self._renderer.set_colormap(stop.colormap)

        # Set type-specific parameters
        if stop.julia_c and stop.fractal_type == 'julia':
            self._renderer.set_julia_c(*stop.julia_c)

        if stop.phoenix_p and stop.fractal_type == 'phoenix':
            self._renderer.set_phoenix_p(*stop.phoenix_p)

        # Render
        self._canvas.request_render(immediate=True)

        # Notify
        if self.on_stop_changed:
            self.on_stop_changed(self._current_stop_index, stop)

        # Schedule next stop
        if self._is_playing:
            self._timer.start(stop.duration_ms)

    def _next_stop(self):
        """Move to next stop or finish."""
        self._timer.stop()

        if not self._current_tour:
            return

        if self._current_stop_index < len(self._current_tour.stops) - 1:
            self._current_stop_index += 1
            self._apply_current_stop()
        else:
            self._is_playing = False
            if self.on_tour_finished:
                self.on_tour_finished()

    @property
    def current_stop(self) -> Optional[TourStop]:
        if self._current_tour and self._current_stop_index < len(self._current_tour.stops):
            return self._current_tour.stops[self._current_stop_index]
        return None

    @property
    def total_stops(self) -> int:
        return len(self._current_tour.stops) if self._current_tour else 0

    @property
    def is_playing(self) -> bool:
        return self._is_playing


class DemoTourDialog(QDialog):
    """Dialog for selecting and playing demo tours."""

    def __init__(self, renderer, canvas, parent=None):
        super().__init__(parent)
        self._renderer = renderer
        self._canvas = canvas
        self._player = TourPlayer(renderer, canvas)
        self._player.on_stop_changed = self._on_stop_changed
        self._player.on_tour_finished = self._on_tour_finished

        self.setWindowTitle("Демонстраційні тури")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel - tour selection
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left.setFixedWidth(250)

        left_layout.addWidget(QLabel("<b>Доступні тури:</b>"))

        self._tour_list = QListWidget()
        for tour_id, tour in TOURS.items():
            item = QListWidgetItem(tour.name)
            item.setData(Qt.ItemDataRole.UserRole, tour_id)
            item.setToolTip(tour.description)
            self._tour_list.addItem(item)
        self._tour_list.currentItemChanged.connect(self._on_tour_selected)
        left_layout.addWidget(self._tour_list)

        # Tour description
        self._tour_desc = QLabel("")
        self._tour_desc.setWordWrap(True)
        self._tour_desc.setStyleSheet("color: #888; padding: 5px;")
        left_layout.addWidget(self._tour_desc)

        layout.addWidget(left)

        # Right panel - playback controls and info
        right = QWidget()
        right_layout = QVBoxLayout(right)

        # Current stop info
        info_group = QGroupBox("Поточна зупинка")
        info_layout = QVBoxLayout(info_group)

        self._stop_name = QLabel("<b>-</b>")
        self._stop_name.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self._stop_name)

        self._stop_desc = QTextBrowser()
        self._stop_desc.setMaximumHeight(120)
        self._stop_desc.setStyleSheet("background: #2d2d2d; border: none;")
        info_layout.addWidget(self._stop_desc)

        right_layout.addWidget(info_group)

        # Progress
        progress_layout = QHBoxLayout()
        self._progress_label = QLabel("0 / 0")
        progress_layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximum(100)
        progress_layout.addWidget(self._progress_bar)
        right_layout.addLayout(progress_layout)

        # Stop list
        stops_group = QGroupBox("Зупинки туру")
        stops_layout = QVBoxLayout(stops_group)

        self._stops_list = QListWidget()
        self._stops_list.itemDoubleClicked.connect(self._on_stop_double_clicked)
        stops_layout.addWidget(self._stops_list)

        right_layout.addWidget(stops_group)

        # Playback controls
        controls = QHBoxLayout()

        self._prev_btn = QPushButton("◀ Назад")
        self._prev_btn.clicked.connect(self._player.previous)
        self._prev_btn.setEnabled(False)
        controls.addWidget(self._prev_btn)

        self._play_btn = QPushButton("▶ Старт")
        self._play_btn.clicked.connect(self._toggle_playback)
        self._play_btn.setEnabled(False)
        controls.addWidget(self._play_btn)

        self._next_btn = QPushButton("Далі ▶")
        self._next_btn.clicked.connect(self._player.next)
        self._next_btn.setEnabled(False)
        controls.addWidget(self._next_btn)

        right_layout.addLayout(controls)

        # Close button
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.close)
        right_layout.addWidget(close_btn)

        layout.addWidget(right)

    def _on_tour_selected(self, item):
        """Handle tour selection."""
        if not item:
            return

        tour_id = item.data(Qt.ItemDataRole.UserRole)
        tour = TOURS.get(tour_id)

        if tour:
            self._tour_desc.setText(tour.description)

            # Populate stops list
            self._stops_list.clear()
            for i, stop in enumerate(tour.stops):
                self._stops_list.addItem(f"{i+1}. {stop.name}")

            # Load tour
            self._player.load_tour(tour_id)

            # Enable controls
            self._play_btn.setEnabled(True)
            self._prev_btn.setEnabled(True)
            self._next_btn.setEnabled(True)

            # Show first stop
            self._player.go_to_stop(0)

    def _on_stop_changed(self, index: int, stop: TourStop):
        """Handle stop change."""
        self._stop_name.setText(f"<b>{stop.name}</b>")
        self._stop_desc.setText(
            f"<p>{stop.description}</p>"
            f"<p style='color: #666;'>"
            f"Фрактал: {stop.fractal_type}<br>"
            f"Позиція: ({stop.center_re:.6f}, {stop.center_im:.6f})<br>"
            f"Масштаб: {stop.scale:.2e}<br>"
            f"Ітерації: {stop.iterations}"
            f"</p>"
        )

        # Update progress
        total = self._player.total_stops
        self._progress_label.setText(f"{index + 1} / {total}")
        self._progress_bar.setValue(int((index + 1) / total * 100))

        # Highlight current stop in list
        self._stops_list.setCurrentRow(index)

    def _on_tour_finished(self):
        """Handle tour completion."""
        self._play_btn.setText("▶ Старт")

    def _toggle_playback(self):
        """Toggle play/pause."""
        if self._player.is_playing:
            self._player.pause()
            self._play_btn.setText("▶ Продовжити")
        else:
            if self._player.current_stop is None:
                self._player.start()
            else:
                self._player.resume()
            self._play_btn.setText("⏸ Пауза")

    def _on_stop_double_clicked(self, item):
        """Handle stop double-click."""
        index = self._stops_list.row(item)
        self._player.go_to_stop(index)

    def closeEvent(self, event):
        """Stop tour on close."""
        self._player.stop()
        event.accept()
