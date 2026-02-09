import pygame
import random
import mysql.connector
from datetime import datetime
import sys

# Конфигурация MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'tetris_db'
}

# Инициализация PyGame
pygame.init()

# Константы
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 300

# Цвета
BACKGROUND = (18, 18, 30)
PRIMARY = (0, 200, 220)
SECONDARY = (100, 80, 255)
ACCENT = (255, 100, 100)
TEXT_COLOR = (240, 240, 245)
DARK_CARD = (30, 30, 45)
LIGHT_CARD = (40, 40, 55)
GRID_BG = (25, 25, 35)

# Цвета фигур
COLORS = [
    (0, 240, 240),    # I
    (0, 120, 255),    # J
    (255, 160, 0),    # L
    (255, 230, 0),    # O
    (0, 230, 0),      # S
    (180, 0, 255),    # T
    (255, 50, 50)     # Z
]

# Фигуры Тетриса
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=(0, 180, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont('Arial', 28, bold=True)
        self.hovered = False
        
    def draw(self, surface):
        # Рисуем кнопку с скругленными углами
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=12)
        
        # Текст
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.hovered else self.color
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rotated = list(zip(*self.shape[::-1]))
        return [list(row) for row in rotated]

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Modern Tetris")
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.big_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.normal_font = pygame.font.SysFont('Arial', 28)
        self.small_font = pygame.font.SysFont('Arial', 22)
        
        # Состояния игры
        self.state = "menu"  # menu, enter_name, game, leaders
        self.reset_game()
        
    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.fall_time = 0
        self.player_name = ""
        
    def create_buttons(self):
        center_x = SCREEN_WIDTH // 2
        
        if self.state == "menu":
            self.buttons = [
                Button(center_x - 150, 350, 300, 60, "НАЧАТЬ ИГРУ"),
                Button(center_x - 150, 430, 300, 60, "ТАБЛИЦА ЛИДЕРОВ"),
                Button(center_x - 150, 510, 300, 60, "ВЫХОД", color=ACCENT)
            ]
        elif self.state == "enter_name":
            self.buttons = [
                Button(center_x - 100, 400, 200, 50, "СОХРАНИТЬ", color=SECONDARY)
            ]
        elif self.state == "game":
            self.buttons = [
                Button(SCREEN_WIDTH - SIDEBAR_WIDTH + 60, 550, 180, 50, "МЕНЮ", color=SECONDARY),
                Button(SCREEN_WIDTH - SIDEBAR_WIDTH + 60, 610, 180, 50, "РЕСТАРТ", color=ACCENT)
            ]
        elif self.state == "leaders":
            self.buttons = [
                Button(center_x - 100, 650, 200, 50, "НАЗАД")
            ]
    
    def draw_menu(self):
        # Фон
        self.screen.fill(BACKGROUND)
        
        # Анимированные фигуры на фоне
        self.draw_background_shapes()
        
        # Заголовок
        title = self.title_font.render("TETRIS", True, PRIMARY)
        title_shadow = self.title_font.render("TETRIS", True, (0, 150, 170))
        self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 4, 154))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        subtitle = self.normal_font.render("Modern Edition", True, TEXT_COLOR)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 230))
        
        # Кнопки
        for button in self.buttons:
            button.draw(self.screen)
            
        # Информация внизу
        info_text = self.small_font.render("Управление: ← → ↑ ↓, Пробел - сбросить, ESC - выход", True, (150, 150, 170))
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 680))
    
    def draw_background_shapes(self):
        # Рисуем случайные фигуры на фоне
        for i in range(15):
            shape_idx = random.randint(0, len(SHAPES) - 1)
            shape = SHAPES[shape_idx]
            color = (*COLORS[shape_idx], 30)  # Прозрачный цвет
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            
            for sy, row in enumerate(shape):
                for sx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(x + sx * 20, y + sy * 20, 18, 18)
                        pygame.draw.rect(self.screen, color[:3], rect)
    
    def draw_enter_name(self):
        self.screen.fill(BACKGROUND)
        
        # Заголовок
        title = self.big_font.render("ВВЕДИТЕ ВАШЕ ИМЯ", True, PRIMARY)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        # Поле ввода
        input_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 300, 400, 70)
        pygame.draw.rect(self.screen, DARK_CARD, input_rect, border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY, input_rect, 3, border_radius=15)
        
        # Текст имени
        name_text = self.normal_font.render(self.player_name + ("|" if pygame.time.get_ticks() % 1000 < 500 else ""), 
                                          True, TEXT_COLOR)
        self.screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, 325))
        
        # Кнопки
        for button in self.buttons:
            button.draw(self.screen)
            
        # Инструкция
        inst_text = self.small_font.render("Имя может содержать только буквы и цифры", True, (150, 150, 170))
        self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, 480))
    
    def draw_game(self):
        self.screen.fill(BACKGROUND)
        
        # Основной контейнер игры
        game_rect = pygame.Rect(40, 40, GRID_WIDTH * GRID_SIZE + 20, GRID_HEIGHT * GRID_SIZE + 20)
        pygame.draw.rect(self.screen, DARK_CARD, game_rect, border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY, game_rect, 3, border_radius=15)
        
        # Игровое поле
        self.draw_grid()
        
        # Боковая панель
        sidebar_rect = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH + 20, 40, 
                                 SIDEBAR_WIDTH - 40, GRID_HEIGHT * GRID_SIZE + 20)
        pygame.draw.rect(self.screen, DARK_CARD, sidebar_rect, border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY, sidebar_rect, 3, border_radius=15)
        
        # Статистика
        stats_y = 80
        stats = [
            ("ИГРОК:", self.player_name),
            ("СЧЕТ:", str(self.score)),
            ("УРОВЕНЬ:", str(self.level)),
            ("ЛИНИИ:", str(self.lines_cleared)),
            ("СКОРОСТЬ:", f"{self.fall_speed:.1f}")
        ]
        
        for i, (label, value) in enumerate(stats):
            label_text = self.small_font.render(label, True, (150, 150, 170))
            value_text = self.normal_font.render(value, True, TEXT_COLOR)
            self.screen.blit(label_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 60, stats_y + i * 55))
            self.screen.blit(value_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 60, stats_y + i * 55 + 25))
        
        # Следующая фигура - ПЕРЕМЕЩЕНА НИЖЕ
        next_text_y = stats_y + len(stats) * 55 + 20  # Добавляем отступ после статистики
        next_text = self.normal_font.render("СЛЕДУЮЩАЯ:", True, PRIMARY)
        self.screen.blit(next_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 60, next_text_y))
        
        # Рисуем следующую фигуру - ПЕРЕМЕЩЕНА ЕЩЕ НИЖЕ
        next_piece_y = next_text_y + 40  # Отступ после текста
        # Центрируем следующую фигуру
        shape_width = len(self.next_piece.shape[0]) * GRID_SIZE
        next_piece_x = SCREEN_WIDTH - SIDEBAR_WIDTH + 60 + (SIDEBAR_WIDTH - 120 - shape_width) // 2
        
        # Рисуем фон для следующей фигуры
        preview_bg_width = max(shape_width, 100) + 20
        preview_bg_height = len(self.next_piece.shape) * GRID_SIZE + 20
        preview_bg_rect = pygame.Rect(
            next_piece_x - 10, 
            next_piece_y - 10, 
            preview_bg_width, 
            preview_bg_height
        )
        pygame.draw.rect(self.screen, LIGHT_CARD, preview_bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, PRIMARY, preview_bg_rect, 2, border_radius=10)
        
        # Рисуем саму фигуру
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        next_piece_x + x * GRID_SIZE,
                        next_piece_y + y * GRID_SIZE,
                        GRID_SIZE - 2, 
                        GRID_SIZE - 2
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect, border_radius=4)
                    pygame.draw.rect(self.screen, TEXT_COLOR, rect, 1, border_radius=4)
        
        # Кнопки - ПЕРЕМЕЩЕНЫ ЕЩЕ НИЖЕ
        button_start_y = next_piece_y + preview_bg_height + 40
        self.buttons[0].rect.y = button_start_y
        self.buttons[1].rect.y = button_start_y + 70
        
        for button in self.buttons:
            button.draw(self.screen)
            
        # Игра окончена
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BACKGROUND)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА!", True, ACCENT)
            score_text = self.normal_font.render(f"Ваш счет: {self.score}", True, TEXT_COLOR)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 300))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 370))
    
    def draw_grid(self):
        # Фон сетки
        grid_bg = pygame.Rect(50, 50, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(self.screen, GRID_BG, grid_bg)
        
        # Заполненные клетки
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    color_idx = self.board[y][x] - 1
                    color = COLORS[color_idx]
                    rect = pygame.Rect(51 + x * GRID_SIZE, 51 + y * GRID_SIZE, 
                                     GRID_SIZE - 2, GRID_SIZE - 2)
                    pygame.draw.rect(self.screen, color, rect, border_radius=3)
                    pygame.draw.rect(self.screen, TEXT_COLOR, rect, 1, border_radius=3)
        
        # Текущая фигура
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(51 + (self.current_piece.x + x) * GRID_SIZE,
                                    51 + (self.current_piece.y + y) * GRID_SIZE,
                                    GRID_SIZE - 2, GRID_SIZE - 2)
                    pygame.draw.rect(self.screen, self.current_piece.color, rect, border_radius=3)
                    pygame.draw.rect(self.screen, TEXT_COLOR, rect, 1, border_radius=3)
        
        # Сетка
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, (40, 40, 55), 
                           (50 + x * GRID_SIZE, 50), 
                           (50 + x * GRID_SIZE, 50 + GRID_HEIGHT * GRID_SIZE), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, (40, 40, 55), 
                           (50, 50 + y * GRID_SIZE), 
                           (50 + GRID_WIDTH * GRID_SIZE, 50 + y * GRID_SIZE), 1)
    
    def draw_leaders(self):
        self.screen.fill(BACKGROUND)
        
        # Заголовок
        title = self.big_font.render("ТАБЛИЦА ЛИДЕРОВ", True, PRIMARY)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Получаем данные
        scores = self.get_high_scores()
        
        # Контейнер таблицы
        table_rect = pygame.Rect(100, 150, SCREEN_WIDTH - 200, 450)
        pygame.draw.rect(self.screen, DARK_CARD, table_rect, border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY, table_rect, 3, border_radius=15)
        
        # Заголовки колонок
        headers = ["МЕСТО", "ИМЯ", "СЧЕТ", "УРОВЕНЬ", "ЛИНИИ", "ДАТА"]
        header_y = 180
        col_width = (SCREEN_WIDTH - 200) // len(headers)
        
        for i, header in enumerate(headers):
            header_text = self.small_font.render(header, True, PRIMARY)
            x = 100 + i * col_width + col_width // 2 - header_text.get_width() // 2
            self.screen.blit(header_text, (x, header_y))
        
        # Разделитель
        pygame.draw.line(self.screen, PRIMARY, (100, 210), (SCREEN_WIDTH - 100, 210), 2)
        
        # Данные игроков
        if scores:
            for idx, score in enumerate(scores[:10]):
                row_y = 230 + idx * 40
                
                # Цвет строки
                row_color = TEXT_COLOR if idx % 2 == 0 else (200, 200, 220)
                
                # Место
                place_text = self.small_font.render(str(idx + 1), True, 
                                                  PRIMARY if idx < 3 else row_color)
                self.screen.blit(place_text, (120, row_y))
                
                # Имя
                name_text = self.small_font.render(score[1][:15], True, row_color)
                self.screen.blit(name_text, (100 + col_width, row_y))
                
                # Счет
                score_text = self.small_font.render(str(score[2]), True, row_color)
                self.screen.blit(score_text, (100 + col_width * 2, row_y))
                
                # Уровень
                level_text = self.small_font.render(str(score[3]), True, row_color)
                self.screen.blit(level_text, (100 + col_width * 3, row_y))
                
                # Линии
                lines_text = self.small_font.render(str(score[4]), True, row_color)
                self.screen.blit(lines_text, (100 + col_width * 4, row_y))
                
                # Дата
                date = score[5].strftime("%d.%m.%Y") if isinstance(score[5], datetime) else str(score[5])
                date_text = self.small_font.render(date, True, row_color)
                self.screen.blit(date_text, (100 + col_width * 5, row_y))
        else:
            no_data = self.normal_font.render("Нет данных о рекордах", True, (150, 150, 170))
            self.screen.blit(no_data, (SCREEN_WIDTH//2 - no_data.get_width()//2, 300))
        
        # Кнопки
        for button in self.buttons:
            button.draw(self.screen)
    
    def check_collision(self, shape, x, y):
        for shape_y, row in enumerate(shape):
            for shape_x, cell in enumerate(row):
                if cell:
                    if (x + shape_x < 0 or x + shape_x >= GRID_WIDTH or
                        y + shape_y >= GRID_HEIGHT or
                        (y + shape_y >= 0 and self.board[y + shape_y][x + shape_x])):
                        return True
        return False
    
    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + y >= 0:
                        self.board[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.shape_idx + 1
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        for line in lines_to_clear:
            del self.board[line]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (1, 2, 5, 10)[min(len(lines_to_clear) - 1, 3)] * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)
    
    def save_score(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = "INSERT INTO scores (player_name, score, level, lines_cleared) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (self.player_name, self.score, self.level, self.lines_cleared))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def get_high_scores(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scores ORDER BY score DESC LIMIT 10")
            scores = cursor.fetchall()
            conn.close()
            return scores
        except Exception as e:
            print(f"Ошибка загрузки рекордов: {e}")
            return []
    
    def run(self):
        running = True
        last_time = pygame.time.get_ticks()
        self.create_buttons()
        
        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # Получаем позицию мыши
            mouse_pos = pygame.mouse.get_pos()
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Проверка нажатия кнопок
                for button in self.buttons:
                    if button.check_hover(mouse_pos):
                        if button.is_clicked(mouse_pos, event):
                            # Обработка кнопок меню
                            if self.state == "menu":
                                if button.text == "НАЧАТЬ ИГРУ":
                                    self.state = "enter_name"
                                    self.create_buttons()
                                elif button.text == "ТАБЛИЦА ЛИДЕРОВ":
                                    self.state = "leaders"
                                    self.create_buttons()
                                elif button.text == "ВЫХОД":
                                    running = False
                            
                            # Обработка кнопок ввода имени
                            elif self.state == "enter_name":
                                if button.text == "СОХРАНИТЬ" and self.player_name:
                                    self.state = "game"
                                    self.create_buttons()
                            
                            # Обработка кнопок игры
                            elif self.state == "game":
                                if button.text == "МЕНЮ":
                                    if self.game_over:
                                        self.save_score()
                                    self.state = "menu"
                                    self.reset_game()
                                    self.create_buttons()
                                elif button.text == "РЕСТАРТ":
                                    if self.game_over:
                                        self.save_score()
                                    self.reset_game()
                            
                            # Обработка кнопок таблицы лидеров
                            elif self.state == "leaders":
                                if button.text == "НАЗАД":
                                    self.state = "menu"
                                    self.create_buttons()
                
                # Обработка клавиатуры
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "game":
                            if self.game_over:
                                self.save_score()
                            self.state = "menu"
                            self.reset_game()
                            self.create_buttons()
                        elif self.state in ["enter_name", "leaders"]:
                            self.state = "menu"
                            self.create_buttons()
                    
                    # Ввод имени
                    if self.state == "enter_name":
                        if event.key == pygame.K_RETURN and self.player_name:
                            self.state = "game"
                            self.create_buttons()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif len(self.player_name) < 15 and event.unicode.isalnum():
                            self.player_name += event.unicode
                    
                    # Управление игрой
                    elif self.state == "game" and not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if not self.check_collision(self.current_piece.shape, 
                                                       self.current_piece.x - 1, 
                                                       self.current_piece.y):
                                self.current_piece.x -= 1
                        
                        elif event.key == pygame.K_RIGHT:
                            if not self.check_collision(self.current_piece.shape, 
                                                       self.current_piece.x + 1, 
                                                       self.current_piece.y):
                                self.current_piece.x += 1
                        
                        elif event.key == pygame.K_DOWN:
                            if not self.check_collision(self.current_piece.shape, 
                                                       self.current_piece.x, 
                                                       self.current_piece.y + 1):
                                self.current_piece.y += 1
                        
                        elif event.key == pygame.K_UP:
                            rotated = self.current_piece.rotate()
                            if not self.check_collision(rotated, 
                                                       self.current_piece.x, 
                                                       self.current_piece.y):
                                self.current_piece.shape = rotated
                        
                        elif event.key == pygame.K_SPACE:
                            while not self.check_collision(self.current_piece.shape, 
                                                          self.current_piece.x, 
                                                          self.current_piece.y + 1):
                                self.current_piece.y += 1
            
            # Логика игры
            if self.state == "game" and not self.game_over:
                self.fall_time += delta_time
                
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    
                    if not self.check_collision(self.current_piece.shape, 
                                              self.current_piece.x, 
                                              self.current_piece.y + 1):
                        self.current_piece.y += 1
                    else:
                        self.merge_piece()
                        self.clear_lines()
                        
                        self.current_piece = self.next_piece
                        self.next_piece = Tetromino()
                        
                        if self.check_collision(self.current_piece.shape, 
                                              self.current_piece.x, 
                                              self.current_piece.y):
                            self.game_over = True
            
            # Отрисовка
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "enter_name":
                self.draw_enter_name()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "leaders":
                self.draw_leaders()
            
            # Обновление hover состояния кнопок
            for button in self.buttons:
                button.check_hover(mouse_pos)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()