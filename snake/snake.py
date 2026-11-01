# Змейка — v2: движение и рост

import random
import time

WIDTH = 20
HEIGHT = 15


class Snake:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.snake = [(5, 7), (4, 7), (3, 7)]
        self.direction = 'right'
        self.food = self.random_food()
        self.score = 0
        self.game_over = False

    def random_food(self):
        """Случайная свободная клетка внутри поля."""
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
        print(f"Счёт: {self.score}   Длина: {len(self.snake)}")
        print("=" * (self.width + 2))
        for row in field:
            print(''.join(row))
        print("=" * (self.width + 2))
        print("w — вверх, s — вниз, a — влево, d — вправо, q — выход")

    def move(self):
        """Один шаг змейки."""
        dx, dy = 0, 0
        if self.direction == 'right': dx = 1
        elif self.direction == 'left': dx = -1
        elif self.direction == 'up': dy = -1
        elif self.direction == 'down': dy = 1

        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        # Стена
        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
                new_head[1] <= 0 or new_head[1] >= self.height - 1):
            self.game_over = True
            return

        # Своё тело
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Поедание еды
        if new_head == self.food:
            self.score += 10
            self.food = self.random_food()
        else:
            self.snake.pop()   # убираем хвост, если не выросла

    def change_direction(self, command):
        opposites = {
            'w': 'down', 's': 'up', 'a': 'right', 'd': 'left',
            'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left',
        }
        new_dir = {
            'w': 'up', 's': 'down', 'a': 'left', 'd': 'right',
        }.get(command)

        if new_dir and new_dir != opposites.get(self.direction):
            self.direction = new_dir

    def play(self):
        while not self.game_over:
            self.print_field()
            command = input("Ход (wasd/q): ").strip().lower()
            if command == 'q':
                break
            self.change_direction(command)
            self.move()
            time.sleep(0.1)

        self.print_field()
        print(f"💀 Игра окончена. Счёт: {self.score}")


if __name__ == '__main__':
    game = Snake()
    game.play()