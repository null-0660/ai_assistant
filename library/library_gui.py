# Библиотека GUI — v1: Десктопное приложение на Tkinter

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")


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


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Моя Библиотека")
        self.root.geometry("750x500")
        self.root.configure(bg="#1e1e2e")

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
        # Заголовок
        tk.Label(self.root, text="📚 Моя Библиотека", font=("Arial", 20, "bold"),
                 bg="#1e1e2e", fg="#a6e3a1").pack(pady=10)

        # Основной фрейм
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Таблица книг
        columns = ("title", "author", "year", "read", "rating")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("year", text="Год")
        self.tree.heading("read", text="Прочитана")
        self.tree.heading("rating", text="Оценка")

        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("year", width=60, anchor="center")
        self.tree.column("read", width=90, anchor="center")
        self.tree.column("rating", width=80, anchor="center")

        # Стилизация таблицы
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#313244",
                        foreground="#cdd6f4",
                        fieldbackground="#313244",
                        font=("Arial", 11))
        style.configure("Treeview.Heading",
                        background="#45475a",
                        foreground="#cdd6f4",
                        font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#89b4fa")])

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        # Кнопки справа
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(side="right", fill="y", padx=(10, 0))

        def make_btn(text, color, cmd):
            return tk.Button(btn_frame, text=text, font=("Arial", 12, "bold"),
                             bg=color, fg="#1e1e2e", relief="flat",
                             width=15, pady=8, cursor="hand2", command=cmd).pack(pady=5)

        make_btn("➕ Добавить", "#a6e3a1", self.add_book)
        make_btn("✅ Прочитано", "#f9e2af", self.toggle_read)
        make_btn("⭐ Оценить", "#f9e2af", self.set_rating)
        make_btn("🔍 Поиск", "#89b4fa", self.search)
        make_btn("📊 Статистика", "#89b4fa", self.show_stats)
        make_btn("🗑 Удалить", "#f38ba8", self.delete_book)
        make_btn("📤 Экспорт", "#cba6f7", self.export_menu)

        # Статус-бар
        self.status = tk.Label(self.root, text="Всего книг: 0", font=("Arial", 11),
                               bg="#1e1e2e", fg="#7f849c")
        self.status.pack(pady=5)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for b in self.books:
            read_status = "✅ Да" if b.is_read else "📖 Нет"
            stars = "⭐" * b.rating if b.rating > 0 else "—"
            self.tree.insert("", "end", values=(b.title, b.author, b.year, read_status, stars))

        self.status.config(text=f"Всего книг: {len(self.books)}")

    def get_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выбери книгу из списка!")
            return None
        idx = self.tree.index(selected[0])
        return idx

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

    def search(self):
        query = simpledialog.askstring("Поиск", "Название или автор:", parent=self.root)
        if not query: return
        query = query.lower()
        
        results = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for b in results:
            read_status = "✅ Да" if b.is_read else "📖 Нет"
            stars = "⭐" * b.rating if b.rating > 0 else "—"
            self.tree.insert("", "end", values=(b.title, b.author, b.year, read_status, stars))
            
        self.status.config(text=f"Найдено: {len(results)} (для сброса нажми 'Показать все')")

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
        # Упрощённый экспорт в TXT
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