# Арканоид — v3: уровни, жизни, бонусы, рекорд

import time
import random
import os

WIDTH = 20
HEIGHT = 15
PADDLE_WIDTH = 4
DEFAULT_PADDLE = 4
WIDE_PADDLE = 6

BONUS_LIFE = '♥'
BONUS_WIDE = 'W'


class Arkanoid:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.paddle_width = DEFAULT_PADDLE
        self.paddle_x = (self.width - self.paddle_width) // 2
        self.ball_x = self.width // 2
        self.ball_y = self.height - 3
        self.ball_dx = 1
        self.ball_dy = -1
        self.level = 1
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.win = False
        self.bonuses = []   # список (x, y, тип)
        self.blocks = self.load_level(1)

    def load_level(self, level):
        """Загружает раскладку блоков для уровня."""
        blocks = []
        if level == 1:
            for row in range(3):
                for col in range(self.width):
                    if col % 2 == 0:
                        blocks.append((col, row + 1))
        elif level == 2:
            for row in range(4):
                for col in range(self.width):
                    if row % 2 == 0 or col % 2 == 1:
                        blocks.append((col, row + 1))
        else:  # level 3
            for row in range(5):
                for col in range(2, self.width - 2):
                    if abs(col - self.width // 2) <= 3 - row:
                        blocks.append((col, row + 1))
        return blocks

    def reset_ball(self):
        """Сбрасывает мяч после потери жизни."""
        self.ball_x = self.paddle_x + self.paddle_width // 2
        self.ball_y = self.height - 3
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = -1
        self.paddle_width = DEFAULT_PADDLE
        self.paddle_x = (self.width - self.paddle_width) // 2

    def build_field(self):
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for c in range(self.width):
            field[0][c] = '-'
            field[self.height - 1][c] = '-'
        for (x, y) in self.blocks:
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = '█'
        for (x, y, kind) in self.bonuses:
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = kind
        for i in range(self.paddle_width):
            px = self.paddle_x + i
            if 0 <= px < self.width:
                field[self.height - 2][px] = '='
        if 0 <= self.ball_x < self.width and 0 <= self.ball_y < self.height:
            field[self.ball_y][self.ball_x] = 'o'
        return field

    def print_field(self):
        field = self.build_field()
        print("\n" + "=" * (self.width + 2))
        print(f"Уровень: {self.level}  Счёт: {self.score}  Жизни: {self.lives}  Блоков: {len(self.blocks)}")
        print("=" * (self.width + 2))
        for row in field:
            print('|' + ''.join(row) + '|')
        print("=" * (self.width + 2))
        print("a — влево, d — вправо, q — выход")

    def move_paddle(self, direction):
        new_x = self.paddle_x + direction
        if 0 <= new_x <= self.width - self.paddle_width:
            self.paddle_x = new_x

    def move_ball(self):
        nx = self.ball_x + self.ball_dx
        ny = self.ball_y + self.ball_dy

        if nx < 0 or nx >= self.width:
            self.ball_dx *= -1
            nx = self.ball_x + self.ball_dx

        if ny < 1:
            self.ball_dy *= -1
            ny = self.ball_y + self.ball_dy

        # Столкновение с блоком
        if (nx, ny) in self.blocks:
            self.blocks.remove((nx, ny))
            self.score += 10
            # Бонус с шансом 20%
            if random.random() < 0.2:
                kind = random.choice([BONUS_LIFE, BONUS_WIDE])
                self.bonuses.append((nx, ny, kind))
            self.ball_dy *= -1
            ny = self.ball_y + self.ball_dy

        # Бонус ловим платформой
        for (bx, by, kind) in list(self.bonuses):
            if by == self.height - 2 and self.paddle_x <= bx < self.paddle_x + self.paddle_width:
                self.bonuses.remove((bx, by, kind))
                if kind == BONUS_LIFE:
                    self.lives += 1
                elif kind == BONUS_WIDE:
                    self.paddle_width = WIDE_PADDLE

        # Бонусы падают вниз
        for (bx, by, kind) in list(self.bonuses):
            if by < self.height - 3:
                self.bonuses.remove((bx, by, kind))
                self.bonuses.append((bx, by + 1, kind))

        # Столкновение с платформой
        if ny == self.height - 2:
            if self.paddle_x <= nx < self.paddle_x + self.paddle_width:
                self.ball_dy *= -1
                ny = self.ball_y + self.ball_dy

        # Мяч упал
        if ny >= self.height - 1:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.reset_ball()
            return

        self.ball_x = nx
        self.ball_y = ny

        # Уровень пройден
        if not self.blocks:
            if self.level < 3:
                self.level += 1
                self.blocks = self.load_level(self.level)
                self.reset_ball()
            else:
                self.win = True
                self.game_over = True

    def step(self, command):
        if command == 'a':
            self.move_paddle(-1)
        elif command == 'd':
            self.move_paddle(1)
        elif command == 'q':
            self.game_over = True
            return
        self.move_ball()

    def play(self):
        print("🎮 АРКАНОИД")
        print("Управление: a — влево, d — вправо, q — выход")
        print("Бонусы: ♥ — жизнь, W — широкая платформа")

        while not self.game_over:
            self.print_field()
            command = input("Твой ход (a/d/q): ").strip().lower()
            self.step(command)
            time.sleep(0.05)

        self.print_field()

        # Рекорд
        high = 0
        path = os.path.join(os.path.dirname(__file__), 'highscore.txt')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    high = int(f.read().strip())
            except:
                high = 0

        if self.score > high:
            high = self.score
            with open(path, 'w') as f:
                f.write(str(high))
            print(f"🏆 НОВЫЙ РЕКОРД: {self.score}!")

        print(f"Рекорд: {high}")
        if self.win:
            print("🏆 ПОБЕДА! Все уровни пройдены!")
        else:
            print(f"💀 Игра окончена. Счёт: {self.score}")


if __name__ == '__main__':
    game = Arkanoid()
    game.play()