# Библиотека — v5: Красивый CLI-интерфейс с цветами и рамками

import json
import os
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")

# ===== Цвета =====
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

# ===== Классы =====
class Book:
    def __init__(self, title, author, year, is_read=False):
        self.title = title
        self.author = author
        self.year = year
        self.is_read = is_read

    def show(self, index=None):
        prefix = f"{CYAN}{index:2}.{RESET} " if index is not None else "  "
        status = f"{GREEN}✅ прочитана{RESET}" if self.is_read else f"{YELLOW}📖 не прочитана{RESET}"
        title_str = f"{BOLD}{WHITE}«{self.title}»{RESET}"
        author_str = f"{DIM}{self.author}{RESET}"
        year_str = f"{BLUE}({self.year}){RESET}"
        print(f"{prefix}{title_str} — {author_str} {year_str} | {status}")

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "is_read": self.is_read
        }

    @staticmethod
    def from_dict(data):
        return Book(data["title"], data["author"], data["year"], data.get("is_read", False))


class Library:
    def __init__(self):
        self.books = []
        self.load()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=2)
        except OSError:
            print(f"{RED}❌ Ошибка сохранения файла.{RESET}")

    def load(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book.from_dict(b) for b in data]
        except (json.JSONDecodeError, OSError):
            print(f"{RED}⚠ Ошибка загрузки, начинаем с пустой библиотеки.{RESET}")

    def add_book(self):
        clear()
        print(f"{MAGENTA}{BOLD}➕ ДОБАВЛЕНИЕ КНИГИ{RESET}\n")
        title = input(f"{CYAN}Название:{RESET} ").strip()
        author = input(f"{CYAN}Автор:{RESET} ").strip()
        try:
            year = int(input(f"{CYAN}Год:{RESET} ").strip())
        except ValueError:
            print(f"{RED}❌ Год должен быть числом.{RESET}")
            input("Нажми Enter...")
            return
        if not title or not author:
            print(f"{RED}❌ Название и автор не могут быть пустыми.{RESET}")
            input("Нажми Enter...")
            return

        self.books.append(Book(title, author, year))
        self.save()
        print(f"{GREEN}✅ Книга «{title}» успешно добавлена!{RESET}")
        input("Нажми Enter...")

    def show_all(self):
        clear()
        print(f"{CYAN}{BOLD}📚 ВСЕ КНИГИ{RESET}")
        print(f"{CYAN}{'─' * 50}{RESET}")
        if not self.books:
            print(f"{DIM}  Библиотека пуста...{RESET}")
        else:
            for i, book in enumerate(self.books, 1):
                book.show(i)
        print(f"{CYAN}{'─' * 50}{RESET}")
        input(f"\n{DIM}Нажми Enter чтобы вернуться...{RESET}")

    def search(self):
        clear()
        print(f"{MAGENTA}{BOLD}🔍 ПОИСК{RESET}\n")
        query = input(f"{CYAN}Введи название или автора:{RESET} ").strip().lower()
        if not query:
            return
        found = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
        
        print(f"\n{CYAN}{'─' * 50}{RESET}")
        if not found:
            print(f"{RED}❌ Ничего не найдено по запросу «{query}».{RESET}")
        else:
            print(f"{GREEN}🔍 Найдено {len(found)}:{RESET}")
            for i, book in enumerate(found, 1):
                book.show(i)
        print(f"{CYAN}{'─' * 50}{RESET}")
        input(f"\n{DIM}Нажми Enter чтобы вернуться...{RESET}")

    def mark_read(self):
        clear()
        if not self.books:
            print(f"{DIM}Библиотека пуста...{RESET}")
            input("Нажми Enter...")
            return
        print(f"{MAGENTA}{BOLD}✅ ОТМЕТИТЬ ПРОЧИТАННОЙ{RESET}\n")
        for i, book in enumerate(self.books, 1):
            book.show(i)
        
        try:
            idx = int(input(f"\n{CYAN}Номер книги:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                self.books[idx].is_read = not self.books[idx].is_read
                self.save()
                status = f"{GREEN}прочитана{RESET}" if self.books[idx].is_read else f"{YELLOW}не прочитана{RESET}"
                print(f"{GREEN}✅ Книга «{self.books[idx].title}» отмечена как {status}.{RESET}")
            else:
                print(f"{RED}❌ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}❌ Введи число.{RESET}")
        input("Нажми Enter...")

    def delete_book(self):
        clear()
        if not self.books:
            print(f"{DIM}Библиотека пуста...{RESET}")
            input("Нажми Enter...")
            return
        print(f"{MAGENTA}{BOLD}🗑 УДАЛЕНИЕ КНИГИ{RESET}\n")
        for i, book in enumerate(self.books, 1):
            book.show(i)
        
        try:
            idx = int(input(f"\n{CYAN}Номер книги для удаления:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                removed = self.books.pop(idx)
                self.save()
                print(f"{GREEN}🗑 Книга «{removed.title}» удалена.{RESET}")
            else:
                print(f"{RED}❌ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}❌ Введи число.{RESET}")
        input("Нажми Enter...")

    def stats(self):
        clear()
        print(f"{MAGENTA}{BOLD}📊 СТАТИСТИКА{RESET}")
        print(f"{CYAN}{'─' * 50}{RESET}")
        if not self.books:
            print(f"{DIM}  Нет данных для статистики...{RESET}")
        else:
            read = sum(1 for b in self.books if b.is_read)
            years = [b.year for b in self.books]
            avg_year = sum(years) / len(years)
            oldest = min(self.books, key=lambda b: b.year)
            newest = max(self.books, key=lambda b: b.year)

            print(f"  Всего книг:     {BOLD}{len(self.books)}{RESET}")
            print(f"  Прочитано:      {GREEN}{read}{RESET}")
            print(f"  Не прочитано:   {YELLOW}{len(self.books) - read}{RESET}")
            print(f"  Средний год:    {BLUE}{avg_year:.0f}{RESET}")
            print(f"  Самая старая:   {BOLD}«{oldest.title}»{RESET} ({oldest.year})")
            print(f"  Самая новая:    {BOLD}«{newest.title}»{RESET} ({newest.year})")
        print(f"{CYAN}{'─' * 50}{RESET}")
        input(f"\n{DIM}Нажми Enter чтобы вернуться...{RESET}")


# ===== Интерфейс =====
def show_menu(lib):
    clear()
    print(f"{CYAN}{BOLD}╔{'═' * 46}╗{RESET}")
    print(f"{CYAN}║{RESET} {MAGENTA}{BOLD}📚 МОЯ БИБЛИОТЕКА{RESET}{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}╠{'═' * 46}╣{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}1.{RESET} Показать все книги{' ' * 23}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}2.{RESET} Добавить книгу{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}3.{RESET} Поиск{' ' * 35}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}4.{RESET} Отметить прочитанной{' ' * 19}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}5.{RESET} Удалить книгу{' ' * 27}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET}  {GREEN}6.{RESET} Статистика{' ' * 30}{CYAN}║{RESET}")
    print(f"{CYAN}╠{'═' * 46}╣{RESET}")
    print(f"{CYAN}║{RESET}  {RED}0.{RESET} Выход{' ' * 36}{CYAN}║{RESET}")
    print(f"{CYAN}╚{'═' * 46}╝{RESET}")
    print(f"{DIM}  Всего в базе: {len(lib.books)} книг{RESET}")


def main():
    lib = Library()
    
    while True:
        show_menu(lib)
        choice = input(f"\n{CYAN}Твой выбор > {RESET}").strip()

        if choice == "1":
            lib.show_all()
        elif choice == "2":
            lib.add_book()
        elif choice == "3":
            lib.search()
        elif choice == "4":
            lib.mark_read()
        elif choice == "5":
            lib.delete_book()
        elif choice == "6":
            lib.stats()
        elif choice == "0":
            clear()
            print(f"{GREEN}👋 До свидания! Твои книги сохранены.{RESET}\n")
            break
        else:
            print(f"{RED}❌ Неизвестная команда.{RESET}")
            input("Нажми Enter...")


if __name__ == "__main__":
    main()