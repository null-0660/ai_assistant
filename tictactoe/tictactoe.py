# Крестики-нолики GUI — v11: звуки

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import os
import sys


# Звук — кроссплатформенно
def play_sound(kind='click'):
    """click / win / draw / error"""
    try:
        if sys.platform == 'win32':
            import winsound
            if kind == 'win':
                winsound.Beep(880, 300)
            elif kind == 'draw':
                winsound.Beep(440, 200)
            elif kind == 'error':
                winsound.Beep(200, 150)
            else:
                winsound.Beep(600, 50)
        elif sys.platform == 'darwin':
            os.system(f'afplay /System/Library/Sounds/Pop.aiff &')
        else:
            print('\a', end='', flush=True)
    except Exception:
        pass


THEMES = {
    'dark': {'name':'Dark','bg':'#1e1e2e','fg':'#cdd6f4','x':'#f38ba8','o':'#89b4fa',
             'btn':'#313244','btn_active':'#45475a','label':'#a6e3a1',
             'gradient':['#1e1e2e','#181825','#11111b']},
    'light': {'name':'Light','bg':'#eff1f5','fg':'#4c4f69','x':'#d20f39','o':'#1e66f5',
              'btn':'#ccd0da','btn_active':'#bcc0cc','label':'#40a02b',
              'gradient':['#eff1f5','#e6e9ef','#dce0e8']},
    'ocean': {'name':'Ocean','bg':'#0a192f','fg':'#ccd6f6','x':'#ff6b6b','o':'#64ffda',
              'btn':'#112240','btn_active':'#1a365d','label':'#64ffda',
              'gradient':['#0a192f','#0d2137','#112240']},
    'sunset': {'name':'Sunset','bg':'#2d1b2e','fg':'#ffd6e0','x':'#ff6b9d','o':'#ffc75f',
               'btn':'#4a2c4d','btn_active':'#5c3a5f','label':'#ffc75f',
               'gradient':['#2d1b2e','#3d2340','#4a2c4d']},
}

THEME_ORDER = ['dark','light','ocean','sunset']
WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-нолики")
        self.root.geometry("500x650")
        self.root.minsize(450, 600)

        self.theme_index = 0
        self.theme_name = THEME_ORDER[0]
        self.theme = THEMES[self.theme_name]

        self.wins = {'X':0,'O':0}
        self.draws = 0
        self.games_played = 0
        self.vs_computer = False
        self.names = {'X':'Игрок X','O':'Игрок O'}

        self.root.configure(bg=self.theme['bg'])
        self.center_window()
        self.show_menu()

    def center_window(self):
        self.root.update_idletasks()
        w,h = 500,650
        sw = self.root.winfo_screenwidth(); sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def next_theme(self):
        play_sound('click')
        self.theme_index = (self.theme_index+1) % len(THEME_ORDER)
        self.theme_name = THEME_ORDER[self.theme_index]
        self.theme = THEMES[self.theme_name]
        self.root.configure(bg=self.theme['bg'])
        self.show_menu()

    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    @staticmethod
    def interpolate_color(c1, c2, t):
        r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

    def apply_gradient(self, frame, h=650, w=500):
        try:
            cs = self.theme['gradient']
            img = tk.PhotoImage(width=w, height=h)
            for y in range(0, h, 2):
                pos = y/h; idx = pos*(len(cs)-1)
                c1 = int(idx); c2 = min(c1+1, len(cs)-1)
                img.put(self.interpolate_color(cs[c1], cs[c2], idx-c1),
                        to=(0, y, w, min(y+2, h)))
            lbl = tk.Label(frame, image=img, bd=0, highlightthickness=0)
            lbl.image = img
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"gradient error: {e}")

    def show_menu(self):
        self.clear_window()
        t = self.theme
        bg = tk.Frame(self.root, bg=t['bg']); bg.place(x=0,y=0,relwidth=1,relheight=1)
        self.apply_gradient(bg)
        c = tk.Frame(self.root, bg=t['bg']); c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="КРЕСТИКИ-НОЛИКИ", font=('Arial',28,'bold'),
                 bg=t['bg'], fg=t['label']).pack(pady=(0,40))

        def btn(text, bgc, fgc, cmd, pady=10):
            tk.Button(c, text=text, font=('Arial',16,'bold'), bg=bgc, fg=fgc,
                      activebackground=t['btn_active'], activeforeground=fgc,
                      relief='flat', bd=0, padx=40, pady=14, width=18,
                      cursor='hand2', command=cmd).pack(pady=pady)

        btn("Два игрока", t['btn'], t['fg'], lambda: self.start_game(False))
        btn("Против компьютера", t['btn'], t['fg'], lambda: self.start_game(True))
        btn("Итог игр", t['label'], t['bg'], self.show_stats)
        btn(f"Скин: {t['name']}", t['btn'], t['fg'], self.next_theme)
        btn("Выход", t['x'], t['bg'], self.root.destroy, pady=(30,0))

    def show_stats(self):
        self.clear_window()
        t = self.theme
        bg = tk.Frame(self.root, bg=t['bg']); bg.place(x=0,y=0,relwidth=1,relheight=1)
        self.apply_gradient(bg)
        c = tk.Frame(self.root, bg=t['bg']); c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="ИТОГ ИГР", font=('Arial',28,'bold'),
                 bg=t['bg'], fg=t['label']).pack(pady=(0,30))

        sf = tk.Frame(c, bg=t['bg']); sf.pack(pady=10)
        def row(label, value, color=None):
            r = tk.Frame(sf, bg=t['bg']); r.pack(pady=8, fill='x')
            tk.Label(r, text=label, font=('Arial',16), bg=t['bg'], fg=t['fg'],
                     width=18, anchor='w').pack(side='left')
            tk.Label(r, text=str(value), font=('Arial',16,'bold'),
                     bg=t['bg'], fg=color or t['fg'], width=6, anchor='e').pack(side='right')

        row("Всего партий:", self.games_played)
        row(f"Победы {self.names['X']}:", self.wins['X'], t['x'])
        row(f"Победы {self.names['O']}:", self.wins['O'], t['o'])
        row("Ничьих:", self.draws)

        tk.Button(c, text="Назад", font=('Arial',16,'bold'), bg=t['btn'], fg=t['fg'],
                  relief='flat', bd=0, padx=40, pady=14, width=18, cursor='hand2',
                  command=self.show_menu).pack(pady=(40,0))

    def ask_names(self, vs_computer):
        if vs_computer:
            name_x = simpledialog.askstring("Имя", "Как тебя зовут?", parent=self.root)
            self.names = {'X': name_x or 'Ты', 'O': 'Компьютер'}
        else:
            name_x = simpledialog.askstring("Имя X", "Имя первого?", parent=self.root)
            name_o = simpledialog.askstring("Имя O", "Имя второго?", parent=self.root)
            self.names = {'X': name_x or 'Игрок X', 'O': name_o or 'Игрок O'}

    def start_game(self, vs_computer):
        play_sound('click')
        self.vs_computer = vs_computer
        self.ask_names(vs_computer)
        self.clear_window()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        t = self.theme
        bg = tk.Frame(self.root, bg=t['bg']); bg.place(x=0,y=0,relwidth=1,relheight=1)
        self.apply_gradient(bg)
        c = tk.Frame(self.root, bg=t['bg']); c.place(relx=.5, rely=.5, anchor='center')

        tk.Label(c, text="КРЕСТИКИ-НОЛИКИ", font=('Arial',22,'bold'),
                 bg=t['bg'], fg=t['label']).grid(row=0, column=0, columnspan=3, pady=(0,10))

        self.status_label = tk.Label(c, text=f"Ход: {self.names['X']}",
                                     font=('Arial',16), bg=t['bg'], fg=t['fg'])
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.score_label = tk.Label(
            c, text=f"{self.names['X']}: 0   {self.names['O']}: 0   Ничьих: 0",
            font=('Arial',12), bg=t['bg'], fg=t['fg'])
        self.score_label.grid(row=2, column=0, columnspan=3, pady=5)

        bf = tk.Frame(c, bg=t['bg']); bf.grid(row=3, column=0, columnspan=3, pady=15)
        self.buttons = []
        for i in range(9):
            b = tk.Button(bf, text=' ', font=('Arial',32,'bold'), width=3, height=1,
                          bg=t['btn'], fg=t['fg'], activebackground=t['btn_active'],
                          activeforeground=t['fg'], relief='flat', bd=0, cursor='hand2',
                          command=lambda idx=i: self.on_click(idx))
            b.grid(row=i//3, column=i%3, padx=4, pady=4)
            self.buttons.append(b)

        ctrl = tk.Frame(c, bg=t['bg']); ctrl.grid(row=4, column=0, columnspan=3, pady=20)
        def cb(text, bgc, fgc, cmd):
            tk.Button(ctrl, text=text, font=('Arial',12,'bold'), bg=bgc, fg=fgc,
                      relief='flat', bd=0, padx=12, pady=8, cursor='hand2',
                      command=cmd).pack(side='left', padx=4)

        cb("Новая", t['label'], t['bg'], self.reset_game)
        cb("Меню", t['btn'], t['fg'], self.show_menu)
        cb("Скин", t['o'], t['bg'], self.next_theme)
        cb("Выход", t['x'], t['bg'], self.root.destroy)

    def reset_game(self):
        play_sound('click')
        t = self.theme
        self.board = [' ']*9
        self.player = 'X'
        self.game_over = False
        for b in self.buttons:
            b.config(text=' ', fg=t['fg'], bg=t['btn'], state='normal')
        self.status_label.config(text=f"Ход: {self.names['X']}", fg=t['fg'])

    def on_click(self, index):
        if self.game_over or self.board[index] != ' ':
            play_sound('error')
            return
        play_sound('click')
        t = self.theme
        self.board[index] = self.player
        self.buttons[index].config(
            text=self.player, fg=t['x'] if self.player=='X' else t['o'])

        line = self.get_winning_line(self.player)
        if line:
            self.finish_game(f"Победил {self.names[self.player]}!", t['label'], line)
            self.wins[self.player] += 1; self.games_played += 1
            return
        if ' ' not in self.board:
            self.finish_game("Ничья!", t['fg'], None)
            self.draws += 1; self.games_played += 1
            return

        self.player = 'O' if self.player=='X' else 'X'
        self.status_label.config(text=f"Ход: {self.names[self.player]}")
        if self.vs_computer and self.player == 'O':
            self.root.after(300, self.computer_turn)

    def computer_turn(self):
        if self.game_over: return
        t = self.theme
        idx = self.computer_move()
        self.board[idx] = 'O'
        self.buttons[idx].config(text='O', fg=t['o'])
        play_sound('click')

        line = self.get_winning_line('O')
        if line:
            self.finish_game(f"{self.names['O']} победил!", t['x'], line)
            self.wins['O'] += 1; self.games_played += 1
            return
        if ' ' not in self.board:
            self.finish_game("Ничья!", t['fg'], None)
            self.draws += 1; self.games_played += 1
            return

        self.player = 'X'
        self.status_label.config(text=f"Ход: {self.names['X']}")

    def computer_move(self):
        for i in range(9):
            if self.board[i] == ' ':
                test = self.board[:]; test[i]='O'
                if self.check_win_list(test,'O'): return i
        for i in range(9):
            if self.board[i] == ' ':
                test = self.board[:]; test[i]='X'
                if self.check_win_list(test,'X'): return i
        if self.board[4] == ' ': return 4
        return random.choice([i for i in range(9) if self.board[i]==' '])

    def get_winning_line(self, player):
        for a,b,c in WIN_LINES:
            if self.board[a] == self.board[b] == self.board[c] == player:
                return (a,b,c)
        return None

    def check_win_list(self, b, p):
        for a,bb,c in WIN_LINES:
            if b[a]==b[bb]==b[c]==p: return True
        return False

    def finish_game(self, message, color, line):
        self.game_over = True
        self.status_label.config(text=message, fg=color)

        if line:
            t = self.theme
            for i in line:
                self.buttons[i].config(bg=t['label'], fg=t['bg'])
            play_sound('win')
        else:
            play_sound('draw')

        self.update_score()
        for b in self.buttons:
            b.config(state='disabled')
        messagebox.showinfo("Игра окончена", message)

    def update_score(self):
        t = self.theme
        self.score_label.config(
            text=f"{self.names['X']}: {self.wins['X']}   {self.names['O']}: {self.wins['O']}   Ничьих: {self.draws}",
            fg=t['fg'])


if __name__ == '__main__':
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop()