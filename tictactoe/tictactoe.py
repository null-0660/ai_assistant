# Крестики-нолики — v4: счёт и replay

import os


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_board(board):
    """Печатает доску. Пустые клетки показывает номерами."""
    print()
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i + j]
            row.append(str(i + j + 1) if cell == ' ' else cell)
        print(f" {row[0]} | {row[1]} | {row[2]} ")
        if i < 6:
            print("---+---+---")
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


def play_game():
    """Одна партия. Возвращает 'X', 'O', 'draw' или None (exit)."""
    board = [' '] * 9
    player = 'X'

    while True:
        clear()
        print_board(board)
        print(f"Ход игрока {player}")

        move = input("Номер клетки (1-9) или exit: ")

        if stop(move):
            return None

        try:
            move = int(move)
        except ValueError:
            print("Ошибка: введите число.")
            input("Enter чтобы продолжить...")
            continue

        if move < 1 or move > 9:
            print("Ошибка: число от 1 до 9.")
            input("Enter чтобы продолжить...")
            continue

        index = move - 1

        if board[index] != ' ':
            print("Клетка занята.")
            input("Enter чтобы продолжить...")
            continue

        board[index] = player

        if check_win(board, player):
            clear()
            print_board(board)
            print(f"Игрок {player} победил!")
            input("Enter чтобы продолжить...")
            return player

        if is_draw(board):
            clear()
            print_board(board)
            print("Ничья!")
            input("Enter чтобы продолжить...")
            return 'draw'

        player = 'O' if player == 'X' else 'X'


def main():
    wins = {'X': 0, 'O': 0}
    draws = 0

    while True:
        clear()
        print("=== КРЕСТИКИ-НОЛИКИ ===")
        print(f"Счёт: X = {wins['X']}, O = {wins['O']}, ничьих = {draws}")
        print()

        result = play_game()

        if result is None:
            print("Выход.")
            break
        elif result == 'draw':
            draws += 1
        else:
            wins[result] += 1

        again = input("Сыграть ещё раз? (да/yes или exit): ")
        if stop(again):
            break

    print()
    print(f"Итог: X = {wins['X']}, O = {wins['O']}, ничьих = {draws}")


main()