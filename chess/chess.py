# Шахматы — v3: режим против бота (случайный)

import random

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
    if len(s) != 2: return None
    col_letter = s[0].lower(); row_digit = s[1]
    if col_letter not in 'abcdefgh' or row_digit not in '12345678':
        return None
    return (8 - int(row_digit), 'abcdefgh'.index(col_letter))


def square_name(r, c):
    """(6, 4) -> 'e2'"""
    return f"{'abcdefgh'[c]}{8 - r}"


def is_white(p): return p.isupper()
def is_black(p): return p.islower() and p != ' '


def valid_moves(board, player):
    """Все допустимые ходы по базовым правилам."""
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == ' ': continue
            if player == 'white' and not is_white(p): continue
            if player == 'black' and not is_black(p): continue
            for tr in range(8):
                for tc in range(8):
                    t = board[tr][tc]
                    if t == ' ': moves.append(((r,c),(tr,tc))); continue
                    if player == 'white' and is_black(t):
                        moves.append(((r,c),(tr,tc)))
                    elif player == 'black' and is_white(t):
                        moves.append(((r,c),(tr,tc)))
    return moves


def make_move(board, fr, to):
    fr_r, fr_c = fr; to_r, to_c = to
    board[to_r][to_c] = board[fr_r][fr_c]
    board[fr_r][fr_c] = ' '


def bot_move(board, player):
    """Случайный допустимый ход."""
    moves = valid_moves(board, player)
    if not moves: return None
    return random.choice(moves)


def human_move(board, player):
    while True:
        cmd = input("Ход (например e2 e4) или exit: ").strip()
        if cmd.lower() in ('exit', 'стоп'):
            return None
        parts = cmd.split()
        if len(parts) != 2:
            print("Нужно два поля."); continue
        fr = parse_square(parts[0]); to = parse_square(parts[1])
        if not fr or not to:
            print("Неверный формат."); continue
        piece = board[fr[0]][fr[1]]
        if piece == ' ':
            print("Там нет фигуры."); continue
        if player == 'white' and not is_white(piece):
            print("Сейчас ходят белые."); continue
        if player == 'black' and not is_black(piece):
            print("Сейчас ходят чёрные."); continue
        target = board[to[0]][to[1]]
        if target != ' ':
            if player == 'white' and not is_black(target):
                print("Нельзя бить свою."); continue
            if player == 'black' and not is_white(target):
                print("Нельзя бить свою."); continue
        return (fr, to)


def main():
    print("1. Два игрока")
    print("2. Против бота (случайный)")
    mode = input("Режим (1-2): ").strip()

    vs_bot = (mode == '2')
    board = create_board()
    player = 'white'

    while True:
        print_board(board)
        print(f"Ход: {'белые' if player == 'white' else 'чёрные'}")

        if vs_bot and player == 'black':
            print("Бот думает...")
            move = bot_move(board, 'black')
            if not move:
                print("Бот не может ходить.")
                break
            fr, to = move
            print(f"Бот: {square_name(*fr)} -> {square_name(*to)}")
            make_move(board, fr, to)
            player = 'white'
            continue

        move = human_move(board, player)
        if move is None:
            print("Выход.")
            break
        fr, to = move
        make_move(board, fr, to)
        player = 'black' if player == 'white' else 'white'


main()