"""Start menu for the game."""
import sys
import math
import pygame

from game_digits import get_font_path
from game_digits import scale
from game_digits.constants import COLORS, TILE_BORDER_COLOR
from game_digits import ui_components as ui
from game_digits import records
from game_digits import ranks
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

        # 3D bevel effect (пропорционально размеру плитки, ~4.7%)
        bevel = max(2, round(scale.TILE_SIZE * 3 / 64))
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

        # Draw text (визуально по центру - смещение пропорционально высоте)
        text_surf = self.button_font.render(text, True, (255, 255, 255))
        text_y_adjust = rect.height // 20
        text_rect = text_surf.get_rect(center=(rect.width // 2, rect.height // 2 - text_y_adjust))
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

    def _draw_trophy(self, surface, center_x, center_y, size, color):
        """Draw a trophy icon programmatically."""
        # Trophy dimensions
        cup_w = size
        cup_h = int(size * 0.6)
        stem_w = int(size * 0.25)
        stem_h = int(size * 0.25)
        base_w = int(size * 0.5)
        base_h = int(size * 0.15)

        # Cup (trapezoid shape - wider at top)
        cup_top = center_y - cup_h // 2 - stem_h // 2
        cup_points = [
            (center_x - cup_w // 2, cup_top),  # top-left
            (center_x + cup_w // 2, cup_top),  # top-right
            (center_x + cup_w // 3, cup_top + cup_h),  # bottom-right
            (center_x - cup_w // 3, cup_top + cup_h),  # bottom-left
        ]
        pygame.draw.polygon(surface, color, cup_points)

        # Stem
        stem_top = cup_top + cup_h
        stem_rect = pygame.Rect(center_x - stem_w // 2, stem_top, stem_w, stem_h)
        pygame.draw.rect(surface, color, stem_rect)

        # Base
        base_top = stem_top + stem_h
        base_rect = pygame.Rect(center_x - base_w // 2, base_top, base_w, base_h)
        pygame.draw.rect(surface, color, base_rect, border_radius=2)

        # Handles (small arcs on sides)
        handle_r = int(size * 0.15)
        pygame.draw.circle(surface, color, (center_x - cup_w // 2 - handle_r // 2, cup_top + cup_h // 2), handle_r, 2)
        pygame.draw.circle(surface, color, (center_x + cup_w // 2 + handle_r // 2, cup_top + cup_h // 2), handle_r, 2)

    def _draw_medal(self, surface, center_x, center_y, size, color, number):
        """Draw a medal icon programmatically."""
        # Medal circle
        radius = size // 2
        pygame.draw.circle(surface, color, (center_x, center_y), radius)

        # Darker edge for depth
        darker = tuple(max(0, int(c * 0.7)) for c in color)
        pygame.draw.circle(surface, darker, (center_x, center_y), radius, 2)

        # Inner highlight (lighter)
        lighter = tuple(min(255, int(c * 1.2)) for c in color)
        pygame.draw.circle(surface, lighter, (center_x - radius // 4, center_y - radius // 4), radius // 4)

        # Ribbon (two small triangles above)
        ribbon_w = size // 3
        ribbon_h = size // 2
        ribbon_top = center_y - radius - ribbon_h
        # Left ribbon
        pygame.draw.polygon(surface, (200, 60, 60), [
            (center_x - ribbon_w, ribbon_top),
            (center_x - 2, center_y - radius + 2),
            (center_x - ribbon_w - 3, center_y - radius + 2),
        ])
        # Right ribbon
        pygame.draw.polygon(surface, (180, 50, 50), [
            (center_x + ribbon_w, ribbon_top),
            (center_x + 2, center_y - radius + 2),
            (center_x + ribbon_w + 3, center_y - radius + 2),
        ])

        # Number in center
        font = pygame.font.Font(get_font_path("2204.ttf"), size // 2)
        num_text = font.render(str(number), True, (255, 255, 255))
        num_rect = num_text.get_rect(center=(center_x, center_y + 1))
        surface.blit(num_text, num_rect)

    def _draw_records_panel(self):
        """Draw the full records table over the game field."""
        if self.records_slide_progress <= 0:
            return

        # Game field dimensions - draw directly on the field
        frame = scale.FRAME_WIDTH
        field_x = 2 * frame
        field_y = 2 * frame
        field_size = self.screen_height - 4 * frame

        # Panel covers the entire game field
        panel_width = field_size
        panel_height = field_size

        # Create panel surface with alpha support for soft shadows
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        # Warm white background (base)
        bg_color = (255, 253, 247)
        panel_surface.fill(bg_color)

        # Draw subtle grid lines (like notebook) - only on outer area
        grid_color = (245, 242, 234)
        cell_size = scale.scaled(25)
        for x in range(0, panel_width, cell_size):
            pygame.draw.line(panel_surface, grid_color, (x, 0), (x, panel_height), 1)
        for y in range(0, panel_height, cell_size):
            pygame.draw.line(panel_surface, grid_color, (0, y), (panel_width, y), 1)

        # Title
        title_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(32))
        title = title_font.render("Таблица рекордов", True, (80, 70, 60))
        title_rect = title.get_rect(center=(panel_width // 2, scale.scaled(35)))
        panel_surface.blit(title, title_rect)

        # Decorative line under title
        line_y = scale.scaled(60)
        pygame.draw.line(panel_surface, (220, 200, 140),
                        (scale.scaled(40), line_y),
                        (panel_width - scale.scaled(40), line_y), 2)

        # Table area dimensions (for solid card background)
        padding = scale.scaled(12)
        table_top = scale.scaled(70)
        table_height = panel_height - table_top - scale.scaled(10)
        content_width = panel_width - 2 * padding

        # Draw soft shadow for table card (multiple layers)
        shadow_offset = scale.scaled(2)
        for i, alpha in enumerate([15, 25, 20]):
            shadow_rect = pygame.Rect(padding + shadow_offset, table_top + shadow_offset + i,
                                     content_width, table_height)
            pygame.draw.rect(panel_surface, (0, 0, 0, alpha), shadow_rect, border_radius=scale.scaled(6))

        # Draw solid white "card" background (no hard border)
        table_card_rect = pygame.Rect(padding, table_top, content_width, table_height)
        pygame.draw.rect(panel_surface, (255, 253, 247, 255), table_card_rect, border_radius=scale.scaled(6))

        # Column positions (x positions for center/alignment of each column)
        col_x = [
            padding + scale.scaled(35),                    # #
            padding + scale.scaled(115),                   # Дата
            padding + scale.scaled(210),                   # Очки
            padding + scale.scaled(295),                   # Бонус
            padding + scale.scaled(385),                   # Итого
            padding + content_width - scale.scaled(95),    # Ранг (badge center)
        ]
        rank_col_max_width = scale.scaled(180)  # Max width for rank badges

        # Header
        header_y = table_top + scale.scaled(18)
        headers = ["#", "Дата", "Очки", "Бонус", "Итого", "Ранг"]
        header_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(16))
        header_color = (120, 110, 100)
        for text, cx in zip(headers, col_x):
            header = header_font.render(text, True, header_color)
            header_rect = header.get_rect(center=(cx, header_y))
            panel_surface.blit(header, header_rect)

        # Header divider
        header_div_y = table_top + scale.scaled(35)
        pygame.draw.line(panel_surface, (200, 190, 170),
                        (padding + scale.scaled(5), header_div_y),
                        (panel_width - padding - scale.scaled(5), header_div_y), 1)

        # Fonts for content
        data_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(20))
        bold_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(21))
        date_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(16))

        # Row highlight colors for top-3
        row_highlights = [
            (255, 244, 214, 255),  # Gold - 1st place
            (242, 245, 248, 255),  # Silver - 2nd place
            (248, 239, 230, 255),  # Bronze - 3rd place
        ]

        if not self.cached_records:
            no_records = data_font.render("Нет записей", True, (150, 140, 130))
            no_records_rect = no_records.get_rect(center=(panel_width // 2, panel_height // 2))
            panel_surface.blit(no_records, no_records_rect)
        else:
            row_height = scale.scaled(45)
            start_y = table_top + scale.scaled(42)
            stripe_width = scale.scaled(5)

            for i, record in enumerate(self.cached_records[:10]):
                row_y = start_y + i * row_height
                row_center_y = row_y + row_height // 2

                # Get rank info
                total = record.get('total', 0)
                rank_name, rank_fg, rank_bg = ranks.get_rank(total)

                # Row highlight for top-3
                if i < 3:
                    highlight_rect = pygame.Rect(padding + scale.scaled(3), row_y,
                                                content_width - scale.scaled(6), row_height - scale.scaled(2))
                    pygame.draw.rect(panel_surface, row_highlights[i], highlight_rect, border_radius=scale.scaled(4))

                # Left vertical stripe (rank color)
                stripe_rect = pygame.Rect(padding + scale.scaled(3), row_y + scale.scaled(5),
                                         stripe_width, row_height - scale.scaled(12))
                pygame.draw.rect(panel_surface, rank_fg, stripe_rect, border_radius=2)

                # Position number with programmatic icons for top-3
                medal_size = scale.scaled(20)
                icon_x = col_x[0] - scale.scaled(12)
                num_x = col_x[0] + scale.scaled(10)
                pos_font = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(16))

                if i == 0:
                    # Draw trophy + "1" for 1st place
                    self._draw_trophy(panel_surface, icon_x, row_center_y, medal_size, (200, 150, 30))
                    pos_text = pos_font.render("1", True, (200, 150, 30))
                    pos_rect = pos_text.get_rect(center=(num_x, row_center_y))
                    panel_surface.blit(pos_text, pos_rect)
                elif i == 1:
                    # Draw silver medal + "2"
                    self._draw_medal(panel_surface, icon_x, row_center_y, medal_size, (160, 165, 175), 2)
                    pos_text = pos_font.render("2", True, (140, 140, 150))
                    pos_rect = pos_text.get_rect(center=(num_x, row_center_y))
                    panel_surface.blit(pos_text, pos_rect)
                elif i == 2:
                    # Draw bronze medal + "3"
                    self._draw_medal(panel_surface, icon_x, row_center_y, medal_size, (185, 135, 85), 3)
                    pos_text = pos_font.render("3", True, (170, 120, 70))
                    pos_rect = pos_text.get_rect(center=(num_x, row_center_y))
                    panel_surface.blit(pos_text, pos_rect)
                else:
                    # Regular position number (centered)
                    pos_font_reg = pygame.font.Font(get_font_path("2204.ttf"), scale.scaled(18))
                    pos_text = pos_font_reg.render(str(i + 1), True, (100, 100, 100))
                    pos_rect = pos_text.get_rect(center=(col_x[0], row_center_y))
                    panel_surface.blit(pos_text, pos_rect)

                # Date (left-aligned)
                date_text = date_font.render(record.get('date', ''), True, (130, 120, 110))
                date_rect = date_text.get_rect(midleft=(col_x[1] - scale.scaled(35), row_center_y))
                panel_surface.blit(date_text, date_rect)

                # Score (right-aligned)
                score_text = data_font.render(str(record.get('score', 0)), True, (70, 70, 70))
                score_rect = score_text.get_rect(midright=(col_x[2] + scale.scaled(28), row_center_y))
                panel_surface.blit(score_text, score_rect)

                # Bonus (right-aligned, green)
                bonus_text = data_font.render(str(record.get('bonus', 0)), True, (50, 140, 50))
                bonus_rect = bonus_text.get_rect(midright=(col_x[3] + scale.scaled(28), row_center_y))
                panel_surface.blit(bonus_text, bonus_rect)

                # Total (right-aligned, bold, golden)
                total_text = bold_font.render(str(total), True, (180, 130, 30))
                total_rect = total_text.get_rect(midright=(col_x[4] + scale.scaled(28), row_center_y))
                panel_surface.blit(total_text, total_rect)

                # Rank badge (auto-sized, centered at col_x[5]) with animation
                badge_height = scale.scaled(30)
                current_time = pygame.time.get_ticks()
                ranks.draw_rank_badge(panel_surface,
                                     (col_x[5], row_center_y, rank_col_max_width, badge_height),
                                     rank_name, rank_fg, rank_bg, time_ms=current_time)

                # Row divider (not after last row)
                if i < min(len(self.cached_records), 10) - 1:
                    div_y = row_y + row_height - scale.scaled(1)
                    pygame.draw.line(panel_surface, (232, 225, 210),
                                    (padding + stripe_width + scale.scaled(10), div_y),
                                    (panel_width - padding - scale.scaled(5), div_y), 1)

        # Apply fade animation
        if self.records_slide_progress < 1:
            alpha = int(255 * self.records_slide_progress)
            panel_surface.set_alpha(alpha)

        # Draw panel on game field
        self.screen.blit(panel_surface, (field_x, field_y))


    def _draw(self):
        """Draw the menu."""
        # Draw background
        self.redraw_background()

        # Draw tiles and button only when records panel is not fully visible
        records_fully_visible = self.show_records and self.records_slide_progress >= 1.0

        if not records_fully_visible:
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
                    # Block start button when records are shown, but allow settings
                    if self.button_rect.collidepoint(event.pos) and not self.show_records:
                        self.button_pressed = True
                    elif self.records_button_rect.collidepoint(event.pos):
                        self.records_button_pressed = True
                    elif self.settings_button_rect.collidepoint(event.pos):
                        self.settings_button_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.button_pressed and self.button_rect.collidepoint(event.pos) and not self.show_records:
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
                        if not self.show_records:
                            self.start_exit_animation()
                    elif event.key == pygame.K_ESCAPE and self.show_records:
                        self._toggle_records()

            pygame.time.delay(16)  # ~60 FPS

        return start_game
