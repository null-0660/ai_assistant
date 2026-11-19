# Библиотека — v7: Экспорт в CSV и TXT

import json
import os
import csv
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")
EXPORT_CSV = os.path.join(os.path.dirname(__file__), "library_export.csv")
EXPORT_TXT = os.path.join(os.path.dirname(__file__), "library_export.txt")

RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class Book:
    def __init__(self, title, author, year, is_read=False, rating=0):
        self.title = title
        self.author = author
        self.year = year
        self.is_read = is_read
        self.rating = rating

    def show(self, index=None):
        prefix = f"{CYAN}{index:2}.{RESET} " if index is not None else "  "
        status = f"{GREEN}✅{RESET}" if self.is_read else f"{YELLOW}📖{RESET}"
        stars = "⭐" * self.rating if self.rating > 0 else f"{DIM}—{RESET}"
        print(f"{prefix}{status} {BOLD}{WHITE}«{self.title}»{RESET} — {DIM}{self.author}{RESET} {BLUE}({self.year}){RESET} | {stars}")

    def to_dict(self):
        return {"title": self.title, "author": self.author, "year": self.year,
                "is_read": self.is_read, "rating": self.rating}

    @staticmethod
    def from_dict(data):
        return Book(data["title"], data["author"], data["year"],
                    data.get("is_read", False), data.get("rating", 0))


class Library:
    def __init__(self):
        self.books = []
        self.load()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=2)
        except OSError:
            print(f"{RED}❌ Ошибка сохранения.{RESET}")

    def load(self):
        if not os.path.exists(DATA_FILE): return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = [Book.from_dict(b) for b in json.load(f)]
        except (json.JSONDecodeError, OSError):
            print(f"{RED}⚠ Ошибка загрузки.{RESET}")

    def add_book(self):
        clear()
        print(f"{MAGENTA}{BOLD}➕ ДОБАВЛЕНИЕ{RESET}\n")
        title = input(f"{CYAN}Название:{RESET} ").strip()
        author = input(f"{CYAN}Автор:{RESET} ").strip()
        try:
            year = int(input(f"{CYAN}Год:{RESET} ").strip())
        except ValueError:
            print(f"{RED}❌ Год должен быть числом.{RESET}"); input("Enter..."); return
        if not title or not author:
            print(f"{RED}❌ Название и автор обязательны.{RESET}"); input("Enter..."); return
        self.books.append(Book(title, author, year))
        self.save()
        print(f"{GREEN}✅ «{title}» добавлена!{RESET}")
        input("Enter...")

    def show_all(self):
        clear()
        print(f"{CYAN}{BOLD}📚 ВСЕ КНИГИ{RESET}")
        print(f"{CYAN}{'─' * 55}{RESET}")
        if not self.books:
            print(f"{DIM}  Пусто...{RESET}")
        else:
            for i, b in enumerate(self.books, 1): b.show(i)
        print(f"{CYAN}{'─' * 55}{RESET}")
        input(f"\n{DIM}Enter...{RESET}")

    def search(self):
        clear()
        print(f"{MAGENTA}{BOLD}🔍 ПОИСК{RESET}\n")
        query = input(f"{CYAN}Запрос:{RESET} ").strip().lower()
        if not query: return
        found = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
        print(f"\n{CYAN}{'─' * 55}{RESET}")
        if not found: print(f"{RED}❌ Не найдено.{RESET}")
        else:
            print(f"{GREEN}🔍 Найдено {len(found)}:{RESET}")
            for i, b in enumerate(found, 1): b.show(i)
        print(f"{CYAN}{'─' * 55}{RESET}")
        input(f"\n{DIM}Enter...{RESET}")

    def mark_read(self):
        clear()
        if not self.books: print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}✅ ПРОЧИТАНО{RESET}\n")
        for i, b in enumerate(self.books, 1): b.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                self.books[idx].is_read = not self.books[idx].is_read
                self.save()
                st = f"{GREEN}прочитана{RESET}" if self.books[idx].is_read else f"{YELLOW}не прочитана{RESET}"
                print(f"{GREEN}✅ «{self.books[idx].title}» — {st}.{RESET}")
        except ValueError: print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def set_rating(self):
        clear()
        if not self.books: print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}⭐ ОЦЕНКА{RESET}\n")
        for i, b in enumerate(self.books, 1): b.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                print(f"\n1⭐ 2⭐⭐ 3⭐⭐⭐ 4⭐⭐⭐⭐ 5⭐⭐⭐⭐⭐")
                r = int(input(f"{CYAN}Оценка:{RESET} ").strip())
                if 1 <= r <= 5:
                    self.books[idx].rating = r; self.save()
                    print(f"{GREEN}✅ Оценка {r}⭐ поставлена!{RESET}")
        except ValueError: print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def delete_book(self):
        clear()
        if not self.books: print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}🗑 УДАЛЕНИЕ{RESET}\n")
        for i, b in enumerate(self.books, 1): b.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                r = self.books.pop(idx); self.save()
                print(f"{GREEN}🗑 «{r.title}» удалена.{RESET}")
        except ValueError: print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def stats(self):
        clear()
        print(f"{MAGENTA}{BOLD}📊 СТАТИСТИКА{RESET}")
        print(f"{CYAN}{'─' * 55}{RESET}")
        if not self.books:
            print(f"{DIM}  Нет данных...{RESET}"); input("Enter..."); return
        read = sum(1 for b in self.books if b.is_read)
        years = [b.year for b in self.books]
        avg_year = sum(years) / len(years)
        rated = [b for b in self.books if b.rating > 0]
        avg_r = sum(b.rating for b in rated) / len(rated) if rated else 0
        authors = {}
        for b in self.books: authors[b.author] = authors.get(b.author, 0) + 1
        fav = max(authors, key=authors.get) if authors else "—"
        print(f"  Всего:        {BOLD}{len(self.books)}{RESET}")
        print(f"  Прочитано:    {GREEN}{read}{RESET}")
        print(f"  Не прочитано: {YELLOW}{len(self.books) - read}{RESET}")
        print(f"  Средний год:  {BLUE}{avg_year:.0f}{RESET}")
        print(f"  Ср. рейтинг:  {YELLOW}{avg_r:.1f}⭐{RESET}")
        print(f"  Люб. автор:   {MAGENTA}{fav}{RESET}")
        print(f"{CYAN}{'─' * 55}{RESET}")
        if rated:
            print(f"\n{YELLOW}{BOLD}🏆 ТОП-3:{RESET}")
            for i, b in enumerate(sorted(rated, key=lambda x: x.rating, reverse=True)[:3], 1):
                print(f"  {i}. ", end=""); b.show()
        input(f"\n{DIM}Enter...{RESET}")

    def export_csv(self):
        clear()
        print(f"{MAGENTA}{BOLD}📤 ЭКСПОРТ В CSV{RESET}\n")
        if not self.books:
            print(f"{DIM}Нечего экспортировать.{RESET}"); input("Enter..."); return
        try:
            with open(EXPORT_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Название", "Автор", "Год", "Прочитана", "Рейтинг"])
                for b in self.books:
                    writer.writerow([b.title, b.author, b.year,
                                     "Да" if b.is_read else "Нет", b.rating])
            print(f"{GREEN}✅ Экспортировано в:{RESET}")
            print(f"  {EXPORT_CSV}")
            print(f"  Книг: {len(self.books)}")
        except OSError as e:
            print(f"{RED}❌ Ошибка: {e}{RESET}")
        input("\nEnter...")

    def export_txt(self):
        clear()
        print(f"{MAGENTA}{BOLD}📤 ЭКСПОРТ В TXT{RESET}\n")
        if not self.books:
            print(f"{DIM}Нечего экспортировать.{RESET}"); input("Enter..."); return
        try:
            with open(EXPORT_TXT, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("МОЯ БИБЛИОТЕКА\n")
                f.write(f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write(f"Всего книг: {len(self.books)}\n")
                f.write("=" * 60 + "\n\n")
                for i, b in enumerate(self.books, 1):
                    status = "✓ прочитана" if b.is_read else "○ не прочитана"
                    stars = "⭐" * b.rating if b.rating > 0 else "—"
                    f.write(f"{i}. «{b.title}» — {b.author} ({b.year})\n")
                    f.write(f"   {status} | Оценка: {stars}\n\n")
                read = sum(1 for b in self.books if b.is_read)
                f.write("=" * 60 + "\n")
                f.write(f"Итого прочитано: {read} из {len(self.books)}\n")
            print(f"{GREEN}✅ Экспортировано в:{RESET}")
            print(f"  {EXPORT_TXT}")
        except OSError as e:
            print(f"{RED}❌ Ошибка: {e}{RESET}")
        input("\nEnter...")

    def export_menu(self):
        while True:
            clear()
            print(f"{MAGENTA}{BOLD}📤 ЭКСПОРТ{RESET}")
            print(f"{CYAN}{'─' * 40}{RESET}")
            print(f"  {GREEN}1.{RESET} Экспорт в CSV (для Excel)")
            print(f"  {GREEN}2.{RESET} Экспорт в TXT (отчёт)")
            print(f"  {RED}0.{RESET} Назад")
            print(f"{CYAN}{'─' * 40}{RESET}")
            choice = input(f"\n{CYAN}Выбор:{RESET} ").strip()
            if choice == "1": self.export_csv()
            elif choice == "2": self.export_txt()
            elif choice == "0": break


def show_menu(lib):
    clear()
    print(f"{CYAN}{BOLD}╔{'═' * 46}╗{RESET}")
    print(f"{CYAN}║{RESET} {MAGENTA}{BOLD}📚 МОЯ БИБЛИОТЕКА{RESET}{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}╠{'═' * 46}╣{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}1.{RESET} Показать все книги{' ' * 23}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}2.{RESET} Добавить книгу{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}3.{RESET} Поиск{' ' * 35}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}4.{RESET} Отметить прочитанной{' ' * 19}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {YELLOW}5.{RESET} Поставить оценку{' ' * 22}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}6.{RESET} Удалить книгу{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}7.{RESET} Статистика{' ' * 30}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {BLUE}8.{RESET} Экспорт (CSV/TXT){' ' * 23}{CYAN}║{RESET}")
    print(f"{CYAN}╠{'═' * 46}╣{RESET}")
    print(f"{CYAN}║{RESET}  {RED}0.{RESET} Выход{' ' * 36}{CYAN}║{RESET}")
    print(f"{CYAN}╚{'═' * 46}╝{RESET}")
    print(f"{DIM}  Всего в базе: {len(lib.books)} книг{RESET}")


def main():
    lib = Library()
    while True:
        show_menu(lib)
        choice = input(f"\n{CYAN}Твой выбор > {RESET}").strip()
        if choice == "1": lib.show_all()
        elif choice == "2": lib.add_book()
        elif choice == "3": lib.search()
        elif choice == "4": lib.mark_read()
        elif choice == "5": lib.set_rating()
        elif choice == "6": lib.delete_book()
        elif choice == "7": lib.stats()
        elif choice == "8": lib.export_menu()
        elif choice == "0":
            clear(); print(f"{GREEN}👋 До свидания!{RESET}\n"); break
        else:
            print(f"{RED}❌ Неизвестная команда.{RESET}"); input("Enter...")


if __name__ == "__main__":
    main()