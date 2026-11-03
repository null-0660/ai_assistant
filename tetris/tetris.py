# Тетрис — v4: цвета, ввод без Enter, пауза, рекорд

import random
import time
import os
import sys

RESET = '\033[0m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BOLD = '\033[1m'
DIM = '\033[2m'

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

COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'L': BLUE,
    'J': MAGENTA,
}


def get_key():
    if sys.platform == 'win32':
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore').lower()
    else:
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.lower()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


class Tetris:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.board = [[0] * self.width for _ in range(self.height)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.fall_counter = 0
        self.fall_speed = 3
        self.spawn_piece()

    def spawn_piece(self):
        self.piece = random.choice(list(SHAPES.keys()))
        self.piece_x = self.width // 2 - 2
        self.piece_y = 0
        if not self.can_place(self.piece_x, self.piece_y):
            self.game_over = True

    def can_place(self, px, py, shape_name=None):
        shape = SHAPES[shape_name or self.piece]
        for (dx, dy) in shape:
            x = px + dx
            y = py + dy
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def build_field(self):
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c]:
                    field[r][c] = f"{DIM}█{RESET}"

        color = COLORS.get(self.piece, CYAN)
        for (dx, dy) in SHAPES[self.piece]:
            x = self.piece_x + dx
            y = self.piece_y + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = f"{color}▓{RESET}"
        return field

    def print_field(self):
        field = self.build_field()
        print()
        print(f"{CYAN}{BOLD}╔{'═' * (self.width + 2)}╗{RESET}")
        print(f"{CYAN}║{RESET} {YELLOW}Счёт:{RESET} {BOLD}{self.score}{RESET}   "
              f"{GREEN}Линии:{RESET} {BOLD}{self.lines}{RESET}   "
              f"{MAGENTA}Фигура:{RESET} {BOLD}{COLORS.get(self.piece, '')}{self.piece}{RESET}  "
              f"{CYAN}║{RESET}")
        print(f"{CYAN}{BOLD}╠{'═' * (self.width + 2)}╣{RESET}")
        for row in field:
            print(f"{CYAN}║{RESET}" + ''.join(row) + f"{CYAN}║{RESET}")
        print(f"{CYAN}{BOLD}╚{'═' * (self.width + 2)}╝{RESET}")
        print(f"{DIM}a — влево, d — вправо, s — вниз, w — поворот, p — пауза, q — выход{RESET}")
        if self.paused:
            print(f"{YELLOW}{BOLD}⏸  ПАУЗА. Нажми p чтобы продолжить.{RESET}")

    def move(self, dx, dy):
        if self.can_place(self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def rotate(self):
        if self.piece == 'O':
            return
        shape = SHAPES[self.piece]
        rotated = [(-dy, dx) for (dx, dy) in shape]
        min_x = min(x for x, y in rotated)
        min_y = min(y for x, y in rotated)
        rotated = [(x - min_x, y - min_y) for (x, y) in rotated]
        for (dx, dy) in rotated:
            x = self.piece_x + dx
            y = self.piece_y + dy
            if x < 0 or x >= self.width or y >= self.height:
                return
            if y >= 0 and self.board[y][x]:
                return
        SHAPES[self.piece] = rotated

    def lock_piece(self):
        for (dx, dy) in SHAPES[self.piece]:
            x = self.piece_x + dx
            y = self.piece_y + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.board[y][x] = 1
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_board = []
        cleared = 0
        for row in self.board:
            if all(row):
                cleared += 1
            else:
                new_board.append(row)
        while len(new_board) < self.height:
            new_board.insert(0, [0] * self.width)
        self.board = new_board
        if cleared:
            self.lines += cleared
            self.score += cleared * 100

    def gravity(self):
        if not self.move(0, 1):
            self.lock_piece()

    def step(self, command):
        if command == 'p':
            self.paused = not self.paused
            return
        if self.paused:
            return

        if command == 'a':
            self.move(-1, 0)
        elif command == 'd':
            self.move(1, 0)
        elif command == 's':
            if not self.move(0, 1):
                self.lock_piece()
                return
        elif command == 'w':
            self.rotate()
        elif command == 'q':
            self.game_over = True
            return

        self.fall_counter += 1
        if self.fall_counter >= self.fall_speed:
            self.fall_counter = 0
            self.gravity()

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
        clear_screen()
        print(f"{CYAN}{BOLD}🧱 ТЕТРИС{RESET}")
        print(f"{YELLOW}Управление:{RESET} a/d/s/w, p — пауза, q — выход")
        print()
        input(f"{DIM}Нажми Enter чтобы начать...{RESET}")

        while not self.game_over:
            clear_screen()
            self.print_field()
            key = get_key()
            self.step(key)
            time.sleep(0.05)

        clear_screen()
        self.print_field()
        high, is_new = self.save_highscore()
        if is_new:
            print(f"{YELLOW}{BOLD}🏆 НОВЫЙ РЕКОРД: {self.score}!{RESET}")
        print(f"{CYAN}Рекорд: {high}{RESET}")
        print(f"{RED}{BOLD}💀 Игра окончена. Счёт: {self.score}{RESET}")


if __name__ == '__main__':
    game = Tetris()
    game.play()