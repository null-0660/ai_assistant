# Библиотека GUI — v2: Современный дизайн (Catppuccin)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")

# ===== Палитра Catppuccin Mocha =====
BG = "#1e1e2e"          # Фон окна
BG_DARKER = "#181825"   # Фон полей
BG_LIGHT = "#313244"    # Фон элементов
FG = "#cdd6f4"          # Основной текст
FG_DIM = "#7f849c"      # Тусклый текст
GREEN = "#a6e3a1"       # Успех/добавить
RED = "#f38ba8"         # Удаление
YELLOW = "#f9e2af"      # Оценка/прочитано
BLUE = "#89b4fa"        # Поиск/инфо
PURPLE = "#cba6f7"      # Экспорт
CYAN = "#89dceb"        # Акценты


class Book:
    def __init__(self, title, author, year, is_read=False, rating=0):
        self.title = title
        self.author = author
        self.year = year
        self.is_read = is_read
        self.rating = rating

    def to_dict(self):
        return {"title": self.title, "author": self.author, "year": self.year,
                "is_read": self.is_read, "rating": self.rating}

    @staticmethod
    def from_dict(data):
        return Book(data["title"], data["author"], data["year"],
                    data.get("is_read", False), data.get("rating", 0))


class RoundedButton(tk.Canvas):
    """Кастомная кнопка с закруглёнными углами и hover-эффектом."""
    def __init__(self, parent, text, color, hover_color, command, width=180, height=40):
        super().__init__(parent, width=width, height=height, bg=BG, highlightthickness=0, bd=0)
        self.color = color
        self.hover_color = hover_color
        self.command = command
        self.text = text
        self.w = width
        self.h = height
        
        self.rect = self.create_round_rect(2, 2, width-2, height-2, 8, fill=color, outline="")
        self.text_id = self.create_text(width/2, height/2, text=text, fill="#11111b", font=("Segoe UI", 10, "bold"))
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        self.command()

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.color)


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Библиотека")
        self.root.geometry("850x600")
        self.root.configure(bg=BG)
        self.root.minsize(800, 500)

        self.books = []
        self.load()

        self.create_widgets()
        self.refresh_list()

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.books = [Book.from_dict(b) for b in data]
            except Exception:
                self.books = []

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def create_widgets(self):
        # ===== Верхняя панель =====
        top_bar = tk.Frame(self.root, bg=BG)
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        # Заголовок
        tk.Label(top_bar, text="📚 Моя Библиотека", font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=GREEN).pack(side="left")

        # Поиск
        search_frame = tk.Frame(top_bar, bg=BG_DARKER, padx=10, pady=5)
        search_frame.pack(side="right")
        
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 12), bg=BG_DARKER, fg=FG_DIM).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_list())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11),
                                bg=BG_DARKER, fg=FG, insertbackground=FG, relief="flat", width=20)
        search_entry.pack(side="left")

        # ===== Основной контент =====
        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Таблица
        columns = ("title", "author", "year", "read", "rating")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("year", text="Год")
        self.tree.heading("read", text="Статус")
        self.tree.heading("rating", text="Оценка")

        self.tree.column("title", width=250)
        self.tree.column("author", width=180)
        self.tree.column("year", width=70, anchor="center")
        self.tree.column("read", width=100, anchor="center")
        self.tree.column("rating", width=90, anchor="center")

        # Стили таблицы
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG_DARKER,
                        foreground=FG,
                        fieldbackground=BG_DARKER,
                        font=("Segoe UI", 11),
                        rowheight=35,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_LIGHT,
                        foreground=FG,
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.map("Treeview.Heading", background=[("active", BG_LIGHT)])
        style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", BG_DARKER)])

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        # Кнопки справа
        btn_frame = tk.Frame(main_frame, bg=BG)
        btn_frame.pack(side="right", fill="y", padx=(15, 0))

        RoundedButton(btn_frame, "➕ Добавить", GREEN, "#94d689", self.add_book).pack(pady=5)
        RoundedButton(btn_frame, "✅ Прочитано", YELLOW, "#e6c88c", self.toggle_read).pack(pady=5)
        RoundedButton(btn_frame, "⭐ Оценить", YELLOW, "#e6c88c", self.set_rating).pack(pady=5)
        RoundedButton(btn_frame, "📊 Статистика", BLUE, "#6f99d9", self.show_stats).pack(pady=5)
        RoundedButton(btn_frame, "🗑 Удалить", RED, "#d96b8b", self.delete_book).pack(pady=5)
        RoundedButton(btn_frame, "📤 Экспорт", PURPLE, "#b48de6", self.export_menu).pack(pady=5)

        # ===== Статус-бар =====
        self.status = tk.Label(self.root, text="", font=("Segoe UI", 10),
                               bg=BG_DARKER, fg=FG_DIM, anchor="w", padx=20, pady=8)
        self.status.pack(fill="x", side="bottom")

    def refresh_list(self, books=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        display_books = books if books is not None else self.books
        
        for b in display_books:
            read_status = "✅ Прочитана" if b.is_read else "📖 В планах"
            stars = "⭐" * b.rating if b.rating > 0 else "—"
            self.tree.insert("", "end", values=(b.title, b.author, b.year, read_status, stars))

        total = len(self.books)
        read = sum(1 for b in self.books if b.is_read)
        self.status.config(text=f"Всего книг: {total}  |  Прочитано: {read}  |  В планах: {total - read}")

    def filter_list(self):
        query = self.search_var.get().lower()
        if not query:
            self.refresh_list()
        else:
            filtered = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
            self.refresh_list(filtered)

    def get_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выбери книгу из списка!")
            return None
        values = self.tree.item(selected[0], "values")
        # Ищем по названию и автору (на случай если фильтр включён)
        for i, b in enumerate(self.books):
            if b.title == values[0] and b.author == values[1]:
                return i
        return None

    def add_book(self):
        title = simpledialog.askstring("Добавить книгу", "Название:", parent=self.root)
        if not title: return
        author = simpledialog.askstring("Добавить книгу", "Автор:", parent=self.root)
        if not author: return
        year_str = simpledialog.askstring("Добавить книгу", "Год:", parent=self.root)
        if not year_str: return
        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return

        self.books.append(Book(title, author, year))
        self.save()
        self.refresh_list()

    def toggle_read(self):
        idx = self.get_selected()
        if idx is None: return
        self.books[idx].is_read = not self.books[idx].is_read
        self.save()
        self.refresh_list()

    def set_rating(self):
        idx = self.get_selected()
        if idx is None: return
        rating = simpledialog.askinteger("Оценка", "Оценка (1-5):", minvalue=1, maxvalue=5, parent=self.root)
        if rating:
            self.books[idx].rating = rating
            self.save()
            self.refresh_list()

    def delete_book(self):
        idx = self.get_selected()
        if idx is None: return
        if messagebox.askyesno("Удалить", f"Удалить «{self.books[idx].title}»?"):
            self.books.pop(idx)
            self.save()
            self.refresh_list()

    def show_stats(self):
        if not self.books:
            messagebox.showinfo("Статистика", "Библиотека пуста.")
            return
        read = sum(1 for b in self.books if b.is_read)
        years = [b.year for b in self.books]
        avg_year = sum(years) / len(years)
        rated = [b for b in self.books if b.rating > 0]
        avg_r = sum(b.rating for b in rated) / len(rated) if rated else 0
        
        msg = (f"Всего книг: {len(self.books)}\n"
               f"Прочитано: {read}\n"
               f"Не прочитано: {len(self.books) - read}\n"
               f"Средний год: {avg_year:.0f}\n"
               f"Средний рейтинг: {avg_r:.1f} ⭐")
        messagebox.showinfo("📊 Статистика", msg)

    def export_menu(self):
        try:
            export_path = os.path.join(os.path.dirname(__file__), "library_export.txt")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("МОЯ БИБЛИОТЕКА\n" + "="*40 + "\n")
                for i, b in enumerate(self.books, 1):
                    status = "✓" if b.is_read else "○"
                    f.write(f"{i}. {status} «{b.title}» — {b.author} ({b.year}) | Оценка: {b.rating}\n")
            messagebox.showinfo("Экспорт", f"Сохранено в:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()