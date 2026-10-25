# Крестики-нолики GUI — v2: логика, счёт, replay

import tkinter as tk
from tkinter import messagebox


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.resizable(False, False)

        self.wins = {'X': 0, 'O': 0}
        self.draws = 0

        self.status_label = tk.Label(
            root, text="Ход: X", font=('Arial', 14)
        )
        self.status_label.grid(row=0, column=0, columnspan=3, pady=5)

        self.score_label = tk.Label(
            root, text="X: 0   O: 0   Ничьих: 0", font=('Arial', 12)
        )
        self.score_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.grid(row=2, column=0, columnspan=3)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                self.buttons_frame,
                text=' ',
                font=('Arial', 24, 'bold'),
                width=3,
                height=1,
                command=lambda idx=i: self.on_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(btn)

        tk.Button(
            root, text="Новая игра", font=('Arial', 12),
            command=self.reset_game
        ).grid(row=3, column=0, pady=10)

        tk.Button(
            root, text="Выход", font=('Arial', 12),
            command=root.destroy
        ).grid(row=3, column=2, pady=10)

        self.reset_game()

    def reset_game(self):
        """Сбрасывает доску и игрока."""
        self.board = [' '] * 9
        self.player = 'X'
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=' ', state='normal')

        self.status_label.config(text="Ход: X")

    def on_click(self, index):
        """Обработка клика."""
        if self.game_over:
            return
        if self.board[index] != ' ':
            return

        self.board[index] = self.player
        self.buttons[index].config(text=self.player)

        if self.check_win(self.player):
            self.finish_game(f"Победил {self.player}!")
            self.wins[self.player] += 1
            return

        if ' ' not in self.board:
            self.finish_game("Ничья!")
            self.draws += 1
            return

        self.player = 'O' if self.player == 'X' else 'X'
        self.status_label.config(text=f"Ход: {self.player}")

    def check_win(self, player):
        """Проверка победы."""
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        ]
        for a, b, c in lines:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return True
        return False

    def finish_game(self, message):
        """Конец партии."""
        self.game_over = True
        self.status_label.config(text=message)
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