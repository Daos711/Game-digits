"""Start menu for the game."""
import sys
import math
import pygame

from game_digits import get_font_path
from game_digits import scale
from game_digits.constants import COLORS, TILE_BORDER_COLOR
from game_digits import ui_components as ui
from game_digits import records
from game_digits.windows.settings_window import SettingsWindow


class MenuTile:
    """A tile displaying a letter for the menu title."""

    def __init__(self, letter, color, target_x, target_y):
        self.letter = letter
        self.color = color
        self.target_x = target_x
        self.target_y = target_y
        self.x = -scale.TILE_SIZE - scale.scaled(50)  # Start off-screen left
        self.y = target_y
        self.velocity = 0

        # Animation offsets
        self.y_offset = 0  # For wave animation
        self.brightness = 0  # For hover effect (-1 to 1)

        # Create tile surface
        self.base_surface = pygame.Surface((scale.TILE_SIZE, scale.TILE_SIZE))
        self._draw_tile(self.base_surface, self.color)

    def _draw_tile(self, surface, color):
        """Draw the tile with letter."""
        surface.fill(color)

        # 3D bevel effect (не масштабируется для сохранения объёма)
        bevel = 3
        dark_factor = 0.4
        dark = tuple(max(0, min(255, int(c * dark_factor))) for c in color)

        w, h = surface.get_size()

        # Bottom shadow
        pygame.draw.rect(surface, dark, (0, h - bevel, w, bevel))
        # Right shadow
        pygame.draw.rect(surface, dark, (w - bevel, 0, bevel, h))

        # Border
        pygame.draw.rect(surface, TILE_BORDER_COLOR, surface.get_rect(), 1)

        # Letter
        font = pygame.font.Font(get_font_path("OpenSans-VariableFont_wdth,wght.ttf"), scale.TILE_FONT_SIZE)
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(w // 2, h // 2))
        surface.blit(text, text_rect)

    def get_surface(self):
        """Get tile surface with current brightness applied."""
        if self.brightness == 0:
            return self.base_surface

        # Create brightened surface
        surface = self.base_surface.copy()
        if self.brightness > 0:
            # Add white overlay for brightness
            overlay = pygame.Surface((scale.TILE_SIZE, scale.TILE_SIZE), pygame.SRCALPHA)
            alpha = int(self.brightness * 60)
            overlay.fill((255, 255, 255, alpha))
            surface.blit(overlay, (0, 0))
        return surface

    def draw(self, surface):
        """Draw tile at current position with offsets."""
        draw_y = int(self.y + self.y_offset)
        surface.blit(self.get_surface(), (int(self.x), draw_y))


class StartMenu:
    """Start menu with animated title tiles."""

    # Animation constants
    TILE_DELAY = 120  # ms between each tile animation start (slower)
    SPRING_STIFFNESS = 0.08  # Spring constant (slower)
    SPRING_DAMPING = 0.80  # Damping factor
    EXIT_SPEED = 15  # Pixels per frame when exiting
    EXIT_DELAY = 50  # ms between each tile exit
    BUTTON_FADE_DURATION = 300  # ms for button fade

    # Wave animation constants
    WAVE_INTERVAL = 4000  # ms between waves
    WAVE_DURATION = 600  # ms for full wave
    WAVE_HEIGHT = 12  # pixels to jump
    WAVE_TILE_DELAY = 80  # ms delay between each tile in wave

    # Records panel constants
    RECORDS_SLIDE_DURATION_OPEN = 400  # ms for opening
    RECORDS_SLIDE_DURATION_CLOSE = 200  # ms for closing (faster)

    def __init__(self, screen, screen_size, redraw_background, test_mode=False):
        self.screen = screen
        self.screen_width, self.screen_height = screen_size
        self.redraw_background = redraw_background
        self.test_mode = test_mode

        # Динамические размеры панели
        self.PANEL_WIDTH = scale.PANEL_WIDTH
        self.PANEL_X = self.screen_height  # Панель начинается после игрового поля
        self.PANEL_HEIGHT = self.screen_height

        # Load fonts
        bold_font_path = get_font_path("2204.ttf")
        self.button_font = pygame.font.Font(bold_font_path, scale.FONT_MENU_BUTTON)
        self.records_title_font = pygame.font.Font(bold_font_path, scale.FONT_MENU_RECORDS_TITLE)
        self.records_font = pygame.font.Font(bold_font_path, scale.FONT_MENU_RECORDS)
        self.records_small_font = pygame.font.Font(bold_font_path, scale.FONT_MENU_RECORDS_SMALL)

        # Title letters and colors (using game tile colors)
        letters = ['Ц', 'И', 'Ф', 'Р', 'Ы']
        tile_colors = [
            COLORS[1],  # Pink/red
            COLORS[2],  # Blue
            COLORS[3],  # Yellow
            COLORS[4],  # Green
            COLORS[8],  # Purple
        ]

        # Calculate tile positions (centered on game field)
        # Game field: starts at 2*FRAME_WIDTH, size = HEIGHT - 4*FRAME_WIDTH
        frame = scale.FRAME_WIDTH
        tile_area = self.screen_height - 4 * frame  # Actual playable area size
        field_center_x = 2 * frame + tile_area // 2
        field_center_y = 2 * frame + tile_area // 2 - scale.scaled(50)  # Slightly above center

        tile_gap = scale.scaled(8)
        total_width = len(letters) * scale.TILE_SIZE + (len(letters) - 1) * tile_gap
        start_x = field_center_x - total_width // 2

        # Create tiles
        self.tiles = []
        for i, (letter, color) in enumerate(zip(letters, tile_colors)):
            x = start_x + i * (scale.TILE_SIZE + tile_gap)
            y = field_center_y - scale.TILE_SIZE // 2
            self.tiles.append(MenuTile(letter, color, x, y))

        # Start game button setup - centered below the title tiles
        # Center button relative to the title tiles for perfect alignment
        title_center_x = start_x + total_width // 2
        self.button_rect = pygame.Rect(
            title_center_x - scale.BUTTON_WIDTH // 2,
            field_center_y + scale.TILE_SIZE // 2 + scale.scaled(40),
            scale.BUTTON_WIDTH,
            scale.BUTTON_HEIGHT
        )

        # Records button setup (on right panel)
        self.records_button_rect = pygame.Rect(
            self.PANEL_X + (self.PANEL_WIDTH - scale.RECORDS_BTN_WIDTH) // 2,
            scale.scaled(30),
            scale.RECORDS_BTN_WIDTH,
            scale.RECORDS_BTN_HEIGHT
        )

        # Settings button setup (on right panel, below records button)
        self.settings_button_rect = pygame.Rect(
            self.PANEL_X + (self.PANEL_WIDTH - scale.RECORDS_BTN_WIDTH) // 2,
            scale.scaled(30) + scale.RECORDS_BTN_HEIGHT + scale.scaled(15),
            scale.RECORDS_BTN_WIDTH,
            scale.RECORDS_BTN_HEIGHT
        )

        # State
        self.state = 'entering'  # 'entering', 'idle', 'exiting'
        self.animation_start_time = 0
        self.button_pressed = False
        self.records_button_pressed = False
        self.settings_button_pressed = False
        self.button_opacity = 0
        self.tiles_arrived = [False] * len(self.tiles)

        # Wave animation state
        self.last_wave_time = 0
        self.wave_active = False
        self.wave_start_time = 0

        # Hover state
        self.button_hovered = False
        self.records_button_hovered = False
        self.settings_button_hovered = False

        # Settings changed flag
        self.settings_changed = False

        # Records display state
        self.show_records = False
        self.records_slide_progress = 0  # 0 = hidden, 1 = fully visible
        self.records_slide_start_time = 0
        self.records_sliding = False
        self.records_slide_direction = 1  # 1 = showing, -1 = hiding
        self.cached_records = []

    def _spring_physics(self, tile, index):
        """Apply spring physics to move tile to target position."""
        # Calculate spring force
        displacement = tile.target_x - tile.x
        spring_force = displacement * self.SPRING_STIFFNESS

        # Apply force and damping
        tile.velocity += spring_force
        tile.velocity *= self.SPRING_DAMPING
        tile.x += tile.velocity

        # Check if arrived (close enough and slow enough)
        if abs(displacement) < 1 and abs(tile.velocity) < 0.5:
            tile.x = tile.target_x
            tile.velocity = 0
            return True
        return False

    def _update_wave_animation(self, current_time):
        """Update wave animation on title tiles."""
        if self.state != 'idle':
            return

        # Check if it's time to start a new wave
        if not self.wave_active:
            if current_time - self.last_wave_time >= self.WAVE_INTERVAL:
                self.wave_active = True
                self.wave_start_time = current_time
        else:
            # Update wave animation
            elapsed = current_time - self.wave_start_time
            total_wave_time = self.WAVE_DURATION + len(self.tiles) * self.WAVE_TILE_DELAY

            if elapsed >= total_wave_time:
                # Wave finished
                self.wave_active = False
                self.last_wave_time = current_time
                for tile in self.tiles:
                    tile.y_offset = 0
            else:
                # Animate each tile
                for i, tile in enumerate(self.tiles):
                    tile_start = i * self.WAVE_TILE_DELAY
                    tile_elapsed = elapsed - tile_start

                    if tile_elapsed < 0:
                        tile.y_offset = 0
                    elif tile_elapsed < self.WAVE_DURATION:
                        # Smooth up and down using sine
                        progress = tile_elapsed / self.WAVE_DURATION
                        tile.y_offset = -math.sin(progress * math.pi) * self.WAVE_HEIGHT
                    else:
                        tile.y_offset = 0

    def _update_hover_effect(self, mouse_pos):
        """Update tile brightness based on button hover."""
        if self.state != 'idle':
            return

        self.button_hovered = self.button_rect.collidepoint(mouse_pos)
        self.records_button_hovered = self.records_button_rect.collidepoint(mouse_pos)
        self.settings_button_hovered = self.settings_button_rect.collidepoint(mouse_pos)

        # Target brightness
        target = 0.5 if self.button_hovered else 0

        # Smooth transition
        for tile in self.tiles:
            if tile.brightness < target:
                tile.brightness = min(target, tile.brightness + 0.08)
            elif tile.brightness > target:
                tile.brightness = max(target, tile.brightness - 0.08)

    def _update_records_slide(self, current_time):
        """Update records panel slide animation."""
        if not self.records_sliding:
            return

        elapsed = current_time - self.records_slide_start_time
        duration = self.RECORDS_SLIDE_DURATION_OPEN if self.records_slide_direction == 1 else self.RECORDS_SLIDE_DURATION_CLOSE
        progress = min(1.0, elapsed / duration)

        if self.records_slide_direction == 1:
            # Opening: ease-out cubic (fast start, slow end)
            self.records_slide_progress = 1 - pow(1 - progress, 3)
        else:
            # Closing: linear, faster
            self.records_slide_progress = 1 - progress

        if progress >= 1.0:
            self.records_sliding = False
            if self.records_slide_direction == -1:
                self.show_records = False

    def _update_entering(self, current_time):
        """Update animation for entering state."""
        elapsed = current_time - self.animation_start_time

        all_arrived = True
        for i, tile in enumerate(self.tiles):
            # Stagger tile start times
            tile_start_time = i * self.TILE_DELAY
            if elapsed >= tile_start_time:
                arrived = self._spring_physics(tile, i)
                self.tiles_arrived[i] = arrived
                if not arrived:
                    all_arrived = False
            else:
                all_arrived = False

        # Update button opacity once tiles start arriving
        if any(self.tiles_arrived):
            button_start = len(self.tiles) * self.TILE_DELAY
            button_elapsed = max(0, elapsed - button_start)
            self.button_opacity = min(255, int(255 * button_elapsed / self.BUTTON_FADE_DURATION))

        if all_arrived and self.button_opacity >= 255:
            self.state = 'idle'
            self.last_wave_time = current_time  # Start wave timer

    def _update_exiting(self, current_time):
        """Update animation for exiting state."""
        elapsed = current_time - self.animation_start_time

        all_exited = True
        for i, tile in enumerate(self.tiles):
            # Stagger tile exit times
            tile_start_time = i * self.EXIT_DELAY
            if elapsed >= tile_start_time:
                tile.x += self.EXIT_SPEED
                if tile.x < self.screen_width + scale.TILE_SIZE:
                    all_exited = False
            else:
                all_exited = False

        # Fade out button
        button_elapsed = elapsed
        self.button_opacity = max(0, 255 - int(255 * button_elapsed / self.BUTTON_FADE_DURATION))

        return all_exited

    def _draw_panel_button(self, rect, text, is_pressed, is_hovered):
        """Draw a panel button (Records or Settings)."""
        if self.button_opacity <= 0:
            return

        # Button colors
        if is_pressed:
            bg_color = (40, 100, 140)
            border_color = (30, 80, 120)
        elif is_hovered:
            bg_color = (70, 140, 180)
            border_color = (50, 120, 160)
        else:
            bg_color = (50, 120, 160)
            border_color = (40, 100, 140)

        btn_surface = pygame.Surface(
            (rect.width, rect.height),
            pygame.SRCALPHA
        )

        # Draw button background
        pygame.draw.rect(btn_surface, bg_color,
                        (0, 0, rect.width, rect.height),
                        border_radius=scale.scaled(8))
        pygame.draw.rect(btn_surface, border_color,
                        (0, 0, rect.width, rect.height),
                        width=scale.BORDER_WIDTH, border_radius=scale.scaled(8))

        # Draw text (визуально по центру)
        text_surf = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(rect.width // 2, rect.height // 2 - 1))
        btn_surface.blit(text_surf, text_rect)

        btn_surface.set_alpha(self.button_opacity)
        self.screen.blit(btn_surface, rect.topleft)

    def _draw_records_button(self):
        """Draw the records button on the right panel."""
        self._draw_panel_button(
            self.records_button_rect, "Рекорды",
            self.records_button_pressed, self.records_button_hovered
        )

    def _draw_settings_button(self):
        """Draw the settings button on the right panel."""
        self._draw_panel_button(
            self.settings_button_rect, "Настройки",
            self.settings_button_pressed, self.settings_button_hovered
        )

    def _draw_records_panel(self):
        """Draw the records list on the right panel."""
        if self.records_slide_progress <= 0:
            return

        # Calculate slide offset (slides down from top)
        panel_height = scale.RECORDS_PANEL_HEIGHT
        offset_y = int((1 - self.records_slide_progress) * -panel_height)

        # Panel position
        panel_x = self.PANEL_X + scale.scaled(10)
        panel_y = scale.RECORDS_PANEL_TOP + offset_y
        panel_width = self.PANEL_WIDTH - scale.scaled(20)

        # Create panel surface
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(panel_surface, (30, 70, 100, 240),
                        (0, 0, panel_width, panel_height), border_radius=scale.CORNER_RADIUS)
        pygame.draw.rect(panel_surface, (50, 100, 140),
                        (0, 0, panel_width, panel_height), width=scale.BORDER_WIDTH, border_radius=scale.CORNER_RADIUS)

        # Column positions (center-aligned)
        col_positions = [scale.RECORDS_COL_1, scale.RECORDS_COL_2, scale.RECORDS_COL_3, scale.RECORDS_COL_4]

        # Column headers
        headers = ["#", "Очки", "Бонус", "Итого"]
        for text, center_x in zip(headers, col_positions):
            header = self.records_small_font.render(text, True, (180, 200, 220))
            header_rect = header.get_rect(center=(center_x, scale.RECORDS_HEADER_Y + scale.scaled(7)))
            panel_surface.blit(header, header_rect)

        # Divider line
        divider_y = scale.scaled(35)
        pygame.draw.line(panel_surface, (80, 120, 160), (scale.scaled(10), divider_y), (panel_width - scale.scaled(10), divider_y), 1)

        # Records
        if not self.cached_records:
            # No records message
            no_records = self.records_font.render("Нет записей", True, (150, 170, 190))
            no_records_rect = no_records.get_rect(center=(panel_width // 2, scale.scaled(100)))
            panel_surface.blit(no_records, no_records_rect)
        else:
            row_height = scale.RECORDS_ROW_HEIGHT
            for i, record in enumerate(self.cached_records[:10]):
                row_y = scale.RECORDS_START_Y + i * row_height

                # Alternate row background
                if i % 2 == 0:
                    pygame.draw.rect(panel_surface, (40, 80, 120, 100),
                                    (scale.scaled(5), row_y, panel_width - scale.scaled(10), row_height - scale.scaled(5)),
                                    border_radius=scale.scaled(5))

                # Position number
                pos_text = self.records_font.render(f"{i + 1}", True, (200, 180, 100))
                pos_rect = pos_text.get_rect(center=(col_positions[0], row_y + scale.scaled(12)))
                panel_surface.blit(pos_text, pos_rect)

                # Score
                score_text = self.records_font.render(str(record.get('score', 0)), True, (255, 255, 255))
                score_rect = score_text.get_rect(center=(col_positions[1], row_y + scale.scaled(12)))
                panel_surface.blit(score_text, score_rect)

                # Bonus
                bonus_text = self.records_font.render(str(record.get('bonus', 0)), True, (150, 220, 150))
                bonus_rect = bonus_text.get_rect(center=(col_positions[2], row_y + scale.scaled(12)))
                panel_surface.blit(bonus_text, bonus_rect)

                # Total
                total_text = self.records_font.render(str(record.get('total', 0)), True, (255, 220, 100))
                total_rect = total_text.get_rect(center=(col_positions[3], row_y + scale.scaled(12)))
                panel_surface.blit(total_text, total_rect)

                # Date (smaller, below, centered under score-bonus area)
                date_text = self.records_small_font.render(record.get('date', ''), True, (140, 160, 180))
                date_rect = date_text.get_rect(center=((col_positions[1] + col_positions[2]) // 2, row_y + scale.scaled(32)))
                panel_surface.blit(date_text, date_rect)

        # Draw panel
        self.screen.blit(panel_surface, (panel_x, max(scale.RECORDS_PANEL_TOP, panel_y)))

    def _draw(self):
        """Draw the menu."""
        # Draw background
        self.redraw_background()

        # Draw tiles
        for tile in self.tiles:
            tile.draw(self.screen)

        # Draw start game button with opacity
        if self.button_opacity > 0:
            # Create temporary surface for button with alpha
            btn_surface = pygame.Surface(
                (self.button_rect.width, self.button_rect.height),
                pygame.SRCALPHA
            )
            ui.draw_new_game_button(
                btn_surface,
                (0, 0, self.button_rect.width, self.button_rect.height),
                self.button_font,
                is_pressed=self.button_pressed,
                text="Начать игру"
            )
            btn_surface.set_alpha(self.button_opacity)
            self.screen.blit(btn_surface, self.button_rect.topleft)

        # Draw records button
        self._draw_records_button()

        # Draw settings button
        self._draw_settings_button()

        # Draw records panel if visible
        if self.show_records or self.records_sliding:
            self._draw_records_panel()

        pygame.display.update()

    def _open_settings(self):
        """Open settings window."""
        settings_window = SettingsWindow(
            self.screen,
            (self.screen_width, self.screen_height),
            self.redraw_background
        )
        result = settings_window.show()
        if result == 'apply':
            self.settings_changed = True

    def _toggle_records(self):
        """Toggle records panel visibility."""
        current_time = pygame.time.get_ticks()

        if self.records_sliding:
            # Mid-animation: reverse direction smoothly from current position
            current_slide = self.records_slide_progress
            self.records_slide_direction *= -1

            # Calculate equivalent progress for new direction
            if self.records_slide_direction == 1:
                # Now opening: find progress where eased = current_slide
                equiv_progress = 1 - pow(1 - current_slide, 1/3)
                duration = self.RECORDS_SLIDE_DURATION_OPEN
            else:
                # Now closing (linear): progress where (1-p) = current_slide
                equiv_progress = 1 - current_slide
                duration = self.RECORDS_SLIDE_DURATION_CLOSE

            elapsed = equiv_progress * duration
            self.records_slide_start_time = current_time - int(elapsed)
        else:
            self.records_sliding = True
            self.records_slide_start_time = current_time

            if self.show_records:
                # Hide records
                self.records_slide_direction = -1
            else:
                # Show records
                self.show_records = True
                self.records_slide_direction = 1
                self.cached_records = records.load_records(self.test_mode)

    def reset_for_entry(self):
        """Reset tiles for entry animation (coming from left)."""
        for tile in self.tiles:
            tile.x = -scale.TILE_SIZE - scale.scaled(50)
            tile.velocity = 0
            tile.y_offset = 0
            tile.brightness = 0
        self.tiles_arrived = [False] * len(self.tiles)
        self.button_opacity = 0
        self.state = 'entering'
        self.animation_start_time = pygame.time.get_ticks()
        self.wave_active = False
        self.button_hovered = False
        self.records_button_hovered = False
        self.show_records = False
        self.records_slide_progress = 0
        self.records_sliding = False

    def start_exit_animation(self):
        """Start the exit animation (tiles go right)."""
        self.state = 'exiting'
        self.animation_start_time = pygame.time.get_ticks()

    def show(self):
        """Display the menu and wait for user interaction.

        Returns:
            bool: True if user wants to start game, False to exit
        """
        self.reset_for_entry()

        running = True
        start_game = False

        while running:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            # Update animation
            if self.state == 'entering':
                self._update_entering(current_time)
            elif self.state == 'idle':
                self._update_wave_animation(current_time)
                self._update_hover_effect(mouse_pos)
                self._update_records_slide(current_time)
            elif self.state == 'exiting':
                if self._update_exiting(current_time):
                    running = False
                    start_game = True

            # Draw
            self._draw()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == 'idle':
                    if self.button_rect.collidepoint(event.pos):
                        self.button_pressed = True
                    elif self.records_button_rect.collidepoint(event.pos):
                        self.records_button_pressed = True
                    elif self.settings_button_rect.collidepoint(event.pos):
                        self.settings_button_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.button_pressed and self.button_rect.collidepoint(event.pos):
                        self.start_exit_animation()
                    elif self.records_button_pressed and self.records_button_rect.collidepoint(event.pos):
                        self._toggle_records()
                    elif self.settings_button_pressed and self.settings_button_rect.collidepoint(event.pos):
                        self._open_settings()
                        if self.settings_changed:
                            return 'settings_changed'
                    self.button_pressed = False
                    self.records_button_pressed = False
                    self.settings_button_pressed = False
                elif event.type == pygame.KEYDOWN and self.state == 'idle':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.start_exit_animation()
                    elif event.key == pygame.K_ESCAPE and self.show_records:
                        self._toggle_records()

            pygame.time.delay(16)  # ~60 FPS

        return start_game
