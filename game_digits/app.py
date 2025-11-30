import sys
import pygame

from game_digits import get_image_path, get_font_path
from game_digits.constants import (
    TILE_SIZE, GAP, COLORS, BOARD_SIZE,
    grid_to_pixel, pixel_to_grid, pixel_to_grid_round, create_background_surface
)
from game_digits.game import Game
from game_digits.sprites import Arrow, ScorePopup
from game_digits import ui_components as ui
from game_digits.windows import ResultWindow


class GameApp:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 953, 713
        self.frame = 10
        self.speed = 2
        self.window = self.HEIGHT - 20
        self.panel_width, self.panel_height = 240, self.HEIGHT
        self.tile_size, self.gap = TILE_SIZE, GAP
        self.offset = (23, 23)
        self.COLORS = COLORS
        pygame.init()
        pygame.font.init()
        # Жирные шрифты для UI панели
        # OpenSans-Bold для кириллицы (Время, Очки, пауза)
        bold_cyrillic = get_font_path("2204.ttf")
        self.font_bold_large = pygame.font.Font(bold_cyrillic, 26)   # "Время", "Очки"
        self.font_bold_medium = pygame.font.Font(bold_cyrillic, 22)  # "пауза"
        self.font_bold_value = pygame.font.Font(bold_cyrillic, 36)   # цифры
        # Состояние UI
        self.is_paused = False
        self.pause_button_rect = None
        # Для сохранения времени паузы
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.paused_progress = 1.0  # Сохранённый прогресс при паузе
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Игра цифры")
        self.icon = pygame.image.load(get_image_path("icon.png"))
        pygame.display.set_icon(self.icon)
        # Параметры для клеточного фона (как в школьной тетради)
        self.grid_cell_size = 18  # Размер клетки в пикселях (мельче)
        self.grid_line_color = (218, 236, 241)  # Светло-голубые линии
        self.arrows = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.score_popups = pygame.sprite.Group()  # Анимация очков
        self.game = Game(self.tiles)
        tile_surface_size = self.HEIGHT - 4 * self.frame
        self.tile_surface = pygame.Surface((tile_surface_size, tile_surface_size))
        # Создаём фоновую текстуру с диагональной штриховкой
        self.background_texture = create_background_surface(tile_surface_size, tile_surface_size)
        self.tile_surface.blit(self.background_texture, (0, 0))
        self.ADD_TILE_EVENT = pygame.USEREVENT + 1
        # Двухфазный таймер: опустошение + заполнение
        self.bar_empty_duration = 9800   # 9.8 секунд - бар пустеет
        self.bar_fill_duration = 500     # 0.5 секунд - бар заполняется
        self.bar_phase = 'emptying'      # 'emptying' или 'filling'
        self.bar_phase_start = 0         # Время начала текущей фазы
        self.timer_running = False
        self.COUNTDOWN_EVENT = self.game.COUNTDOWN_EVENT
        self.TILE_APPEAR_EVENT = self.game.TILE_APPEAR_EVENT

        # Start tile appearance animation
        self.game.start_tile_appearance()

    def draw_background(self):
        # Заливаем фон белым
        self.screen.fill((255, 255, 255))
        # Рисуем клеточный паттерн (как в школьной тетради)
        for x in range(0, self.WIDTH + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (x, 0), (x, self.HEIGHT), 1)
        for y in range(0, self.HEIGHT + 1, self.grid_cell_size):
            pygame.draw.line(self.screen, self.grid_line_color, (0, y), (self.WIDTH, y), 1)
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
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (self.HEIGHT, 0, self.panel_width, self.panel_height),
        )
        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))
        self.draw_score_and_timer_window()

    def draw_score_and_timer_window(self):
        panel_x = self.HEIGHT  # Начало правой панели
        padding = 15
        current_y = padding

        # === 1. Кнопка "Пауза" (центрированная) ===
        button_width = 120
        button_height = 40
        button_x = panel_x + (self.panel_width - button_width) // 2  # Центрирование
        self.pause_button_rect = ui.draw_pause_button(
            self.screen,
            (button_x, current_y, button_width, button_height),
            self.font_bold_medium,
            is_pressed=self.is_paused
        )

        current_y += button_height + 25

        # === 2. Блок "Время" ===
        # Заголовок "Время"
        time_label = self.font_bold_large.render("Время", True, (255, 255, 255))
        label_x = panel_x + (self.panel_width - time_label.get_width()) // 2
        self.screen.blit(time_label, (label_x, current_y))
        current_y += time_label.get_height() + 10

        # Строка со значением времени (иконка + полоска)
        # Полоска заходит ПОД иконку - иконка перекрывает левый край полоски
        icon_size = 50
        icon_x = panel_x + padding
        # Полоска начинается от центра иконки (иконка перекрывает левую часть)
        bar_x = icon_x + icon_size // 2
        bar_width = self.panel_width - padding - bar_x + panel_x
        bar_height = 44

        # СНАЧАЛА рисуем голубую полоску с временем (она будет ПОД иконкой)
        ui.draw_value_bar(
            self.screen,
            (bar_x, current_y + 3, bar_width, bar_height),
            self.game.current_time,
            self.font_bold_value
        )

        # ЗАТЕМ рисуем иконку часов ПОВЕРХ полоски
        ui.draw_clock_icon(self.screen, (icon_x + icon_size // 2, current_y + icon_size // 2), icon_size)
        current_y += icon_size + 15

        # === 3. Прогресс-бар (индикатор времени до появления новой цифры) ===
        progress_height = 22
        progress_x = panel_x + padding
        progress_width = self.panel_width - padding * 2

        if self.timer_running:
            if self.is_paused:
                # На паузе используем сохранённое значение прогресса
                progress = self.paused_progress
            else:
                elapsed = pygame.time.get_ticks() - self.bar_phase_start
                if self.bar_phase == 'emptying':
                    # Бар уменьшается от 1 до 0
                    progress = max(0, 1 - elapsed / self.bar_empty_duration)
                elif self.bar_phase == 'waiting_spawn':
                    # Бар на нуле, ждём спавна
                    progress = 0
                else:  # filling
                    # Бар увеличивается от 0 до 1
                    progress = min(1, elapsed / self.bar_fill_duration)
        else:
            # Таймер не запущен - используем сохранённый прогресс (или 1.0 в начале игры)
            progress = self.paused_progress

        ui.draw_progress_bar(
            self.screen,
            (progress_x, current_y, progress_width, progress_height),
            progress
        )
        current_y += progress_height + 25

        # === 4. Блок "Очки" ===
        # Заголовок "Очки"
        score_label = self.font_bold_large.render("Очки", True, (255, 255, 255))
        label_x = panel_x + (self.panel_width - score_label.get_width()) // 2
        self.screen.blit(score_label, (label_x, current_y))
        current_y += score_label.get_height() + 10

        # Строка со значением очков (иконка + полоска)
        # СНАЧАЛА рисуем голубую полоску с очками (она будет ПОД иконкой)
        ui.draw_value_bar(
            self.screen,
            (bar_x, current_y + 3, bar_width, bar_height),
            self.game.score,
            self.font_bold_value
        )

        # ЗАТЕМ рисуем иконку солнца ПОВЕРХ полоски
        ui.draw_sun_icon(self.screen, (icon_x + icon_size // 2, current_y + icon_size // 2), icon_size)

    def show_result_window(self):
        """Display the game result window with final score.

        Returns:
            bool: True if user wants to start new game, False to exit
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
        self.game = Game(self.tiles)

        # Reset timer state
        self.timer_running = False
        self.bar_phase = 'emptying'
        self.bar_phase_start = 0
        self.is_paused = False
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.paused_progress = 1.0

        # Recreate background texture
        tile_surface_size = self.HEIGHT - 4 * self.frame
        self.background_texture = create_background_surface(tile_surface_size, tile_surface_size)
        self.tile_surface.blit(self.background_texture, (0, 0))

        # Start tile appearance animation
        self.game.start_tile_appearance()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

            # Проверяем нажатие на кнопку паузы
            if self.pause_button_rect and self.pause_button_rect.collidepoint(pos):
                self.toggle_pause()
                return True

            # Блокируем игровые взаимодействия на паузе
            if self.is_paused:
                return True

            # Block interaction during tile appearance animation
            if self.game.is_initializing:
                return True

            pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
            self.handle_mouse_click(pos)
        return True

    def toggle_pause(self):
        """Переключает состояние паузы."""
        self.is_paused = not self.is_paused

        if self.is_paused:
            # Остановка игры
            self.pause_start_time = pygame.time.get_ticks()
            # Сохраняем текущий прогресс
            if self.timer_running:
                elapsed = pygame.time.get_ticks() - self.bar_phase_start
                if self.bar_phase == 'emptying':
                    self.paused_progress = max(0, 1 - elapsed / self.bar_empty_duration)
                elif self.bar_phase == 'waiting_spawn':
                    self.paused_progress = 0
                else:  # filling
                    self.paused_progress = min(1, elapsed / self.bar_fill_duration)
            # Останавливаем таймер обратного отсчёта
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 0)
        else:
            # Возобновление игры
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.total_pause_time += pause_duration

            # Корректируем время начала фазы
            if self.timer_running:
                self.bar_phase_start += pause_duration

            # Возобновляем таймер обратного отсчёта
            pygame.time.set_timer(self.COUNTDOWN_EVENT, 1000)

    def handle_mouse_click(self, pos):
        for arrow in self.arrows:
            if arrow.rect.collidepoint(pos):
                tile = arrow.tile
                direction = arrow.direction
                # Вычисляем сколько ячеек плитка пройдёт
                old_row, old_col = tile.position
                target_rect = tile.target_move(direction, self.game.board)
                new_row, new_col = pixel_to_grid(target_rect.topleft[0], target_rect.topleft[1])
                total_cells = abs(new_row - old_row) + abs(new_col - old_col)
                # Инициализируем отслеживание движения для анимации
                tile.move_start_pos = tile.position
                tile.last_grid_pos = tile.position
                tile.cells_left_count = 0
                tile.total_cells_to_move = total_cells
                tile.move_animation_group = pygame.sprite.Group()
                # Начинаем движение
                tile.is_moving = True
                tile.current_direction = direction
                self.arrows.empty()
                return
        for tile in self.tiles:
            if tile.rect.collidepoint(pos):
                self.handle_tile_click(tile)
                break

    def handle_tile_click(self, tile):
        # Не позволяем выбирать плитку которая сама движется
        if tile.is_moving:
            return
        if self.game.selected_tile:
            if self.game.selected_tile == tile:
                return
            positions = self.game.remove_tiles(self.game.selected_tile, tile)
            if positions:
                self.arrows.empty()  # Очищаем стрелки после удаления плиток
                self.spawn_score_animation(positions)  # Создаём анимацию очков
                self.update_display()
                self.game.selected_tile = None
                if not self.timer_running and any(
                    self.game.board[i][j] is None for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)
                ):
                    self.timer_running = True
                    self.bar_phase = 'emptying'
                    self.bar_phase_start = pygame.time.get_ticks()
                return
        # Разрешаем выбор новой плитки даже когда другие движутся
        self.arrows.empty()
        self.game.select_tile(tile)
        self.draw_arrows_for_tile(tile)

    def spawn_score_animation(self, positions):
        """Создаёт анимацию очков от первой плитки ко второй."""
        delay_per_number = 80  # Задержка между появлением чисел (мс)
        max_value = len(positions)
        # Создаём отдельную группу для этой анимации
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
                for row in range(max(0, top_row), min(BOARD_SIZE, bottom_row + 1)):
                    for col in range(max(0, left_col), min(BOARD_SIZE, right_col + 1)):
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
        # Удаляем popup-ы которые перекрываются стрелками
        self.remove_popups_at_positions(arrow_grid_positions)
        self.update_display()
        self.arrows.draw(self.tile_surface)

    def remove_popups_at_positions(self, grid_positions):
        """Удаляет анимации очков, находящиеся на указанных позициях."""
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
                for row in range(max(0, top_row), min(BOARD_SIZE, bottom_row + 1)):
                    for col in range(max(0, left_col), min(BOARD_SIZE, right_col + 1)):
                        # Исключаем стартовую позицию - плитка оттуда уезжает
                        if (row, col) != tile.position:
                            occupied_by_moving.add((row, col))
        for arrow in list(self.arrows):
            # Вычисляем grid позицию стрелки
            arrow_row, arrow_col = pixel_to_grid(arrow.rect.x, arrow.rect.y)
            if 0 <= arrow_row < BOARD_SIZE and 0 <= arrow_col < BOARD_SIZE:
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
                    # Если other уезжает из области куда едет tile - не коллизия
                    tile_target = tile.target_move(dir1, self.game.board)
                    other_start = other.position  # откуда уехала other
                    tile_target_pos = pixel_to_grid(tile_target.x, tile_target.y)
                    if other_start == tile_target_pos:
                        continue  # other уезжает оттуда куда едет tile

                    return other
        return None

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

        # Проверяем, покинула ли плитка ячейку (для анимации -N)
        if hasattr(tile, 'last_grid_pos'):
            current_row, current_col = pixel_to_grid(tile.rect.centerx, tile.rect.centery)
            current_pos = (current_row, current_col)
            if current_pos != tile.last_grid_pos:
                # Плитка покинула ячейку - показываем popup там
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

    def resolve_collision(self, tile1, tile2):
        """Останавливает обе плитки при столкновении."""
        self.snap_to_grid(tile1)
        self.snap_to_grid(tile2)

    def snap_to_grid(self, tile):
        """Привязывает плитку к ближайшей ячейке сетки."""
        # Вычисляем ближайшую позицию на сетке
        grid_row, grid_col = pixel_to_grid_round(tile.rect.topleft[0], tile.rect.topleft[1])

        # Ограничиваем в пределах поля
        grid_col = max(0, min(BOARD_SIZE - 1, grid_col))
        grid_row = max(0, min(BOARD_SIZE - 1, grid_row))

        # Если ячейка занята, ищем ближайшую свободную в направлении движения
        if self.game.board[grid_row][grid_col] is not None and self.game.board[grid_row][grid_col] != tile:
            # Откатываемся на предыдущую позицию
            grid_row, grid_col = tile.position[0], tile.position[1]

        # Устанавливаем новую позицию
        new_rect_x, new_rect_y = grid_to_pixel(grid_row, grid_col)
        tile.rect.topleft = (new_rect_x, new_rect_y)

        # Финализируем движение
        self.finalize_move(tile)

    def finalize_move(self, tile):
        tile.is_moving = False
        tile.current_direction = None
        # Очищаем атрибуты отслеживания движения
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
        # Очищаем стрелки только если это была выбранная плитка
        if self.game.selected_tile == tile:
            self.game.deselect_tile()
            self.arrows.empty()
        # Удаляем стрелки на занятых ячейках (плитка могла приехать на чужую стрелку)
        self.remove_arrows_on_occupied_cells()
        delta_x = abs(new_x - old_x)
        delta_y = abs(new_y - old_y)
        cells_moved = delta_x + delta_y
        if cells_moved > 0:
            self.game.deduct_score(cells_moved)
        self.update_display()
        pygame.display.flip()

    def update_display(self):
        self.tile_surface.blit(self.background_texture, (0, 0))
        # Рисуем сначала статичные плитки
        for tile in self.tiles:
            if not tile.is_moving:
                self.tile_surface.blit(tile.image, tile.rect)
        # Обновляем и рисуем анимацию очков
        self.score_popups.update()
        for popup in self.score_popups:
            popup.draw(self.tile_surface)
        # Стрелки
        self.arrows.draw(self.tile_surface)
        # Движущиеся плитки поверх стрелок
        for tile in self.tiles:
            if tile.is_moving:
                self.tile_surface.blit(tile.image, tile.rect)
        self.draw_background()
        pygame.display.update()

    def run(self):
        running = True
        show_result = False
        prepare_to_show_result = False
        # Флаг для добавления плитки (когда бар становится пустым)
        pending_tile_spawn = False
        while running:
            # Обработка двухфазного таймера
            if self.timer_running and not self.is_paused:
                elapsed = pygame.time.get_ticks() - self.bar_phase_start
                if self.bar_phase == 'emptying':
                    # Проверяем: бар опустел?
                    if elapsed >= self.bar_empty_duration:
                        pending_tile_spawn = True
                        # Ждём спавна - бар остаётся на 0
                        self.bar_phase = 'waiting_spawn'
                elif self.bar_phase == 'waiting_spawn':
                    # Бар ждёт на 0 пока спавн не произойдёт
                    pass
                elif self.bar_phase == 'filling':
                    # Проверяем: бар заполнился?
                    if elapsed >= self.bar_fill_duration:
                        # Переходим к фазе опустошения
                        self.bar_phase = 'emptying'
                        self.bar_phase_start = pygame.time.get_ticks()

            # Очищаем и перерисовываем tile_surface каждый кадр
            self.tile_surface.blit(self.background_texture, (0, 0))
            # Рисуем сначала статичные плитки
            for tile in self.tiles:
                if not tile.is_moving:
                    self.tile_surface.blit(tile.image, tile.rect)
            # Обновляем и рисуем анимацию очков в каждом кадре (только если не пауза)
            if not self.is_paused:
                self.score_popups.update()
            for popup in self.score_popups:
                popup.draw(self.tile_surface)
            # Рисуем стрелки
            self.arrows.draw(self.tile_surface)
            # Рисуем движущиеся плитки поверх стрелок
            for tile in self.tiles:
                if tile.is_moving:
                    self.tile_surface.blit(tile.image, tile.rect)
            self.draw_background()
            # Движение плиток только если не пауза
            if not self.is_paused:
                for tile in self.tiles:
                    if tile.is_moving:
                        direction = tile.current_direction
                        if direction:
                            self.move_tile(tile, direction)
                            target_rect = tile.target_move(direction, self.game.board)
                            # Проверяем достижение цели с допуском (для float координат)
                            dx = abs(tile.rect.x - target_rect.x)
                            dy = abs(tile.rect.y - target_rect.y)
                            if dx < 1 and dy < 1:
                                tile.rect.topleft = target_rect.topleft
                                self.finalize_move(tile)
            pygame.display.update()

            # Добавляем плитку когда бар опустел
            if pending_tile_spawn:
                spawn_result = self.game.add_new_tile()
                if spawn_result == 'pending':
                    # Движущиеся плитки блокируют спавн - ждём
                    pass  # pending_tile_spawn остаётся True, бар на 0
                else:
                    pending_tile_spawn = False
                    # Спавн произошёл - запускаем фазу заполнения бара
                    self.bar_phase = 'filling'
                    self.bar_phase_start = pygame.time.get_ticks()
                    self.remove_arrows_on_occupied_cells()
                    empty = any(
                        self.game.board[i][j] is None
                        for i in range(BOARD_SIZE)
                        for j in range(BOARD_SIZE)
                    )
                    if not empty:
                        self.timer_running = False

            for event in pygame.event.get():
                if event.type == self.TILE_APPEAR_EVENT:
                    # Spawn next tile in appearance animation
                    self.game.spawn_next_tile()
                    self.update_display()
                elif event.type == self.COUNTDOWN_EVENT:
                    self.game.handle_countdown()
                else:
                    running = self.handle_event(event)
            # Проверяем успешное завершение (все плитки убраны)
            if self.game.prepare_to_end:
                self.game.prepare_to_end = False
                prepare_to_show_result = True
                # Сохраняем текущий прогресс перед остановкой
                if self.timer_running:
                    elapsed = pygame.time.get_ticks() - self.bar_phase_start
                    if self.bar_phase == 'emptying':
                        self.paused_progress = max(0, 1 - elapsed / self.bar_empty_duration)
                    elif self.bar_phase == 'waiting_spawn':
                        self.paused_progress = 0
                    else:  # filling
                        self.paused_progress = min(1, elapsed / self.bar_fill_duration)
                self.timer_running = False  # Останавливаем прогресс-бар
            elif prepare_to_show_result:
                prepare_to_show_result = False
                show_result = True

            # Проверяем завершение по таймеру (время истекло)
            if self.game.game_over_flag:
                show_result = True

            if show_result and not any(tile.is_moving for tile in self.tiles) and len(self.score_popups) == 0:
                # Анимации очков закончились - показываем результат
                self.update_display()
                pygame.display.flip()
                start_new_game = self.show_result_window()
                if start_new_game:
                    # Reset game and continue
                    self.reset_game()
                    show_result = False
                    prepare_to_show_result = False
                    pending_tile_spawn = False
                else:
                    running = False
