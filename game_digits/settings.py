# Модуль настроек игры
# Поддерживает динамическое изменение масштаба и скорости

# Пресеты размеров
PRESETS = {
    'small': {
        'name': 'Маленький',
        'scale': 0.7,
        'speed': 2,
    },
    'medium': {
        'name': 'Средний',
        'scale': 0.9,
        'speed': 2,
    },
    'large': {
        'name': 'Большой',
        'scale': 1.0,
        'speed': 3,
    },
    'xlarge': {
        'name': 'Очень большой',
        'scale': 1.2,
        'speed': 4,
    },
}

# Порядок пресетов для переключения
PRESET_ORDER = ['small', 'medium', 'large', 'xlarge']

# Текущие настройки (глобальное состояние)
_current_preset = 'medium'


def get_current_preset():
    """Получить текущий пресет."""
    return _current_preset


def get_current_settings():
    """Получить текущие настройки."""
    return PRESETS[_current_preset]


def get_preset_name():
    """Получить название текущего пресета на русском."""
    return PRESETS[_current_preset]['name']


def get_scale():
    """Получить текущий масштаб."""
    return PRESETS[_current_preset]['scale']


def get_speed():
    """Получить текущую скорость."""
    return PRESETS[_current_preset]['speed']


def set_preset(preset_key):
    """Установить пресет по ключу."""
    global _current_preset
    if preset_key in PRESETS:
        _current_preset = preset_key
        return True
    return False


def next_preset():
    """Переключить на следующий пресет."""
    global _current_preset
    idx = PRESET_ORDER.index(_current_preset)
    idx = (idx + 1) % len(PRESET_ORDER)
    _current_preset = PRESET_ORDER[idx]
    return _current_preset


def prev_preset():
    """Переключить на предыдущий пресет."""
    global _current_preset
    idx = PRESET_ORDER.index(_current_preset)
    idx = (idx - 1) % len(PRESET_ORDER)
    _current_preset = PRESET_ORDER[idx]
    return _current_preset


def get_all_presets():
    """Получить все пресеты."""
    return [(key, PRESETS[key]['name']) for key in PRESET_ORDER]
