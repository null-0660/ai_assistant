# Крестики-нолики — v6: два режима (2 игрока / компьютер)

import os
import random


# ANSI-коды цветов
RESET = '\033[0m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
GREEN = '\033[92m'


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def colorize(cell):
    if cell == 'X':
        return f"{RED}X{RESET}"
    if cell == 'O':
        return f"{BLUE}O{RESET}"
    return f"{YELLOW}{cell}{RESET}"


def print_board(board):
    print()
    print(f"{CYAN}+-----------+{RESET}")
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i + j]
            if cell == ' ':
                row.append(colorize(str(i + j + 1)))
            else:
                row.append(colorize(cell))
        print(f"{CYAN}|{RESET} {row[0]} {CYAN}|{RESET} {row[1]} {CYAN}|{RESET} {row[2]} {CYAN}|{RESET}")
        if i < 6:
            print(f"{CYAN}+---+---+---+{RESET}")
    print(f"{CYAN}+-----------+{RESET}")
    print()


def check_win(board, player):
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] == player:
            return True
    return False


def is_draw(board):
    return ' ' not in board


def stop(text):
    return text.lower().strip() in ('exit', 'стоп')


def free_cells(board):
    """Список индексов свободных клеток."""
    return [i for i in range(9) if board[i] == ' ']


def find_winning_move(board, player):
    """Если player может выиграть следующим ходом — вернуть индекс. Иначе None."""
    for i in free_cells(board):
        test = board[:]
        test[i] = player
        if check_win(test, player):
            return i
    return None


def computer_move(board, comp, human):
    """
    Средний уровень:
    1. Выиграть, если можно.
    2. Заблокировать победу человека.
    3. Занять центр.
    4. Случайная свободная клетка.
    """
    win = find_winning_move(board, comp)
    if win is not None:
        return win

    block = find_winning_move(board, human)
    if block is not None:
        return block

    if board[4] == ' ':
        return 4

    return random.choice(free_cells(board))


def get_human_move(board, player):
    """Спрашивает ход у человека. Возвращает индекс или None (exit)."""
    while True:
        move = input("Номер клетки (1-9) или exit: ")

        if stop(move):
            return None

        try:
            move = int(move)
        except ValueError:
            print("Ошибка: введите число.")
            input("Enter чтобы продолжить...")
            return -1

        if move < 1 or move > 9:
            print("Ошибка: число от 1 до 9.")
            input("Enter чтобы продолжить...")
            return -1

        index = move - 1

        if board[index] != ' ':
            print("Клетка занята.")
            input("Enter чтобы продолжить...")
            return -1

        return index


def play_game(vs_computer):
    """
    Одна партия.
    vs_computer=True: X — человек, O — компьютер.
    Возвращает 'X', 'O', 'draw' или None (exit).
    """
    board = [' '] * 9
    player = 'X'

    while True:
        clear()
        print(f"{GREEN}=== КРЕСТИКИ-НОЛИКИ ==={RESET}")
        if vs_computer:
            print(f"Ты: {colorize('X')}   Компьютер: {colorize('O')}")
        print_board(board)
        print(f"Ход игрока: {colorize(player)}")

        if vs_computer and player == 'O':
            # Ход компьютера
            index = computer_move(board, 'O', 'X')
            board[index] = 'O'
            print(f"Компьютер сходил в клетку {index + 1}")
            input("Enter чтобы продолжить...")
        else:
            index = get_human_move(board, player)
            if index is None:
                return None
            if index == -1:
                continue
            board[index] = player

        if check_win(board, player):
            clear()
            print_board(board)
            if vs_computer and player == 'O':
                print(f"{RED}Компьютер победил!{RESET}")
            else:
                print(f"{GREEN}Игрок {colorize(player)} победил!{RESET}")
            input("Enter чтобы продолжить...")
            return player

        if is_draw(board):
            clear()
            print_board(board)
            print(f"{YELLOW}Ничья!{RESET}")
            input("Enter чтобы продолжить...")
            return 'draw'

        player = 'O' if player == 'X' else 'X'


def choose_mode():
    """Спрашивает режим. Возвращает True/False или None (exit)."""
    while True:
        clear()
        print(f"{GREEN}=== КРЕСТИКИ-НОЛИКИ ==={RESET}")
        print("1. Два игрока")
        print("2. Против компьютера (средний)")
        print("3. Выход")
        print()

        choice = input("Выбери режим (1-3): ").strip()

        if choice == '1':
            return False
        elif choice == '2':
            return True
        elif choice == '3':
            return None
        else:
            print("Неверный выбор.")
            input("Enter чтобы продолжить...")


def main():
    wins = {'X': 0, 'O': 0}
    draws = 0

    while True:
        vs_computer = choose_mode()
        if vs_computer is None:
            break

        while True:
            result = play_game(vs_computer)

            if result is None:
                break
            elif result == 'draw':
                draws += 1
            else:
                wins[result] += 1

            clear()
            print(f"{GREEN}=== КРЕСТИКИ-НОЛИКИ ==={RESET}")
            print(f"Счёт: {RED}X{RESET} = {wins['X']}, "
                  f"{BLUE}O{RESET} = {wins['O']}, ничьих = {draws}")
            print()

            again = input("Сыграть ещё раз? (да/yes или exit): ")
            if stop(again):
                break

    print()
    print(f"Итог: {RED}X{RESET} = {wins['X']}, "
          f"{BLUE}O{RESET} = {wins['O']}, ничьих = {draws}")


main()