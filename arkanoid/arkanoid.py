# Арканоид — v4: цветная консоль, удобное управление

import time
import random
import os
import sys


# ===== Цвета ANSI =====
RESET = '\033[0m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
DIM = '\033[2m'

# ===== Константы =====
WIDTH = 20
HEIGHT = 15
PADDLE_WIDTH = 4
DEFAULT_PADDLE = 4
WIDE_PADDLE = 6

BONUS_LIFE = '♥'
BONUS_WIDE = 'W'


# ===== Ввод без Enter =====
def get_key():
    """Читает одну клавишу без Enter (Windows / Linux/macOS)."""
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
    """Очищает экран."""
    os.system('cls' if os.name == 'nt' else 'clear')


# ===== Игра =====
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
        self.paused = False
        self.bonuses = []
        self.blocks = self.load_level(1)

    def load_level(self, level):
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
        else:
            for row in range(5):
                for col in range(2, self.width - 2):
                    if abs(col - self.width // 2) <= 3 - row:
                        blocks.append((col, row + 1))
        return blocks

    def reset_ball(self):
        self.ball_x = self.paddle_x + self.paddle_width // 2
        self.ball_y = self.height - 3
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = -1
        self.paddle_width = DEFAULT_PADDLE
        self.paddle_x = (self.width - self.paddle_width) // 2

    def build_field(self):
        """Собирает поле из цветных символов."""
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Верхняя/нижняя граница
        for c in range(self.width):
            field[0][c] = f"{CYAN}-{RESET}"
            field[self.height - 1][c] = f"{CYAN}-{RESET}"

        # Блоки
        for (x, y) in self.blocks:
            if 0 <= x < self.width and 0 <= y < self.height:
                field[y][x] = f"{RED}█{RESET}"

        # Бонусы
        for (x, y, kind) in self.bonuses:
            if 0 <= x < self.width and 0 <= y < self.height:
                if kind == BONUS_LIFE:
                    field[y][x] = f"{MAGENTA}♥{RESET}"
                else:
                    field[y][x] = f"{BLUE}W{RESET}"

        # Платформа
        for i in range(self.paddle_width):
            px = self.paddle_x + i
            if 0 <= px < self.width:
                field[self.height - 2][px] = f"{GREEN}={RESET}"

        # Мяч
        if 0 <= self.ball_x < self.width and 0 <= self.ball_y < self.height:
            field[self.ball_y][self.ball_x] = f"{YELLOW}o{RESET}"

        return field

    def print_field(self):
        """Красивый цветной вывод."""
        field = self.build_field()

        # HUD
        print()
        print(f"{CYAN}{BOLD}╔{'═' * (self.width + 2)}╗{RESET}")
        print(f"{CYAN}║{RESET} "
              f"{GREEN}Уровень:{RESET} {BOLD}{self.level}{RESET}   "
              f"{YELLOW}Счёт:{RESET} {BOLD}{self.score}{RESET}   "
              f"{RED}Жизни:{RESET} {BOLD}{'♥' * self.lives}{RESET}   "
              f"{BLUE}Блоков:{RESET} {BOLD}{len(self.blocks)}{RESET} "
              f"{CYAN}║{RESET}")
        print(f"{CYAN}{BOLD}╠{'═' * (self.width + 2)}╣{RESET}")

        # Поле
        for row in field:
            print(f"{CYAN}║{RESET}" + ''.join(row) + f"{CYAN}║{RESET}")

        print(f"{CYAN}{BOLD}╚{'═' * (self.width + 2)}╝{RESET}")

        # Подсказки
        print(f"{DIM}a — влево, d — вправо, p — пауза, q — выход{RESET}")
        if self.paused:
            print(f"{YELLOW}{BOLD}⏸  ПАУЗА. Нажми p чтобы продолжить.{RESET}")

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

        if (nx, ny) in self.blocks:
            self.blocks.remove((nx, ny))
            self.score += 10
            if random.random() < 0.2:
                kind = random.choice([BONUS_LIFE, BONUS_WIDE])
                self.bonuses.append((nx, ny, kind))
            self.ball_dy *= -1
            ny = self.ball_y + self.ball_dy

        # Ловим бонусы
        for (bx, by, kind) in list(self.bonuses):
            if by == self.height - 2 and self.paddle_x <= bx < self.paddle_x + self.paddle_width:
                self.bonuses.remove((bx, by, kind))
                if kind == BONUS_LIFE:
                    self.lives += 1
                elif kind == BONUS_WIDE:
                    self.paddle_width = WIDE_PADDLE

        # Бонусы падают
        for (bx, by, kind) in list(self.bonuses):
            if by < self.height - 3:
                self.bonuses.remove((bx, by, kind))
                self.bonuses.append((bx, by + 1, kind))

        # Платформа
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
        if command == 'p':
            self.paused = not self.paused
            return
        if self.paused:
            return
        if command == 'a':
            self.move_paddle(-1)
        elif command == 'd':
            self.move_paddle(1)
        elif command == 'q':
            self.game_over = True
            return
        self.move_ball()

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
        print(f"{CYAN}{BOLD}🎮 АРКАНОИД{RESET}")
        print(f"{GREEN}Управление:{RESET} a — влево, d — вправо, p — пауза, q — выход")
        print(f"{MAGENTA}Бонусы:{RESET} ♥ — жизнь, W — широкая платформа")
        print()
        input(f"{DIM}Нажми Enter чтобы начать...{RESET}")

        while not self.game_over:
            clear_screen()
            self.print_field()

            command = get_key()
            self.step(command)
            time.sleep(0.08)

        clear_screen()
        self.print_field()

        high, is_new = self.save_highscore()

        if is_new:
            print(f"{YELLOW}{BOLD}🏆 НОВЫЙ РЕКОРД: {self.score}!{RESET}")
        print(f"{CYAN}Рекорд: {high}{RESET}")

        if self.win:
            print(f"{GREEN}{BOLD}🏆 ПОБЕДА! Все уровни пройдены!{RESET}")
        else:
            print(f"{RED}{BOLD}💀 Игра окончена. Счёт: {self.score}{RESET}")


if __name__ == '__main__':
    game = Arkanoid()
    game.play()