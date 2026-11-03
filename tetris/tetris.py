# Тетрис — v1: класс, поле, одна фигура

WIDTH = 10
HEIGHT = 20


# Фигуры: список координат (x, y) относительно центра
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

        # Стакан: 0 — пусто, 1 — занято
        self.board = [[0] * self.width for _ in range(self.height)]

        # Текущая фигура
        self.piece = 'T'
        self.piece_x = 4
        self.piece_y = 0

        self.score = 0
        self.game_over = False

    def build_field(self):
        """Собирает поле с фигурой в 2D-список символов."""
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Занятые клетки
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c]:
                    field[r][c] = '█'

        # Текущая фигура
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


if __name__ == '__main__':
    game = Tetris()
    game.print_field()