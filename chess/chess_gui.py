# Шахматы GUI — v2: полные правила

import tkinter as tk
from tkinter import messagebox
import random


WHITE_PIECES = {'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙'}
BLACK_PIECES = {'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'}

LIGHT = '#f0d9b5'
DARK = '#b58863'
SELECT = '#f6f669'
HINT = '#9bcf6b'
WHITE_COLOR = '#ffffff'
BLACK_COLOR = '#000000'


def piece_symbol(p):
    if p == ' ': return ''
    if p.isupper(): return WHITE_PIECES.get(p, p)
    return BLACK_PIECES.get(p, p)


def create_board():
    b = [[' '] * 8 for _ in range(8)]
    b[0] = ['r','n','b','q','k','b','n','r']
    b[1] = ['p'] * 8
    b[6] = ['P'] * 8
    b[7] = ['R','N','B','Q','K','B','N','R']
    return b


def is_white(p): return p.isupper()
def is_black(p): return p.islower() and p != ' '
def in_board(r, c): return 0 <= r < 8 and 0 <= c < 8


def is_enemy(p, player):
    if p == ' ': return False
    return is_black(p) if player == 'white' else is_white(p)


def is_friend(p, player):
    if p == ' ': return False
    return is_white(p) if player == 'white' else is_black(p)


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
    m = []
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = r+dr, c+dc
        if in_board(nr, nc) and not is_friend(board[nr][nc], player):
            m.append((nr, nc))
    return m


def sliding_moves(board, r, c, player, dirs):
    m = []
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        while in_board(nr, nc):
            p = board[nr][nc]
            if p == ' ': m.append((nr, nc))
            elif is_enemy(p, player):
                m.append((nr, nc)); break
            else: break
            nr += dr; nc += dc
    return m


def bishop_moves(b,r,c,p): return sliding_moves(b,r,c,p,[(-1,-1),(-1,1),(1,-1),(1,1)])
def rook_moves(b,r,c,p): return sliding_moves(b,r,c,p,[(-1,0),(1,0),(0,-1),(0,1)])
def queen_moves(b,r,c,p): return bishop_moves(b,r,c,p)+rook_moves(b,r,c,p)


def king_moves(board, r, c, player):
    m = []
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            nr, nc = r+dr, c+dc
            if in_board(nr, nc) and not is_friend(board[nr][nc], player):
                m.append((nr, nc))
    return m


def get_moves(board, r, c):
    p = board[r][c]
    if p == ' ': return []
    player = 'white' if is_white(p) else 'black'
    k = p.upper()
    if k=='P': return pawn_moves(board,r,c,player)
    if k=='N': return knight_moves(board,r,c,player)
    if k=='B': return bishop_moves(board,r,c,player)
    if k=='R': return rook_moves(board,r,c,player)
    if k=='Q': return queen_moves(board,r,c,player)
    if k=='K': return king_moves(board,r,c,player)
    return []


def find_king(board, player):
    king = 'K' if player=='white' else 'k'
    for r in range(8):
        for c in range(8):
            if board[r][c] == king: return (r,c)
    return None


def is_attacked(board, r, c, by_player):
    for rr in range(8):
        for cc in range(8):
            p = board[rr][cc]
            if p == ' ': continue
            if by_player == 'white' and not is_white(p): continue
            if by_player == 'black' and not is_black(p): continue
            if (r,c) in get_moves(board, rr, cc):
                return True
    return False


def in_check(board, player):
    k = find_king(board, player)
    if not k: return False
    enemy = 'black' if player=='white' else 'white'
    return is_attacked(board, k[0], k[1], enemy)


def castling_moves(board, player):
    moves = []
    if player == 'white':
        row, king, rook, enemy = 7, 'K', 'R', 'black'
    else:
        row, king, rook, enemy = 0, 'k', 'r', 'white'

    if board[row][4] != king: return []

    if board[row][7] == rook and board[row][5] == ' ' and board[row][6] == ' ':
        if not is_attacked(board,row,4,enemy) and not is_attacked(board,row,5,enemy) and not is_attacked(board,row,6,enemy):
            moves.append(('O-O', (row,6)))

    if board[row][0] == rook and board[row][1] == ' ' and board[row][2] == ' ' and board[row][3] == ' ':
        if not is_attacked(board,row,4,enemy) and not is_attacked(board,row,3,enemy) and not is_attacked(board,row,2,enemy):
            moves.append(('O-O-O', (row,2)))

    return moves


def en_passant_moves(board, r, c, player, last_move):
    moves = []
    if last_move is None: return []
    if board[r][c].upper() != 'P': return []
    direction = -1 if player=='white' else 1
    last_fr, last_fc, last_to = last_move
    if last_to[0] != r: return []
    if abs(last_fr - last_to[0]) != 2: return []
    if abs(last_to[1] - c) != 1: return []
    nr, nc = last_to[0]+direction, last_to[1]
    if in_board(nr,nc) and board[nr][nc] == ' ':
        moves.append((nr,nc))
    return moves


def all_pawn_moves(board, r, c, player, last_move):
    return pawn_moves(board,r,c,player) + en_passant_moves(board,r,c,player,last_move)


def legal_moves(board, player, last_move=None):
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == ' ': continue
            if player == 'white' and not is_white(p): continue
            if player == 'black' and not is_black(p): continue

            piece_moves = get_moves(board,r,c)
            if p.upper() == 'P':
                piece_moves = all_pawn_moves(board,r,c,player,last_move)
            if p.upper() == 'K':
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


def apply_move(board, fr, to):
    piece = board[fr[0]][fr[1]]
    captured = board[to[0]][to[1]]
    if piece.upper()=='P' and captured==' ' and fr[1] != to[1]:
        board[fr[0]][to[1]] = ' '
    board[to[0]][to[1]] = piece
    board[fr[0]][fr[1]] = ' '


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Шахматы")
        self.root.resizable(False, False)
        self.board = create_board()
        self.selected = None
        self.player = 'white'
        self.vs_bot = False
        self.game_over = False
        self.last_move = None
        self.highlight = []
        self.buttons = []
        self.show_menu()

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_menu(self):
        self.clear_window()
        self.root.configure(bg='#2d2d2d')
        tk.Label(self.root, text="ШАХМАТЫ", font=('Arial',28,'bold'),
                 bg='#2d2d2d', fg='#ffffff').pack(pady=(40,30))

        def btn(text, cmd):
            tk.Button(self.root, text=text, font=('Arial',16,'bold'),
                      bg='#4d4d4d', fg='#ffffff',
                      activebackground='#6d6d6d', activeforeground='#ffffff',
                      relief='flat', bd=0, padx=40, pady=14, width=18,
                      cursor='hand2', command=cmd).pack(pady=8)

        btn("Два игрока", lambda: self.start_game(False))
        btn("Против бота", lambda: self.start_game(True))
        btn("Выход", self.root.destroy)

    def start_game(self, vs_bot):
        self.vs_bot = vs_bot
        self.board = create_board()
        self.selected = None
        self.player = 'white'
        self.game_over = False
        self.last_move = None
        self.highlight = []
        self.clear_window()
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        self.root.configure(bg='#2d2d2d')
        self.status = tk.Label(self.root, text="Ход: белые",
                               font=('Arial',16,'bold'),
                               bg='#2d2d2d', fg='#ffffff')
        self.status.pack(pady=10)

        bf = tk.Frame(self.root, bg='#2d2d2d')
        bf.pack(padx=10, pady=10)

        self.buttons = []
        for r in range(8):
            row = []
            for c in range(8):
                base = LIGHT if (r+c)%2==0 else DARK
                btn = tk.Button(bf, text='', font=('Arial',28),
                                width=2, height=1, bg=base, fg=BLACK_COLOR,
                                relief='flat', bd=0, activebackground=base,
                                command=lambda rr=r, cc=c: self.on_click(rr, cc))
                btn.grid(row=r, column=c)
                row.append(btn)
            self.buttons.append(row)

        tk.Button(self.root, text="В меню", font=('Arial',12,'bold'),
                  bg='#4d4d4d', fg='#ffffff', relief='flat', bd=0,
                  padx=20, pady=8, cursor='hand2',
                  command=self.show_menu).pack(pady=10)

    def refresh(self):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                base = LIGHT if (r+c)%2==0 else DARK
                btn = self.buttons[r][c]

                if self.selected == (r,c):
                    btn.config(bg=SELECT)
                elif (r,c) in self.highlight:
                    btn.config(bg=HINT)
                else:
                    btn.config(bg=base)

                if p == ' ':
                    btn.config(text='')
                else:
                    btn.config(text=piece_symbol(p),
                               fg=WHITE_COLOR if is_white(p) else BLACK_COLOR)

    def on_click(self, r, c):
        if self.game_over: return
        if self.vs_bot and self.player == 'black': return

        p = self.board[r][c]

        if self.selected is None:
            if p == ' ': return
            if self.player == 'white' and not is_white(p): return
            if self.player == 'black' and not is_black(p): return
            self.selected = (r,c)
            self.highlight = [to for (fr, to) in legal_moves(self.board, self.player, self.last_move) if fr == (r,c)]
            self.refresh()
            return

        if self.selected == (r,c):
            self.selected = None
            self.highlight = []
            self.refresh()
            return

        # Проверка легальности
        allowed = legal_moves(self.board, self.player, self.last_move)
        found = None
        for m in allowed:
            fr, to = m[0], m[1]
            if fr == self.selected and to == (r,c):
                found = m
                break

        if not found:
            # Может, выбрал другую свою
            if p != ' ' and ((self.player=='white' and is_white(p)) or (self.player=='black' and is_black(p))):
                self.selected = (r,c)
                self.highlight = [to for (fr, to) in allowed if fr == (r,c)]
                self.refresh()
                return
            return

        fr, to = self.selected, (r,c)
        self.do_move(fr, to)

    def do_move(self, fr, to):
        apply_move(self.board, fr, to)

        # Рокировка — двигаем ладью
        piece = self.board[to[0]][to[1]]
        if piece.upper() == 'K' and abs(to[1] - fr[1]) == 2:
            row = to[0]
            if to[1] == 6:
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = ' '
            else:
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = ' '

        # Превращение
        if piece == 'P' and to[0] == 0:
            self.ask_promotion(to[0], to[1], 'white')
        if piece == 'p' and to[0] == 7:
            self.ask_promotion(to[0], to[1], 'black')

        self.last_move = (fr[0], fr[1], to)
        self.selected = None
        self.highlight = []
        self.player = 'black' if self.player == 'white' else 'white'
        self.status.config(text=f"Ход: {'белые' if self.player=='white' else 'чёрные'}")
        self.refresh()

        # Проверка мата/пата
        moves = legal_moves(self.board, self.player, self.last_move)
        if not moves:
            self.game_over = True
            if in_check(self.board, self.player):
                winner = 'чёрные' if self.player == 'white' else 'белые'
                messagebox.showinfo("МАТ!", f"Победили {winner}.")
            else:
                messagebox.showinfo("ПАТ", "Ничья.")
            return

        # Шах
        if in_check(self.board, self.player):
            self.status.config(text=f"ШАХ! Ход: {'белые' if self.player=='white' else 'чёрные'}")

        # Ход бота
        if self.vs_bot and self.player == 'black':
            self.root.after(500, self.bot_turn)

    def ask_promotion(self, r, c, player):
        choice = messagebox.askquestion("Превращение", "В ферзя? (No = ладья)")
        if choice == 'yes':
            self.board[r][c] = 'Q' if player == 'white' else 'q'
        else:
            self.board[r][c] = 'R' if player == 'white' else 'r'

    def bot_turn(self):
        if self.game_over: return
        moves = legal_moves(self.board, 'black', self.last_move)
        if not moves: return
        # Простая эвристика: предпочитаем взятия
        best = []
        for m in moves:
            fr, to = m[0], m[1]
            if self.board[to[0]][to[1]] != ' ':
                best.append(m)
        if best:
            move = random.choice(best)
        else:
            move = random.choice(moves)
        fr, to = move[0], move[1]
        self.do_move(fr, to)


if __name__ == '__main__':
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()