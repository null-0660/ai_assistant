# Библиотека — v6: Рейтинги и топ книг

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "library.json")

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
        self.rating = rating  # 0-5

    def show(self, index=None):
        prefix = f"{CYAN}{index:2}.{RESET} " if index is not None else "  "
        status = f"{GREEN}✅{RESET}" if self.is_read else f"{YELLOW}📖{RESET}"
        stars = "⭐" * self.rating if self.rating > 0 else f"{DIM}без оценки{RESET}"
        title_str = f"{BOLD}{WHITE}«{self.title}»{RESET}"
        author_str = f"{DIM}{self.author}{RESET}"
        year_str = f"{BLUE}({self.year}){RESET}"
        print(f"{prefix}{status} {title_str} — {author_str} {year_str} | {stars}")

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "is_read": self.is_read,
            "rating": self.rating
        }

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
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book.from_dict(b) for b in data]
        except (json.JSONDecodeError, OSError):
            print(f"{RED}⚠ Ошибка загрузки.{RESET}")

    def add_book(self):
        clear()
        print(f"{MAGENTA}{BOLD}➕ ДОБАВЛЕНИЕ КНИГИ{RESET}\n")
        title = input(f"{CYAN}Название:{RESET} ").strip()
        author = input(f"{CYAN}Автор:{RESET} ").strip()
        try:
            year = int(input(f"{CYAN}Год:{RESET} ").strip())
        except ValueError:
            print(f"{RED}❌ Год должен быть числом.{RESET}")
            input("Enter..."); return
        if not title or not author:
            print(f"{RED}❌ Название и автор обязательны.{RESET}")
            input("Enter..."); return

        self.books.append(Book(title, author, year))
        self.save()
        print(f"{GREEN}✅ Книга «{title}» добавлена!{RESET}")
        input("Enter...")

    def show_all(self):
        clear()
        print(f"{CYAN}{BOLD}📚 ВСЕ КНИГИ{RESET}")
        print(f"{CYAN}{'─' * 55}{RESET}")
        if not self.books:
            print(f"{DIM}  Библиотека пуста...{RESET}")
        else:
            for i, book in enumerate(self.books, 1):
                book.show(i)
        print(f"{CYAN}{'─' * 55}{RESET}")
        input(f"\n{DIM}Enter...{RESET}")

    def search(self):
        clear()
        print(f"{MAGENTA}{BOLD}🔍 ПОИСК{RESET}\n")
        query = input(f"{CYAN}Название или автор:{RESET} ").strip().lower()
        if not query: return
        
        found = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
        print(f"\n{CYAN}{'─' * 55}{RESET}")
        if not found:
            print(f"{RED}❌ Не найдено.{RESET}")
        else:
            print(f"{GREEN}🔍 Найдено {len(found)}:{RESET}")
            for i, book in enumerate(found, 1):
                book.show(i)
        print(f"{CYAN}{'─' * 55}{RESET}")
        input(f"\n{DIM}Enter...{RESET}")

    def mark_read(self):
        clear()
        if not self.books:
            print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}✅ ОТМЕТИТЬ ПРОЧИТАННОЙ{RESET}\n")
        for i, book in enumerate(self.books, 1):
            book.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                self.books[idx].is_read = not self.books[idx].is_read
                self.save()
                status = f"{GREEN}прочитана{RESET}" if self.books[idx].is_read else f"{YELLOW}не прочитана{RESET}"
                print(f"{GREEN}✅ Книга «{self.books[idx].title}» отмечена как {status}.{RESET}")
            else:
                print(f"{RED}❌ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def set_rating(self):
        clear()
        if not self.books:
            print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}⭐ ПОСТАВИТЬ ОЦЕНКУ{RESET}\n")
        for i, book in enumerate(self.books, 1):
            book.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер книги:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                print(f"\nОценка для «{self.books[idx].title}»:")
                print("1 ⭐  2 ⭐⭐  3 ⭐⭐⭐  4 ⭐⭐⭐⭐  5 ⭐⭐⭐⭐⭐")
                rating = int(input(f"{CYAN}Оценка (1-5):{RESET} ").strip())
                if 1 <= rating <= 5:
                    self.books[idx].rating = rating
                    self.save()
                    print(f"{GREEN}✅ Оценка {rating} ⭐ поставлена!{RESET}")
                else:
                    print(f"{RED}❌ Оценка от 1 до 5.{RESET}")
            else:
                print(f"{RED}❌ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def delete_book(self):
        clear()
        if not self.books:
            print(f"{DIM}Пусто.{RESET}"); input("Enter..."); return
        print(f"{MAGENTA}{BOLD}🗑 УДАЛЕНИЕ{RESET}\n")
        for i, book in enumerate(self.books, 1):
            book.show(i)
        try:
            idx = int(input(f"\n{CYAN}Номер для удаления:{RESET} ").strip()) - 1
            if 0 <= idx < len(self.books):
                removed = self.books.pop(idx)
                self.save()
                print(f"{GREEN}🗑 «{removed.title}» удалена.{RESET}")
            else:
                print(f"{RED}❌ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}❌ Введи число.{RESET}")
        input("Enter...")

    def stats(self):
        clear()
        print(f"{MAGENTA}{BOLD}📊 СТАТИСТИКА{RESET}")
        print(f"{CYAN}{'─' * 55}{RESET}")
        if not self.books:
            print(f"{DIM}  Нет данных...{RESET}")
            input("Enter..."); return

        read = sum(1 for b in self.books if b.is_read)
        years = [b.year for b in self.books]
        avg_year = sum(years) / len(years)
        
        # Рейтинги
        rated = [b for b in self.books if b.rating > 0]
        avg_rating = sum(b.rating for b in rated) / len(rated) if rated else 0
        
        # Любимый автор
        authors = {}
        for b in self.books:
            authors[b.author] = authors.get(b.author, 0) + 1
        fav_author = max(authors, key=authors.get) if authors else "—"
        fav_count = authors[fav_author] if authors else 0

        print(f"  Всего книг:     {BOLD}{len(self.books)}{RESET}")
        print(f"  Прочитано:      {GREEN}{read}{RESET}")
        print(f"  Не прочитано:   {YELLOW}{len(self.books) - read}{RESET}")
        print(f"  Средний год:    {BLUE}{avg_year:.0f}{RESET}")
        print(f"  Средний рейтинг:{YELLOW} {avg_rating:.1f} ⭐{RESET}")
        print(f"  Любимый автор:  {MAGENTA}{fav_author}{RESET} ({fav_count} книг)")
        print(f"{CYAN}{'─' * 55}{RESET}")

        # Топ-3
        if rated:
            print(f"\n{YELLOW}{BOLD}🏆 ТОП-3 КНИГИ:{RESET}")
            top3 = sorted(rated, key=lambda b: b.rating, reverse=True)[:3]
            for i, b in enumerate(top3, 1):
                print(f"  {i}. ", end="")
                b.show()

        print(f"{CYAN}{'─' * 55}{RESET}")
        input(f"\n{DIM}Enter...{RESET}")


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
        elif choice == "0":
            clear()
            print(f"{GREEN}👋 До свидания!{RESET}\n")
            break
        else:
            print(f"{RED}❌ Неизвестная команда.{RESET}")
            input("Enter...")


if __name__ == "__main__":
    main()