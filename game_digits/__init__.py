import sys
from pathlib import Path


def _get_base_path():
    """Возвращает базовый путь - для PyInstaller или обычного запуска."""
    if getattr(sys, 'frozen', False):
        # Запуск из скомпилированного exe (PyInstaller)
        return Path(sys._MEIPASS)
    else:
        # Обычный запуск из исходников
        return Path(__file__).parent


# Путь к директории assets
ASSETS_DIR = _get_base_path() / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"


def get_asset_path(relative_path: str) -> str:
    """Получает путь к ресурсу в папке assets."""
    return str(ASSETS_DIR / relative_path)


def get_image_path(filename: str) -> str:
    """Получает путь к изображению."""
    return str(IMAGES_DIR / filename)


def get_font_path(filename: str) -> str:
    """Получает путь к шрифту."""
    return str(FONTS_DIR / filename)


def get_sound_path(filename: str) -> str:
    """Получает путь к звуковому файлу."""
    return str(SOUNDS_DIR / filename)
