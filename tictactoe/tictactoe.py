# Крестики-нолики — v7: красивое меню и финальный экран

import os
import random


# ANSI-коды цветов
RESET = '\033[0m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BOLD = '\033[1m'
DIM = '\033[2m'


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def colorize(cell):
    if cell == 'X':
        return f"{RED}{BOLD}X{RESET}"
    if cell == 'O':
        return f"{BLUE}{BOLD}O{RESET}"
    return f"{YELLOW}{cell}{RESET}"


def print_header(subtitle=""):
    """Красивый заголовок с рамкой."""
    width = 40
    print()
    print(f"{CYAN}+{'=' * width}+{RESET}")
    print(f"{CYAN}|{RESET}{GREEN}{BOLD}{'КРЕСТИКИ-НОЛИКИ'.center(width)}{RESET}{CYAN}|{RESET}")
    if subtitle:
        print(f"{CYAN}|{RESET}{DIM}{subtitle.center(width)}{RESET}{CYAN}|{RESET}")
    print(f"{CYAN}+{'=' * width}+{RESET}")
    print()


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
    return [i for i in range(9) if board[i] == ' ']


def find_winning_move(board, player):
    for i in free_cells(board):
        test = board[:]
        test[i] = player
        if check_win(test, player):
            return i
    return None


def computer_move(board, comp, human):
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
    while True:
        move = input(f"  {colorize(player)} → номер клетки (1-9) или exit: ")

        if stop(move):
            return None

        try:
            move = int(move)
        except ValueError:
            print("  Ошибка: введите число.")
            input("  Enter чтобы продолжить...")
            return -1

        if move < 1 or move > 9:
            print("  Ошибка: число от 1 до 9.")
            input("  Enter чтобы продолжить...")
            return -1

        index = move - 1

        if board[index] != ' ':
            print("  Клетка занята.")
            input("  Enter чтобы продолжить...")
            return -1

        return index


def play_game(vs_computer):
    board = [' '] * 9
    player = 'X'

    while True:
        clear()
        if vs_computer:
            print_header("Ты — X   |   Компьютер — O")
        else:
            print_header("Два игрока")
        print_board(board)

        if vs_computer and player == 'O':
            index = computer_move(board, 'O', 'X')
            board[index] = 'O'
            print(f"  {BLUE}Компьютер{RESET} сходил в клетку {YELLOW}{index + 1}{RESET}")
            input("  Enter чтобы продолжить...")
        else:
            index = get_human_move(board, player)
            if index is None:
                return None
            if index == -1:
                continue
            board[index] = player

        if check_win(board, player):
            clear()
            print_header("ПОБЕДА")
            print_board(board)
            if vs_computer and player == 'O':
                print(f"  {RED}{BOLD}Компьютер победил!{RESET}")
            else:
                print(f"  {GREEN}{BOLD}Игрок {colorize(player)} победил!{RESET}")
            input("\n  Enter чтобы продолжить...")
            return player

        if is_draw(board):
            clear()
            print_header("НИЧЬЯ")
            print_board(board)
            print(f"  {YELLOW}{BOLD}Ничья!{RESET}")
            input("\n  Enter чтобы продолжить...")
            return 'draw'

        player = 'O' if player == 'X' else 'X'


def choose_mode():
    while True:
        clear()
        print_header("Выбери режим")
        print(f"  {CYAN}1.{RESET} Два игрока")
        print(f"  {CYAN}2.{RESET} Против компьютера {DIM}(средний){RESET}")
        print(f"  {CYAN}3.{RESET} Выход")
        print()

        choice = input("  → твой выбор (1-3): ").strip()

        if choice == '1':
            return False
        elif choice == '2':
            return True
        elif choice == '3':
            return None
        else:
            print("  Неверный выбор.")
            input("  Enter чтобы продолжить...")


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
            print_header("СЧЁТ")
            print(f"  {RED}{BOLD}X{RESET} = {wins['X']}")
            print(f"  {BLUE}{BOLD}O{RESET} = {wins['O']}")
            print(f"  {YELLOW}Ничьих{RESET} = {draws}")
            print()

            again = input("  Сыграть ещё раз? (да/yes или exit): ")
            if stop(again):
                break

    clear()
    print_header("ИТОГ")
    print(f"  {RED}{BOLD}X{RESET} = {wins['X']}")
    print(f"  {BLUE}{BOLD}O{RESET} = {wins['O']}")
    print(f"  {YELLOW}Ничьих{RESET} = {draws}")
    print()
    print(f"  {DIM}Спасибо за игру!{RESET}")
    print()


main()