# Модуль для управления масштабом игры
# Измените SCALE для увеличения/уменьшения ВСЕХ размеров

# Коэффициент масштабирования (1.0 = 100%, 0.9 = 90%, 1.1 = 110%)
SCALE = 0.9


def scaled(value):
    """Масштабирует значение и округляет до целого."""
    return max(1, int(value * SCALE))


# ============================================
# ПЛИТКИ
# ============================================
BASE_TILE_SIZE = 64
BASE_GAP = 3
BASE_TILE_FONT_SIZE = 40

TILE_SIZE = scaled(BASE_TILE_SIZE)
GAP = scaled(BASE_GAP)
TILE_FONT_SIZE = scaled(BASE_TILE_FONT_SIZE)

# ============================================
# ПАНЕЛЬ СПРАВА
# ============================================
BASE_PANEL_WIDTH = 240

PANEL_WIDTH = scaled(BASE_PANEL_WIDTH)

# ============================================
# ШРИФТЫ ПАНЕЛИ (app.py) - "Время", "Очки", цифры, "пауза"
# ============================================
BASE_FONT_PANEL_LABEL = 26    # "Время", "Очки"
BASE_FONT_PANEL_VALUE = 36    # цифры очков/времени
BASE_FONT_PANEL_PAUSE = 22    # "пауза"

FONT_PANEL_LABEL = scaled(BASE_FONT_PANEL_LABEL)
FONT_PANEL_VALUE = scaled(BASE_FONT_PANEL_VALUE)
FONT_PANEL_PAUSE = scaled(BASE_FONT_PANEL_PAUSE)

# ============================================
# ШРИФТЫ МЕНЮ (start_menu.py)
# ============================================
BASE_FONT_MENU_BUTTON = 28
BASE_FONT_MENU_RECORDS_TITLE = 24
BASE_FONT_MENU_RECORDS = 16
BASE_FONT_MENU_RECORDS_SMALL = 14

FONT_MENU_BUTTON = scaled(BASE_FONT_MENU_BUTTON)
FONT_MENU_RECORDS_TITLE = scaled(BASE_FONT_MENU_RECORDS_TITLE)
FONT_MENU_RECORDS = scaled(BASE_FONT_MENU_RECORDS)
FONT_MENU_RECORDS_SMALL = scaled(BASE_FONT_MENU_RECORDS_SMALL)

# ============================================
# ШРИФТЫ РЕЗУЛЬТАТА (result_window.py)
# ============================================
BASE_FONT_RESULT_TITLE = 32
BASE_FONT_RESULT_LABEL = 26
BASE_FONT_RESULT_VALUE = 30
BASE_FONT_RESULT_BUTTON = 28

FONT_RESULT_TITLE = scaled(BASE_FONT_RESULT_TITLE)
FONT_RESULT_LABEL = scaled(BASE_FONT_RESULT_LABEL)
FONT_RESULT_VALUE = scaled(BASE_FONT_RESULT_VALUE)
FONT_RESULT_BUTTON = scaled(BASE_FONT_RESULT_BUTTON)

# ============================================
# ШРИФТЫ ПАУЗЫ (pause_overlay.py)
# ============================================
BASE_FONT_PAUSE_TEXT = 32
BASE_FONT_PAUSE_TITLE = 28

FONT_PAUSE_TEXT = scaled(BASE_FONT_PAUSE_TEXT)
FONT_PAUSE_TITLE = scaled(BASE_FONT_PAUSE_TITLE)

# ============================================
# РАЗМЕРЫ КНОПОК
# ============================================
BASE_BUTTON_WIDTH = 200       # кнопка "Играть" в меню
BASE_BUTTON_HEIGHT = 50
BASE_RECORDS_BTN_WIDTH = 180
BASE_RECORDS_BTN_HEIGHT = 45
BASE_CLOSE_BTN_SIZE = 32
BASE_PAUSE_BTN_WIDTH = 120    # кнопка "пауза" на панели
BASE_PAUSE_BTN_HEIGHT = 40

BUTTON_WIDTH = scaled(BASE_BUTTON_WIDTH)
BUTTON_HEIGHT = scaled(BASE_BUTTON_HEIGHT)
RECORDS_BTN_WIDTH = scaled(BASE_RECORDS_BTN_WIDTH)
RECORDS_BTN_HEIGHT = scaled(BASE_RECORDS_BTN_HEIGHT)
CLOSE_BTN_SIZE = scaled(BASE_CLOSE_BTN_SIZE)
PAUSE_BTN_WIDTH = scaled(BASE_PAUSE_BTN_WIDTH)
PAUSE_BTN_HEIGHT = scaled(BASE_PAUSE_BTN_HEIGHT)

# ============================================
# РАЗМЕРЫ ИКОНОК И ПАНЕЛИ
# ============================================
BASE_ICON_SIZE = 50           # солнце, циферблат
BASE_VALUE_BAR_HEIGHT = 44    # высота полосок времени/очков
BASE_PROGRESS_BAR_HEIGHT = 22 # высота прогресс-бара
BASE_PANEL_PADDING = 20       # отступы на панели

ICON_SIZE = scaled(BASE_ICON_SIZE)
VALUE_BAR_HEIGHT = scaled(BASE_VALUE_BAR_HEIGHT)
PROGRESS_BAR_HEIGHT = scaled(BASE_PROGRESS_BAR_HEIGHT)
PANEL_PADDING = scaled(BASE_PANEL_PADDING)

# ============================================
# РАЗМЕРЫ РАМОК И ОТСТУПОВ
# ============================================
BASE_FRAME_WIDTH = 10
BASE_BORDER_WIDTH = 2
BASE_CORNER_RADIUS = 12
BASE_GRID_CELL_SIZE = 18  # клеточки фона

FRAME_WIDTH = scaled(BASE_FRAME_WIDTH)
BORDER_WIDTH = scaled(BASE_BORDER_WIDTH)
CORNER_RADIUS = scaled(BASE_CORNER_RADIUS)
GRID_CELL_SIZE = scaled(BASE_GRID_CELL_SIZE)

# ============================================
# ПАНЕЛЬ РЕКОРДОВ (start_menu.py)
# ============================================
BASE_RECORDS_PANEL_TOP = 90       # отступ сверху
BASE_RECORDS_ROW_HEIGHT = 50
BASE_RECORDS_HEADER_Y = 15
BASE_RECORDS_START_Y = 45        # начало списка рекордов
BASE_RECORDS_BOTTOM_PAD = 10     # отступ снизу
# Позиции колонок (от левого края панели)
BASE_RECORDS_COL_1 = 20          # #
BASE_RECORDS_COL_2 = 65          # Очки
BASE_RECORDS_COL_3 = 120         # Бонус
BASE_RECORDS_COL_4 = 175         # Итого

RECORDS_PANEL_TOP = scaled(BASE_RECORDS_PANEL_TOP)
RECORDS_ROW_HEIGHT = scaled(BASE_RECORDS_ROW_HEIGHT)
RECORDS_HEADER_Y = scaled(BASE_RECORDS_HEADER_Y)
RECORDS_START_Y = scaled(BASE_RECORDS_START_Y)
RECORDS_COL_1 = scaled(BASE_RECORDS_COL_1)
RECORDS_COL_2 = scaled(BASE_RECORDS_COL_2)
RECORDS_COL_3 = scaled(BASE_RECORDS_COL_3)
RECORDS_COL_4 = scaled(BASE_RECORDS_COL_4)
# Высота вычисляется: начало + 10 строк + отступ
RECORDS_PANEL_HEIGHT = RECORDS_START_Y + 10 * RECORDS_ROW_HEIGHT + scaled(BASE_RECORDS_BOTTOM_PAD)
