"""API клиент для отправки лучшего результата в Supabase."""
import threading
import urllib.request
import urllib.error
import json
import uuid
import ssl
from pathlib import Path

from game_digits import settings

# Supabase конфигурация
SUPABASE_URL = "https://tuskcdlcbasehlrsrsoe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1c2tjZGxjYmFzZWhscnNyc29lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYyOTM4NzcsImV4cCI6MjA4MTg2OTg3N30.VdfhknWL4SgbMUOxFZKsnAsjI3SUbcyoYXDiONjOjao"

# Путь к файлу с ID игрока
PLAYER_ID_PATH = Path.home() / ".game_digits" / "player_id"
LOG_PATH = Path.home() / ".game_digits" / "api_log.txt"


def _log(message):
    """Записать сообщение в лог-файл."""
    try:
        LOG_PATH.parent.mkdir(exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    except:
        pass


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
            _log(f"Отправка: game_score={game_score}, remaining_time={remaining_time}")

            # Расчёт бонуса и общего счёта (формула как в игре)
            time_bonus = 300 + 5 * remaining_time
            total_score = game_score + time_bonus

            data = json.dumps({
                "player_id": get_player_id(),
                "name": settings.get_player_name(),
                "score": total_score,
                "game_score": game_score,
                "time_bonus": time_bonus,
                "remaining_time": remaining_time
            }).encode('utf-8')

            url = f"{SUPABASE_URL}/rest/v1/scores?on_conflict=player_id"
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

            # SSL контекст для PyInstaller
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                result = resp.read().decode()
                _log(f"Успех: {result}")
                if callback:
                    callback(True, result)
        except urllib.error.URLError as e:
            _log(f"URLError: {e.reason}")
            if callback:
                callback(False, f"Server unavailable: {e.reason}")
        except Exception as e:
            _log(f"Exception: {e}")
            if callback:
                callback(False, str(e))

    # Отправляем в фоновом потоке, чтобы не блокировать игру
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
