# Шахматы GUI — v1: доска, фигуры, клик-ход, бот

import tkinter as tk
from tkinter import messagebox
import random


WHITE_PIECES = {'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙'}
BLACK_PIECES = {'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟'}

LIGHT = '#f0d9b5'
DARK = '#b58863'
SELECT = '#f6f669'
WHITE_COLOR = '#ffffff'
BLACK_COLOR = '#000000'


def piece_symbol(p):
    if p == ' ':
        return ''
    if p.isupper():
        return WHITE_PIECES.get(p, p)
    return BLACK_PIECES.get(p, p)


def create_board():
    board = [[' '] * 8 for _ in range(8)]
    board[0] = ['r','n','b','q','k','b','n','r']
    board[1] = ['p'] * 8
    board[6] = ['P'] * 8
    board[7] = ['R','N','B','Q','K','B','N','R']
    return board


def is_white(p): return p.isupper()
def is_black(p): return p.islower() and p != ' '


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Шахматы")
        self.root.resizable(False, False)

        self.board = create_board()
        self.selected = None   # (row, col) выбранной фигуры
        self.player = 'white'
        self.vs_bot = False
        self.game_started = False

        self.buttons = []
        self.show_menu()

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_menu(self):
        self.clear_window()
        self.root.configure(bg='#2d2d2d')

        tk.Label(self.root, text="ШАХМАТЫ", font=('Arial', 28, 'bold'),
                 bg='#2d2d2d', fg='#ffffff').pack(pady=(40, 30))

        def btn(text, cmd):
            tk.Button(self.root, text=text, font=('Arial', 16, 'bold'),
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
        self.game_started = True
        self.clear_window()
        self.create_board_widgets()

    def create_board_widgets(self):
        self.root.configure(bg='#2d2d2d')

        self.status = tk.Label(self.root, text="Ход: белые",
                               font=('Arial', 16, 'bold'),
                               bg='#2d2d2d', fg='#ffffff')
        self.status.pack(pady=10)

        board_frame = tk.Frame(self.root, bg='#2d2d2d')
        board_frame.pack(padx=10, pady=10)

        self.buttons = []
        for r in range(8):
            row_btns = []
            for c in range(8):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                btn = tk.Button(
                    board_frame,
                    text='',
                    font=('Arial', 28),
                    width=2, height=1,
                    bg=color, fg=BLACK_COLOR,
                    relief='flat', bd=0,
                    activebackground=color,
                    command=lambda rr=r, cc=c: self.on_click(rr, cc)
                )
                btn.grid(row=r, column=c)
                row_btns.append(btn)
            self.buttons.append(row_btns)

        # Финальная кнопка «В меню»
        tk.Button(self.root, text="В меню", font=('Arial', 12, 'bold'),
                  bg='#4d4d4d', fg='#ffffff', relief='flat', bd=0,
                  padx=20, pady=8, cursor='hand2',
                  command=self.show_menu).pack(pady=10)

        self.refresh_board()

    def refresh_board(self):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                base = LIGHT if (r + c) % 2 == 0 else DARK
                btn = self.buttons[r][c]

                # Цвет выбранной клетки
                if self.selected == (r, c):
                    btn.config(bg=SELECT)
                else:
                    btn.config(bg=base)

                # Символ и цвет фигуры
                if p == ' ':
                    btn.config(text='')
                else:
                    btn.config(text=piece_symbol(p),
                               fg=WHITE_COLOR if is_white(p) else BLACK_COLOR)

    def on_click(self, r, c):
        if not self.game_started:
            return

        p = self.board[r][c]

        # Если ничего не выбрано — выбираем свою фигуру
        if self.selected is None:
            if p == ' ':
                return
            if self.player == 'white' and not is_white(p):
                return
            if self.player == 'black' and not is_black(p):
                return
            self.selected = (r, c)
            self.refresh_board()
            return

        # Если выбрана та же клетка — снять выбор
        if self.selected == (r, c):
            self.selected = None
            self.refresh_board()
            return

        # Проверка: не своя ли цель
        if p != ' ':
            if self.player == 'white' and not is_black(p):
                # Своя фигура — переключить выбор
                self.selected = (r, c)
                self.refresh_board()
                return
            if self.player == 'black' and not is_white(p):
                self.selected = (r, c)
                self.refresh_board()
                return

        # Выполнить ход
        fr = self.selected
        to = (r, c)
        self.board[to[0]][to[1]] = self.board[fr[0]][fr[1]]
        self.board[fr[0]][fr[1]] = ' '
        self.selected = None

        # Смена игрока
        self.player = 'black' if self.player == 'white' else 'white'
        self.status.config(text=f"Ход: {'белые' if self.player == 'white' else 'чёрные'}")
        self.refresh_board()

        # Ход бота
        if self.vs_bot and self.player == 'black':
            self.root.after(400, self.bot_turn)

    def bot_turn(self):
        moves = self.all_valid_moves('black')
        if not moves:
            messagebox.showinfo("Шахматы", "Бот не может ходить.")
            return
        fr, to = random.choice(moves)
        self.board[to[0]][to[1]] = self.board[fr[0]][fr[1]]
        self.board[fr[0]][fr[1]] = ' '

        self.player = 'white'
        self.status.config(text="Ход: белые")
        self.refresh_board()

    def all_valid_moves(self, player):
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == ' ': continue
                if player == 'white' and not is_white(p): continue
                if player == 'black' and not is_black(p): continue
                for tr in range(8):
                    for tc in range(8):
                        t = self.board[tr][tc]
                        if t == ' ':
                            moves.append(((r,c),(tr,tc)))
                        elif player == 'white' and is_black(t):
                            moves.append(((r,c),(tr,tc)))
                        elif player == 'black' and is_white(t):
                            moves.append(((r,c),(tr,tc)))
        return moves


if __name__ == '__main__':
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()