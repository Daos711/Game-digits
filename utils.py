import sys
import os

def resource_path(relative_path):
    """ Получает путь к ресурсам, работая как в исходном коде, так и в собранном файле """
    try:
        # PyInstaller создаёт временную папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
