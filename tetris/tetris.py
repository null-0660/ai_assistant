# Тетрис — v2: движение и поворот

WIDTH = 10
HEIGHT = 20

SHAPES = {
    'I': [(0,0), (1,0), (2,0), (3,0)],
    'O': [(0,0), (1,0), (0,1), (1,1)],
    'T': [(0,0), (1,0), (2,0), (1,1)],
    'S': [(1,0), (2,0), (0,1), (1,1)],
    'Z': [(0,0), (1,0), (1,1), (2,1)],
    'L': [(0,0), (0,1), (0,2), (1,2)],
    'J': [(1,0), (1,1), (1,2), (0,2)],
}


class Tetris:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.board = [[0] * self.width for _ in range(self.height)]
        self.piece = 'T'
        self.piece_x = 4
        self.piece_y = 0
        self.score = 0
        self.game_over = False

    def build_field(self):
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c]:
                    field[r][c] = '█'
        for (dx, dy) in SHAPES[self.piece]:
            x = self.piece_x + dx
            y = self.piece_y + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = '▓'
        return field

    def print_field(self):
        field = self.build_field()
        print("\n" + "=" * (self.width + 2))
        print(f"Счёт: {self.score}   Фигура: {self.piece}")
        print("=" * (self.width + 2))
        for row in field:
            print('|' + ''.join(row) + '|')
        print("=" * (self.width + 2))
        print("a — влево, d — вправо, s — вниз, w — поворот, q — выход")

    def can_place(self, px, py, shape_name=None):
        """Проверяет, можно ли поставить фигуру в (px, py)."""
        shape = SHAPES[shape_name or self.piece]
        for (dx, dy) in shape:
            x = px + dx
            y = py + dy
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def move(self, dx, dy):
        """Пробует сдвинуть фигуру."""
        if self.can_place(self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def rotate(self):
        """Поворот фигуры на 90° вокруг центра."""
        shape = SHAPES[self.piece]
        if self.piece == 'O':
            return
        rotated = [(-dy, dx) for (dx, dy) in shape]
        # Нормализуем: минимальный x,y = 0
        min_x = min(x for x, y in rotated)
        min_y = min(y for x, y in rotated)
        rotated = [(x - min_x, y - min_y) for (x, y) in rotated]

        # Пробуем поставить повёрнутую
        for (dx, dy) in rotated:
            x = self.piece_x + dx
            y = self.piece_y + dy
            if x < 0 or x >= self.width or y >= self.height:
                return
            if y >= 0 and self.board[y][x]:
                return

        SHAPES[self.piece] = rotated

    def step(self, command):
        if command == 'a':
            self.move(-1, 0)
        elif command == 'd':
            self.move(1, 0)
        elif command == 's':
            if not self.move(0, 1):
                pass  # в будущем — фиксация
        elif command == 'w':
            self.rotate()
        elif command == 'q':
            self.game_over = True

    def play(self):
        while not self.game_over:
            self.print_field()
            command = input("Ход (a/d/s/w/q): ").strip().lower()
            self.step(command)


if __name__ == '__main__':
    game = Tetris()
    game.play()