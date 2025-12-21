"""API клиент для отправки лучшего результата на сервер."""
import threading
import urllib.request
import urllib.error
import json

# URL сервера (локальная разработка)
API_URL = "http://localhost:3001/api/digits/score"


def submit_score(name: str, game_score: int, remaining_time: int, callback=None):
    """Отправляет лучший результат на сервер (в фоновом потоке).

    Args:
        name: Имя игрока
        game_score: Очки за игру
        remaining_time: Оставшееся время (для расчёта бонуса на сервере)
        callback: Функция(success, response) вызывается после завершения
    """
    def _send():
        try:
            data = json.dumps({
                "name": name,
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
