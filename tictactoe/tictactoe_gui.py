# Крестики-нолики GUI — v8: большое окно, быстрый градиент

import tkinter as tk
from tkinter import messagebox
import random


# 4 скина
THEMES = {
    'dark': {
        'name': 'Dark',
        'bg': '#1e1e2e',
        'fg': '#cdd6f4',
        'x': '#f38ba8',
        'o': '#89b4fa',
        'btn': '#313244',
        'btn_active': '#45475a',
        'label': '#a6e3a1',
        'gradient': ['#1e1e2e', '#181825', '#11111b'],
    },
    'light': {
        'name': 'Light',
        'bg': '#eff1f5',
        'fg': '#4c4f69',
        'x': '#d20f39',
        'o': '#1e66f5',
        'btn': '#ccd0da',
        'btn_active': '#bcc0cc',
        'label': '#40a02b',
        'gradient': ['#eff1f5', '#e6e9ef', '#dce0e8'],
    },
    'ocean': {
        'name': 'Ocean',
        'bg': '#0a192f',
        'fg': '#ccd6f6',
        'x': '#ff6b6b',
        'o': '#64ffda',
        'btn': '#112240',
        'btn_active': '#1a365d',
        'label': '#64ffda',
        'gradient': ['#0a192f', '#0d2137', '#112240'],
    },
    'sunset': {
        'name': 'Sunset',
        'bg': '#2d1b2e',
        'fg': '#ffd6e0',
        'x': '#ff6b9d',
        'o': '#ffc75f',
        'btn': '#4a2c4d',
        'btn_active': '#5c3a5f',
        'label': '#ffc75f',
        'gradient': ['#2d1b2e', '#3d2340', '#4a2c4d'],
    },
}

THEME_ORDER = ['dark', 'light', 'ocean', 'sunset']


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.geometry("500x650")
        self.root.minsize(450, 600)

        self.theme_index = 0
        self.theme_name = THEME_ORDER[self.theme_index]
        self.theme = THEMES[self.theme_name]

        self.wins = {'X': 0, 'O': 0}
        self.draws = 0
        self.games_played = 0
        self.vs_computer = False

        self.root.configure(bg=self.theme['bg'])
        self.center_window()
        self.show_menu()

    def center_window(self):
        """Центрирует окно на экране."""
        self.root.update_idletasks()
        w = 500
        h = 650
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEME_ORDER)
        self.theme_name = THEME_ORDER[self.theme_index]
        self.theme = THEMES[self.theme_name]
        self.root.configure(bg=self.theme['bg'])
        self.show_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    @staticmethod
    def interpolate_color(c1, c2, t):
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def apply_gradient(self, frame, height=650, width=500):
        """Быстрый градиент: одна картинка через PhotoImage, без линий."""
        try:
            colors = self.theme['gradient']
            img = tk.PhotoImage(width=width, height=height)

            # Проходим по строкам, но добавляем цвет блоками по 5 строк — быстрее
            step = 2
            for y in range(0, height, step):
                pos = y / height
                idx = pos * (len(colors) - 1)
                c1 = int(idx)
                c2 = min(c1 + 1, len(colors) - 1)
                frac = idx - c1
                color = self.interpolate_color(colors[c1], colors[c2], frac)

                # Заливаем полосу
                img.put(color, to=(0, y, width, min(y + step, height)))

            # Создаём Label с картинкой и ложим в фон
            label = tk.Label(frame, image=img, bd=0, highlightthickness=0)
            label.image = img   # защита от сборки мусора
            label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            # Если что-то пошло не так — просто фон
            print(f"Градиент не загрузился: {e}")

    def show_menu(self):
        self.clear_window()
        t = self.theme

        # Фон
        bg = tk.Frame(self.root, bg=t['bg'])
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.apply_gradient(bg, height=650, width=500)

        # Центральный контейнер
        container = tk.Frame(self.root, bg=t['bg'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            container, text="КРЕСТИКИ-НОЛИКИ",
            font=('Arial', 28, 'bold'),
            bg=t['bg'], fg=t['label']
        ).pack(pady=(0, 40))

        def make_btn(text, bg_color, fg_color, command, pady=10):
            return tk.Button(
                container, text=text,
                font=('Arial', 16, 'bold'),
                bg=bg_color, fg=fg_color,
                activebackground=t['btn_active'], activeforeground=fg_color,
                relief='flat', bd=0, padx=40, pady=14, width=18,
                cursor='hand2',
                command=command
            ).pack(pady=pady)

        make_btn("Два игрока", t['btn'], t['fg'], lambda: self.start_game(False))
        make_btn("Против компьютера", t['btn'], t['fg'], lambda: self.start_game(True))
        make_btn("Итог игр", t['label'], t['bg'], self.show_stats)
        make_btn(f"Скин: {t['name']}", t['btn'], t['fg'], self.next_theme)

        make_btn("Выход", t['x'], t['bg'], self.root.destroy, pady=(30, 0))

    def show_stats(self):
        self.clear_window()
        t = self.theme

        bg = tk.Frame(self.root, bg=t['bg'])
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.apply_gradient(bg, height=650, width=500)

        container = tk.Frame(self.root, bg=t['bg'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            container, text="ИТОГ ИГР",
            font=('Arial', 28, 'bold'),
            bg=t['bg'], fg=t['label']
        ).pack(pady=(0, 30))

        stats_frame = tk.Frame(container, bg=t['bg'])
        stats_frame.pack(pady=10)

        def row(label, value, color=None):
            r = tk.Frame(stats_frame, bg=t['bg'])
            r.pack(pady=8, fill='x')
            tk.Label(
                r, text=label, font=('Arial', 16),
                bg=t['bg'], fg=t['fg'], width=18, anchor='w'
            ).pack(side='left')
            tk.Label(
                r, text=str(value), font=('Arial', 16, 'bold'),
                bg=t['bg'], fg=color or t['fg'], width=6, anchor='e'
            ).pack(side='right')

        row("Всего партий:", self.games_played)
        row("Победы X:", self.wins['X'], t['x'])
        row("Победы O:", self.wins['O'], t['o'])
        row("Ничьих:", self.draws)

        tk.Button(
            container, text="Назад",
            font=('Arial', 16, 'bold'),
            bg=t['btn'], fg=t['fg'],
            relief='flat', bd=0, padx=40, pady=14, width=18,
            cursor='hand2',
            command=self.show_menu
        ).pack(pady=(40, 0))

    def start_game(self, vs_computer):
        self.vs_computer = vs_computer
        self.clear_window()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        t = self.theme

        bg = tk.Frame(self.root, bg=t['bg'])
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.apply_gradient(bg, height=650, width=500)

        container = tk.Frame(self.root, bg=t['bg'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            container, text="КРЕСТИКИ-НОЛИКИ",
            font=('Arial', 22, 'bold'),
            bg=t['bg'], fg=t['label']
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self.status_label = tk.Label(
            container, text="Ход: X",
            font=('Arial', 16),
            bg=t['bg'], fg=t['fg']
        )
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.score_label = tk.Label(
            container, text="X: 0   O: 0   Ничьих: 0",
            font=('Arial', 12),
            bg=t['bg'], fg=t['fg']
        )
        self.score_label.grid(row=2, column=0, columnspan=3, pady=5)

        self.buttons_frame = tk.Frame(container, bg=t['bg'])
        self.buttons_frame.grid(row=3, column=0, columnspan=3, pady=15)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                self.buttons_frame,
                text=' ',
                font=('Arial', 32, 'bold'),
                width=3,
                height=1,
                bg=t['btn'], fg=t['fg'],
                activebackground=t['btn_active'],
                activeforeground=t['fg'],
                relief='flat',
                bd=0,
                cursor='hand2',
                command=lambda idx=i: self.on_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.buttons.append(btn)

        control = tk.Frame(container, bg=t['bg'])
        control.grid(row=4, column=0, columnspan=3, pady=20)

        def ctrl_btn(text, bg_color, fg_color, command):
            return tk.Button(
                control, text=text,
                font=('Arial', 12, 'bold'),
                bg=bg_color, fg=fg_color,
                relief='flat', bd=0,
                padx=12, pady=8,
                cursor='hand2',
                command=command
            ).pack(side='left', padx=4)

        ctrl_btn("Новая", t['label'], t['bg'], self.reset_game)
        ctrl_btn("Меню", t['btn'], t['fg'], self.show_menu)
        ctrl_btn("Скин", t['o'], t['bg'], self.next_theme)
        ctrl_btn("Выход", t['x'], t['bg'], self.root.destroy)

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