"""
Animated pause overlay with multiple animation patterns.
"""

import math
import random
import pygame
from game_digits import get_font_path
from game_digits.scale import (
    FONT_PAUSE_TEXT, FONT_PAUSE_TITLE, scaled,
    BUTTON_WIDTH, BUTTON_HEIGHT, FONT_MENU_BUTTON, CORNER_RADIUS
)


class PauseTile:
    """A single animated tile for the pause screen."""

    def __init__(self, letter: str, color: tuple, x: float, y: float, tile_size: int = None):
        self.letter = letter
        self.color = color
        self.tile_size = tile_size if tile_size is not None else scaled(52)
        self.x = x
        self.y = y

        # For bounce pattern
        self.vx = 0
        self.vy = 0

        # Font for the letter
        self.font = pygame.font.Font(get_font_path("2204.ttf"), FONT_PAUSE_TEXT)

        # Pre-render the tile surface
        self._render_tile()

    def _render_tile(self):
        """Pre-render the tile with letter."""
        self.surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)

        radius = 8
        rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)

        pygame.draw.rect(self.surface, self.color, rect, border_radius=radius)

        highlight = pygame.Surface((self.tile_size, self.tile_size // 2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.surface.blit(highlight, (0, 0))

        border_color = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(self.surface, border_color, rect, width=2, border_radius=radius)

        text = self.font.render(self.letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
        self.surface.blit(text, text_rect)

    def draw(self, surface: pygame.Surface):
        """Draw the tile at current position."""
        pos = (int(self.x - self.tile_size // 2), int(self.y - self.tile_size // 2))
        surface.blit(self.surface, pos)


class WavePattern:
    """Tiles in a row with wave pulsing effect."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60

    def update(self, time_ms):
        t = time_ms / 1000.0
        total_width = (len(self.tiles) - 1) * self.base_spacing
        start_x = self.center_x - total_width / 2

        for i, tile in enumerate(self.tiles):
            tile.x = start_x + i * self.base_spacing
            # Wave motion - each tile has phase offset
            wave_offset = math.sin(t * 2 + i * 0.8) * 25
            tile.y = self.center_y + wave_offset


class BouncePattern:
    """DVD screensaver style - tiles bounce off edges (slowed down)."""

    def __init__(self, tiles, width, height):
        self.tiles = tiles
        self.width = width
        self.height = height
        self.margin = 30

        # Initialize positions and velocities - SLOWER speed
        for i, tile in enumerate(tiles):
            tile.x = width // 2 + (i - 2) * 60
            tile.y = height // 2
            angle = random.uniform(0, 2 * math.pi)
            speed = 0.8 + random.uniform(0, 0.4)  # Reduced from 2-3 to 0.8-1.2
            tile.vx = math.cos(angle) * speed
            tile.vy = math.sin(angle) * speed

    def update(self, time_ms):
        for tile in self.tiles:
            tile.x += tile.vx
            tile.y += tile.vy

            half = tile.tile_size // 2
            if tile.x - half < self.margin or tile.x + half > self.width - self.margin:
                tile.vx = -tile.vx
                tile.x = max(self.margin + half, min(self.width - self.margin - half, tile.x))
            if tile.y - half < self.margin or tile.y + half > self.height - self.margin:
                tile.vy = -tile.vy
                tile.y = max(self.margin + half, min(self.height - self.margin - half, tile.y))


class SnakePattern:
    """Tiles follow each other in a snake pattern (slowed down)."""

    def __init__(self, tiles, center_x, center_y, width, height):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height

        # Path history for snake following
        self.path = []
        self.head_x = center_x
        self.head_y = center_y
        self.angle = 0
        self.path_spacing = 30

    def update(self, time_ms):
        t = time_ms / 1000.0

        # Move head in a smooth wandering pattern - SLOWER
        self.angle += math.sin(t * 0.5) * 0.03 + math.cos(t * 0.7) * 0.02
        speed = 1.2  # Reduced from 3 to 1.2
        self.head_x += math.cos(self.angle) * speed
        self.head_y += math.sin(self.angle) * speed

        # Bounce off walls
        margin = 80
        if self.head_x < margin:
            self.head_x = margin
            self.angle = math.pi - self.angle
        if self.head_x > self.width - margin:
            self.head_x = self.width - margin
            self.angle = math.pi - self.angle
        if self.head_y < margin:
            self.head_y = margin
            self.angle = -self.angle
        if self.head_y > self.height - margin:
            self.head_y = self.height - margin
            self.angle = -self.angle

        # Add to path
        self.path.append((self.head_x, self.head_y))

        # Keep path limited
        max_path = len(self.tiles) * self.path_spacing + 100
        if len(self.path) > max_path:
            self.path = self.path[-max_path:]

        # Position tiles along path
        for i, tile in enumerate(self.tiles):
            path_index = len(self.path) - 1 - i * self.path_spacing
            if path_index >= 0 and path_index < len(self.path):
                tile.x, tile.y = self.path[path_index]
            else:
                tile.x, tile.y = self.center_x, self.center_y


class FloatPattern:
    """Tiles float gently like bubbles."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60

        # Random parameters for each tile
        for i, tile in enumerate(tiles):
            tile.float_speed = 0.8 + random.uniform(0, 0.4)
            tile.float_phase = random.uniform(0, 2 * math.pi)
            tile.float_amplitude = 15 + random.uniform(0, 10)
            tile.drift_speed = 0.3 + random.uniform(0, 0.2)
            tile.drift_phase = random.uniform(0, 2 * math.pi)

    def update(self, time_ms):
        t = time_ms / 1000.0
        total_width = (len(self.tiles) - 1) * self.base_spacing
        start_x = self.center_x - total_width / 2

        for i, tile in enumerate(self.tiles):
            # Base position in row
            base_x = start_x + i * self.base_spacing
            # Gentle vertical float
            float_y = math.sin(t * tile.float_speed + tile.float_phase) * tile.float_amplitude
            # Slight horizontal drift
            drift_x = math.sin(t * tile.drift_speed + tile.drift_phase) * 8

            tile.x = base_x + drift_x
            tile.y = self.center_y + float_y


class SwingPattern:
    """Tiles swing like pendulums from the top."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60
        self.rope_length = 80

        # Different swing parameters for each tile
        for i, tile in enumerate(tiles):
            tile.swing_speed = 1.5 + i * 0.15
            tile.swing_phase = i * 0.4
            tile.swing_amplitude = 0.4 + i * 0.05

    def update(self, time_ms):
        t = time_ms / 1000.0
        total_width = (len(self.tiles) - 1) * self.base_spacing
        start_x = self.center_x - total_width / 2

        anchor_y = self.center_y - self.rope_length

        for i, tile in enumerate(self.tiles):
            anchor_x = start_x + i * self.base_spacing
            # Pendulum swing angle
            angle = math.sin(t * tile.swing_speed + tile.swing_phase) * tile.swing_amplitude

            tile.x = anchor_x + math.sin(angle) * self.rope_length
            tile.y = anchor_y + math.cos(angle) * self.rope_length


class BreathePattern:
    """Tiles breathe in and out together, expanding and contracting."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60

    def update(self, time_ms):
        t = time_ms / 1000.0

        # Breathing scale factor
        breath = 1 + math.sin(t * 1.2) * 0.3

        total_width = (len(self.tiles) - 1) * self.base_spacing * breath
        start_x = self.center_x - total_width / 2

        for i, tile in enumerate(self.tiles):
            tile.x = start_x + i * self.base_spacing * breath
            # Slight vertical bob
            tile.y = self.center_y + math.sin(t * 0.8 + i * 0.3) * 8


class CarouselPattern:
    """Tiles rotate like a 3D carousel with depth effect."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.radius = 100

    def update(self, time_ms):
        t = time_ms / 1000.0

        for i, tile in enumerate(self.tiles):
            # Base angle for this tile
            base_angle = (i / len(self.tiles)) * 2 * math.pi

            # Slow rotation
            angle = base_angle + t * 0.5

            # 3D carousel effect
            tile.x = self.center_x + math.sin(angle) * self.radius
            # Compress Y for perspective, offset for depth
            z = math.cos(angle)
            tile.y = self.center_y + z * 30


class TypewriterPattern:
    """Tiles appear one by one like typing, then reset."""

    def __init__(self, tiles, center_x, center_y):
        self.tiles = tiles
        self.center_x = center_x
        self.center_y = center_y
        self.base_spacing = 60
        self.char_delay = 400  # ms per character
        self.pause_time = 2000  # ms to pause when complete
        self.cycle_time = len(tiles) * self.char_delay + self.pause_time

    def update(self, time_ms):
        cycle_pos = time_ms % self.cycle_time

        total_width = (len(self.tiles) - 1) * self.base_spacing
        start_x = self.center_x - total_width / 2

        for i, tile in enumerate(self.tiles):
            appear_time = i * self.char_delay

            if cycle_pos < appear_time:
                # Not yet appeared - hide off screen
                tile.x = -100
                tile.y = -100
            else:
                # Appeared - in position with slight bounce
                time_since_appear = cycle_pos - appear_time
                bounce = 0
                if time_since_appear < 200:
                    # Quick bounce on appear
                    progress = time_since_appear / 200
                    bounce = math.sin(progress * math.pi) * 15

                tile.x = start_x + i * self.base_spacing
                tile.y = self.center_y - bounce


class PauseOverlay:
    """Animated overlay shown when game is paused.

    Randomly selects from multiple animation patterns.
    """

    COLORS = [
        (231, 125, 128),  # П - red/pink
        (111, 183, 214),  # А - blue
        (136, 189, 134),  # У - green
        (178, 161, 199),  # З - purple
        (245, 203, 105),  # А - yellow
    ]

    PATTERN_NAMES = ['wave', 'float', 'swing', 'breathe', 'carousel', 'typewriter', 'bounce', 'snake']

    def __init__(self, field_width: int, field_height: int):
        self.field_width = field_width
        self.field_height = field_height

        self.tiles = []
        self.pattern = None
        self.pattern_index = 0
        self.start_time = 0

        self.title_font = pygame.font.Font(get_font_path("2204.ttf"), FONT_PAUSE_TITLE)
        self.button_font = pygame.font.Font(get_font_path("2204.ttf"), FONT_MENU_BUTTON)

        # Кнопка "В меню"
        btn_width = scaled(160)
        btn_height = scaled(45)
        self.menu_button_rect = pygame.Rect(
            (field_width - btn_width) // 2,
            field_height - scaled(100),
            btn_width,
            btn_height
        )
        self.menu_button_hovered = False
        self.menu_button_pressed = False
        # Смещение для преобразования в экранные координаты
        self.offset_x = 0
        self.offset_y = 0

        self._create_tiles()

    def _create_tiles(self):
        """Create tile objects for ПАУЗА."""
        letters = "ПАУЗА"
        center_x = self.field_width // 2
        center_y = self.field_height // 2

        self.tiles = []
        for i, letter in enumerate(letters):
            tile = PauseTile(
                letter=letter,
                color=self.COLORS[i],
                x=center_x,
                y=center_y
            )
            self.tiles.append(tile)

    def _select_pattern(self, pattern_name=None):
        """Select an animation pattern by name or use current index."""
        if pattern_name is None:
            pattern_name = self.PATTERN_NAMES[self.pattern_index]

        center_x = self.field_width // 2
        center_y = self.field_height // 2

        self._create_tiles()  # Reset tiles for new pattern

        if pattern_name == 'wave':
            self.pattern = WavePattern(self.tiles, center_x, center_y)
        elif pattern_name == 'bounce':
            self.pattern = BouncePattern(self.tiles, self.field_width, self.field_height)
        elif pattern_name == 'snake':
            self.pattern = SnakePattern(self.tiles, center_x, center_y,
                                        self.field_width, self.field_height)
        elif pattern_name == 'float':
            self.pattern = FloatPattern(self.tiles, center_x, center_y)
        elif pattern_name == 'swing':
            self.pattern = SwingPattern(self.tiles, center_x, center_y)
        elif pattern_name == 'breathe':
            self.pattern = BreathePattern(self.tiles, center_x, center_y)
        elif pattern_name == 'carousel':
            self.pattern = CarouselPattern(self.tiles, center_x, center_y)
        elif pattern_name == 'typewriter':
            self.pattern = TypewriterPattern(self.tiles, center_x, center_y)

    def start(self):
        """Start the animation with a random pattern."""
        self.start_time = pygame.time.get_ticks()
        self.pattern_index = random.randint(0, len(self.PATTERN_NAMES) - 1)
        self._select_pattern()

    def update(self):
        """Update tile positions based on current pattern."""
        if self.pattern:
            current_time = pygame.time.get_ticks() - self.start_time
            self.pattern.update(current_time)

    def _draw_menu_button(self, surface: pygame.Surface):
        """Draw the 'В меню' button."""
        rect = self.menu_button_rect

        # Цвета кнопки (оранжевый градиент как у кнопки паузы)
        if self.menu_button_pressed:
            color_top = (180, 120, 0)
            color_bottom = (130, 85, 0)
        elif self.menu_button_hovered:
            color_top = (255, 180, 20)
            color_bottom = (200, 145, 10)
        else:
            color_top = (243, 165, 0)
            color_bottom = (186, 127, 0)

        # Рисуем кнопку с градиентом
        btn_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            t = y / rect.height
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
            pygame.draw.line(btn_surface, (r, g, b), (0, y), (rect.width, y))

        # Маска для скругленных углов
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height),
                        border_radius=scaled(8))
        btn_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Текст
        text = self.button_font.render("В меню", True, (255, 255, 255))
        text_rect = text.get_rect(center=(rect.width // 2, rect.height // 2))

        # Тень текста
        shadow = self.button_font.render("В меню", True, (140, 95, 0))
        btn_surface.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
        btn_surface.blit(text, text_rect)

        surface.blit(btn_surface, rect.topleft)

    def get_screen_button_rect(self) -> pygame.Rect:
        """Get button rect in screen coordinates."""
        return pygame.Rect(
            self.menu_button_rect.x + self.offset_x,
            self.menu_button_rect.y + self.offset_y,
            self.menu_button_rect.width,
            self.menu_button_rect.height
        )

    def handle_mouse_move(self, screen_pos: tuple):
        """Update hover state based on mouse position."""
        btn_rect = self.get_screen_button_rect()
        self.menu_button_hovered = btn_rect.collidepoint(screen_pos)

    def handle_mouse_down(self, screen_pos: tuple) -> bool:
        """Handle mouse button down. Returns True if button was pressed."""
        btn_rect = self.get_screen_button_rect()
        if btn_rect.collidepoint(screen_pos):
            self.menu_button_pressed = True
            return True
        return False

    def handle_mouse_up(self, screen_pos: tuple) -> bool:
        """Handle mouse button up. Returns True if button was clicked."""
        was_pressed = self.menu_button_pressed
        self.menu_button_pressed = False
        btn_rect = self.get_screen_button_rect()
        return was_pressed and btn_rect.collidepoint(screen_pos)

    def draw(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """Draw the pause overlay."""
        self.offset_x = offset_x
        self.offset_y = offset_y

        overlay = pygame.Surface((self.field_width, self.field_height), pygame.SRCALPHA)

        # Fully opaque dark background
        overlay.fill((35, 50, 65, 255))

        # Update and draw tiles
        self.update()
        for tile in self.tiles:
            tile.draw(overlay)

        # Draw "В меню" button
        self._draw_menu_button(overlay)

        # Draw "Игра приостановлена" text at bottom
        title_text = self.title_font.render("Игра приостановлена", True, (180, 190, 200))
        title_rect = title_text.get_rect(center=(self.field_width // 2, self.field_height - scaled(40)))
        overlay.blit(title_text, title_rect)

        surface.blit(overlay, (offset_x, offset_y))
