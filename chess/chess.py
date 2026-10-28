# Шахматы — v1: доска и расстановка

# Фигуры юникодом
WHITE_PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'
}
BLACK_PIECES = {
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}


def create_board():
    """Возвращает доску 8x8 — список списков."""
    board = [[' '] * 8 for _ in range(8)]

    # Чёрные фигуры — верх (строки 0 и 1)
    board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    board[1] = ['p'] * 8

    # Белые фигуры — низ (строки 6 и 7)
    board[6] = ['P'] * 8
    board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

    return board


def piece_symbol(piece):
    """Возвращает юникод-символ для фигуры."""
    if piece == ' ':
        return '·'
    if piece.isupper():
        return WHITE_PIECES.get(piece, piece)
    return BLACK_PIECES.get(piece, piece)


def print_board(board):
    """Печатает доску с координатами."""
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


board = create_board()
print_board(board)