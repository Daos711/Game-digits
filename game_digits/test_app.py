"""
Test mode application for quick result window testing.
10x10 board with 6 tiles (3 pairs).
"""
import sys
import pygame

from game_digits import get_image_path, get_font_path
from game_digits.constants import (
    TILE_SIZE, GAP, COLORS,
    grid_to_pixel, pixel_to_grid, pixel_to_grid_round, create_background_surface
)
from game_digits.test_game import TestGame, TEST_BOARD_SIZE
from game_digits.sprites import Arrow, ScorePopup
from game_digits import ui_components as ui
from game_digits.windows import ResultWindow, StartMenu


class TestGameApp:
    """Test mode app with 10x10 board and 6 tiles (3 pairs)."""

    def __init__(self):
        # Window size adjusted for smaller board
        self.board_size = TEST_BOARD_SIZE
        tile_area = self.board_size * TILE_SIZE + (self.board_size + 1) * GAP
        self.frame = 10
        self.window = tile_area + 2 * self.frame
        self.panel_width = 240
        self.WIDTH = self.window + 2 * self.frame + self.panel_width
        self.HEIGHT = self.window + 2 * self.frame

        self.speed = 2
        self.tile_size, self.gap = TILE_SIZE, GAP
        self.offset = (23, 23)
        self.COLORS = COLORS

        pygame.init()
        pygame.font.init()

        bold_cyrillic = get_font_path("2204.ttf")
        self.font_bold_large = pygame.font.Font(bold_cyrillic, 26)
        self.font_bold_medium = pygame.font.Font(bold_cyrillic, 22)
        self.font_bold_value = pygame.font.Font(bold_cyrillic, 36)

        self.is_paused = False
        self.pause_button_rect = None
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.paused_progress = 1.0

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Test Mode - 6 Tiles (3 pairs)")
        self.icon = pygame.image.load(get_image_path("icon.png"))
        pygame.display.set_icon(self.icon)

        self.grid_cell_size = 18  # Мельче клетки
        self.grid_line_color = (218, 236, 241)  # Светло-голубые линии

        self.arrows = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.score_popups = pygame.sprite.Group()

        self.game = TestGame(self.tiles, time_limit=60)

        tile_surface_size = tile_area
        self.tile_surface = pygame.Surface((tile_surface_size, tile_surface_size))
        self.background_texture = create_background_surface(tile_surface_size, tile_surface_size)
        self.tile_surface.blit(self.background_texture, (0, 0))

        # No auto-add tiles in test mode
        self.timer_running = False
        # Двухфазный таймер: опустошение + заполнение (для тестирования прогресс-бара)
        self.bar_empty_duration = 9800   # 9.8 секунд - бар пустеет
        self.bar_fill_duration = 500     # 0.5 секунд - бар заполняется
        self.bar_phase = 'emptying'      # 'emptying' или 'filling'
        self.bar_phase_start = 0         # Время начала текущей фазы

        self.COUNTDOWN_EVENT = self.game.COUNTDOWN_EVENT
        self.TILE_APPEAR_EVENT = self.game.TILE_APPEAR_EVENT

        # Game state: 'menu' or 'playing'
        self.state = 'menu'

        # Panel animation state
        self.panel_animation_start = 0
        self.panel_animation_active = False
        # Animation constants for panel elements
        self.PANEL_ANIM_DURATION = 400  # ms for each element to slide in
        self.PANEL_ANIM_DELAY = 150     # ms delay between elements

        # Create start menu
        self.start_menu = StartMenu(
            screen=self.screen,
            screen_size=(self.WIDTH, self.HEIGHT),
            redraw_background=self.draw_background_for_menu
        )

    def draw_background(self):
        self.screen.fill((255, 255, 255))

        for x in range(0, self.WIDTH + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (x, 0), (x, self.HEIGHT), 1)
        for y in range(0, self.HEIGHT + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (0, y), (self.WIDTH, y), 1)

        # Yellow border around tile area
        # Желтая рамка с границами
        border_color = (168, 134, 33)
        frame_color = (247, 204, 74)
        # Внешняя граница (1 пиксель)
        pygame.draw.rect(
            self.screen,
            border_color,
            (self.frame, self.frame, self.window, self.window),
            1,
        )
        # Желтая рамка (8 пикселей)
        pygame.draw.rect(
            self.screen,
            frame_color,
            (self.frame + 1, self.frame + 1, self.window - 2, self.window - 2),
            self.frame - 2,
        )
        # Внутренняя граница (1 пиксель)
        pygame.draw.rect(
            self.screen,
            border_color,
            (self.frame * 2 - 1, self.frame * 2 - 1, self.window - self.frame * 2 + 2, self.window - self.frame * 2 + 2),
            1,
        )

        # Blue panel on the right
        panel_x = self.window + 2 * self.frame
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (panel_x, 0, self.panel_width, self.HEIGHT),
        )

        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))
        self.draw_score_and_timer_window()

    def draw_background_for_menu(self):
        """Draw background for menu (without UI panel elements)."""
        self.screen.fill((255, 255, 255))

        for x in range(0, self.WIDTH + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (x, 0), (x, self.HEIGHT), 1)
        for y in range(0, self.HEIGHT + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (0, y), (self.WIDTH, y), 1)

        border_color = (162, 140, 40)
        frame_color = (247, 204, 74)
        pygame.draw.rect(
            self.screen,
            border_color,
            (self.frame, self.frame, self.window, self.window),
            1,
        )
        pygame.draw.rect(
            self.screen,
            frame_color,
            (self.frame + 1, self.frame + 1, self.window - 2, self.window - 2),
            self.frame - 2,
        )
        pygame.draw.rect(
            self.screen,
            border_color,
            (self.frame * 2 - 1, self.frame * 2 - 1, self.window - self.frame * 2 + 2, self.window - self.frame * 2 + 2),
            1,
        )

        panel_x = self.window + 2 * self.frame
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (panel_x, 0, self.panel_width, self.HEIGHT),
        )

        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))

    def _get_panel_element_offset(self, element_index):
        """Calculate Y offset for panel element based on animation state."""
        if not self.panel_animation_active:
            return 0

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.panel_animation_start
        element_start = element_index * self.PANEL_ANIM_DELAY

        if elapsed < element_start:
            return -300

        element_elapsed = elapsed - element_start
        if element_elapsed >= self.PANEL_ANIM_DURATION:
            total_duration = 2 * self.PANEL_ANIM_DELAY + self.PANEL_ANIM_DURATION
            if elapsed >= total_duration:
                self.panel_animation_active = False
            return 0

        progress = element_elapsed / self.PANEL_ANIM_DURATION
        eased = 1 - (1 - progress) ** 3
        return int(-300 * (1 - eased))

    def draw_score_and_timer_window(self):
        panel_x = self.window + 2 * self.frame
        padding = 15

        pause_offset = self._get_panel_element_offset(0)
        time_offset = self._get_panel_element_offset(1)
        score_offset = self._get_panel_element_offset(2)

        current_y = padding

        # Pause button
        button_width = 120
        button_height = 40
        button_x = panel_x + (self.panel_width - button_width) // 2
        button_y = current_y + pause_offset

        if button_y > -button_height:
            self.pause_button_rect = ui.draw_pause_button(
                self.screen,
                (button_x, button_y, button_width, button_height),
                self.font_bold_medium,
                is_pressed=self.is_paused
            )
        else:
            self.pause_button_rect = None

        current_y += button_height + 25

        # Time block
        time_block_y = current_y + time_offset
        time_label = self.font_bold_large.render("Время", True, (255, 255, 255))
        label_x = panel_x + (self.panel_width - time_label.get_width()) // 2

        icon_size = 50
        icon_x = panel_x + padding
        bar_x = icon_x + icon_size // 2
        bar_width = self.panel_width - padding - bar_x + panel_x
        bar_height = 44

        if time_block_y > -150:
            self.screen.blit(time_label, (label_x, time_block_y))
            icon_y = time_block_y + time_label.get_height() + 10

            ui.draw_value_bar(
                self.screen,
                (bar_x, icon_y + 3, bar_width, bar_height),
                self.game.current_time,
                self.font_bold_value
            )
            ui.draw_clock_icon(self.screen, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size)

            # Progress bar
            progress_y = icon_y + icon_size + 15
            progress_height = 22
            progress_x = panel_x + padding
            progress_width = self.panel_width - padding * 2

            if self.timer_running:
                if self.is_paused:
                    progress = self.paused_progress
                else:
                    elapsed = pygame.time.get_ticks() - self.bar_phase_start
                    if self.bar_phase == 'emptying':
                        progress = max(0, 1 - elapsed / self.bar_empty_duration)
                    else:
                        progress = min(1, elapsed / self.bar_fill_duration)
            else:
                progress = self.paused_progress

            ui.draw_progress_bar(
                self.screen,
                (progress_x, progress_y, progress_width, progress_height),
                progress
            )

        current_y += time_label.get_height() + 10 + icon_size + 15 + 22 + 25

        # Score block
        score_block_y = current_y + score_offset

        if score_block_y > -100:
            score_label = self.font_bold_large.render("Очки", True, (255, 255, 255))
            label_x = panel_x + (self.panel_width - score_label.get_width()) // 2
            self.screen.blit(score_label, (label_x, score_block_y))
            score_icon_y = score_block_y + score_label.get_height() + 10

            ui.draw_value_bar(
                self.screen,
                (bar_x, score_icon_y + 3, bar_width, bar_height),
                self.game.score,
                self.font_bold_value
            )
            ui.draw_sun_icon(self.screen, (icon_x + icon_size // 2, score_icon_y + icon_size // 2), icon_size)

    def show_result_window(self):
        """Display the game result window with final score.

        Returns:
            str: 'new_game', 'menu', or None
        """
        def redraw_background():
            """Callback to redraw game scene before result window."""
            self.tile_surface.blit(self.background_texture, (0, 0))
            for popup in self.score_popups:
                popup.draw(self.tile_surface)
            self.draw_background()

        result_window = ResultWindow(
            screen=self.screen,
            screen_size=(self.WIDTH, self.HEIGHT),
            game_score=self.game.score,
            current_time=self.game.current_time,
            redraw_callback=redraw_background
        )
        return result_window.show()

    def reset_game(self):
        """Reset the game state to start a new game."""
        # Clear all sprites
        self.arrows.empty()
        self.tiles.empty()
        self.score_popups.empty()

        # Reset game state
        self.game = TestGame(self.tiles, time_limit=60)

        # Reset timer state
        self.timer_running = False
        self.is_paused = False
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.paused_progress = 1.0

        # Recreate background texture
        tile_area = self.board_size * TILE_SIZE + (self.board_size + 1) * GAP
        self.background_texture = create_background_surface(tile_area, tile_area)
        self.tile_surface.blit(self.background_texture, (0, 0))

        # Start tile appearance animation
        self.game.start_tile_appearance()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

            if self.pause_button_rect and self.pause_button_rect.collidepoint(pos):
                self.toggle_pause()
                return True

            if self.is_paused:
                return True

            if self.game.is_initializing:
                return True

            pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
            self.handle_mouse_click(pos)
        return True

    def toggle_pause(self):
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_start_time = pygame.time.get_ticks()
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)
        else:
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.total_pause_time += pause_duration
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 1000)

    def handle_mouse_click(self, pos):
        for arrow in self.arrows:
            if arrow.rect.collidepoint(pos):
                tile = arrow.tile
                direction = arrow.direction
                old_row, old_col = tile.position
                target_rect = tile.target_move(direction, self.game.board)
                new_row, new_col = pixel_to_grid(target_rect.topleft[0], target_rect.topleft[1])
                total_cells = abs(new_row - old_row) + abs(new_col - old_col)
                tile.move_start_pos = tile.position
                tile.last_grid_pos = tile.position
                tile.cells_left_count = 0
                tile.total_cells_to_move = total_cells
                tile.move_animation_group = pygame.sprite.Group()
                tile.is_moving = True
                tile.current_direction = direction
                self.arrows.empty()
                return

        for tile in self.tiles:
            if tile.rect.collidepoint(pos):
                self.handle_tile_click(tile)
                break

    def handle_tile_click(self, tile):
        if tile.is_moving:
            return
        if self.game.selected_tile:
            if self.game.selected_tile == tile:
                return
            positions = self.game.remove_tiles(self.game.selected_tile, tile)
            if positions:
                self.arrows.empty()
                self.spawn_score_animation(positions)
                self.update_display()
                self.game.selected_tile = None
                # Запускаем таймер при первом удалении пары
                if not self.timer_running:
                    self.timer_running = True
                    self.bar_phase = 'emptying'
                    self.bar_phase_start = pygame.time.get_ticks()
                return

        self.arrows.empty()
        self.game.select_tile(tile)
        self.draw_arrows_for_tile(tile)

    def spawn_score_animation(self, positions):
        delay_per_number = 80
        max_value = len(positions)
        animation_group = pygame.sprite.Group()
        for i, pos in enumerate(positions):
            value = i + 1
            delay = i * delay_per_number
            popup = ScorePopup(value, pos, delay, max_value, group=animation_group, board=self.game.board)
            animation_group.add(popup)
            self.score_popups.add(popup)

    def draw_arrows_for_tile(self, tile):
        # Вычисляем ячейки где ФИЗИЧЕСКИ находятся движущиеся плитки (1-2 ячейки)
        # Исключаем стартовую позицию - плитка оттуда уезжает
        occupied_by_moving = set()
        cell_size = TILE_SIZE + GAP
        for t in self.tiles:
            if t.is_moving:
                left_col = (t.rect.x - GAP) // cell_size
                top_row = (t.rect.y - GAP) // cell_size
                right_col = (t.rect.x + TILE_SIZE - 1 - GAP) // cell_size
                bottom_row = (t.rect.y + TILE_SIZE - 1 - GAP) // cell_size
                for row in range(max(0, top_row), min(self.board_size, bottom_row + 1)):
                    for col in range(max(0, left_col), min(self.board_size, right_col + 1)):
                        # Исключаем стартовую позицию - плитка оттуда уезжает
                        if (row, col) != t.position:
                            occupied_by_moving.add((row, col))

        arrow_grid_positions = []
        for direction in ["up", "down", "left", "right"]:
            if self.game.can_move(tile, direction):
                arrow_position = self.get_arrow_position(tile.rect.topleft, direction)
                row, col = tile.position
                if direction == "up":
                    arrow_row, arrow_col = row - 1, col
                elif direction == "down":
                    arrow_row, arrow_col = row + 1, col
                elif direction == "left":
                    arrow_row, arrow_col = row, col - 1
                elif direction == "right":
                    arrow_row, arrow_col = row, col + 1
                # Стрелка не появляется где физически находится движущаяся плитка
                if (arrow_row, arrow_col) not in occupied_by_moving:
                    self.arrows.add(Arrow(direction, arrow_position, self.game, tile))
                    arrow_grid_positions.append((arrow_row, arrow_col))

        self.remove_popups_at_positions(arrow_grid_positions)
        self.update_display()
        self.arrows.draw(self.tile_surface)

    def remove_popups_at_positions(self, grid_positions):
        for popup in list(self.score_popups):
            if popup.grid_position in grid_positions:
                popup.kill()

    def remove_arrows_on_occupied_cells(self):
        """Удаляет стрелки, находящиеся на занятых ячейках."""
        # Позиции, где сейчас визуально находятся движущиеся плитки (1-2 ячейки)
        # Исключаем стартовые позиции - плитки оттуда уезжают
        occupied_by_moving = set()
        cell_size = TILE_SIZE + GAP
        for tile in self.tiles:
            if tile.is_moving:
                left_col = (tile.rect.x - GAP) // cell_size
                top_row = (tile.rect.y - GAP) // cell_size
                right_col = (tile.rect.x + TILE_SIZE - 1 - GAP) // cell_size
                bottom_row = (tile.rect.y + TILE_SIZE - 1 - GAP) // cell_size
                for row in range(max(0, top_row), min(self.board_size, bottom_row + 1)):
                    for col in range(max(0, left_col), min(self.board_size, right_col + 1)):
                        # Исключаем стартовую позицию - плитка оттуда уезжает
                        if (row, col) != tile.position:
                            occupied_by_moving.add((row, col))
        for arrow in list(self.arrows):
            # Вычисляем grid позицию стрелки
            arrow_row, arrow_col = pixel_to_grid(arrow.rect.x, arrow.rect.y)
            if 0 <= arrow_row < self.board_size and 0 <= arrow_col < self.board_size:
                cell = self.game.board[arrow_row][arrow_col]
                # Удаляем стрелку если:
                # 1. Ячейка занята статичной плиткой (не движущейся)
                # 2. Или ячейка физически занята движущейся плиткой (кроме стартовой позиции)
                is_static_tile = cell is not None and not cell.is_moving
                if is_static_tile or (arrow_row, arrow_col) in occupied_by_moving:
                    arrow.kill()

    def get_arrow_position(self, tile_position, direction):
        x, y = tile_position
        if direction == "up":
            return (x, y - self.tile_size - self.gap)
        elif direction == "down":
            return (x, y + self.tile_size + self.gap)
        elif direction == "left":
            return (x - self.tile_size - self.gap, y)
        elif direction == "right":
            return (x + self.tile_size + self.gap, y)

    def check_collision(self, tile):
        """Проверяет столкновение с другими движущимися плитками."""
        for other in self.tiles:
            if other != tile and other.is_moving:
                if tile.rect.colliderect(other.rect):
                    dir1 = tile.current_direction
                    dir2 = other.current_direction

                    # Проверяем противоположные направления
                    horizontal_opposite = (dir1, dir2) in [("left", "right"), ("right", "left")]
                    vertical_opposite = (dir1, dir2) in [("up", "down"), ("down", "up")]

                    # Порог для определения "одной линии" - половина размера ячейки
                    threshold = (TILE_SIZE + GAP) // 2

                    if horizontal_opposite:
                        # Проверяем по Y: на одной строке или параллельно?
                        if abs(tile.rect.y - other.rect.y) <= threshold:
                            # Лоб в лоб на одной строке - столкновение!
                            return other
                        else:
                            # Параллельные пути - пропускаем
                            continue

                    if vertical_opposite:
                        # Проверяем по X: на одном столбце или параллельно?
                        if abs(tile.rect.x - other.rect.x) <= threshold:
                            # Лоб в лоб на одном столбце - столкновение!
                            return other
                        else:
                            # Параллельные пути - пропускаем
                            continue

                    # Если движутся в одном направлении - одна догоняет другую, не коллизия
                    if dir1 == dir2:
                        continue

                    # Если движутся перпендикулярно - проверяем кто куда едет
                    tile_target = tile.target_move(dir1, self.game.board)
                    other_start = other.position
                    tile_target_pos = pixel_to_grid(tile_target.x, tile_target.y)
                    if other_start == tile_target_pos:
                        continue

                    return other
        return None

    def resolve_collision(self, tile1, tile2):
        """Останавливает обе плитки при столкновении."""
        self.snap_to_grid(tile1)
        self.snap_to_grid(tile2)

    def snap_to_grid(self, tile):
        grid_row, grid_col = pixel_to_grid_round(tile.rect.topleft[0], tile.rect.topleft[1])
        grid_col = max(0, min(self.board_size - 1, grid_col))
        grid_row = max(0, min(self.board_size - 1, grid_row))

        if self.game.board[grid_row][grid_col] is not None and self.game.board[grid_row][grid_col] != tile:
            grid_row, grid_col = tile.position[0], tile.position[1]

        new_rect_x, new_rect_y = grid_to_pixel(grid_row, grid_col)
        tile.rect.topleft = (new_rect_x, new_rect_y)
        self.finalize_move(tile)

    def finalize_move(self, tile):
        tile.is_moving = False
        tile.current_direction = None

        if hasattr(tile, 'last_grid_pos'):
            del tile.last_grid_pos
            del tile.move_start_pos
            del tile.cells_left_count
            del tile.total_cells_to_move
            del tile.move_animation_group

        old_x, old_y = tile.position
        new_x, new_y = pixel_to_grid(tile.rect.topleft[0], tile.rect.topleft[1])
        tile.position = (new_x, new_y)
        self.game.update_board((old_x, old_y), (new_x, new_y), tile)

        if self.game.selected_tile == tile:
            self.game.deselect_tile()
            self.arrows.empty()

        delta_x = abs(new_x - old_x)
        delta_y = abs(new_y - old_y)
        cells_moved = delta_x + delta_y
        if cells_moved > 0:
            self.game.deduct_score(cells_moved)

        self.update_display()
        pygame.display.flip()

    def move_tile(self, tile, direction):
        target_rect = tile.target_move(direction, self.game.board)
        dx = target_rect.topleft[0] - tile.rect.topleft[0]
        dy = target_rect.topleft[1] - tile.rect.topleft[1]

        if dx == 0 and dy != 0:
            # Ограничиваем шаг чтобы не перескочить цель
            step_y = min(self.speed, abs(dy)) * (1 if dy > 0 else -1)
            tile.rect.y += step_y
        elif dy == 0 and dx != 0:
            # Ограничиваем шаг чтобы не перескочить цель
            step_x = min(self.speed, abs(dx)) * (1 if dx > 0 else -1)
            tile.rect.x += step_x

        if hasattr(tile, 'last_grid_pos'):
            current_row, current_col = pixel_to_grid(tile.rect.centerx, tile.rect.centery)
            current_pos = (current_row, current_col)
            if current_pos != tile.last_grid_pos:
                tile.cells_left_count += 1
                left_pos = tile.last_grid_pos
                popup = ScorePopup(
                    tile.cells_left_count, left_pos, 0, tile.total_cells_to_move,
                    group=tile.move_animation_group,
                    board=self.game.board,
                    negative=True
                )
                tile.move_animation_group.add(popup)
                self.score_popups.add(popup)
                tile.last_grid_pos = current_pos

        # Проверяем коллизию с другими движущимися плитками
        collided = self.check_collision(tile)
        if collided:
            self.resolve_collision(tile, collided)

        # Удаляем стрелки на ячейках где сейчас находится движущаяся плитка
        self.remove_arrows_on_occupied_cells()

        self.update_display()

    def update_display(self):
        self.tile_surface.blit(self.background_texture, (0, 0))
        self.tiles.draw(self.tile_surface)
        self.score_popups.update()
        for popup in self.score_popups:
            popup.draw(self.tile_surface)
        self.arrows.draw(self.tile_surface)
        self.draw_background()
        pygame.display.update()

    def run(self):
        running = True
        show_result = False
        prepare_to_show_result = False

        while running:
            # === MENU STATE ===
            if self.state == 'menu':
                start_game = self.start_menu.show()
                if start_game:
                    self.state = 'playing'
                    # Start panel animation
                    self.panel_animation_active = True
                    self.panel_animation_start = pygame.time.get_ticks()
                    self.game.start_tile_appearance()
                else:
                    running = False
                continue

            self.tile_surface.blit(self.background_texture, (0, 0))
            self.tiles.draw(self.tile_surface)

            if not self.is_paused:
                self.score_popups.update()
            for popup in self.score_popups:
                popup.draw(self.tile_surface)

            self.arrows.draw(self.tile_surface)
            self.draw_background()

            if not self.is_paused:
                for tile in self.tiles:
                    if tile.is_moving:
                        direction = tile.current_direction
                        if direction:
                            self.move_tile(tile, direction)
                            target_rect = tile.target_move(direction, self.game.board)
                            dx = abs(tile.rect.x - target_rect.x)
                            dy = abs(tile.rect.y - target_rect.y)
                            if dx < 1 and dy < 1:
                                tile.rect.topleft = target_rect.topleft
                                self.finalize_move(tile)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == self.TILE_APPEAR_EVENT:
                    self.game.spawn_next_tile()
                    self.update_display()
                elif event.type == self.COUNTDOWN_EVENT:
                    self.game.handle_countdown()
                else:
                    running = self.handle_event(event)

            if self.game.prepare_to_end:
                self.game.prepare_to_end = False
                prepare_to_show_result = True
                # Сохраняем текущий прогресс перед остановкой
                if self.timer_running:
                    elapsed = pygame.time.get_ticks() - self.bar_phase_start
                    if self.bar_phase == 'emptying':
                        self.paused_progress = max(0, 1 - elapsed / self.bar_empty_duration)
                    else:  # filling
                        self.paused_progress = min(1, elapsed / self.bar_fill_duration)
                self.timer_running = False  # Останавливаем прогресс-бар
            elif prepare_to_show_result:
                prepare_to_show_result = False
                show_result = True

            if self.game.game_over_flag:
                show_result = True

            if show_result and not any(tile.is_moving for tile in self.tiles) and len(self.score_popups) == 0:
                # Анимации очков закончились - показываем результат
                self.update_display()
                pygame.display.flip()
                result = self.show_result_window()
                if result == 'new_game':
                    # Reset game and continue playing
                    self.reset_game()
                    # Start panel animation
                    self.panel_animation_active = True
                    self.panel_animation_start = pygame.time.get_ticks()
                    self.game.start_tile_appearance()
                    show_result = False
                    prepare_to_show_result = False
                elif result == 'menu':
                    # Return to menu
                    self.reset_game()
                    self.state = 'menu'
                    show_result = False
                    prepare_to_show_result = False
                else:
                    running = False
