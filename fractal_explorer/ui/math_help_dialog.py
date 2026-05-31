"""
Mathematical help dialog with detailed fractal descriptions.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QTextBrowser, QWidget
)
from PyQt6.QtCore import Qt


class MathHelpDialog(QDialog):
    """Dialog showing mathematical descriptions of fractal algorithms."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Математика фракталів")
        self.setMinimumSize(700, 600)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        tabs.addTab(self._create_mandelbrot_tab(), "Мандельброт")
        tabs.addTab(self._create_julia_tab(), "Жюліа")
        tabs.addTab(self._create_newton_tab(), "Ньютон")
        tabs.addTab(self._create_pythagoras_tab(), "Піфагор")
        tabs.addTab(self._create_burning_ship_tab(), "Корабель")
        tabs.addTab(self._create_tricorn_tab(), "Трикорн")
        tabs.addTab(self._create_phoenix_tab(), "Фенікс")
        tabs.addTab(self._create_ifs_tab(), "IFS")
        tabs.addTab(self._create_dimension_tab(), "Розмірність")

        layout.addWidget(tabs)

    def _create_mandelbrot_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
            code { background: #37474f; padding: 2px 6px; border-radius: 3px; }
        </style>
        <h2>Множина Мандельброта</h2>

        <h3>Визначення</h3>
        <p>Множина Мандельброта — це множина комплексних чисел <b>c</b>, для яких послідовність</p>

        <div class="formula">
            z<sub>n+1</sub> = z<sub>n</sub><sup>2</sup> + c
        </div>

        <p>при z<sub>0</sub> = 0 залишається обмеженою (не прямує до нескінченності).</p>

        <h3>Алгоритм</h3>
        <ol>
            <li>Для кожної точки (x, y) на екрані створюємо комплексне число c = x + yi</li>
            <li>Починаємо з z<sub>0</sub> = 0</li>
            <li>Ітеративно обчислюємо z<sub>n+1</sub> = z<sub>n</sub><sup>2</sup> + c</li>
            <li>Якщо |z| > 2 (точка "втекла"), зупиняємось і розфарбовуємо за номером ітерації</li>
            <li>Якщо досягли max_iterations — точка належить множині (чорний колір)</li>
        </ol>

        <h3>Умова втечі</h3>
        <div class="formula">
            |z<sub>n</sub>| = √(Re(z)<sup>2</sup> + Im(z)<sup>2</sup>) > 2
        </div>
        <p>Доведено математично: якщо |z| > 2, послідовність гарантовано прямує до нескінченності.</p>

        <h3>Цікаві факти</h3>
        <div class="note">
            <ul>
                <li>Периметр множини Мандельброта — <b>нескінченний</b></li>
                <li>Площа — приблизно <b>1.5065</b></li>
                <li>Фрактальна розмірність границі — <b>2</b> (максимально можлива для 2D)</li>
                <li>Множина <b>зв'язна</b> — складається з одного шматка</li>
            </ul>
        </div>

        <h3>Координати цікавих місць</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Назва</th><th>Re</th><th>Im</th><th>Масштаб</th></tr>
            <tr><td>Долина морських коників</td><td>-0.747</td><td>0.1</td><td>10<sup>-4</sup></td></tr>
            <tr><td>Долина слонів</td><td>0.275</td><td>0.0</td><td>10<sup>-3</sup></td></tr>
            <tr><td>Спіраль</td><td>-0.7436</td><td>0.1318</td><td>10<sup>-10</sup></td></tr>
        </table>
        """)
        return browser

    def _create_julia_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Множина Жюліа</h2>

        <h3>Визначення</h3>
        <p>Множина Жюліа — це множина точок z<sub>0</sub>, для яких послідовність</p>

        <div class="formula">
            z<sub>n+1</sub> = z<sub>n</sub><sup>2</sup> + c
        </div>

        <p>залишається обмеженою при <b>фіксованому</b> значенні c.</p>

        <h3>Зв'язок з Мандельбротом</h3>
        <div class="note">
            <p><b>Мандельброт:</b> c змінюється, z<sub>0</sub> = 0 (фіксовано)</p>
            <p><b>Жюліа:</b> c фіксовано, z<sub>0</sub> змінюється (кожна точка екрану)</p>
        </div>
        <p>Множина Мандельброта — це "каталог" всіх множин Жюліа!</p>

        <h3>Типи множин Жюліа</h3>
        <ul>
            <li><b>Зв'язна</b> — якщо c належить множині Мандельброта</li>
            <li><b>Канторова пил</b> — якщо c не належить множині Мандельброта</li>
        </ul>

        <h3>Відомі значення c</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Назва</th><th>c</th><th>Опис</th></tr>
            <tr><td>Кролик Дуаді</td><td>-0.123 + 0.745i</td><td>Нагадує кролика з вухами</td></tr>
            <tr><td>Дракон</td><td>-0.8 + 0.156i</td><td>Драконоподібна форма</td></tr>
            <tr><td>Дендрит</td><td>0 + 1i</td><td>Деревоподібна структура</td></tr>
            <tr><td>Спіраль</td><td>-0.4 + 0.6i</td><td>Спіральні візерунки</td></tr>
            <tr><td>Галактика</td><td>-0.7269 + 0.1889i</td><td>Спіральна галактика</td></tr>
        </table>

        <h3>Анімація</h3>
        <p>Якщо c рухається по колу з центром (0, 0) і радіусом ~0.7885,
        множина Жюліа плавно "дихає" — це класична анімація для демонстрації фракталів.</p>
        """)
        return browser

    def _create_newton_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Фрактал Ньютона</h2>

        <h3>Метод Ньютона</h3>
        <p>Метод Ньютона — це ітеративний алгоритм знаходження коренів рівняння f(z) = 0:</p>

        <div class="formula">
            z<sub>n+1</sub> = z<sub>n</sub> - f(z<sub>n</sub>) / f'(z<sub>n</sub>)
        </div>

        <h3>Для z³ - 1 = 0</h3>
        <p>Рівняння z³ = 1 має три корені (кубічні корені з одиниці):</p>
        <div class="formula">
            ω<sub>0</sub> = 1, &nbsp;&nbsp; ω<sub>1</sub> = e<sup>2πi/3</sup> = -½ + i√3/2, &nbsp;&nbsp; ω<sub>2</sub> = e<sup>4πi/3</sup> = -½ - i√3/2
        </div>

        <p>Ітераційна формула:</p>
        <div class="formula">
            z<sub>n+1</sub> = z<sub>n</sub> - (z<sub>n</sub>³ - 1) / (3z<sub>n</sub>²) = (2z<sub>n</sub>³ + 1) / (3z<sub>n</sub>²)
        </div>

        <h3>Фрактальна природа</h3>
        <div class="note">
            <p>Басейни притягання (області, з яких метод збігається до певного кореня)
            мають <b>фрактальну границю</b>!</p>
            <p>На границі метод хаотично "стрибає" між коренями — неможливо передбачити результат.</p>
        </div>

        <h3>Розфарбування</h3>
        <ul>
            <li><b>Колір</b> — до якого кореня збіглася точка</li>
            <li><b>Яскравість</b> — скільки ітерацій знадобилось</li>
        </ul>

        <h3>Узагальнення</h3>
        <p>Можна будувати фрактали Ньютона для будь-якого многочлена:</p>
        <ul>
            <li>z⁴ - 1 = 0 → 4 корені, 4 кольори</li>
            <li>z⁵ - 1 = 0 → 5 коренів, складніша структура</li>
            <li>z³ - 2z + 2 = 0 → асиметричні візерунки</li>
        </ul>
        """)
        return browser

    def _create_pythagoras_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Дерево Піфагора</h2>

        <h3>Конструкція</h3>
        <p>Дерево Піфагора — це фрактал, побудований на теоремі Піфагора:</p>

        <div class="formula">
            a² + b² = c²
        </div>

        <h3>Алгоритм побудови</h3>
        <ol>
            <li>Малюємо початковий квадрат (стовбур)</li>
            <li>На верхній стороні будуємо прямокутний трикутник</li>
            <li>На катетах трикутника будуємо нові квадрати (гілки)</li>
            <li>Рекурсивно повторюємо для нових квадратів</li>
        </ol>

        <h3>Математичні властивості</h3>
        <div class="note">
            <p><b>Теорема Піфагора в дії:</b> площа квадрата на гіпотенузі
            дорівнює сумі площ квадратів на катетах.</p>
            <p>Це означає, що загальна площа всіх квадратів на кожному рівні <b>однакова</b>!</p>
        </div>

        <h3>Параметри</h3>
        <ul>
            <li><b>Кут α</b> — кут нахилу гілок (20°-70°)</li>
            <li><b>Глибина</b> — кількість рівнів рекурсії</li>
        </ul>

        <h3>Коефіцієнт масштабування</h3>
        <p>При куті α розмір гілок зменшується:</p>
        <div class="formula">
            Ліва гілка: k<sub>L</sub> = cos(α)<br>
            Права гілка: k<sub>R</sub> = sin(α)
        </div>

        <h3>Особливі випадки</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Кут</th><th>Результат</th></tr>
            <tr><td>45°</td><td>Симетричне дерево, класична форма</td></tr>
            <tr><td>30°</td><td>Нахил вліво, тонкі гілки</td></tr>
            <tr><td>60°</td><td>Нахил вправо, товсті гілки</td></tr>
        </table>

        <h3>Загальна площа</h3>
        <p>При глибині n → ∞ і куті 45° загальна площа дерева:</p>
        <div class="formula">
            S = S<sub>0</sub> × (1 + 1 + 1 + ...) = ∞
        </div>
        <p>Але дерево залишається обмеженим у просторі — це парадокс нескінченної площі в обмеженій області!</p>
        """)
        return browser

    def _create_burning_ship_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Палаючий Корабель (Burning Ship)</h2>

        <h3>Визначення</h3>
        <p>Фрактал "Палаючий Корабель" — це варіація множини Мандельброта, де перед піднесенням до квадрата
        беруться абсолютні значення дійсної та уявної частин:</p>

        <div class="formula">
            z<sub>n+1</sub> = (|Re(z<sub>n</sub>)| + i|Im(z<sub>n</sub>)|)² + c
        </div>

        <h3>Розгорнута формула</h3>
        <p>Якщо z = x + yi, то:</p>
        <div class="formula">
            x<sub>n+1</sub> = x<sub>n</sub>² - y<sub>n</sub>² + c<sub>x</sub><br>
            y<sub>n+1</sub> = |2·x<sub>n</sub>·y<sub>n</sub>| + c<sub>y</sub>
        </div>

        <h3>Особливості</h3>
        <div class="note">
            <ul>
                <li>Взяття абсолютних значень порушує <b>аналітичність</b> функції</li>
                <li>Форма нагадує <b>палаючий корабель</b>, звідси назва</li>
                <li>Фрактал має характерні "антени" та "вежі"</li>
                <li>Відкритий у 1992 році Майклом Міхельсеном</li>
            </ul>
        </div>

        <h3>Цікаві координати</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Назва</th><th>Re</th><th>Im</th><th>Опис</th></tr>
            <tr><td>Головний корабель</td><td>-1.762</td><td>-0.028</td><td>Основна структура</td></tr>
            <tr><td>Антена</td><td>-1.756</td><td>-0.0235</td><td>Тонка деталь</td></tr>
            <tr><td>Міні-корабель</td><td>-1.771</td><td>-0.054</td><td>Самоподібна копія</td></tr>
        </table>

        <h3>Порівняння з Мандельбротом</h3>
        <p>Основна відмінність — взяття модуля перед множенням створює "згини" у фракталі,
        що надає йому характерний вигляд горіючого корабля з полум'ям.</p>
        """)
        return browser

    def _create_tricorn_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Трикорн (Mandelbar)</h2>

        <h3>Визначення</h3>
        <p>Трикорн (також відомий як Mandelbar або "Анти-Мандельброт") використовує
        комплексне спряження замість звичайного квадрату:</p>

        <div class="formula">
            z<sub>n+1</sub> = <span style="text-decoration: overline;">z<sub>n</sub></span>² + c
        </div>

        <p>де <span style="text-decoration: overline;">z</span> = x - yi (комплексне спряження z = x + yi)</p>

        <h3>Розгорнута формула</h3>
        <div class="formula">
            x<sub>n+1</sub> = x<sub>n</sub>² - y<sub>n</sub>² + c<sub>x</sub><br>
            y<sub>n+1</sub> = <b>-</b>2·x<sub>n</sub>·y<sub>n</sub> + c<sub>y</sub>
        </div>
        <p>Єдина відмінність від Мандельброта — знак мінус у формулі для y!</p>

        <h3>Особливості форми</h3>
        <div class="note">
            <ul>
                <li>Має <b>три "роги"</b> (звідси назва "Tricorn" — три роги)</li>
                <li>Симетричний відносно дійсної осі</li>
                <li>Не має спіральних структур як Мандельброт</li>
                <li>Відкритий у 1989 році</li>
            </ul>
        </div>

        <h3>Математичний зміст</h3>
        <p>Комплексне спряження — це відображення відносно дійсної осі.
        Формула <span style="text-decoration: overline;">z</span>² означає:</p>
        <ol>
            <li>Взяти спряження z (відобразити відносно осі x)</li>
            <li>Піднести до квадрату</li>
        </ol>

        <h3>Цікаві координати</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Назва</th><th>Re</th><th>Im</th><th>Опис</th></tr>
            <tr><td>Лівий ріг</td><td>-1.0</td><td>0.0</td><td>Один з трьох рогів</td></tr>
            <tr><td>Верхня область</td><td>0.25</td><td>0.5</td><td>Деталі структури</td></tr>
            <tr><td>Спіраль</td><td>-1.292</td><td>-0.43</td><td>Спіральні візерунки</td></tr>
        </table>

        <h3>Зв'язок з іншими фракталами</h3>
        <p>Трикорн — це "дзеркальний двійник" Мандельброта. Якщо Мандельброт показує
        поведінку z², то Трикорн показує поведінку антиголоморфного відображення
        <span style="text-decoration: overline;">z</span>².</p>
        """)
        return browser

    def _create_phoenix_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Фрактал Фенікс</h2>

        <h3>Визначення</h3>
        <p>Фрактал Фенікс — це ітеративний фрактал з "пам'яттю", який використовує
        не тільки поточне значення z, але й попереднє:</p>

        <div class="formula">
            z<sub>n+1</sub> = z<sub>n</sub>² + p<sub>re</sub> + p<sub>im</sub> · z<sub>n-1</sub>
        </div>

        <p>де p = p<sub>re</sub> + i·p<sub>im</sub> — параметр фракталу</p>

        <h3>Розгорнута формула</h3>
        <div class="formula">
            x<sub>n+1</sub> = x<sub>n</sub>² - y<sub>n</sub>² + p<sub>re</sub> + p<sub>im</sub> · x<sub>n-1</sub><br>
            y<sub>n+1</sub> = 2·x<sub>n</sub>·y<sub>n</sub> + p<sub>im</sub> · y<sub>n-1</sub>
        </div>

        <h3>Особливості</h3>
        <div class="note">
            <ul>
                <li>Використовує <b>два попередні значення</b> (пам'ять системи)</li>
                <li>Створює форми, схожі на <b>птаха Фенікса</b></li>
                <li>Різні значення p дають драматично різні форми</li>
                <li>Запропонований Шинджі Садехарою у 1988 році</li>
            </ul>
        </div>

        <h3>Параметри</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Назва</th><th>p<sub>re</sub></th><th>p<sub>im</sub></th><th>Опис</th></tr>
            <tr><td>Класичний</td><td>0.5667</td><td>-0.5</td><td>Оригінальний Фенікс</td></tr>
            <tr><td>Полум'я</td><td>0.2</td><td>-0.6</td><td>Вогняні візерунки</td></tr>
            <tr><td>Перо</td><td>-0.5</td><td>0.0</td><td>Пероподібні структури</td></tr>
            <tr><td>Спіраль</td><td>0.56667</td><td>-0.5</td><td>Спіральні форми</td></tr>
            <tr><td>Дракон</td><td>0.4</td><td>-0.65</td><td>Драконоподібний вигляд</td></tr>
        </table>

        <h3>Математичний зміст</h3>
        <p>Член p<sub>im</sub> · z<sub>n-1</sub> додає "інерцію" до системи — поточний стан
        залежить не тільки від попереднього, але й від перед-попереднього значення.
        Це створює більш складну динаміку.</p>

        <h3>Порівняння з Мандельбротом</h3>
        <div class="note">
            <p><b>Мандельброт:</b> z<sub>n+1</sub> = z<sub>n</sub>² + c (без пам'яті)</p>
            <p><b>Фенікс:</b> z<sub>n+1</sub> = z<sub>n</sub>² + p<sub>re</sub> + p<sub>im</sub> · z<sub>n-1</sub> (з пам'яттю)</p>
        </div>

        <h3>Анімація</h3>
        <p>Плавна зміна параметрів p<sub>re</sub> та p<sub>im</sub> по колу або еліпсу
        створює гіпнотичну анімацію "дихаючого" Фенікса.</p>
        """)
        return browser

    def _create_ifs_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>IFS-фрактали (Iterated Function Systems)</h2>

        <h3>Що таке IFS?</h3>
        <p>Система ітерованих функцій — це набір афінних перетворень, які застосовуються
        випадково для генерації фрактальних структур.</p>

        <h3>Папороть Барнслі</h3>
        <p>Класичний IFS-фрактал, що імітує листок папороті. Використовує 4 афінні перетворення:</p>
        <div class="formula">
            f<sub>1</sub>: стебло (ймовірність 1%)<br>
            f<sub>2</sub>: основні листочки (85%)<br>
            f<sub>3</sub>: ліва гілка (7%)<br>
            f<sub>4</sub>: права гілка (7%)
        </div>

        <h3>Трикутник Серпінського</h3>
        <p>Алгоритм "Гра хаосу" (Chaos Game):</p>
        <ol>
            <li>Визначити 3 вершини рівностороннього трикутника</li>
            <li>Обрати випадкову початкову точку</li>
            <li>Випадково обрати вершину, перемістити точку на половину відстані до неї</li>
            <li>Повторювати крок 3 мільйони разів</li>
        </ol>
        <div class="note">
            <p><b>Фрактальна розмірність:</b> D = log(3)/log(2) ≈ 1.585</p>
        </div>

        <h3>Сніжинка Коха</h3>
        <p>L-система, де кожен відрізок замінюється на 4 нових:</p>
        <div class="formula">
            _____ → __/\\__
        </div>
        <div class="note">
            <p><b>Фрактальна розмірність:</b> D = log(4)/log(3) ≈ 1.2619</p>
            <p>Периметр → ∞, але площа залишається обмеженою!</p>
        </div>

        <h3>Буддаброт</h3>
        <p>Альтернативна візуалізація Мандельброта. Замість розфарбування за номером ітерації,
        відстежуються орбіти <b>втікаючих</b> точок, і накопичується карта щільності.</p>
        <div class="note">
            <p>Результат нагадує фігуру Будди, що медитує — звідси назва.</p>
            <p>Відкритий Мелінд Грін у 1993 році.</p>
        </div>
        """)
        return browser

    def _create_dimension_tab(self) -> QWidget:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e1e; color: #e0e0e0; padding: 15px; }
            h2 { color: #4fc3f7; }
            h3 { color: #81c784; }
            .formula { background: #2d2d2d; padding: 15px; border-radius: 8px; font-family: 'Cambria Math', serif; font-size: 16px; margin: 10px 0; text-align: center; }
            .note { background: #37474f; padding: 10px; border-left: 4px solid #4fc3f7; margin: 10px 0; }
        </style>
        <h2>Фрактальна розмірність</h2>

        <h3>Інтуїція</h3>
        <p>Фрактальна розмірність описує "складність" об'єкта — наскільки він заповнює простір.</p>
        <ul>
            <li>Точка: D = 0</li>
            <li>Пряма лінія: D = 1</li>
            <li>Квадрат: D = 2</li>
            <li>Куб: D = 3</li>
            <li><b>Фрактали: нецілі значення!</b></li>
        </ul>

        <h3>Метод Box-counting (підрахунок комірок)</h3>
        <p>Алгоритм обчислення розмірності Хаусдорфа:</p>
        <ol>
            <li>Покрити фрактал сіткою з комірок розміру s</li>
            <li>Підрахувати N(s) — кількість комірок, що містять фрактал</li>
            <li>Повторити для різних s (степені двійки)</li>
            <li>Розмірність — нахил графіка log(N) vs log(1/s)</li>
        </ol>

        <div class="formula">
            D = lim<sub>s→0</sub> [log N(s) / log(1/s)]
        </div>

        <h3>Приклади розмірностей</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr><th>Фрактал</th><th>Розмірність D</th></tr>
            <tr><td>Границя Мандельброта</td><td><b>2.0</b> (доведено 1991)</td></tr>
            <tr><td>Множина Жюліа</td><td>1.3 — 2.0 (залежить від c)</td></tr>
            <tr><td>Трикутник Серпінського</td><td>log(3)/log(2) ≈ <b>1.585</b></td></tr>
            <tr><td>Сніжинка Коха</td><td>log(4)/log(3) ≈ <b>1.262</b></td></tr>
            <tr><td>Папороть Барнслі</td><td>≈ <b>1.7</b></td></tr>
        </table>

        <h3>Практичне значення</h3>
        <div class="note">
            <ul>
                <li><b>Медицина:</b> діагностика пухлин за формою клітин</li>
                <li><b>Географія:</b> аналіз берегових ліній, русел річок</li>
                <li><b>Матеріалознавство:</b> характеристика пористості</li>
                <li><b>Фінанси:</b> аналіз волатильності ринку</li>
                <li><b>Комп'ютерна графіка:</b> генерація реалістичних текстур</li>
            </ul>
        </div>
        """)
        return browser
