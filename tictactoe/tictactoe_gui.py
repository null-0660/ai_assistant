# Крестики-нолики GUI — v6: темы (тёмная/светлая)

import tkinter as tk
from tkinter import messagebox
import random


# Темы
THEMES = {
    'dark': {
        'bg': '#1e1e2e',
        'fg': '#cdd6f4',
        'x': '#f38ba8',
        'o': '#89b4fa',
        'btn': '#313244',
        'btn_active': '#45475a',
        'label': '#a6e3a1',
    },
    'light': {
        'bg': '#eff1f5',
        'fg': '#4c4f69',
        'x': '#d20f39',
        'o': '#1e66f5',
        'btn': '#ccd0da',
        'btn_active': '#bcc0cc',
        'label': '#40a02b',
    },
}


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.resizable(False, False)

        self.theme_name = 'dark'
        self.theme = THEMES[self.theme_name]

        self.wins = {'X': 0, 'O': 0}
        self.draws = 0
        self.games_played = 0
        self.vs_computer = False

        self.root.configure(bg=self.theme['bg'])
        self.show_menu()

    def toggle_theme(self):
        """Переключение темы."""
        self.theme_name = 'light' if self.theme_name == 'dark' else 'dark'
        self.theme = THEMES[self.theme_name]
        self.root.configure(bg=self.theme['bg'])
        self.show_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_window()
        t = self.theme

        tk.Label(
            self.root, text="КРЕСТИКИ-НОЛИКИ",
            font=('Arial', 20, 'bold'),
            bg=t['bg'], fg=t['label']
        ).pack(pady=(30, 20))

        tk.Button(
            self.root, text="Два игрока",
            font=('Arial', 14, 'bold'),
            bg=t['btn'], fg=t['fg'],
            activebackground=t['btn_active'], activeforeground=t['fg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=lambda: self.start_game(False)
        ).pack(pady=8)

        tk.Button(
            self.root, text="Против компьютера",
            font=('Arial', 14, 'bold'),
            bg=t['btn'], fg=t['fg'],
            activebackground=t['btn_active'], activeforeground=t['fg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=lambda: self.start_game(True)
        ).pack(pady=8)

        tk.Button(
            self.root, text="Итог игр",
            font=('Arial', 14, 'bold'),
            bg=t['label'], fg=t['bg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=self.show_stats
        ).pack(pady=8)

        tk.Button(
            self.root, text=f"Тема: {self.theme_name}",
            font=('Arial', 14, 'bold'),
            bg=t['btn'], fg=t['fg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=self.toggle_theme
        ).pack(pady=8)

        tk.Button(
            self.root, text="Выход",
            font=('Arial', 14, 'bold'),
            bg=t['x'], fg=t['bg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=self.root.destroy
        ).pack(pady=(20, 10))

    def show_stats(self):
        self.clear_window()
        t = self.theme

        tk.Label(
            self.root, text="ИТОГ ИГР",
            font=('Arial', 20, 'bold'),
            bg=t['bg'], fg=t['label']
        ).pack(pady=(30, 20))

        stats_frame = tk.Frame(self.root, bg=t['bg'])
        stats_frame.pack(pady=10)

        def row(label, value, color=None):
            frame = tk.Frame(stats_frame, bg=t['bg'])
            frame.pack(pady=5, fill='x')
            tk.Label(
                frame, text=label, font=('Arial', 14),
                bg=t['bg'], fg=t['fg'], width=18, anchor='w'
            ).pack(side='left')
            tk.Label(
                frame, text=str(value), font=('Arial', 14, 'bold'),
                bg=t['bg'], fg=color or t['fg'], width=6, anchor='e'
            ).pack(side='right')

        row("Всего партий:", self.games_played)
        row("Победы X:", self.wins['X'], t['x'])
        row("Победы O:", self.wins['O'], t['o'])
        row("Ничьих:", self.draws)

        tk.Button(
            self.root, text="Назад",
            font=('Arial', 14, 'bold'),
            bg=t['btn'], fg=t['fg'],
            relief='flat', bd=0, padx=30, pady=10,
            command=self.show_menu
        ).pack(pady=(30, 10))

    def start_game(self, vs_computer):
        self.vs_computer = vs_computer
        self.clear_window()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        t = self.theme

        self.title_label = tk.Label(
            self.root, text="КРЕСТИКИ-НОЛИКИ",
            font=('Arial', 20, 'bold'),
            bg=t['bg'], fg=t['label']
        )
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(15, 5))

        self.status_label = tk.Label(
            self.root, text="Ход: X",
            font=('Arial', 14),
            bg=t['bg'], fg=t['fg']
        )
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.score_label = tk.Label(
            self.root, text="X: 0   O: 0   Ничьих: 0",
            font=('Arial', 11),
            bg=t['bg'], fg=t['fg']
        )
        self.score_label.grid(row=2, column=0, columnspan=3, pady=5)

        self.buttons_frame = tk.Frame(self.root, bg=t['bg'])
        self.buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                self.buttons_frame,
                text=' ',
                font=('Arial', 26, 'bold'),
                width=3,
                height=1,
                bg=t['btn'], fg=t['fg'],
                activebackground=t['btn_active'],
                activeforeground=t['fg'],
                relief='flat',
                bd=0,
                command=lambda idx=i: self.on_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.buttons.append(btn)

        control = tk.Frame(self.root, bg=t['bg'])
        control.grid(row=4, column=0, columnspan=3, pady=15)

        tk.Button(
            control, text="Новая игра",
            font=('Arial', 12, 'bold'),
            bg=t['label'], fg=t['bg'],
            relief='flat', bd=0,
            padx=15, pady=5,
            command=self.reset_game
        ).pack(side='left', padx=5)

        tk.Button(
            control, text="В меню",
            font=('Arial', 12, 'bold'),
            bg=t['btn'], fg=t['fg'],
            relief='flat', bd=0,
            padx=15, pady=5,
            command=self.show_menu
        ).pack(side='left', padx=5)

        tk.Button(
            control, text="Выход",
            font=('Arial', 12, 'bold'),
            bg=t['x'], fg=t['bg'],
            relief='flat', bd=0,
            padx=15, pady=5,
            command=self.root.destroy
        ).pack(side='left', padx=5)

    def reset_game(self):
        t = self.theme
        self.board = [' '] * 9
        self.player = 'X'
        self.game_over = False

        for btn in self.buttons:
            btn.config(text=' ', fg=t['fg'], state='normal')

        self.status_label.config(text="Ход: X", fg=t['fg'])

    def on_click(self, index):
        if self.game_over:
            return
        if self.board[index] != ' ':
            return

        t = self.theme
        self.board[index] = self.player
        color = t['x'] if self.player == 'X' else t['o']
        self.buttons[index].config(text=self.player, fg=color)

        if self.check_win(self.player):
            self.finish_game(f"Победил {self.player}!", t['label'])
            self.wins[self.player] += 1
            self.games_played += 1
            return

        if ' ' not in self.board:
            self.finish_game("Ничья!", t['fg'])
            self.draws += 1
            self.games_played += 1
            return

        self.player = 'O' if self.player == 'X' else 'X'
        self.status_label.config(text=f"Ход: {self.player}")

        if self.vs_computer and self.player == 'O':
            self.root.after(300, self.computer_turn)

    def computer_turn(self):
        if self.game_over:
            return

        t = self.theme
        index = self.computer_move()
        self.board[index] = 'O'
        self.buttons[index].config(text='O', fg=t['o'])

        if self.check_win('O'):
            self.finish_game("Компьютер победил!", t['x'])
            self.wins['O'] += 1
            self.games_played += 1
            return

        if ' ' not in self.board:
            self.finish_game("Ничья!", t['fg'])
            self.draws += 1
            self.games_played += 1
            return

        self.player = 'X'
        self.status_label.config(text="Ход: X")

    def computer_move(self):
        for i in range(9):
            if self.board[i] == ' ':
                test = self.board[:]
                test[i] = 'O'
                if self.check_win_list(test, 'O'):
                    return i
        for i in range(9):
            if self.board[i] == ' ':
                test = self.board[:]
                test[i] = 'X'
                if self.check_win_list(test, 'X'):
                    return i
        if self.board[4] == ' ':
            return 4
        free = [i for i in range(9) if self.board[i] == ' ']
        return random.choice(free)

    def check_win(self, player):
        return self.check_win_list(self.board, player)

    def check_win_list(self, board, player):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        ]
        for a, b, c in lines:
            if board[a] == board[b] == board[c] == player:
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
        t = self.theme
        self.score_label.config(
            text=f"X: {self.wins['X']}   O: {self.wins['O']}   Ничьих: {self.draws}",
            fg=t['fg']
        )


if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()