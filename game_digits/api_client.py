"""API клиент для отправки лучшего результата в Supabase."""
import threading
import urllib.request
import urllib.error
import json
import uuid
from pathlib import Path

from game_digits import settings

# Supabase конфигурация
SUPABASE_URL = "https://tuskcdlcbasehlrsrsoe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1c2tjZGxjYmFzZWhscnNyc29lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYyOTM4NzcsImV4cCI6MjA4MTg2OTg3N30.VdfhknWL4SgbMUOxFZKsnAsjI3SUbcyoYXDiONjOjao"

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
    """Отправляет лучший результат в Supabase (в фоновом потоке).

    Args:
        game_score: Очки за игру
        remaining_time: Оставшееся время в секундах
        callback: Функция(success, response) вызывается после завершения
    """
    def _send():
        try:
            # Расчёт бонуса и общего счёта
            time_bonus = remaining_time * 10
            total_score = game_score + time_bonus

            data = json.dumps({
                "player_id": get_player_id(),
                "name": settings.get_player_name(),
                "score": total_score,
                "game_score": game_score,
                "time_bonus": time_bonus,
                "remaining_time": remaining_time
            }).encode('utf-8')

            url = f"{SUPABASE_URL}/rest/v1/scores"
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
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
