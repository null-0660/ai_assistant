# Крестики-нолики GUI — v1: окно и кнопки

import tkinter as tk


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.resizable(False, False)

        self.board = [' '] * 9
        self.player = 'X'
        self.buttons = []

        self.create_widgets()

    def create_widgets(self):
        """Создаёт 9 кнопок в сетке 3x3."""
        for i in range(9):
            btn = tk.Button(
                self.root,
                text=' ',
                font=('Arial', 24, 'bold'),
                width=3,
                height=1,
                command=lambda idx=i: self.on_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(btn)

    def on_click(self, index):
        """Обработка клика по кнопке."""
        if self.board[index] != ' ':
            return

        self.board[index] = self.player
        self.buttons[index].config(text=self.player)

        self.player = 'O' if self.player == 'X' else 'X'


if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()