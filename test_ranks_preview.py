#!/usr/bin/env python3
"""
Test window to preview all ranks with their badges.
Run: python test_ranks_preview.py
"""
import pygame
import sys

# Initialize pygame first
pygame.init()

from game_digits import ranks
from game_digits import scale
from game_digits import get_font_path


def main():
    # Set up display
    screen_width = 700
    screen_height = 850
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Просмотр всех рангов")

    # Fonts
    title_font = pygame.font.Font(get_font_path("2204.ttf"), 28)
    header_font = pygame.font.Font(get_font_path("2204.ttf"), 16)
    score_font = pygame.font.Font(get_font_path("2204.ttf"), 14)

    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill((255, 253, 247))

        # Draw subtle grid
        grid_color = (245, 242, 234)
        for x in range(0, screen_width, 25):
            pygame.draw.line(screen, grid_color, (x, 0), (x, screen_height), 1)
        for y in range(0, screen_height, 25):
            pygame.draw.line(screen, grid_color, (0, y), (screen_width, y), 1)

        # Title
        title = title_font.render("Все ранги игры «Цифры»", True, (80, 70, 60))
        title_rect = title.get_rect(center=(screen_width // 2, 30))
        screen.blit(title, title_rect)

        # Decorative line
        pygame.draw.line(screen, (220, 200, 140), (50, 55), (screen_width - 50, 55), 2)

        # Column headers
        headers = ["Очки", "Ранг", "Бейдж"]
        header_x = [80, 200, 480]
        header_y = 75
        for text, x in zip(headers, header_x):
            h = header_font.render(text, True, (120, 110, 100))
            screen.blit(h, (x, header_y))

        # Header divider
        pygame.draw.line(screen, (200, 190, 170), (30, 100), (screen_width - 30, 100), 1)

        # Draw all ranks
        row_height = 38
        start_y = 110
        badge_max_width = 220
        badge_height = 28

        for i, (min_score, name, fg_color, bg_color) in enumerate(ranks.RANKS):
            row_y = start_y + i * row_height
            row_center_y = row_y + row_height // 2

            # Highlight legendary ranks (3000+)
            if min_score >= 3000:
                highlight_rect = pygame.Rect(25, row_y, screen_width - 50, row_height - 2)
                pygame.draw.rect(screen, (255, 250, 240, 200), highlight_rect, border_radius=4)

            # Score
            score_text = score_font.render(f"{min_score}+", True, (100, 100, 100))
            screen.blit(score_text, (80, row_center_y - score_text.get_height() // 2))

            # Rank name (text only)
            name_color = (60, 60, 60) if min_score < 3000 else (180, 100, 20)
            name_text = score_font.render(name, True, name_color)
            screen.blit(name_text, (150, row_center_y - name_text.get_height() // 2))

            # Badge
            badge_center_x = 480
            ranks.draw_rank_badge(
                screen,
                (badge_center_x, row_center_y, badge_max_width, badge_height),
                name, fg_color, bg_color,
                time_ms=current_time
            )

            # Row divider
            if i < len(ranks.RANKS) - 1:
                div_y = row_y + row_height - 1
                pygame.draw.line(screen, (235, 230, 220), (30, div_y), (screen_width - 30, div_y), 1)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
