# Библиотека — v2: меню и поиск


class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
        self.is_read = False

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

        book = Book(title, author, year)
        self.books.append(book)
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

        found = []
        for book in self.books:
            if query in book.title.lower() or query in book.author.lower():
                found.append(book)

        if not found:
            print(f"❌ Ничего не найдено по запросу «{query}».")
            return

        print(f"\n🔍 Найдено {len(found)}:")
        for i, book in enumerate(found, 1):
            print(f"{i}. ", end="")
            book.show()


def show_menu():
    print("\n" + "=" * 40)
    print("📚 БИБЛИОТЕКА")
    print("=" * 40)
    print("1. Показать все книги")
    print("2. Добавить книгу")
    print("3. Поиск")
    print("4. Выход")
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
            print("👋 До свидания!")
            break
        else:
            print("❌ Неизвестная команда.")


if __name__ == "__main__":
    main()