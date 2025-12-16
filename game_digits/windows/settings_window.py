"""Settings window for game configuration."""
import pygame

from game_digits import get_font_path
from game_digits import ui_components as ui
from game_digits import settings
from game_digits import scale


class SettingsWindow:
    """Modal window for game settings.

    Args:
        screen: Pygame screen surface
        screen_size: Tuple (width, height) of the screen
        redraw_callback: Function to call to redraw background
    """

    def __init__(self, screen, screen_size, redraw_callback):
        # Window dimensions - computed at runtime (сохраняем при создании, чтобы не менялись при смене пресета)
        self.WINDOW_WIDTH = scale.scaled(380)
        self.WINDOW_HEIGHT = scale.scaled(250)
        self.HEADER_HEIGHT = scale.scaled(50)
        self.PADDING = scale.scaled(25)
        self.ROW_HEIGHT = scale.scaled(50)
        self.ROW_GAP = scale.scaled(20)

        # Дополнительные масштабируемые значения (фиксируем при создании)
        self.close_btn_size = scale.scaled(32)
        self.close_btn_margin = scale.scaled(8)
        self.arrow_radius = scale.scaled(6)
        self.corner_radius = scale.CORNER_RADIUS
        self.cell_size = scale.scaled(18)
        self.value_gap = scale.scaled(15)
        self.value_border_radius = scale.scaled(8)

        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.redraw_callback = redraw_callback

        # Window position (centered)
        self.window_x = (self.screen_width - self.WINDOW_WIDTH) // 2
        self.window_y = (self.screen_height - self.WINDOW_HEIGHT) // 2

        # Load fonts
        bold_font_path = get_font_path("2204.ttf")
        self.title_font = pygame.font.Font(bold_font_path, scale.scaled(28))
        self.label_font = pygame.font.Font(bold_font_path, scale.scaled(22))
        self.value_font = pygame.font.Font(bold_font_path, scale.scaled(20))
        self.button_font = pygame.font.Font(bold_font_path, scale.scaled(24))

        # Button dimensions
        self.arrow_btn_size = scale.scaled(36)
        self.apply_btn_width = self.WINDOW_WIDTH - 2 * self.PADDING
        self.apply_btn_height = scale.scaled(45)

        # State
        self.close_pressed = False
        self.left_arrow_pressed = False
        self.right_arrow_pressed = False
        self.apply_pressed = False

        # Track if settings changed
        self.original_preset = settings.get_current_preset()
        self.settings_changed = False

    def _get_close_button_rect(self):
        """Get the close button rectangle."""
        return pygame.Rect(
            self.window_x + self.WINDOW_WIDTH - self.close_btn_size - self.close_btn_margin,
            self.window_y + (self.HEADER_HEIGHT - self.close_btn_size) // 2,
            self.close_btn_size,
            self.close_btn_size
        )

    def _get_left_arrow_rect(self):
        """Get left arrow button rectangle."""
        y = self.window_y + self.HEADER_HEIGHT + self.PADDING + self.ROW_HEIGHT
        return pygame.Rect(
            self.window_x + self.PADDING,
            y + (self.ROW_HEIGHT - self.arrow_btn_size) // 2,
            self.arrow_btn_size,
            self.arrow_btn_size
        )

    def _get_right_arrow_rect(self):
        """Get right arrow button rectangle."""
        y = self.window_y + self.HEADER_HEIGHT + self.PADDING + self.ROW_HEIGHT
        return pygame.Rect(
            self.window_x + self.WINDOW_WIDTH - self.PADDING - self.arrow_btn_size,
            y + (self.ROW_HEIGHT - self.arrow_btn_size) // 2,
            self.arrow_btn_size,
            self.arrow_btn_size
        )

    def _get_apply_button_rect(self):
        """Get apply button rectangle."""
        return pygame.Rect(
            self.window_x + self.PADDING,
            self.window_y + self.WINDOW_HEIGHT - self.PADDING - self.apply_btn_height,
            self.apply_btn_width,
            self.apply_btn_height
        )

    def _draw_arrow_button(self, surface, rect, direction, is_pressed=False):
        """Draw an arrow button (< or >)."""
        x, y, w, h = rect
        radius = self.arrow_radius

        if is_pressed:
            color_top = (200, 135, 0)
            color_bottom = (150, 100, 0)
        else:
            color_top = (243, 165, 0)
            color_bottom = (186, 127, 0)

        ui.draw_gradient_rounded_rect(surface, rect, color_top, color_bottom, radius)

        # Draw arrow
        arrow_color = (255, 255, 255)
        center_x = x + w // 2
        center_y = y + h // 2
        arrow_size = w // 3

        if direction == 'left':
            points = [
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y),
                (center_x + arrow_size // 2, center_y + arrow_size),
            ]
        else:  # right
            points = [
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y),
                (center_x - arrow_size // 2, center_y + arrow_size),
            ]

        pygame.draw.polygon(surface, arrow_color, points)

    def _draw_window(self):
        """Draw the settings window."""
        # Create window surface
        window_surface = pygame.Surface(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.SRCALPHA
        )

        # Draw content area (checkered background)
        ui.draw_checkered_content_area(
            window_surface,
            (0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            self.HEADER_HEIGHT,
            corner_radius=self.corner_radius,
            cell_size=self.cell_size,
            border_color=(100, 150, 130),
            border_width=2
        )

        # Draw header
        close_rect_rel = ui.draw_result_window_header(
            window_surface,
            (0, 0, self.WINDOW_WIDTH, self.HEADER_HEIGHT),
            "Настройки",
            self.title_font,
            close_pressed=self.close_pressed
        )

        # === Resolution setting ===
        current_y = self.HEADER_HEIGHT + self.PADDING

        # Label "Размер:" (по центру)
        label_text = "Размер:"
        label_surf = self.label_font.render(label_text, True, (40, 92, 120))
        label_x = (self.WINDOW_WIDTH - label_surf.get_width()) // 2
        window_surface.blit(label_surf, (label_x, current_y))

        current_y += self.ROW_HEIGHT

        # Value display area (between arrows)
        value_area_x = self.PADDING + self.arrow_btn_size + self.value_gap
        value_area_width = self.WINDOW_WIDTH - 2 * self.PADDING - 2 * self.arrow_btn_size - 2 * self.value_gap

        # Draw value background
        value_rect = (value_area_x, current_y, value_area_width, self.ROW_HEIGHT)
        pygame.draw.rect(window_surface, (230, 240, 250), value_rect, border_radius=self.value_border_radius)
        pygame.draw.rect(window_surface, (150, 180, 200), value_rect, width=2, border_radius=self.value_border_radius)

        # Draw current preset name
        preset_name = settings.get_preset_name()
        value_surf = self.value_font.render(preset_name, True, (40, 80, 120))
        value_x = value_area_x + (value_area_width - value_surf.get_width()) // 2
        value_y = current_y + (self.ROW_HEIGHT - value_surf.get_height()) // 2
        window_surface.blit(value_surf, (value_x, value_y))

        # Draw arrow buttons
        left_rect = (self.PADDING, current_y + (self.ROW_HEIGHT - self.arrow_btn_size) // 2,
                    self.arrow_btn_size, self.arrow_btn_size)
        right_rect = (self.WINDOW_WIDTH - self.PADDING - self.arrow_btn_size,
                     current_y + (self.ROW_HEIGHT - self.arrow_btn_size) // 2,
                     self.arrow_btn_size, self.arrow_btn_size)

        self._draw_arrow_button(window_surface, left_rect, 'left', self.left_arrow_pressed)
        self._draw_arrow_button(window_surface, right_rect, 'right', self.right_arrow_pressed)

        # Draw apply button
        apply_rect = (self.PADDING,
                     self.WINDOW_HEIGHT - self.PADDING - self.apply_btn_height,
                     self.apply_btn_width, self.apply_btn_height)
        ui.draw_new_game_button(window_surface, apply_rect, self.button_font,
                               is_pressed=self.apply_pressed, text="Применить")

        # Blit window to screen
        self.screen.blit(window_surface, (self.window_x, self.window_y))

    def show(self):
        """Show the settings window and handle events.

        Returns:
            'apply' if settings changed and should restart
            'close' if closed without changes
            None if window was closed by X
        """
        clock = pygame.time.Clock()
        running = True

        while running:
            # Redraw background
            self.redraw_callback()

            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            # Draw window
            self._draw_window()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()

                    # Check close button
                    if self._get_close_button_rect().collidepoint(pos):
                        self.close_pressed = True

                    # Check left arrow
                    elif self._get_left_arrow_rect().collidepoint(pos):
                        self.left_arrow_pressed = True
                        settings.prev_preset()
                        self.settings_changed = (settings.get_current_preset() != self.original_preset)

                    # Check right arrow
                    elif self._get_right_arrow_rect().collidepoint(pos):
                        self.right_arrow_pressed = True
                        settings.next_preset()
                        self.settings_changed = (settings.get_current_preset() != self.original_preset)

                    # Check apply button
                    elif self._get_apply_button_rect().collidepoint(pos):
                        self.apply_pressed = True

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    pos = pygame.mouse.get_pos()

                    # Check close button release
                    if self.close_pressed and self._get_close_button_rect().collidepoint(pos):
                        # Restore original preset if changed but not applied
                        if self.settings_changed:
                            settings.set_preset(self.original_preset)
                        return 'close'

                    # Check apply button release
                    if self.apply_pressed and self._get_apply_button_rect().collidepoint(pos):
                        if self.settings_changed:
                            return 'apply'
                        else:
                            return 'close'

                    # Reset button states
                    self.close_pressed = False
                    self.left_arrow_pressed = False
                    self.right_arrow_pressed = False
                    self.apply_pressed = False

            clock.tick(60)

        return 'close'
