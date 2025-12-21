# Модуль настроек игры
# Поддерживает динамическое изменение масштаба и скорости

import json
from pathlib import Path

# Путь к файлу конфигурации
CONFIG_PATH = Path.home() / ".game_digits" / "config.json"

# Пресеты размеров
SIZE_PRESETS = {
    'small': {'name': 'Маленький', 'scale': 0.7},
    'medium': {'name': 'Средний', 'scale': 0.9},
    'large': {'name': 'Большой', 'scale': 1.0},
    'xlarge': {'name': 'Очень большой', 'scale': 1.2},
}

# Пресеты скорости
SPEED_PRESETS = {
    'slow': {'name': 'Медленно', 'speed': 2},
    'normal': {'name': 'Нормально', 'speed': 3},
    'fast': {'name': 'Быстро', 'speed': 5},
    'very_fast': {'name': 'Очень быстро', 'speed': 8},
}

# Порядок пресетов для переключения
SIZE_ORDER = ['small', 'medium', 'large', 'xlarge']
SPEED_ORDER = ['slow', 'normal', 'fast', 'very_fast']

# Текущие настройки (глобальное состояние)
_current_size = 'medium'
_current_speed = 'normal'

# Для обратной совместимости
PRESETS = SIZE_PRESETS
PRESET_ORDER = SIZE_ORDER
_current_preset = _current_size


def get_current_preset():
    """Получить текущий пресет размера (для обратной совместимости)."""
    return _current_size


def get_current_settings():
    """Получить текущие настройки."""
    return {
        'scale': SIZE_PRESETS[_current_size]['scale'],
        'speed': SPEED_PRESETS[_current_speed]['speed'],
    }


def get_preset_name():
    """Получить название текущего пресета размера."""
    return SIZE_PRESETS[_current_size]['name']


def get_scale():
    """Получить текущий масштаб."""
    return SIZE_PRESETS[_current_size]['scale']


def get_speed():
    """Получить текущую скорость."""
    return SPEED_PRESETS[_current_speed]['speed']


def get_speed_name():
    """Получить название текущего пресета скорости."""
    return SPEED_PRESETS[_current_speed]['name']


def get_current_speed_preset():
    """Получить текущий пресет скорости."""
    return _current_speed


def set_preset(preset_key):
    """Установить пресет размера по ключу."""
    global _current_size
    if preset_key in SIZE_PRESETS:
        _current_size = preset_key
        return True
    return False


def set_speed_preset(preset_key):
    """Установить пресет скорости по ключу."""
    global _current_speed
    if preset_key in SPEED_PRESETS:
        _current_speed = preset_key
        return True
    return False


def next_preset():
    """Переключить на следующий пресет размера."""
    global _current_size
    idx = SIZE_ORDER.index(_current_size)
    idx = (idx + 1) % len(SIZE_ORDER)
    _current_size = SIZE_ORDER[idx]
    return _current_size


def prev_preset():
    """Переключить на предыдущий пресет размера."""
    global _current_size
    idx = SIZE_ORDER.index(_current_size)
    idx = (idx - 1) % len(SIZE_ORDER)
    _current_size = SIZE_ORDER[idx]
    return _current_size


def next_speed():
    """Переключить на следующий пресет скорости."""
    global _current_speed
    idx = SPEED_ORDER.index(_current_speed)
    idx = (idx + 1) % len(SPEED_ORDER)
    _current_speed = SPEED_ORDER[idx]
    return _current_speed


def prev_speed():
    """Переключить на предыдущий пресет скорости."""
    global _current_speed
    idx = SPEED_ORDER.index(_current_speed)
    idx = (idx - 1) % len(SPEED_ORDER)
    _current_speed = SPEED_ORDER[idx]
    return _current_speed


def get_all_presets():
    """Получить все пресеты размера."""
    return [(key, SIZE_PRESETS[key]['name']) for key in SIZE_ORDER]


# === Имя игрока ===

_player_name = "Player"  # Значение по умолчанию


def _load_config():
    """Загрузить конфигурацию из файла."""
    global _player_name
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                _player_name = config.get('player_name', 'Player')
        except (json.JSONDecodeError, IOError):
            pass


def _save_config():
    """Сохранить конфигурацию в файл."""
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    config = {'player_name': _player_name}
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def get_player_name():
    """Получить имя игрока."""
    return _player_name


def set_player_name(name):
    """Установить имя игрока и сохранить."""
    global _player_name
    _player_name = name.strip() or "Player"
    _save_config()


# Загружаем конфиг при импорте модуля
_load_config()
