"""API клиент для отправки лучшего результата на сервер."""
import threading
import urllib.request
import urllib.error
import json
import uuid
from pathlib import Path

from game_digits import settings

# URL сервера (локальная разработка)
API_URL = "http://localhost:3001/api/digits/score"

# Путь к файлу с ID игрока
PLAYER_ID_PATH = Path.home() / ".game_digits" / "player_id"


def get_player_id():
    """Получить или создать уникальный ID игрока."""
    PLAYER_ID_PATH.parent.mkdir(exist_ok=True)

    if PLAYER_ID_PATH.exists():
        return PLAYER_ID_PATH.read_text().strip()

    # Создаём новый ID при первом запуске
    player_id = str(uuid.uuid4())
    PLAYER_ID_PATH.write_text(player_id)
    return player_id


def submit_score(game_score: int, remaining_time: int, callback=None):
    """Отправляет лучший результат на сервер (в фоновом потоке).

    Args:
        game_score: Очки за игру
        remaining_time: Оставшееся время (для расчёта бонуса на сервере)
        callback: Функция(success, response) вызывается после завершения
    """
    def _send():
        try:
            data = json.dumps({
                "playerId": get_player_id(),
                "name": settings.get_player_name(),
                "gameScore": game_score,
                "remainingTime": remaining_time
            }).encode('utf-8')

            req = urllib.request.Request(
                API_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                if callback:
                    callback(True, result)
        except urllib.error.URLError as e:
            # Сервер недоступен - не критично, игра продолжает работать
            if callback:
                callback(False, f"Server unavailable: {e.reason}")
        except Exception as e:
            if callback:
                callback(False, str(e))

    # Отправляем в фоновом потоке, чтобы не блокировать игру
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
