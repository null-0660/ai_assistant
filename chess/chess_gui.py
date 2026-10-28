# Шахматы — v5: шах и мат

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
    return f"{'abcdefgh'[c]}{8 - r}"


def is_white(p): return p.isupper()
def is_black(p): return p.islower() and p != ' '
def is_enemy(p, player):
    if p == ' ': return False
    return is_black(p) if player == 'white' else is_white(p)
def is_friend(p, player):
    if p == ' ': return False
    return is_white(p) if player == 'white' else is_black(p)
def in_board(r, c): return 0 <= r < 8 and 0 <= c < 8


def pawn_moves(board, r, c, player):
    moves = []
    direction = -1 if player == 'white' else 1
    start_row = 6 if player == 'white' else 1
    nr = r + direction
    if in_board(nr, c) and board[nr][c] == ' ':
        moves.append((nr, c))
        if r == start_row and board[r + 2*direction][c] == ' ':
            moves.append((r + 2*direction, c))
    for dc in (-1, 1):
        nr, nc = r + direction, c + dc
        if in_board(nr, nc) and is_enemy(board[nr][nc], player):
            moves.append((nr, nc))
    return moves


def knight_moves(board, r, c, player):
    moves = []
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = r + dr, c + dc
        if in_board(nr, nc) and not is_friend(board[nr][nc], player):
            moves.append((nr, nc))
    return moves


def sliding_moves(board, r, c, player, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_board(nr, nc):
            p = board[nr][nc]
            if p == ' ':
                moves.append((nr, nc))
            elif is_enemy(p, player):
                moves.append((nr, nc)); break
            else:
                break
            nr += dr; nc += dc
    return moves


def bishop_moves(b, r, c, p): return sliding_moves(b, r, c, p, [(-1,-1),(-1,1),(1,-1),(1,1)])
def rook_moves(b, r, c, p): return sliding_moves(b, r, c, p, [(-1,0),(1,0),(0,-1),(0,1)])
def queen_moves(b, r, c, p): return bishop_moves(b, r, c, p) + rook_moves(b, r, c, p)


def king_moves(board, r, c, player):
    moves = []
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if in_board(nr, nc) and not is_friend(board[nr][nc], player):
                moves.append((nr, nc))
    return moves


def get_moves(board, r, c):
    p = board[r][c]
    if p == ' ': return []
    player = 'white' if is_white(p) else 'black'
    kind = p.upper()
    if kind == 'P': return pawn_moves(board, r, c, player)
    if kind == 'N': return knight_moves(board, r, c, player)
    if kind == 'B': return bishop_moves(board, r, c, player)
    if kind == 'R': return rook_moves(board, r, c, player)
    if kind == 'Q': return queen_moves(board, r, c, player)
    if kind == 'K': return king_moves(board, r, c, player)
    return []


def find_king(board, player):
    king = 'K' if player == 'white' else 'k'
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return (r, c)
    return None


def is_attacked(board, r, c, by_player):
    """Атакована ли клетка (r,c) фигурами by_player."""
    for rr in range(8):
        for cc in range(8):
            p = board[rr][cc]
            if p == ' ': continue
            if by_player == 'white' and not is_white(p): continue
            if by_player == 'black' and not is_black(p): continue
            if (r, c) in get_moves(board, rr, cc):
                return True
    return False


def in_check(board, player):
    """Под шахом ли король player."""
    k = find_king(board, player)
    if not k: return False
    enemy = 'black' if player == 'white' else 'white'
    return is_attacked(board, k[0], k[1], enemy)


def legal_moves(board, player):
    """Только ходы, после которых свой король не под шахом."""
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == ' ': continue
            if player == 'white' and not is_white(p): continue
            if player == 'black' and not is_black(p): continue
            for to in get_moves(board, r, c):
                test = [row[:] for row in board]
                test[to[0]][to[1]] = test[r][c]
                test[r][c] = ' '
                if not in_check(test, player):
                    moves.append(((r,c), to))
    return moves


def make_move(board, fr, to):
    board[to[0]][to[1]] = board[fr[0]][fr[1]]
    board[fr[0]][fr[1]] = ' '


def human_move(board, player):
    while True:
        cmd = input("Ход (e2 e4) или exit: ").strip()
        if cmd.lower() in ('exit', 'стоп'): return None
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
        if to not in get_moves(board, fr[0], fr[1]):
            print("Так эта фигура не ходит."); continue
        if ((fr[0], fr[1]), to) not in legal_moves(board, player):
            print("Этот ход оставляет короля под шахом."); continue
        return (fr, to)


def main():
    board = create_board()
    player = 'white'
    while True:
        print_board(board)
        if in_check(board, player):
            print("ШАХ!")
        moves = legal_moves(board, player)
        if not moves:
            if in_check(board, player):
                winner = 'чёрные' if player == 'white' else 'белые'
                print(f"МАТ! Победили {winner}.")
            else:
                print("ПАТ. Ничья.")
            break
        print(f"Ход: {'белые' if player == 'white' else 'чёрные'}")
        move = human_move(board, player)
        if move is None: break
        make_move(board, *move)
        player = 'black' if player == 'white' else 'white'


main()