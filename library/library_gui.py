# Библиотека GUI — v4: Идеальный дизайн (CustomTkinter)

import customtkinter as ctk
from tkinter import messagebox, simpledialog
import json
import os
import tkinter as tk

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")

# Настройки темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Цвета
BG_MAIN = "#181825"      # Темный фон
BG_PANEL = "#1e1e2e"     # Панели
BG_ROW = "#313244"       # Строки таблицы
BG_HOVER = "#45475a"     # Наведение на строку
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
BLUE = "#89b4fa"
PURPLE = "#cba6f7"
TEXT = "#cdd6f4"
TEXT_DIM = "#7f849c"


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
        self.geometry("1000x650")
        self.minsize(850, 500)
        self.configure(fg_color=BG_MAIN)

        self.books = []
        self.selected_index = None  # Индекс выбранной книги
        self.row_frames = []        # Ссылки на фреймы строк для подсветки
        
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

        ctk.CTkLabel(top_frame, text="📚 Моя Библиотека", 
                     font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                     text_color=GREEN).pack(side="left")

        # Поиск
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_list())
        
        search_entry = ctk.CTkEntry(top_frame, textvariable=self.search_var, 
                                    placeholder_text="🔍 Поиск (название или автор)...",
                                    width=300, height=40,
                                    font=ctk.CTkFont(family="Segoe UI", size=14),
                                    fg_color=BG_PANEL, border_width=0)
        search_entry.pack(side="right")

        # ===== Основной контент =====
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Левая панель — Таблица
        table_frame = ctk.CTkFrame(main_frame, fg_color=BG_PANEL, corner_radius=12)
        table_frame.pack(side="left", fill="both", expand=True)

        # Шапка таблицы (фиксированная)
        header = ctk.CTkFrame(table_frame, fg_color=BG_MAIN, height=45, corner_radius=8)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="Название", width=220, anchor="w", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Автор", width=160, anchor="w", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Год", width=70, anchor="center", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Статус", width=110, anchor="center", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Оценка", width=90, anchor="center", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)

        # Прокручиваемый список
        self.scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Правая панель — Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=220)
        btn_frame.pack(side="right", fill="y", padx=(15, 0))

        def make_btn(text, color, hover, cmd):
            return ctk.CTkButton(btn_frame, text=text, fg_color=color, hover_color=hover,
                                 text_color="#11111b", font=ctk.CTkFont(size=14, weight="bold"),
                                 height=45, corner_radius=10, anchor="w", command=cmd)

        make_btn("➕ Добавить книгу", GREEN, "#94d689", self.add_book).pack(pady=6, fill="x")
        make_btn("✅ Прочитано", YELLOW, "#e6c88c", self.toggle_read).pack(pady=6, fill="x")
        make_btn("⭐ Оценить", YELLOW, "#e6c88c", self.set_rating).pack(pady=6, fill="x")
        make_btn("📊 Статистика", BLUE, "#6f99d9", self.show_stats).pack(pady=6, fill="x")
        make_btn("📤 Экспорт", PURPLE, "#b48de6", self.export_menu).pack(pady=6, fill="x")
        make_btn("🗑 Удалить", RED, "#d96b8b", self.delete_book).pack(pady=(25, 6), fill="x")

        # Статус-бар
        self.status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13),
                                   text_color=TEXT_DIM, anchor="w")
        self.status.pack(fill="x", padx=25, pady=(0, 15))

    def refresh_list(self, books=None):
        # Очищаем список
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.row_frames.clear()
        
        display_books = books if books is not None else self.books
        
        for i, b in enumerate(display_books):
            # Фрейм строки
            row = ctk.CTkFrame(self.scroll_frame, fg_color=BG_ROW, height=45, corner_radius=6, cursor="hand2")
            row.pack(fill="x", pady=3, padx=5)
            row.pack_propagate(False)
            
            # Сохраняем связь индекса
            row.book_index = self.books.index(b)
            self.row_frames.append(row)
            
            # Привязка клика ко всей строке
            row.bind("<Button-1>", lambda e, r=row: self.select_row(r))
            
            # Текст
            ctk.CTkLabel(row, text=f"«{b.title}»", width=220, anchor="w", font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=b.author, width=160, anchor="w", fg_color="transparent").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(b.year), width=70, anchor="center", fg_color="transparent").pack(side="left", padx=5)
            
            read_text = "✅ Прочитана" if b.is_read else "📖 В планах"
            read_color = GREEN if b.is_read else YELLOW
            ctk.CTkLabel(row, text=read_text, width=110, anchor="center", text_color=read_color, fg_color="transparent").pack(side="left", padx=5)
            
            stars = "⭐" * b.rating if b.rating > 0 else "—"
            ctk.CTkLabel(row, text=stars, width=90, anchor="center", fg_color="transparent").pack(side="left", padx=5)

            # Hover-эффект (при наведении мыши)
            row.bind("<Enter>", lambda e, r=row: r.configure(fg_color=BG_HOVER) if self.selected_index != r.book_index else None)
            row.bind("<Leave>", lambda e, r=row: r.configure(fg_color=BG_ROW) if self.selected_index != r.book_index else None)

        total = len(self.books)
        read = sum(1 for b in self.books if b.is_read)
        self.status.configure(text=f"Всего книг: {total}  |  Прочитано: {read}  |  В планах: {total - read}")

    def select_row(self, row):
        # Снимаем выделение со всех
        for r in self.row_frames:
            r.configure(fg_color=BG_ROW)
        # Подсвечиваем выбранную
        row.configure(fg_color=BLUE)
        self.selected_index = row.book_index

    def filter_list(self):
        query = self.search_var.get().lower()
        if not query:
            self.refresh_list()
        else:
            filtered = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
            self.refresh_list(filtered)

    def get_selected(self):
        if self.selected_index is None:
            messagebox.showwarning("Внимание", "Сначала выбери книгу из списка!")
            return None
        return self.selected_index

    def add_book(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавить книгу")
        dialog.geometry("400x350")
        dialog.configure(fg_color=BG_PANEL)
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="➕ Новая книга", font=ctk.CTkFont(size=22, weight="bold"), text_color=GREEN).pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Название:", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=30)
        title_entry = ctk.CTkEntry(dialog, width=340, height=35, font=ctk.CTkFont(size=14))
        title_entry.pack(pady=(0, 10), padx=30)
        
        ctk.CTkLabel(dialog, text="Автор:", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=30)
        author_entry = ctk.CTkEntry(dialog, width=340, height=35, font=ctk.CTkFont(size=14))
        author_entry.pack(pady=(0, 10), padx=30)
        
        ctk.CTkLabel(dialog, text="Год:", anchor="w", font=ctk.CTkFont(size=14)).pack(fill="x", padx=30)
        year_entry = ctk.CTkEntry(dialog, width=340, height=35, font=ctk.CTkFont(size=14))
        year_entry.pack(pady=(0, 15), padx=30)
        
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
            
        ctk.CTkButton(dialog, text="Сохранить", fg_color=GREEN, text_color="#11111b", 
                      height=45, font=ctk.CTkFont(size=15, weight="bold"), command=save_book).pack(pady=10)

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
            self.selected_index = None
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
        
        msg = (f"📊 СТАТИСТИКА\n\n"
               f"Всего книг: {len(self.books)}\n"
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