"""Result window for displaying game results."""
import sys
import pygame

from game_digits import get_font_path
from game_digits import ui_components as ui
from game_digits import records
from game_digits import ranks
from game_digits import scale
from game_digits.sprites import ConfettiSystem


class ResultWindow:
    """Display the game result window with final score.

    Args:
        screen: Pygame screen surface
        screen_size: Tuple (width, height) of the screen
        game_score: Player's score from the game
        current_time: Remaining time when game ended
        redraw_callback: Function to call to redraw game background
    """

    # Animation timing constants (in milliseconds)
    WINDOW_FADE_IN_DURATION = 200   # Fade in of window and overlay
    ROW_APPEAR_DELAY = 1000         # Interval between row appearances (1s)
    NUMBER_ANIMATION_DURATION = 2500  # Number animation duration (2.5s)

    def __init__(self, screen, screen_size, game_score, current_time, redraw_callback, play_sound_callback=None, test_mode=False):
        # Window dimensions (масштабируемые - вычисляем в __init__ для динамического масштаба)
        self.WINDOW_WIDTH = scale.scaled(420)
        self.WINDOW_HEIGHT = scale.scaled(340)

        # Layout constants (масштабируемые)
        self.HEADER_HEIGHT = scale.scaled(50)
        self.PADDING = scale.scaled(20)
        self.ROW_HEIGHT = scale.scaled(50)
        self.ROW_GAP = scale.scaled(12)
        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.game_score = game_score
        self.current_time = current_time
        self.redraw_callback = redraw_callback
        self.play_sound = play_sound_callback
        self.test_mode = test_mode

        # Calculate window position (centered)
        self.window_x = (self.screen_width - self.WINDOW_WIDTH) // 2
        self.window_y = (self.screen_height - self.WINDOW_HEIGHT) // 2

        # Calculate scores
        self.remaining_time = round(self.current_time)
        self.bonus = 300 + 5 * self.remaining_time
        self.total_score = self.game_score + self.bonus

        # Get rank info (name, fg_color, bg_color)
        self.rank_name, self.rank_fg, self.rank_bg = ranks.get_rank(self.total_score)

        # Add height for rank row (same as other rows)
        self.RANK_ROW_HEIGHT = self.ROW_HEIGHT + self.ROW_GAP  # Same visual height as other rows
        self.WINDOW_HEIGHT += self.RANK_ROW_HEIGHT

        # Save record FIRST to know if we need extra space
        self.record_position = records.add_record(
            score=self.game_score,
            bonus=self.bonus,
            total=self.total_score,
            test_mode=self.test_mode
        )

        # Adjust window height if showing congratulations
        self.CONGRATS_HEIGHT = scale.scaled(35) if self.record_position is not None else 0
        self.actual_window_height = self.WINDOW_HEIGHT + self.CONGRATS_HEIGHT

        # Recalculate window position with new height
        self.window_y = (self.screen_height - self.actual_window_height) // 2

        # Load fonts
        bold_font_path = get_font_path("2204.ttf")
        self.title_font = pygame.font.Font(bold_font_path, scale.FONT_RESULT_TITLE)
        self.label_font = pygame.font.Font(bold_font_path, scale.FONT_RESULT_LABEL)
        self.value_font = pygame.font.Font(bold_font_path, scale.FONT_RESULT_VALUE)
        self.button_font = pygame.font.Font(bold_font_path, scale.FONT_RESULT_BUTTON)
        self.rank_fallback_font = pygame.font.Font(bold_font_path, scale.scaled(20))  # For long rank names

        # Button positions (relative to window) - adjusted for congrats row and rank row
        self.new_game_btn_rel = pygame.Rect(
            self.PADDING,
            self.HEADER_HEIGHT + self.PADDING + (self.ROW_HEIGHT + self.ROW_GAP) * 3 + self.RANK_ROW_HEIGHT + self.CONGRATS_HEIGHT + scale.scaled(12),
            self.WINDOW_WIDTH - 2 * self.PADDING,
            scale.scaled(50)
        )

        # Button state tracking
        self.new_game_pressed = False
        self.close_pressed = False

        # Animation state
        self.animation_start_time = 0
        self.visible_rows = 0
        self.animated_total = 0
        self.total_animation_started = False
        self.total_animation_start_time = 0
        self.rows_animation_started = False
        self.rows_animation_start_time = 0
        self.animation_complete = False

        # Конфетти для топ-10
        self.confetti = None
        self.confetti_started = False
        if self.record_position is not None:
            self.confetti = ConfettiSystem(self.screen_width, self.screen_height)

    def _draw_window(self, rows_to_show=3, current_total=None, opacity=255, overlay_alpha=128):
        """Draw the complete result window with animation state.

        Returns:
            Tuple of (close_btn_rect, new_game_btn_rect)
        """
        # Redraw game scene via callback
        self.redraw_callback()

        # Darken background with fade-in
        if overlay_alpha > 0:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            self.screen.blit(overlay, (0, 0))

        # Create window surface
        window_surface = pygame.Surface((self.WINDOW_WIDTH, self.actual_window_height), pygame.SRCALPHA)

        # Draw header FIRST
        close_btn_rect = ui.draw_result_window_header(
            window_surface,
            (0, 0, self.WINDOW_WIDTH, self.HEADER_HEIGHT),
            "Результат игры",
            self.title_font,
            close_pressed=self.close_pressed
        )

        # Draw checkered ON TOP with rounded corners visible
        ui.draw_checkered_content_area(
            window_surface,
            (0, 0, self.WINDOW_WIDTH, self.actual_window_height),
            self.HEADER_HEIGHT,
            corner_radius=scale.CORNER_RADIUS,
            cell_size=scale.scaled(18),
            border_color=(145, 179, 163)
        )

        # Draw result rows based on animation state
        row_x = self.PADDING
        row_width = self.WINDOW_WIDTH - 2 * self.PADDING
        current_y = self.HEADER_HEIGHT + self.PADDING

        # Row 1: Your result
        if rows_to_show >= 1:
            ui.draw_result_row(
                window_surface,
                (row_x, current_y, row_width, self.ROW_HEIGHT),
                "Ваш результат:",
                self.game_score,
                self.label_font,
                self.value_font
            )
        current_y += self.ROW_HEIGHT + self.ROW_GAP

        # Row 2: Speed bonus
        if rows_to_show >= 2:
            ui.draw_result_row(
                window_surface,
                (row_x, current_y, row_width, self.ROW_HEIGHT),
                "Бонус за скорость:",
                self.bonus,
                self.label_font,
                self.value_font
            )
        current_y += self.ROW_HEIGHT + self.ROW_GAP

        # Row 3: Total (with number animation)
        if rows_to_show >= 3:
            display_total = current_total if current_total is not None else self.total_score
            ui.draw_result_row(
                window_surface,
                (row_x, current_y, row_width, self.ROW_HEIGHT),
                "Итого:",
                display_total,
                self.label_font,
                self.value_font
            )
        current_y += self.ROW_HEIGHT + self.ROW_GAP

        # Row 4: Rank (show when total animation is complete)
        if rows_to_show >= 3 and current_total == self.total_score:
            # Same style as other rows: blue background with border
            rank_row_h = self.ROW_HEIGHT  # Same height as other rows
            radius = scale.scaled(10)
            border_width = scale.BORDER_WIDTH

            # Create temp surface for proper alpha handling
            temp = pygame.Surface((row_width, rank_row_h), pygame.SRCALPHA)

            # Draw border first (filled rounded rect)
            border_color = (120, 170, 190)
            ui.draw_rounded_rect(temp, (*border_color, 255), (0, 0, row_width, rank_row_h), radius)

            # Draw background on top (smaller by border_width)
            bg_color = (168, 212, 242)
            inner_radius = max(1, radius - border_width)
            ui.draw_rounded_rect(temp, (*bg_color, 255),
                              (border_width, border_width, row_width - 2 * border_width, rank_row_h - 2 * border_width),
                              inner_radius)

            # Apply transparency
            temp.set_alpha(170)
            window_surface.blit(temp, (row_x, current_y))

            # Text color - same as other rows
            text_color = (40, 92, 120)
            text_padding = scale.scaled(15)
            text_y = current_y + rank_row_h // 2 - scale.scaled(2)  # Slight upward adjustment for visual centering

            # "Ранг:" label
            rank_label = self.label_font.render("Ранг:", True, text_color)
            label_rect = rank_label.get_rect(midleft=(row_x + text_padding, text_y))
            window_surface.blit(rank_label, label_rect)

            # Rank name as text (right-aligned)
            # Calculate available width for rank name
            available_width = row_width - label_rect.width - text_padding * 3

            # Try with normal font first, reduce if too wide
            rank_font = self.value_font
            rank_text = rank_font.render(self.rank_name, True, text_color)

            # If text is too wide, use smaller font (cached)
            if rank_text.get_width() > available_width:
                rank_text = self.rank_fallback_font.render(self.rank_name, True, text_color)

            rank_text_rect = rank_text.get_rect(midright=(row_x + row_width - text_padding, text_y))
            window_surface.blit(rank_text, rank_text_rect)

        current_y += self.RANK_ROW_HEIGHT

        # Поздравление при попадании в топ-10
        if self.record_position is not None and rows_to_show >= 3 and current_total == self.total_score:
            # Рамка поздравления (цвет как в оригинале)
            congrats_bg_color = (255, 238, 194)  # Светло-жёлтый
            congrats_text_color = (171, 78, 59)   # Красно-коричневый
            congrats_rect = pygame.Rect(row_x, current_y, row_width, self.CONGRATS_HEIGHT)
            pygame.draw.rect(window_surface, congrats_bg_color, congrats_rect, border_radius=scale.scaled(8))
            # Тонкая обводка
            pygame.draw.rect(window_surface, (220, 200, 160), congrats_rect, width=1, border_radius=scale.scaled(8))
            # Текст по центру рамки
            place_text = self._get_place_text(self.record_position)
            congrats_surf = self.label_font.render(place_text, True, congrats_text_color)
            text_rect = congrats_surf.get_rect(center=congrats_rect.center)
            window_surface.blit(congrats_surf, text_rect)

        # "New game" button (show only when animation is complete)
        if rows_to_show >= 3 and current_total == self.total_score:
            new_game_btn_rect = ui.draw_new_game_button(
                window_surface,
                (self.new_game_btn_rel.x, self.new_game_btn_rel.y,
                 self.new_game_btn_rel.width, self.new_game_btn_rel.height),
                self.button_font,
                is_pressed=self.new_game_pressed
            )
        else:
            new_game_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Apply opacity to window
        if opacity < 255:
            window_surface.set_alpha(opacity)

        # Blit window to screen
        self.screen.blit(window_surface, (self.window_x, self.window_y))
        pygame.display.update()

        return close_btn_rect, new_game_btn_rect

    def _update_animation(self, current_time):
        """Update animation state based on current time."""
        elapsed = current_time - self.animation_start_time

        # Phase 1: Fade-in window and overlay (no rows)
        if elapsed < self.WINDOW_FADE_IN_DURATION:
            progress = elapsed / self.WINDOW_FADE_IN_DURATION
            window_opacity = int(255 * progress)
            overlay_alpha = int(128 * progress)
            self.visible_rows = 0
        else:
            window_opacity = 255
            overlay_alpha = 128

            # Phase 2: After fade-in, start row appearance countdown
            if not self.rows_animation_started:
                self.rows_animation_started = True
                self.rows_animation_start_time = current_time

            # Row appearance animation (each after 1s)
            if self.rows_animation_started:
                rows_elapsed = current_time - self.rows_animation_start_time
                if rows_elapsed < self.ROW_APPEAR_DELAY:
                    self.visible_rows = 1
                elif rows_elapsed < self.ROW_APPEAR_DELAY * 2:
                    self.visible_rows = 2
                else:
                    self.visible_rows = 3
                    # Start number animation when 3rd row appears
                    if not self.total_animation_started:
                        self.total_animation_started = True
                        self.total_animation_start_time = current_time

        # Animate total number
        if self.total_animation_started:
            anim_elapsed = current_time - self.total_animation_start_time
            if anim_elapsed >= self.NUMBER_ANIMATION_DURATION:
                self.animated_total = self.total_score
                self.animation_complete = True
            else:
                # Easing function for smooth slowdown at the end
                progress = anim_elapsed / self.NUMBER_ANIMATION_DURATION
                # Ease-out quad: 1 - (1 - t)^2
                eased_progress = 1 - (1 - progress) ** 2
                self.animated_total = int(self.total_score * eased_progress)
        else:
            self.animated_total = 0

        return window_opacity, overlay_alpha

    def _get_place_text(self, position):
        """Возвращает текст поздравления с местом."""
        if position == 1:
            return "Новый рекорд! 1 место!"
        elif position == 2:
            return "Отлично! 2 место!"
        elif position == 3:
            return "Отлично! 3 место!"
        else:
            return f"Топ-10! {position} место!"

    def show(self):
        """Display the result window and wait for user interaction.

        Returns:
            str: 'new_game' if user wants to start new game,
                 'menu' if user clicked close button,
                 None if window closed
        """
        self.animation_start_time = pygame.time.get_ticks()

        # Initial draw (transparent window for fade-in)
        close_btn_rect, new_game_btn_rect = self._draw_window(
            rows_to_show=0, opacity=0, overlay_alpha=0
        )

        # Adjust button rects for screen coordinates
        close_btn_screen = pygame.Rect(
            self.window_x + close_btn_rect.x,
            self.window_y + close_btn_rect.y,
            close_btn_rect.width,
            close_btn_rect.height
        )
        new_game_btn_screen = pygame.Rect(
            self.window_x + self.new_game_btn_rel.x,
            self.window_y + self.new_game_btn_rel.y,
            self.new_game_btn_rel.width,
            self.new_game_btn_rel.height
        )

        waiting = True
        result = None

        while waiting:
            current_time = pygame.time.get_ticks()

            # Update animation
            window_opacity, overlay_alpha = self._update_animation(current_time)

            # Redraw with current animation state
            close_btn_rect, new_game_btn_rect = self._draw_window(
                rows_to_show=self.visible_rows,
                current_total=self.animated_total if self.visible_rows >= 3 else None,
                opacity=window_opacity,
                overlay_alpha=overlay_alpha
            )

            # Конфетти при попадании в топ-10
            if self.confetti is not None:
                # Запускаем конфетти когда анимация завершена
                if self.animation_complete and not self.confetti_started:
                    self.confetti.start()
                    self.confetti_started = True
                    if self.play_sound:
                        self.play_sound('celebration')

                # Обновляем и рисуем конфетти
                if self.confetti_started:
                    self.confetti.update()
                    self.confetti.draw(self.screen)
                    pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.animation_complete:
                    pos = event.pos
                    # Check close button
                    if close_btn_screen.collidepoint(pos):
                        self.close_pressed = True
                    # Check new game button
                    elif new_game_btn_screen.collidepoint(pos):
                        self.new_game_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP and self.animation_complete:
                    pos = event.pos
                    # Check close button release - return to menu
                    if self.close_pressed and close_btn_screen.collidepoint(pos):
                        waiting = False
                        result = 'menu'
                    # Check new game button release - start new game
                    elif self.new_game_pressed and new_game_btn_screen.collidepoint(pos):
                        waiting = False
                        result = 'new_game'
                    # Reset pressed states
                    self.close_pressed = False
                    self.new_game_pressed = False
                elif event.type == pygame.KEYDOWN and self.animation_complete:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        waiting = False
                        result = 'new_game'

            pygame.time.delay(16)  # ~60 FPS

        return result
