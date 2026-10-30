# Арканоид — v2: движение и отскоки

import time

WIDTH = 20
HEIGHT = 15
PADDLE_WIDTH = 4


class Arkanoid:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.paddle_x = (self.width - PADDLE_WIDTH) // 2
        self.ball_x = self.width // 2
        self.ball_y = self.height - 3
        self.ball_dx = 1
        self.ball_dy = -1
        self.blocks = []
        for row in range(3):
            for col in range(self.width):
                if col % 2 == 0:
                    self.blocks.append((col, row + 1))
        self.score = 0
        self.game_over = False
        self.win = False

    def build_field(self):
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for c in range(self.width):
            field[0][c] = '-'
            field[self.height - 1][c] = '-'
        for (x, y) in self.blocks:
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = '█'
        for i in range(PADDLE_WIDTH):
            px = self.paddle_x + i
            if 0 <= px < self.width:
                field[self.height - 2][px] = '='
        if 0 <= self.ball_x < self.width and 0 <= self.ball_y < self.height:
            field[self.ball_y][self.ball_x] = 'o'
        return field

    def print_field(self):
        field = self.build_field()
        print("\n" + "=" * (self.width + 2))
        print(f"Счёт: {self.score}   Блоков: {len(self.blocks)}")
        print("=" * (self.width + 2))
        for row in field:
            print('|' + ''.join(row) + '|')
        print("=" * (self.width + 2))
        print("a — влево, d — вправо, q — выход")

    def move_paddle(self, direction):
        """direction = -1 (влево) или +1 (вправо)."""
        new_x = self.paddle_x + direction
        if 0 <= new_x <= self.width - PADDLE_WIDTH:
            self.paddle_x = new_x

    def move_ball(self):
        """Двигает мяч, обрабатывает отскоки и столкновения."""
        # Следующая позиция
        nx = self.ball_x + self.ball_dx
        ny = self.ball_y + self.ball_dy

        # Отскок от левой/правой стены
        if nx < 0 or nx >= self.width:
            self.ball_dx *= -1
            nx = self.ball_x + self.ball_dx

        # Отскок от верхней стены
        if ny < 1:
            self.ball_dy *= -1
            ny = self.ball_y + self.ball_dy

        # Столкновение с блоком
        if (nx, ny) in self.blocks:
            self.blocks.remove((nx, ny))
            self.score += 10
            self.ball_dy *= -1
            ny = self.ball_y + self.ball_dy

        # Столкновение с платформой
        if ny == self.height - 2:
            if self.paddle_x <= nx < self.paddle_x + PADDLE_WIDTH:
                self.ball_dy *= -1
                ny = self.ball_y + self.ball_dy

        # Мяч упал вниз
        if ny >= self.height - 1:
            self.game_over = True
            return

        self.ball_x = nx
        self.ball_y = ny

        # Победа
        if not self.blocks:
            self.win = True
            self.game_over = True

    def step(self, command):
        """Один шаг игры: команда + движение мяча."""
        if command == 'a':
            self.move_paddle(-1)
        elif command == 'd':
            self.move_paddle(1)
        elif command == 'q':
            self.game_over = True
            return

        self.move_ball()

    def play(self):
        while not self.game_over:
            self.print_field()
            command = input("Твой ход (a/d/q): ").strip().lower()
            self.step(command)
            time.sleep(0.05)

        self.print_field()
        if self.win:
            print("🏆 ПОБЕДА! Все блоки сбиты.")
        else:
            print("💀 Игра окончена. Мяч упал.")


if __name__ == '__main__':
    game = Arkanoid()
    game.play()