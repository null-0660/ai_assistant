# Шахматы — v2: ходы (без правил фигур)

WHITE_PIECES = {'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙'}
BLACK_PIECES = {'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'}


def create_board():
    board = [[' '] * 8 for _ in range(8)]
    board[0] = ['r','n','b','q','k','b','n','r']
    board[1] = ['p'] * 8
    board[6] = ['P'] * 8
    board[7] = ['R','N','B','Q','K','B','N','R']
    return board


def piece_symbol(p):
    if p == ' ': return '·'
    if p.isupper(): return WHITE_PIECES.get(p, p)
    return BLACK_PIECES.get(p, p)


def print_board(board):
    print()
    print("   a b c d e f g h")
    print("  +----------------+")
    for row in range(8):
        line = f"{8 - row} |"
        for col in range(8):
            line += f" {piece_symbol(board[row][col])}"
        line += " |"
        print(line)
    print("  +----------------+")
    print("   a b c d e f g h")
    print()


def parse_square(s):
    """'e2' -> (row, col) или None."""
    if len(s) != 2:
        return None
    col_letter = s[0].lower()
    row_digit = s[1]
    if col_letter not in 'abcdefgh' or row_digit not in '12345678':
        return None
    col = 'abcdefgh'.index(col_letter)
    row = 8 - int(row_digit)
    return (row, col)


def is_white(p): return p.isupper()
def is_black(p): return p.islower() and p != ' '


def move(board, fr, to, player):
    """Проверка и выполнение хода. Возвращает True/False."""
    fr_r, fr_c = fr
    to_r, to_c = to
    piece = board[fr_r][fr_c]
    target = board[to_r][to_c]

    if piece == ' ':
        print("Там нет фигуры.")
        return False

    if player == 'white' and not is_white(piece):
        print("Сейчас ходят белые.")
        return False
    if player == 'black' and not is_black(piece):
        print("Сейчас ходят чёрные.")
        return False

    if target != ' ':
        if player == 'white' and not is_black(target):
            print("Нельзя бить свою фигуру.")
            return False
        if player == 'black' and not is_white(target):
            print("Нельзя бить свою фигуру.")
            return False

    board[to_r][to_c] = piece
    board[fr_r][fr_c] = ' '
    return True


def main():
    board = create_board()
    player = 'white'

    while True:
        print_board(board)
        print(f"Ход: {'белые' if player == 'white' else 'чёрные'}")

        cmd = input("Ход (например e2 e4) или exit: ").strip()
        if cmd.lower() in ('exit', 'стоп'):
            print("Выход.")
            break

        parts = cmd.split()
        if len(parts) != 2:
            print("Нужно два поля: откуда и куда.")
            continue

        fr = parse_square(parts[0])
        to = parse_square(parts[1])
        if not fr or not to:
            print("Неверный формат. Пример: e2 e4")
            continue

        if move(board, fr, to, player):
            player = 'black' if player == 'white' else 'white'


main()