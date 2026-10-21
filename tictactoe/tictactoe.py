# Крестики-нолики — v2: играбельная версия

def print_board(board):
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()


def check_win(board, player):
    """Проверяет победу игрока."""
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


board = [' '] * 9
player = 'X'

while True:
    print_board(board)
    print(f"Ход игрока {player}")

    move = input("Номер клетки (1-9) или exit: ")

    if stop(move):
        print("Выход.")
        break

    try:
        move = int(move)
    except ValueError:
        print("Ошибка: введите число.")
        continue

    if move < 1 or move > 9:
        print("Ошибка: число от 1 до 9.")
        continue

    index = move - 1

    if board[index] != ' ':
        print("Клетка занята.")
        continue

    board[index] = player

    if check_win(board, player):
        print_board(board)
        print(f"Игрок {player} победил!")
        break

    if is_draw(board):
        print_board(board)
        print("Ничья!")
        break

    player = 'O' if player == 'X' else 'X'

print("Игра окончена.")