# Библиотека GUI — v3: Современный UI на CustomTkinter

import customtkinter as ctk
from tkinter import messagebox, simpledialog
import json
import os
import tkinter as tk

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")

# Настройка темы
ctk.set_appearance_mode("dark")  # Темная тема
ctk.set_default_color_theme("blue")  # Синий акцент

# Цвета
COLOR_BG = "#1e1e2e"
COLOR_FRAME = "#181825"
COLOR_GREEN = "#a6e3a1"
COLOR_RED = "#f38ba8"
COLOR_YELLOW = "#f9e2af"
COLOR_TEXT = "#cdd6f4"


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


class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("📚 Моя Библиотека")
        self.geometry("950x600")
        self.minsize(800, 500)
        
        # Основной фон
        self.configure(fg_color=COLOR_BG)

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
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Заголовок
        title_label = ctk.CTkLabel(top_frame, text="📚 Моя Библиотека", 
                                   font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                   text_color=COLOR_GREEN)
        title_label.pack(side="left")

        # Поиск на лету
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_list())
        
        search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var, 
                                    placeholder_text="🔍 Поиск по названию или автору...",
                                    width=300, height=35,
                                    font=ctk.CTkFont(family="Segoe UI", size=13),
                                    fg_color=COLOR_FRAME, border_width=0)
        search_entry.pack(side="right")

        # ===== Основной контент =====
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Левая панель — Таблица
        table_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_FRAME, corner_radius=10)
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("title", "author", "year", "read", "rating")
        self.tree = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Шапка таблицы
        header_frame = ctk.CTkFrame(self.tree, fg_color=COLOR_BG, height=35)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="Название", width=200, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Автор", width=150, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Год", width=60, anchor="center", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Статус", width=100, anchor="center", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Оценка", width=80, anchor="center", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        self.rows_frame = ctk.CTkFrame(self.tree, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True)

        # Правая панель — Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=200)
        btn_frame.pack(side="right", fill="y", padx=(20, 0))

        # Стили кнопок
        btn_style = {
            "font": ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            "height": 40,
            "corner_radius": 10,
            "anchor": "w",
            "text_color": "#11111b"
        }

        ctk.CTkButton(btn_frame, text="➕ Добавить книгу", fg_color=COLOR_GREEN, 
                      hover_color="#94d689", command=self.add_book, **btn_style).pack(pady=8, fill="x")
        
        ctk.CTkButton(btn_frame, text="✅ Отметить прочитанной", fg_color=COLOR_YELLOW, 
                      hover_color="#e6c88c", command=self.toggle_read, **btn_style).pack(pady=8, fill="x")
        
        ctk.CTkButton(btn_frame, text="⭐ Поставить оценку", fg_color=COLOR_YELLOW, 
                      hover_color="#e6c88c", command=self.set_rating, **btn_style).pack(pady=8, fill="x")
        
        ctk.CTkButton(btn_frame, text="📊 Статистика", fg_color="#89b4fa", 
                      hover_color="#6f99d9", command=self.show_stats, **btn_style).pack(pady=8, fill="x")
        
        ctk.CTkButton(btn_frame, text="📤 Экспорт в TXT", fg_color="#cba6f7", 
                      hover_color="#b48de6", command=self.export_menu, **btn_style).pack(pady=8, fill="x")
        
        ctk.CTkButton(btn_frame, text="🗑 Удалить книгу", fg_color=COLOR_RED, 
                      hover_color="#d96b8b", command=self.delete_book, **btn_style).pack(pady=8, fill="x")

        # ===== Статус-бар =====
        self.status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=12),
                                   text_color="#7f849c", anchor="w")
        self.status.pack(fill="x", padx=25, pady=(0, 15))

    def refresh_list(self, books=None):
        # Очищаем старые строки
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        display_books = books if books is not None else self.books
        
        # Создаем строки
        for b in display_books:
            row = ctk.CTkFrame(self.rows_frame, fg_color=COLOR_BG, height=45, corner_radius=5)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"«{b.title}»", width=200, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=b.author, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(b.year), width=60, anchor="center").pack(side="left", padx=5)
            
            read_text = "✅ Прочитана" if b.is_read else "📖 В планах"
            read_color = COLOR_GREEN if b.is_read else COLOR_YELLOW
            ctk.CTkLabel(row, text=read_text, width=100, anchor="center", text_color=read_color).pack(side="left", padx=5)
            
            stars = "⭐" * b.rating if b.rating > 0 else "—"
            ctk.CTkLabel(row, text=stars, width=80, anchor="center").pack(side="left", padx=5)

        total = len(self.books)
        read = sum(1 for b in self.books if b.is_read)
        self.status.configure(text=f"Всего книг: {total}  |  Прочитано: {read}  |  В планах: {total - read}")

    def filter_list(self):
        query = self.search_var.get().lower()
        if not query:
            self.refresh_list()
        else:
            filtered = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
            self.refresh_list(filtered)

    def get_selected(self):
        # В CustomTkinter нет стандартного выделения, поэтому используем ввод номера
        # Или можно искать по названию. Упростим: пусть выбирает через диалоговое окно.
        # Но для красоты сделаем кастомный диалог выбора.
        if not self.books:
            messagebox.showinfo("Инфо", "Библиотека пуста.")
            return None
        
        # Просто спросим номер книги (от 1 до N)
        try:
            num = simpledialog.askinteger("Выбор книги", f"Введите номер книги (1-{len(self.books)}):", 
                                          minvalue=1, maxvalue=len(self.books), parent=self)
            if num is None: return None
            return num - 1
        except:
            return None

    def add_book(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавить книгу")
        dialog.geometry("350x300")
        dialog.configure(fg_color=COLOR_BG)
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Новая книга", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_GREEN).pack(pady=15)
        
        ctk.CTkLabel(dialog, text="Название:", anchor="w").pack(fill="x", padx=20)
        title_entry = ctk.CTkEntry(dialog, width=300, fg_color=COLOR_FRAME)
        title_entry.pack(pady=(0, 10), padx=20)
        
        ctk.CTkLabel(dialog, text="Автор:", anchor="w").pack(fill="x", padx=20)
        author_entry = ctk.CTkEntry(dialog, width=300, fg_color=COLOR_FRAME)
        author_entry.pack(pady=(0, 10), padx=20)
        
        ctk.CTkLabel(dialog, text="Год:", anchor="w").pack(fill="x", padx=20)
        year_entry = ctk.CTkEntry(dialog, width=300, fg_color=COLOR_FRAME)
        year_entry.pack(pady=(0, 15), padx=20)
        
        def save_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            year_str = year_entry.get().strip()
            
            if not title or not author:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            try:
                year = int(year_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Год должен быть числом!")
                return
                
            self.books.append(Book(title, author, year))
            self.save()
            self.refresh_list()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Сохранить", fg_color=COLOR_GREEN, text_color="#11111b", command=save_book).pack(pady=10)

    def toggle_read(self):
        idx = self.get_selected()
        if idx is None: return
        self.books[idx].is_read = not self.books[idx].is_read
        self.save()
        self.refresh_list()

    def set_rating(self):
        idx = self.get_selected()
        if idx is None: return
        rating = simpledialog.askinteger("Оценка", "Оценка (1-5):", minvalue=1, maxvalue=5, parent=self)
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
    app = LibraryApp()
    app.mainloop()