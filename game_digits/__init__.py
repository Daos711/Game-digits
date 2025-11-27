from pathlib import Path

# Путь к директории assets
ASSETS_DIR = Path(__file__).parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"


def get_asset_path(relative_path: str) -> str:
    """Получает путь к ресурсу в папке assets."""
    return str(ASSETS_DIR / relative_path)


def get_image_path(filename: str) -> str:
    """Получает путь к изображению."""
    return str(IMAGES_DIR / filename)


def get_font_path(filename: str) -> str:
    """Получает путь к шрифту."""
    return str(FONTS_DIR / filename)
