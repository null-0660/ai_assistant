# Змейка — v1: класс и поле

WIDTH = 20
HEIGHT = 15


class Snake:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT

        # Змейка: список (x, y), голова — первый элемент
        self.snake = [(5, 7), (4, 7), (3, 7)]
        self.direction = 'right'   # right / left / up / down

        # Еда
        self.food = (15, 7)

        # Счёт
        self.score = 0
        self.game_over = False

    def build_field(self):
        """Собирает поле в 2D-список символов."""
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Границы
        for c in range(self.width):
            field[0][c] = '-'
            field[self.height - 1][c] = '-'
        for r in range(self.height):
            field[r][0] = '|'
            field[r][self.width - 1] = '|'

        # Еда
        fx, fy = self.food
        if 0 <= fx < self.width and 0 <= fy < self.height:
            field[fy][fx] = '*'

        # Змейка
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


if __name__ == '__main__':
    game = Snake()
    game.print_field()