# Крестики-нолики — версия 1: только доска

def print_board(board):
    """Печатает доску 3x3 с номерами клеток."""
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()


# Доска — список из 9 клеток, все пустые
board = [' '] * 9

# Показать пустую доску
print_board(board)