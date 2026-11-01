# Змейка — v4: цветная консоль, ввод без Enter

import random
import time
import os
import sys


# Цвета
RESET = '\033[0m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
DIM = '\033[2m'

WIDTH = 20
HEIGHT = 15


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


class Snake:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.level = 1
        self.base_delay = 0.15
        self.snake = [(5, 7), (4, 7), (3, 7)]
        self.direction = 'right'
        self.food = self.random_food()
        self.score = 0
        self.game_over = False
        self.paused = False

    def delay(self):
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

        # Границы
        for c in range(self.width):
            field[0][c] = f"{CYAN}-{RESET}"
            field[self.height - 1][c] = f"{CYAN}-{RESET}"
        for r in range(self.height):
            field[r][0] = f"{CYAN}|{RESET}"
            field[r][self.width - 1] = f"{CYAN}|{RESET}"

        # Еда
        fx, fy = self.food
        if 0 <= fx < self.width and 0 <= fy < self.height:
            field[fy][fx] = f"{RED}{BOLD}*{RESET}"

        # Змейка
        for i, (x, y) in enumerate(self.snake):
            if 0 <= x < self.width and 0 <= y < self.height:
                if i == 0:
                    field[y][x] = f"{GREEN}{BOLD}@{RESET}"
                else:
                    field[y][x] = f"{GREEN}o{RESET}"

        return field

    def print_field(self):
        field = self.build_field()

        print()
        print(f"{CYAN}{BOLD}╔{'═' * (self.width + 2)}╗{RESET}")
        print(f"{CYAN}║{RESET} {YELLOW}Уровень:{RESET} {BOLD}{self.level}{RESET}   "
              f"{YELLOW}Счёт:{RESET} {BOLD}{self.score}{RESET}   "
              f"{YELLOW}Длина:{RESET} {BOLD}{len(self.snake)}{RESET}  "
              f"{CYAN}║{RESET}")
        print(f"{CYAN}{BOLD}╠{'═' * (self.width + 2)}╣{RESET}")

        for row in field:
            print(f"{CYAN}║{RESET}" + ''.join(row) + f"{CYAN}║{RESET}")

        print(f"{CYAN}{BOLD}╚{'═' * (self.width + 2)}╝{RESET}")
        print(f"{DIM}w — вверх, s — вниз, a — влево, d — вправо, p — пауза, q — выход{RESET}")
        if self.paused:
            print(f"{YELLOW}{BOLD}⏸  ПАУЗА. Нажми p чтобы продолжить.{RESET}")

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
            if self.score >= self.level * 50 and self.level < 3:
                self.level += 1
                self.base_delay = max(0.05, self.base_delay - 0.03)
            self.food = self.random_food()
        else:
            self.snake.pop()

    def change_direction(self, command):
        opposites = {'w': 'down', 's': 'up', 'a': 'right', 'd': 'left'}
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
        clear_screen()
        print(f"{GREEN}{BOLD}🐍 ЗМЕЙКА{RESET}")
        print(f"{CYAN}Управление:{RESET} w/a/s/d, p — пауза, q — выход")
        print()
        input(f"{DIM}Нажми Enter чтобы начать...{RESET}")

        while not self.game_over:
            clear_screen()
            self.print_field()

            key = get_key()

            if key == 'q':
                break
            if key == 'p':
                self.paused = not self.paused
                continue
            if self.paused:
                continue

            self.change_direction(key)
            self.move()
            time.sleep(self.delay())

        clear_screen()
        self.print_field()

        high, is_new = self.save_highscore()
        if is_new:
            print(f"{YELLOW}{BOLD}🏆 НОВЫЙ РЕКОРД: {self.score}!{RESET}")
        print(f"{CYAN}Рекорд: {high}{RESET}")
        print(f"{RED}{BOLD}💀 Игра окончена. Счёт: {self.score}{RESET}")


if __name__ == '__main__':
    game = Snake()
    game.play()