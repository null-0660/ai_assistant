# Библиотека — v3: статус, удаление, рейтинг


class Book:
    def __init__(self, title, author, year, is_read=False):
        self.title = title
        self.author = author
        self.year = year
        self.is_read = is_read

    def show(self):
        status = "✅ прочитана" if self.is_read else "📖 не прочитана"
        print(f"«{self.title}» — {self.author} ({self.year}) | {status}")

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "is_read": self.is_read
        }


class Library:
    def __init__(self):
        self.books = []

    def add_book(self):
        print("\n➕ Добавление книги")
        title = input("Название: ").strip()
        author = input("Автор: ").strip()
        try:
            year = int(input("Год: ").strip())
        except ValueError:
            print("❌ Год должен быть числом.")
            return
        if not title or not author:
            print("❌ Название и автор не могут быть пустыми.")
            return

        self.books.append(Book(title, author, year))
        print(f"✅ Книга «{title}» добавлена!")

    def show_all(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return
        print(f"\n📚 В библиотеке {len(self.books)} книг(и):")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. ", end="")
            book.show()

    def search(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return
        query = input("🔍 Поиск (название или автор): ").strip().lower()
        if not query:
            return

        found = [b for b in self.books if query in b.title.lower() or query in b.author.lower()]
        if not found:
            print(f"❌ Ничего не найдено по запросу «{query}».")
            return
        print(f"\n🔍 Найдено {len(found)}:")
        for i, book in enumerate(found, 1):
            print(f"{i}. ", end="")
            book.show()

    def mark_read(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return
        self.show_all()
        try:
            idx = int(input("\nНомер книги: ").strip()) - 1
            if 0 <= idx < len(self.books):
                self.books[idx].is_read = not self.books[idx].is_read
                status = "прочитана" if self.books[idx].is_read else "не прочитана"
                print(f"✅ Книга «{self.books[idx].title}» отмечена как {status}.")
            else:
                print("❌ Неверный номер.")
        except ValueError:
            print("❌ Введи число.")

    def delete_book(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return
        self.show_all()
        try:
            idx = int(input("\nНомер книги для удаления: ").strip()) - 1
            if 0 <= idx < len(self.books):
                removed = self.books.pop(idx)
                print(f"🗑 Книга «{removed.title}» удалена.")
            else:
                print("❌ Неверный номер.")
        except ValueError:
            print("❌ Введи число.")

    def stats(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return

        read = sum(1 for b in self.books if b.is_read)
        years = [b.year for b in self.books]
        avg_year = sum(years) / len(years)
        oldest = min(self.books, key=lambda b: b.year)
        newest = max(self.books, key=lambda b: b.year)

        print("\n📊 Статистика:")
        print(f"  Всего книг:     {len(self.books)}")
        print(f"  Прочитано:      {read}")
        print(f"  Не прочитано:   {len(self.books) - read}")
        print(f"  Средний год:    {avg_year:.0f}")
        print(f"  Самая старая:   «{oldest.title}» ({oldest.year})")
        print(f"  Самая новая:    «{newest.title}» ({newest.year})")


def show_menu():
    print("\n" + "=" * 40)
    print("📚 БИБЛИОТЕКА")
    print("=" * 40)
    print("1. Показать все книги")
    print("2. Добавить книгу")
    print("3. Поиск")
    print("4. Отметить прочитанной")
    print("5. Удалить книгу")
    print("6. Статистика")
    print("7. Выход")
    print("=" * 40)


def main():
    lib = Library()

    while True:
        show_menu()
        choice = input("> ").strip()

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
        elif choice == "7":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неизвестная команда.")


if __name__ == "__main__":
    main()