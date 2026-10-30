# Арканоид — v1: класс и поле

WIDTH = 20
HEIGHT = 15
PADDLE_WIDTH = 4


class Arkanoid:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT

        # Платформа: позиция левого края
        self.paddle_x = (self.width - PADDLE_WIDTH) // 2

        # Мяч: позиция и скорость
        self.ball_x = self.width // 2
        self.ball_y = self.height - 3
        self.ball_dx = 1
        self.ball_dy = -1

        # Блоки: список (x, y)
        self.blocks = []
        for row in range(3):
            for col in range(self.width):
                if col % 2 == 0:
                    self.blocks.append((col, row + 1))

        self.score = 0

    def build_field(self):
        """Собирает поле в список строк."""
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Верхняя и нижняя граница
        for c in range(self.width):
            field[0][c] = '-'
            field[self.height - 1][c] = '-'

        # Блоки
        for (x, y) in self.blocks:
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = '█'

        # Платформа
        for i in range(PADDLE_WIDTH):
            px = self.paddle_x + i
            if 0 <= px < self.width:
                field[self.height - 2][px] = '='

        # Мяч
        if 0 <= self.ball_x < self.width and 0 <= self.ball_y < self.height:
            field[self.ball_y][self.ball_x] = 'o'

        return field

    def print_field(self):
        """Печатает поле в консоль."""
        field = self.build_field()

        print("\n" + "=" * (self.width + 2))
        print(f"Счёт: {self.score}   Блоков: {len(self.blocks)}")
        print("=" * (self.width + 2))

        for row in field:
            print('|' + ''.join(row) + '|')

        print("=" * (self.width + 2))
        print("a — влево, d — вправо, q — выход")


if __name__ == '__main__':
    game = Arkanoid()
    game.print_field()