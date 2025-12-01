"""
Records storage and management for the game.
Stores top 10 best results in a JSON file.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def get_records_path():
    """Get the path to the records file."""
    # Store in user's home directory under .game_digits
    home = Path.home()
    records_dir = home / ".game_digits"
    records_dir.mkdir(exist_ok=True)
    return records_dir / "records.json"


def load_records():
    """Load records from file.

    Returns:
        list: List of record dictionaries, sorted by total score descending.
              Each record has: score, bonus, total, date
    """
    records_path = get_records_path()

    if not records_path.exists():
        return []

    try:
        with open(records_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        # Ensure records are sorted by total descending
        records.sort(key=lambda x: x.get('total', 0), reverse=True)
        return records[:10]  # Keep only top 10
    except (json.JSONDecodeError, IOError):
        return []


def save_records(records):
    """Save records to file.

    Args:
        records: List of record dictionaries
    """
    records_path = get_records_path()

    # Sort and keep only top 10
    records.sort(key=lambda x: x.get('total', 0), reverse=True)
    records = records[:10]

    try:
        with open(records_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except IOError:
        pass  # Silently fail if can't write


def add_record(score, bonus, total):
    """Add a new record if it qualifies for top 10.

    Args:
        score: Game score (points collected)
        bonus: Speed bonus (300 + 5 * remaining_time)
        total: Total score (score + bonus)

    Returns:
        int or None: Position in leaderboard (1-10) if record was added,
                     None if didn't qualify for top 10
    """
    records = load_records()

    new_record = {
        'score': score,
        'bonus': bonus,
        'total': total,
        'date': datetime.now().strftime('%d.%m.%Y')
    }

    # Check if this score qualifies for top 10
    if len(records) < 10 or total > records[-1].get('total', 0):
        records.append(new_record)
        records.sort(key=lambda x: x.get('total', 0), reverse=True)
        records = records[:10]
        save_records(records)

        # Find position of new record
        for i, rec in enumerate(records):
            if rec == new_record:
                return i + 1  # 1-indexed position

    return None


def get_best_score():
    """Get the best total score.

    Returns:
        int: Best total score, or 0 if no records
    """
    records = load_records()
    if records:
        return records[0].get('total', 0)
    return 0


def is_new_record(total):
    """Check if a score would be a new record (top 10).

    Args:
        total: Total score to check

    Returns:
        bool: True if this would qualify for top 10
    """
    records = load_records()
    if len(records) < 10:
        return True
    return total > records[-1].get('total', 0)
