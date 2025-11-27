import sys
import pygame

from game_digits import get_image_path
from game_digits.game import Game
from game_digits.sprites import Arrow, ScorePopup

TILE_SIZE = 64
GAP = 3


class GameApp:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 953, 713
        self.frame = 10
        self.speed = 1
        self.window = self.HEIGHT - 20
        self.panel_width, self.panel_height = 240, self.HEIGHT
        self.tile_size, self.gap = TILE_SIZE, GAP
        self.offset = (23, 23)
        self.COLORS = {
            1: (250, 130, 124),
            2: (98, 120, 255),
            3: (249, 204, 122),
            4: (127, 254, 138),
            5: (251, 94, 223),
            6: (126, 253, 205),
            7: (239, 255, 127),
            8: (174, 121, 251),
            9: (255, 152, 123),
        }
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Игра цифры")
        self.icon = pygame.image.load(get_image_path("icon.png"))
        pygame.display.set_icon(self.icon)
        self.background_tile = pygame.image.load(get_image_path("cell.JPG"))
        self.arrows = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.score_popups = pygame.sprite.Group()  # Анимация очков
        self.game = Game(self.tiles)
        self.tile_surface = pygame.Surface(
            (self.HEIGHT - 4 * self.frame, self.HEIGHT - 4 * self.frame)
        )
        self.tile_surface.fill((249, 246, 247))
        self.ADD_TILE_EVENT = pygame.USEREVENT + 1
        self.tile_timer_interval = 10000  # 10 секунд
        self.timer_running = False
        self.tile_timer_start = 0  # Время начала таймера для прогресс-бара
        self.COUNTDOWN_EVENT = self.game.COUNTDOWN_EVENT

    def draw_background(self):
        for i in range(0, 960, self.background_tile.get_width()):
            for j in range(0, 720, self.background_tile.get_height()):
                self.screen.blit(self.background_tile, (i, j))
        pygame.draw.rect(
            self.screen,
            (247, 204, 74),
            (self.frame, self.frame, self.window, self.window),
            self.frame,
        )
        pygame.draw.rect(
            self.screen,
            (62, 157, 203),
            (self.HEIGHT, 0, self.panel_width, self.panel_height),
        )
        self.screen.blit(self.tile_surface, (2 * self.frame, 2 * self.frame))
        self.draw_score_and_timer_window()

    def draw_score_and_timer_window(self):
        # Окно счётчика очков
        score_window_rect = pygame.Rect(
            self.HEIGHT + 10, 10, self.panel_width - 20, 100
        )
        pygame.draw.rect(self.screen, (255, 255, 255), score_window_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), score_window_rect, 2)

        score_label = self.font.render("Очки", True, (0, 0, 0))
        label_rect = score_label.get_rect(
            center=(score_window_rect.centerx, score_window_rect.top + 20)
        )
        self.screen.blit(score_label, label_rect)

        score_text = self.font.render(str(self.game.score), True, (0, 0, 0))
        score_rect = score_text.get_rect(
            center=(score_window_rect.centerx, score_window_rect.top + 60)
        )
        self.screen.blit(score_text, score_rect)

        # Окно таймера
        time_window_rect = pygame.Rect(
            self.HEIGHT + 10, 120, self.panel_width - 20, 100
        )
        pygame.draw.rect(self.screen, (255, 255, 255), time_window_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), time_window_rect, 2)

        time_label = self.font.render("Время", True, (0, 0, 0))
        label_rect = time_label.get_rect(
            center=(time_window_rect.centerx, time_window_rect.top + 20)
        )
        self.screen.blit(time_label, label_rect)

        time_text = self.font.render(f"{self.game.current_time}", True, (0, 0, 0))
        time_rect = time_text.get_rect(
            center=(time_window_rect.centerx, time_window_rect.top + 60)
        )
        self.screen.blit(time_text, time_rect)

        # Прогресс-бар для таймера появления новых цифр
        if self.timer_running:
            progress_rect = pygame.Rect(
                self.HEIGHT + 10, 230, self.panel_width - 20, 20
            )
            # Фон прогресс-бара (серый)
            pygame.draw.rect(self.screen, (200, 200, 200), progress_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), progress_rect, 2)

            # Вычисляем прогресс (уменьшается справа налево)
            elapsed = pygame.time.get_ticks() - self.tile_timer_start
            progress = max(0, 1 - elapsed / self.tile_timer_interval)
            bar_width = int((self.panel_width - 24) * progress)

            if bar_width > 0:
                bar_rect = pygame.Rect(
                    progress_rect.left + 2, progress_rect.top + 2,
                    bar_width, progress_rect.height - 4
                )
                pygame.draw.rect(self.screen, (247, 204, 74), bar_rect)  # Желтый

    def show_result_window(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        window_width, window_height = 400, 300
        window_surface = pygame.Surface((window_width, window_height))
        window_surface.fill((255, 255, 255))
        pygame.draw.rect(
            window_surface, (0, 0, 0), (0, 0, window_width, window_height), 2
        )

        window_x = (self.WIDTH - window_width) // 2
        window_y = (self.HEIGHT - window_height) // 2

        title_font = pygame.font.Font(None, 48)
        label_font = pygame.font.Font(None, 36)

        # Определяем победа или проигрыш
        is_victory = not self.game.game_over_flag or self.game.current_time > 0

        if is_victory:
            title_text = title_font.render("Победа!", True, (0, 128, 0))
        else:
            title_text = title_font.render("Время вышло!", True, (200, 0, 0))

        # Бонус за скорость: 300 + 5*t (всегда по формуле)
        remaining_time = round(self.game.current_time)
        bonus = 300 + 5 * remaining_time

        title_rect = title_text.get_rect(center=(window_width // 2, 50))
        window_surface.blit(title_text, title_rect)

        total_score = self.game.score + bonus

        result_label = label_font.render("Ваш результат:", True, (0, 0, 0))
        result_label_rect = result_label.get_rect(topleft=(50, 100))
        window_surface.blit(result_label, result_label_rect)

        result_value = label_font.render(str(self.game.score), True, (0, 0, 0))
        result_value_rect = result_value.get_rect(topright=(window_width - 50, 100))
        window_surface.blit(result_value, result_value_rect)

        bonus_label = label_font.render("Бонус за скорость:", True, (0, 0, 0))
        bonus_label_rect = bonus_label.get_rect(topleft=(50, 150))
        window_surface.blit(bonus_label, bonus_label_rect)

        bonus_value = label_font.render(str(bonus), True, (0, 0, 0))
        bonus_value_rect = bonus_value.get_rect(topright=(window_width - 50, 150))
        window_surface.blit(bonus_value, bonus_value_rect)

        total_label = label_font.render("Итого:", True, (0, 0, 0))
        total_label_rect = total_label.get_rect(topleft=(50, 200))
        window_surface.blit(total_label, total_label_rect)

        total_value = label_font.render(str(total_score), True, (0, 0, 0))
        total_value_rect = total_value.get_rect(topright=(window_width - 50, 200))
        window_surface.blit(total_value, total_value_rect)

        self.screen.blit(window_surface, (window_x, window_y))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(100)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            pos = (pos[0] - self.offset[0], pos[1] - self.offset[1])
            self.handle_mouse_click(pos)
        return True

    def handle_mouse_click(self, pos):
        for arrow in self.arrows:
            if arrow.rect.collidepoint(pos):
                tile = arrow.tile
                tile.is_moving = True
                tile.current_direction = arrow.direction
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
                    self.game.board[i][j] is None for i in range(10) for j in range(10)
                ):
                    pygame.time.set_timer(self.ADD_TILE_EVENT, self.tile_timer_interval)
                    self.timer_running = True
                    self.tile_timer_start = pygame.time.get_ticks()
                return
        # Разрешаем выбор новой плитки даже когда другие движутся
        self.arrows.empty()
        self.game.select_tile(tile)
        self.draw_arrows_for_tile(tile)

    def spawn_score_animation(self, positions):
        """Создаёт анимацию очков от первой плитки ко второй."""
        delay_per_number = 100  # Задержка между появлением чисел (мс)
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
        arrow_grid_positions = []
        for direction in ["up", "down", "left", "right"]:
            if self.game.can_move(tile, direction):
                arrow_position = self.get_arrow_position(tile.rect.topleft, direction)
                self.arrows.add(Arrow(direction, arrow_position, self.game, tile))
                # Вычисляем grid позицию стрелки
                row, col = tile.position
                if direction == "up":
                    arrow_grid_positions.append((row - 1, col))
                elif direction == "down":
                    arrow_grid_positions.append((row + 1, col))
                elif direction == "left":
                    arrow_grid_positions.append((row, col - 1))
                elif direction == "right":
                    arrow_grid_positions.append((row, col + 1))
        # Удаляем popup-ы которые перекрываются стрелками
        self.remove_popups_at_positions(arrow_grid_positions)
        self.update_display()
        self.arrows.draw(self.tile_surface)

    def remove_popups_at_positions(self, grid_positions):
        """Удаляет анимации очков, находящиеся на указанных позициях."""
        for popup in list(self.score_popups):
            if popup.grid_position in grid_positions:
                popup.kill()

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
                    return other
        return None

    def move_tile(self, tile, direction):
        target_rect = tile.target_move(direction, self.game.board)
        dx = target_rect.topleft[0] - tile.rect.topleft[0]
        dy = target_rect.topleft[1] - tile.rect.topleft[1]
        if dx == 0:
            step_y = self.speed * (1 if dy > 0 else -1)
            tile.rect.y += step_y
        elif dy == 0:
            step_x = self.speed * (1 if dx > 0 else -1)
            tile.rect.x += step_x

        # Проверяем коллизию с другими движущимися плитками
        collided = self.check_collision(tile)
        if collided:
            self.resolve_collision(tile, collided)

        self.update_display()

    def resolve_collision(self, tile1, tile2):
        """Останавливает обе плитки при столкновении."""
        self.snap_to_grid(tile1)
        self.snap_to_grid(tile2)

    def snap_to_grid(self, tile):
        """Привязывает плитку к ближайшей ячейке сетки."""
        # Вычисляем ближайшую позицию на сетке
        grid_x = round((tile.rect.topleft[0] - self.gap) / (self.tile_size + self.gap))
        grid_y = round((tile.rect.topleft[1] - self.gap) / (self.tile_size + self.gap))

        # Ограничиваем в пределах поля
        grid_x = max(0, min(9, grid_x))
        grid_y = max(0, min(9, grid_y))

        # Если ячейка занята, ищем ближайшую свободную в направлении движения
        if self.game.board[grid_y][grid_x] is not None and self.game.board[grid_y][grid_x] != tile:
            # Откатываемся на предыдущую позицию
            grid_x, grid_y = tile.position[1], tile.position[0]

        # Устанавливаем новую позицию
        new_rect_x = (grid_x + 1) * self.gap + grid_x * self.tile_size
        new_rect_y = (grid_y + 1) * self.gap + grid_y * self.tile_size
        tile.rect.topleft = (new_rect_x, new_rect_y)

        # Финализируем движение
        self.finalize_move(tile)

    def finalize_move(self, tile):
        tile.is_moving = False
        tile.current_direction = None
        old_x, old_y = tile.position
        new_x = (tile.rect.topleft[1] - self.gap) // (self.tile_size + self.gap)
        new_y = (tile.rect.topleft[0] - self.gap) // (self.tile_size + self.gap)
        tile.position = (new_x, new_y)
        self.game.update_board((old_x, old_y), (new_x, new_y), tile)
        # Очищаем стрелки только если это была выбранная плитка
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

    def update_display(self):
        self.tile_surface.fill((249, 246, 247))
        self.tiles.draw(self.tile_surface)
        # Обновляем и рисуем анимацию очков (под стрелками)
        self.score_popups.update()
        for popup in self.score_popups:
            popup.draw(self.tile_surface)
        self.arrows.draw(self.tile_surface)  # Стрелки поверх всего
        self.draw_background()
        pygame.display.update()

    def run(self):
        running = True
        show_result = False
        prepare_to_show_result = False
        while running:
            # Очищаем и перерисовываем tile_surface каждый кадр
            self.tile_surface.fill((249, 246, 247))
            self.tiles.draw(self.tile_surface)
            # Обновляем и рисуем анимацию очков в каждом кадре
            self.score_popups.update()
            for popup in self.score_popups:
                popup.draw(self.tile_surface)
            # Рисуем стрелки поверх
            self.arrows.draw(self.tile_surface)
            self.draw_background()
            for tile in self.tiles:
                if tile.is_moving:
                    direction = tile.current_direction
                    if direction:
                        self.move_tile(tile, direction)
                        target_rect = tile.target_move(direction, self.game.board)
                        if tile.rect.topleft == target_rect.topleft:
                            self.finalize_move(tile)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == self.ADD_TILE_EVENT:
                    self.game.add_new_tile()
                    self.update_display()
                    empty = any(
                        self.game.board[i][j] is None
                        for i in range(10)
                        for j in range(10)
                    )
                    if not empty:
                        pygame.time.set_timer(self.ADD_TILE_EVENT, 0)
                        self.timer_running = False
                    else:
                        # Перезапускаем таймер для прогресс-бара
                        self.tile_timer_start = pygame.time.get_ticks()
                elif event.type == self.COUNTDOWN_EVENT:
                    self.game.handle_countdown()
                else:
                    running = self.handle_event(event)
            # Проверяем успешное завершение (все плитки убраны)
            if self.game.prepare_to_end:
                self.game.prepare_to_end = False
                prepare_to_show_result = True
            elif prepare_to_show_result:
                prepare_to_show_result = False
                show_result = True

            # Проверяем завершение по таймеру (время истекло)
            if self.game.game_over_flag:
                show_result = True

            if show_result and not any(tile.is_moving for tile in self.tiles):
                self.update_display()
                pygame.display.flip()
                self.show_result_window()
                running = False
