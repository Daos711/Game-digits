"""
Animated pause overlay with floating letter tiles.
"""

import math
import pygame
from game_digits import get_font_path


class PauseTile:
    """A single animated tile for the pause screen."""

    def __init__(self, letter: str, color: tuple, center_x: float, center_y: float,
                 orbit_radius: float, orbit_speed: float, phase: float, tile_size: int = 52):
        self.letter = letter
        self.color = color
        self.tile_size = tile_size
        self.center_x = center_x
        self.center_y = center_y
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.phase = phase  # Starting phase in radians

        # Current position
        self.x = center_x
        self.y = center_y

        # Font for the letter
        self.font = pygame.font.Font(get_font_path("2204.ttf"), 32)

        # Pre-render the tile surface
        self._render_tile()

    def _render_tile(self):
        """Pre-render the tile with letter."""
        self.surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)

        # Draw rounded rectangle background
        radius = 8
        rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)

        # Main color
        pygame.draw.rect(self.surface, self.color, rect, border_radius=radius)

        # Subtle gradient effect (lighter top)
        highlight = pygame.Surface((self.tile_size, self.tile_size // 2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.surface.blit(highlight, (0, 0))

        # Border
        border_color = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(self.surface, border_color, rect, width=2, border_radius=radius)

        # Letter
        text = self.font.render(self.letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
        self.surface.blit(text, text_rect)

    def update(self, time_ms: int):
        """Update tile position based on time."""
        # Calculate position on orbit
        angle = self.phase + (time_ms / 1000.0) * self.orbit_speed
        self.x = self.center_x + math.cos(angle) * self.orbit_radius
        self.y = self.center_y + math.sin(angle) * self.orbit_radius * 0.5  # Elliptical orbit

    def draw(self, surface: pygame.Surface):
        """Draw the tile at current position."""
        pos = (int(self.x - self.tile_size // 2), int(self.y - self.tile_size // 2))
        surface.blit(self.surface, pos)


class PauseOverlay:
    """Animated overlay shown when game is paused.

    Displays floating tiles spelling "ПАУЗА" that orbit around the center
    in an interesting pattern.
    """

    # Tile colors (matching game tiles)
    COLORS = [
        (231, 125, 128),  # П - red/pink
        (111, 183, 214),  # А - blue
        (136, 189, 134),  # У - green
        (178, 161, 199),  # З - purple
        (245, 203, 105),  # А - yellow
    ]

    def __init__(self, field_width: int, field_height: int):
        """Initialize pause overlay.

        Args:
            field_width: Width of game field in pixels
            field_height: Height of game field in pixels
        """
        self.field_width = field_width
        self.field_height = field_height

        # Create tiles for "ПАУЗА"
        self.tiles = []
        letters = "ПАУЗА"
        center_x = field_width // 2
        center_y = field_height // 2

        for i, letter in enumerate(letters):
            # Each tile has different orbit parameters
            phase = (i / len(letters)) * 2 * math.pi  # Evenly spaced around circle
            orbit_radius = 80 + (i % 2) * 30  # Alternating orbit sizes
            orbit_speed = 0.5 + (i * 0.1)  # Slightly different speeds

            tile = PauseTile(
                letter=letter,
                color=self.COLORS[i],
                center_x=center_x,
                center_y=center_y,
                orbit_radius=orbit_radius,
                orbit_speed=orbit_speed,
                phase=phase
            )
            self.tiles.append(tile)

        # Font for subtitle
        self.subtitle_font = pygame.font.Font(get_font_path("2204.ttf"), 24)

        # Animation start time
        self.start_time = 0

    def start(self):
        """Start the animation."""
        self.start_time = pygame.time.get_ticks()

    def update(self):
        """Update all tile positions."""
        current_time = pygame.time.get_ticks() - self.start_time
        for tile in self.tiles:
            tile.update(current_time)

    def draw(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """Draw the pause overlay.

        Args:
            surface: Surface to draw on
            offset_x: X offset for the overlay position
            offset_y: Y offset for the overlay position
        """
        # Create overlay surface
        overlay = pygame.Surface((self.field_width, self.field_height), pygame.SRCALPHA)

        # Dark semi-transparent background
        overlay.fill((30, 45, 60, 230))

        # Update and draw tiles
        self.update()
        for tile in self.tiles:
            tile.draw(overlay)

        # Draw subtitle
        subtitle = self.subtitle_font.render("Нажмите для продолжения", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.field_width // 2, self.field_height - 50))
        overlay.blit(subtitle, subtitle_rect)

        # Blit to main surface
        surface.blit(overlay, (offset_x, offset_y))
