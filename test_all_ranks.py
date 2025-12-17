#!/usr/bin/env python
"""Test script to view result window with all ranks."""
import pygame
import sys

# Add game_digits to path
sys.path.insert(0, '.')

from game_digits import scale
from game_digits.ranks import RANKS
from game_digits.windows.result_window import ResultWindow


def main():
    pygame.init()

    # Initialize scale
    screen_size = (800, 600)
    scale.init(screen_size)

    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Test All Ranks")

    # Background color
    bg_color = (240, 235, 220)

    def redraw_callback():
        screen.fill(bg_color)

    print("Press SPACE or click 'Новая игра' to see next rank")
    print("Press ESC or close window to exit")
    print("-" * 40)

    for min_score, rank_name, fg, bg in RANKS:
        # Calculate score to get this rank
        # total = score + bonus, bonus = 300 + 5*time
        # For simplicity, set game_score so total equals min_score + 50
        test_total = min_score + 50 if min_score > 0 else 100
        test_bonus = 300  # minimum bonus (time=0)
        test_score = test_total - test_bonus

        print(f"Showing: {rank_name} (score {min_score}+)")

        # Create result window in test mode
        result_window = ResultWindow(
            screen=screen,
            screen_size=screen_size,
            game_score=test_score,
            current_time=0,  # No time bonus
            redraw_callback=redraw_callback,
            play_sound_callback=None,
            test_mode=True  # Don't save to records
        )

        result = result_window.show()

        if result is None:
            # Window closed
            break
        elif result == 'menu':
            # Close button - exit
            break
        # 'new_game' - continue to next rank

    pygame.quit()
    print("Done!")


if __name__ == "__main__":
    main()
