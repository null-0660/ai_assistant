# Шахматы GUI — v6: фикс координат, подсветки, отступов

import tkinter as tk
from tkinter import messagebox
import random


WHITE_PIECES = {'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙'}
BLACK_PIECES = {'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'}

LIGHT = '#f5e6c8'
DARK = '#8b6914'
SELECT = '#f6f669'
HINT = '#a8e063'
LAST_MOVE = '#f9d56e'
WHITE_COLOR = '#ffffff'
BLACK_COLOR = '#1a1a1a'
BG_DARK = '#1a1a1a'
BORDER = '#d4af37'

CELL_SIZE = 56   # размер клетки в пикселях

PIECE_VALUE = {'P':1,'N':3,'B':3,'R':5,'Q':9,'K':100}


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


def evaluate(board):
    score = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == ' ': continue
            v = PIECE_VALUE.get(p.upper(), 0)
            score += v if is_white(p) else -v
    return score


def minimax(board, depth, alpha, beta, maximizing, last_move):
    player = 'white' if maximizing else 'black'
    moves = legal_moves(board, player, last_move)
    if depth == 0 or not moves:
        return evaluate(board), None
    best_move = random.choice(moves) if moves else None
    if maximizing:
        max_eval = -float('inf')
        for m in moves:
            fr, to = m[0], m[1]
            test = [row[:] for row in board]
            apply_move(test, fr, to)
            ev, _ = minimax(test, depth-1, alpha, beta, False, (fr[0], fr[1], to))
            if ev > max_eval:
                max_eval = ev; best_move = m
            alpha = max(alpha, ev)
            if beta <= alpha: break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for m in moves:
            fr, to = m[0], m[1]
            test = [row[:] for row in board]
            apply_move(test, fr, to)
            ev, _ = minimax(test, depth-1, alpha, beta, True, (fr[0], fr[1], to))
            if ev < min_eval:
                min_eval = ev; best_move = m
            beta = min(beta, ev)
            if beta <= alpha: break
        return min_eval, best_move


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("♔ Шахматы ♚")
        self.root.minsize(560, 680)
        self.root.configure(bg=BG_DARK)
        self.board = create_board()
        self.selected = None
        self.player = 'white'
        self.vs_bot = False
        self.difficulty = 'medium'
        self.game_over = False
        self.last_move = None
        self.highlight = []
        self.buttons = []
        self.center_window()
        self.show_menu()

    def center_window(self):
        self.root.update_idletasks()
        w = CELL_SIZE * 8 + 100
        h = CELL_SIZE * 8 + 200
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    def hover_button(self, btn, normal, hover):
        btn.bind('<Enter>', lambda e: btn.config(bg=hover))
        btn.bind('<Leave>', lambda e: btn.config(bg=normal))

    def show_menu(self):
        self.clear_window()
        self.root.configure(bg=BG_DARK)

        title_frame = tk.Frame(self.root, bg=BG_DARK)
        title_frame.pack(pady=(60, 10))
        tk.Label(title_frame, text="♔", font=('Arial',44),
                 bg=BG_DARK, fg=BORDER).pack(side='left', padx=10)
        tk.Label(title_frame, text="ШАХМАТЫ", font=('Arial',34,'bold'),
                 bg=BG_DARK, fg=BORDER).pack(side='left')
        tk.Label(title_frame, text="♚", font=('Arial',44),
                 bg=BG_DARK, fg=BORDER).pack(side='left', padx=10)

        tk.Label(self.root, text="Выбери режим",
                 font=('Arial',12,'italic'),
                 bg=BG_DARK, fg='#888').pack(pady=(0, 20))

        def btn(text, cmd, color, hover_color):
            b = tk.Button(self.root, text=text, font=('Arial',14,'bold'),
                          bg=color, fg='#ffffff',
                          activebackground=hover_color, activeforeground='#ffffff',
                          relief='flat', bd=0, padx=40, pady=12, width=24,
                          cursor='hand2', command=cmd)
            b.pack(pady=6)
            self.hover_button(b, color, hover_color)

        btn("Два игрока", lambda: self.start_game(False, 'medium'), '#3d5a80', '#4a6fa5')
        btn("Бот — Лёгкий", lambda: self.start_game(True, 'easy'), '#3d8b3d', '#4aa14a')
        btn("Бот — Средний", lambda: self.start_game(True, 'medium'), '#c9a227', '#e0b83a')
        btn("Бот — Тяжёлый", lambda: self.start_game(True, 'hard'), '#8b3d3d', '#a54a4a')
        btn("Выход", self.root.destroy, '#333333', '#4d4d4d')

    def start_game(self, vs_bot, difficulty):
        self.vs_bot = vs_bot
        self.difficulty = difficulty
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
        self.root.configure(bg=BG_DARK)

        mode_text = "Два игрока" if not self.vs_bot else f"Бот ({self.difficulty})"
        self.status = tk.Label(self.root,
                               text=f"{mode_text}  |  ♔ Ход: белые",
                               font=('Arial',13,'bold'),
                               bg=BG_DARK, fg=BORDER)
        self.status.pack(pady=8)

        # Единый контейнер: рамка + сетка + координаты
        outer = tk.Frame(self.root, bg=BORDER)
        outer.pack(padx=10, pady=8)

        # Внутри: сетка 9×9, где крайние — координаты
        grid = tk.Frame(outer, bg=BG_DARK)
        grid.pack(padx=2, pady=2)

        # Верхняя строка: пустая + a..h + пустая
        tk.Label(grid, text='', bg=BG_DARK, width=2).grid(row=0, column=0)
        for c in range(8):
            tk.Label(grid, text='abcdefgh'[c], font=('Arial',10,'bold'),
                     bg=BG_DARK, fg=BORDER, width=4).grid(row=0, column=c+1)
        tk.Label(grid, text='', bg=BG_DARK, width=2).grid(row=0, column=9)

        # Доска: слева цифры, по центру кнопки, справа цифры
        for r in range(8):
            tk.Label(grid, text=str(8-r), font=('Arial',10,'bold'),
                     bg=BG_DARK, fg=BORDER, width=2, height=1
                     ).grid(row=r+1, column=0)
            for c in range(8):
                base = LIGHT if (r+c)%2==0 else DARK
                btn = tk.Button(grid, text='', font=('Arial',26,'bold'),
                                width=2, height=1, bg=base, fg=BLACK_COLOR,
                                relief='flat', bd=0, activebackground=base,
                                highlightthickness=0,
                                cursor='hand2',
                                command=lambda rr=r, cc=c: self.on_click(rr, cc))
                btn.grid(row=r+1, column=c+1, sticky='nsew')
                self.buttons.append(btn)
            tk.Label(grid, text=str(8-r), font=('Arial',10,'bold'),
                     bg=BG_DARK, fg=BORDER, width=2, height=1
                     ).grid(row=r+1, column=9)

        # Нижняя строка
        tk.Label(grid, text='', bg=BG_DARK, width=2).grid(row=9, column=0)
        for c in range(8):
            tk.Label(grid, text='abcdefgh'[c], font=('Arial',10,'bold'),
                     bg=BG_DARK, fg=BORDER, width=4).grid(row=9, column=c+1)
        tk.Label(grid, text='', bg=BG_DARK, width=2).grid(row=9, column=9)

        # Перестроим кнопки в 2D
        self.buttons_2d = [[self.buttons[r*8 + c] for c in range(8)] for r in range(8)]
        self.buttons = self.buttons_2d

        menu_btn = tk.Button(self.root, text="← В меню", font=('Arial',11,'bold'),
                             bg='#333333', fg=BORDER, relief='flat', bd=0,
                             padx=20, pady=6, cursor='hand2',
                             command=self.show_menu)
        menu_btn.pack(pady=8)
        self.hover_button(menu_btn, '#333333', '#4d4d4d')

    def refresh(self):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                base = LIGHT if (r+c)%2==0 else DARK
                btn = self.buttons[r][c]

                # Фон
                if self.selected == (r,c):
                    btn.config(bg=SELECT)
                elif self.last_move and (r,c) in (self.last_move[0], self.last_move[2]):
                    btn.config(bg=LAST_MOVE)
                elif (r,c) in self.highlight:
                    btn.config(bg=HINT)
                else:
                    btn.config(bg=base)

                # Фигура
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
            self.highlight = [m[1] for m in legal_moves(self.board, self.player, self.last_move) if m[0] == (r,c)]
            self.refresh()
            return

        if self.selected == (r,c):
            self.selected = None
            self.highlight = []
            self.refresh()
            return

        allowed = legal_moves(self.board, self.player, self.last_move)
        found = None
        for m in allowed:
            fr, to = m[0], m[1]
            if fr == self.selected and to == (r,c):
                found = m; break

        if not found:
            if p != ' ' and ((self.player=='white' and is_white(p)) or (self.player=='black' and is_black(p))):
                self.selected = (r,c)
                self.highlight = [m[1] for m in allowed if m[0] == (r,c)]
                self.refresh()
                return
            return

        self.do_move(self.selected, (r,c))

    def do_move(self, fr, to):
        apply_move(self.board, fr, to)
        piece = self.board[to[0]][to[1]]

        if piece.upper() == 'K' and abs(to[1] - fr[1]) == 2:
            row = to[0]
            if to[1] == 6:
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = ' '
            else:
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = ' '

        if piece == 'P' and to[0] == 0:
            self.ask_promotion(to[0], to[1], 'white')
        if piece == 'p' and to[0] == 7:
            self.ask_promotion(to[0], to[1], 'black')

        self.last_move = (fr[0], fr[1], to)
        self.selected = None
        self.highlight = []
        self.player = 'black' if self.player == 'white' else 'white'

        icon = '♔' if self.player == 'white' else '♚'
        mode_text = "Два игрока" if not self.vs_bot else f"Бот ({self.difficulty})"
        self.status.config(text=f"{mode_text}  |  {icon} Ход: {'белые' if self.player=='white' else 'чёрные'}")
        self.refresh()

        moves = legal_moves(self.board, self.player, self.last_move)
        if not moves:
            self.game_over = True
            if in_check(self.board, self.player):
                winner = 'чёрные' if self.player == 'white' else 'белые'
                messagebox.showinfo("МАТ!", f"Победили {winner}.")
            else:
                messagebox.showinfo("ПАТ", "Ничья.")
            return

        if in_check(self.board, self.player):
            self.status.config(text=f"ШАХ!  {mode_text}  |  {icon} Ход: {'белые' if self.player=='white' else 'чёрные'}")

        if self.vs_bot and self.player == 'black':
            self.root.after(400, self.bot_turn)

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

        if self.difficulty == 'easy':
            move = random.choice(moves)
        elif self.difficulty == 'medium':
            best, best_score = None, -float('inf')
            for m in moves:
                fr, to = m[0], m[1]
                test = [row[:] for row in self.board]
                apply_move(test, fr, to)
                score = -evaluate(test)
                if score > best_score:
                    best_score, best = score, m
            move = best
        else:
            _, move = minimax(self.board, 2, -float('inf'), float('inf'), False, self.last_move)
            if move is None:
                move = random.choice(moves)

        self.do_move(move[0], move[1])


if __name__ == '__main__':
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()