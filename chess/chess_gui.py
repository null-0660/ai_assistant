# Шахматы — v6: рокировка, превращение, en passant

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
    k = find_king(board, player)
    if not k: return False
    enemy = 'black' if player == 'white' else 'white'
    return is_attacked(board, k[0], k[1], enemy)


# ===== Специальные ходы =====

def castling_moves(board, player):
    """Рокировка: короткая и длинная (если возможно)."""
    moves = []
    if player == 'white':
        row = 7
        king = 'K'; rook = 'R'
        enemy = 'black'
    else:
        row = 0
        king = 'k'; rook = 'r'
        enemy = 'white'

    # Король на e1/e8, ещё не двигался — проверяем через позицию
    if board[row][4] != king: return []

    # Короткая: f1/g1 пусты, ладья h1, клетки не под атакой
    if (board[row][7] == rook and board[row][5] == ' '
            and board[row][6] == ' '):
        if not is_attacked(board, row, 4, enemy) and \
           not is_attacked(board, row, 5, enemy) and \
           not is_attacked(board, row, 6, enemy):
            moves.append(('O-O', (row, 6)))

    # Длинная: b1/c1/d1 пусты, ладья a1
    if (board[row][0] == rook and board[row][1] == ' '
            and board[row][2] == ' ' and board[row][3] == ' '):
        if not is_attacked(board, row, 4, enemy) and \
           not is_attacked(board, row, 3, enemy) and \
           not is_attacked(board, row, 2, enemy):
            moves.append(('O-O-O', (row, 2)))

    return moves


def en_passant_moves(board, r, c, player, last_move):
    """Взятие на проходе."""
    moves = []
    if last_move is None: return []
    if board[r][c].upper() != 'P': return []

    direction = -1 if player == 'white' else 1

    # Проверяем, была ли последняя пешка противника в 2 клетках
    last_fr, last_fc, last_to = last_move
    if last_to[0] != r:  # та же строка
        return []
    if abs(last_fr - last_to[0]) != 2:  # не двойной ход
        return []
    if abs(last_to[1] - c) != 1:  # не соседняя колонка
        return []

    # Клетка за пешкой противника
    nr, nc = last_to[0] + direction, last_to[1]
    if in_board(nr, nc) and board[nr][nc] == ' ':
        moves.append((nr, nc))
    return moves


def all_pawn_moves(board, r, c, player, last_move):
    """Пешка + en passant."""
    moves = pawn_moves(board, r, c, player) + en_passant_moves(board, r, c, player, last_move)
    return moves


def legal_moves(board, player, last_move=None):
    """Только ходы, после которых свой король не под шахом."""
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == ' ': continue
            if player == 'white' and not is_white(p): continue
            if player == 'black' and not is_black(p): continue

            piece_moves = get_moves(board, r, c)
            if p.upper() == 'P':
                piece_moves = all_pawn_moves(board, r, c, player, last_move)
            if p.upper() == 'K':
                # Рокировка отдельным кодом
                for name, to in castling_moves(board, player):
                    test = [row[:] for row in board]
                    test[to[0]][to[1]] = test[r][c]
                    test[r][c] = ' '
                    if not in_check(test, player):
                        moves.append(((r,c), to, name))

            for to in piece_moves:
                test = [row[:] for row in board]
                test[to[0]][to[1]] = test[r][c]
                test[r][c] = ' '
                if not in_check(test, player):
                    moves.append(((r,c), to))
    return moves


def apply_move(board, fr, to, last_move=None):
    """Выполняет ход, возвращает (new_last_move, promotion_needed)."""
    piece = board[fr[0]][fr[1]]
    captured = board[to[0]][to[1]]

    # En passant
    if piece.upper() == 'P' and captured == ' ' and fr[1] != to[1]:
        # Диагональный ход на пустую — это en passant
        board[fr[0]][to[1]] = ' '  # убираем пешку противника

    board[to[0]][to[1]] = piece
    board[fr[0]][fr[1]] = ' '

    # Превращение пешки
    promotion = False
    if piece == 'P' and to[0] == 0:
        promotion = True
    if piece == 'p' and to[0] == 7:
        promotion = True

    return (fr[0], fr[1], to), promotion


def do_promotion(board, r, c, player):
    """Спрашивает, в кого превратить пешку."""
    print("Превращение! Выбери фигуру: Q (ферзь), R (ладья), B (слон), N (конь)")
    while True:
        choice = input("Q/R/B/N: ").strip().upper()
        if choice in ('Q','R','B','N'):
            new = choice if player == 'white' else choice.lower()
            board[r][c] = new
            return


def human_move(board, player, last_move):
    moves = legal_moves(board, player, last_move)
    while True:
        cmd = input("Ход (e2 e4) или exit: ").strip()
        if cmd.lower() in ('exit', 'стоп'): return None

        # Рокировка
        if cmd.lower() in ('o-o', '0-0'):
            for m in moves:
                if len(m) == 3 and m[2] == 'O-O':
                    return (m[0], m[1])
            print("Рокировка невозможна."); continue
        if cmd.lower() in ('o-o-o', '0-0-0'):
            for m in moves:
                if len(m) == 3 and m[2] == 'O-O-O':
                    return (m[0], m[1])
            print("Длинная рокировка невозможна."); continue

        parts = cmd.split()
        if len(parts) != 2:
            print("Нужно два поля."); continue
        fr = parse_square(parts[0]); to = parse_square(parts[1])
        if not fr or not to:
            print("Неверный формат."); continue

        # Ищем ход в legal_moves
        found = None
        for m in moves:
            if m[0] == fr and m[1] == to:
                found = m
                break
        if not found:
            print("Недопустимый ход."); continue
        return (fr, to)


def main():
    board = create_board()
    player = 'white'
    last_move = None

    while True:
        print_board(board)
        if in_check(board, player):
            print("ШАХ!")

        moves = legal_moves(board, player, last_move)
        if not moves:
            if in_check(board, player):
                winner = 'чёрные' if player == 'white' else 'белые'
                print(f"МАТ! Победили {winner}.")
            else:
                print("ПАТ. Ничья.")
            break

        print(f"Ход: {'белые' if player == 'white' else 'чёрные'}")
        move = human_move(board, player, last_move)
        if move is None: break

        fr, to = move
        old_last = last_move
        new_last, promotion = apply_move(board, fr, to, last_move)

        # Рокировка: двигаем ладью
        piece = board[to[0]][to[1]]
        if piece.upper() == 'K' and abs(to[1] - fr[1]) == 2:
            row = to[0]
            if to[1] == 6:  # короткая
                board[row][5] = board[row][7]
                board[row][7] = ' '
            else:  # длинная
                board[row][3] = board[row][0]
                board[row][0] = ' '

        # Превращение пешки
        if promotion:
            do_promotion(board, to[0], to[1], player)

        last_move = new_last
        player = 'black' if player == 'white' else 'white'


main()