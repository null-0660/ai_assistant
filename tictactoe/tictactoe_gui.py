# Крестики-нолики GUI — v3: цвета, шрифты, стиль

import tkinter as tk
from tkinter import messagebox


# Цвета
BG_COLOR = '#1e1e2e'
FG_COLOR = '#cdd6f4'
X_COLOR = '#f38ba8'
O_COLOR = '#89b4fa'
BTN_BG = '#313244'
BTN_ACTIVE = '#45475a'
LABEL_COLOR = '#a6e3a1'


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.wins = {'X': 0, 'O': 0}
        self.draws = 0

        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        # Заголовок
        tk.Label(
            self.root, text="КРЕСТИКИ-НОЛИКИ",
            font=('Arial', 20, 'bold'),
            bg=BG_COLOR, fg=LABEL_COLOR
        ).grid(row=0, column=0, columnspan=3, pady=(15, 5))

        # Статус
        self.status_label = tk.Label(
            self.root, text="Ход: X",
            font=('Arial', 14),
            bg=BG_COLOR, fg=FG_COLOR
        )
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        # Счёт
        self.score_label = tk.Label(
            self.root, text="X: 0   O: 0   Ничьих: 0",
            font=('Arial', 11),
            bg=BG_COLOR, fg=FG_COLOR
        )
        self.score_label.grid(row=2, column=0, columnspan=3, pady=5)

        # Кнопки 3x3
        self.buttons_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                self.buttons_frame,
                text=' ',
                font=('Arial', 26, 'bold'),
                width=3,
                height=1,
                bg=BTN_BG, fg=FG_COLOR,
                activebackground=BTN_ACTIVE,
                activeforeground=FG_COLOR,
                relief='flat',
                bd=0,
                command=lambda idx=i: self.on_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.buttons.append(btn)

        # Кнопки управления
        control = tk.Frame(self.root, bg=BG_COLOR)
        control.grid(row=4, column=0, columnspan=3, pady=15)

        tk.Button(
            control, text="Новая игра",
            font=('Arial', 12, 'bold'),
            bg=LABEL_COLOR, fg=BG_COLOR,
            relief='flat', bd=0,
            padx=15, pady=5,
            command=self.reset_game
        ).pack(side='left', padx=5)

        tk.Button(
            control, text="Выход",
            font=('Arial', 12, 'bold'),
            bg=X_COLOR, fg=BG_COLOR,
            relief='flat', bd=0,
            padx=15, pady=5,
            command=self.root.destroy
        ).pack(side='left', padx=5)

    def reset_game(self):
        self.board = [' '] * 9
        self.player = 'X'
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=' ', fg=FG_COLOR, state='normal')

        self.status_label.config(text="Ход: X", fg=FG_COLOR)

    def on_click(self, index):
        if self.game_over:
            return
        if self.board[index] != ' ':
            return

        self.board[index] = self.player

        color = X_COLOR if self.player == 'X' else O_COLOR
        self.buttons[index].config(text=self.player, fg=color)

        if self.check_win(self.player):
            self.finish_game(f"Победил {self.player}!", LABEL_COLOR)
            self.wins[self.player] += 1
            return

        if ' ' not in self.board:
            self.finish_game("Ничья!", FG_COLOR)
            self.draws += 1
            return

        self.player = 'O' if self.player == 'X' else 'X'
        self.status_label.config(text=f"Ход: {self.player}")

    def check_win(self, player):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        ]
        for a, b, c in lines:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return True
        return False

    def finish_game(self, message, color):
        self.game_over = True
        self.status_label.config(text=message, fg=color)
        self.update_score()
        for btn in self.buttons:
            btn.config(state='disabled')
        messagebox.showinfo("Игра окончена", message)

    def update_score(self):
        self.score_label.config(
            text=f"X: {self.wins['X']}   O: {self.wins['O']}   Ничьих: {self.draws}"
        )


if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()