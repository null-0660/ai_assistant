# Змейка — v3: скорость, уровни, рекорд

import random
import time
import os

WIDTH = 20
HEIGHT = 15


class Snake:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.level = 1
        self.base_delay = 0.15   # начальная задержка
        self.snake = [(5, 7), (4, 7), (3, 7)]
        self.direction = 'right'
        self.food = self.random_food()
        self.score = 0
        self.game_over = False

    def delay(self):
        """Задержка уменьшается с ростом счёта."""
        return max(0.03, self.base_delay - self.score * 0.002)

    def random_food(self):
        free = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (x, y) not in self.snake:
                    free.append((x, y))
        return random.choice(free) if free else (1, 1)

    def build_field(self):
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for c in range(self.width):
            field[0][c] = '-'
            field[self.height - 1][c] = '-'
        for r in range(self.height):
            field[r][0] = '|'
            field[r][self.width - 1] = '|'
        fx, fy = self.food
        if 0 <= fx < self.width and 0 <= fy < self.height:
            field[fy][fx] = '*'
        for i, (x, y) in enumerate(self.snake):
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = '@' if i == 0 else 'o'
        return field

    def print_field(self):
        field = self.build_field()
        print("\n" + "=" * (self.width + 2))
        print(f"Уровень: {self.level}   Счёт: {self.score}   Длина: {len(self.snake)}")
        print("=" * (self.width + 2))
        for row in field:
            print(''.join(row))
        print("=" * (self.width + 2))
        print("w — вверх, s — вниз, a — влево, d — вправо, q — выход")

    def move(self):
        dx, dy = 0, 0
        if self.direction == 'right': dx = 1
        elif self.direction == 'left': dx = -1
        elif self.direction == 'up': dy = -1
        elif self.direction == 'down': dy = 1

        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
                new_head[1] <= 0 or new_head[1] >= self.height - 1):
            self.game_over = True
            return
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            # Новый уровень каждые 50 очков
            if self.score >= self.level * 50 and self.level < 3:
                self.level += 1
                self.base_delay = max(0.05, self.base_delay - 0.03)
            self.food = self.random_food()
        else:
            self.snake.pop()

    def change_direction(self, command):
        opposites = {
            'w': 'down', 's': 'up', 'a': 'right', 'd': 'left',
        }
        new_dir = {'w': 'up', 's': 'down', 'a': 'left', 'd': 'right'}.get(command)
        if new_dir and new_dir != opposites.get(self.direction):
            self.direction = new_dir

    def save_highscore(self):
        path = os.path.join(os.path.dirname(__file__), 'highscore.txt')
        high = 0
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
            return high, True
        return high, False

    def play(self):
        while not self.game_over:
            self.print_field()
            command = input("Ход (wasd/q): ").strip().lower()
            if command == 'q':
                break
            self.change_direction(command)
            self.move()
            time.sleep(self.delay())

        self.print_field()
        high, is_new = self.save_highscore()
        if is_new:
            print(f"🏆 НОВЫЙ РЕКОРД: {self.score}!")
        print(f"Рекорд: {high}")
        print(f"💀 Игра окончена. Счёт: {self.score}")


if __name__ == '__main__':
    game = Snake()
    game.play()