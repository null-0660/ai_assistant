# Библиотека — v1: классы Book и Library


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

    def add_book(self, title, author, year):
        book = Book(title, author, year)
        self.books.append(book)
        print(f"📚 Книга «{title}» добавлена.")

    def show_all(self):
        if not self.books:
            print("📭 Библиотека пуста.")
            return
        print(f"\n📚 В библиотеке {len(self.books)} книг(и):")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. ", end="")
            book.show()


def main():
    lib = Library()
    lib.add_book("Мастер и Маргарита", "Булгаков", 1967)
    lib.add_book("1984", "Оруэлл", 1949)
    lib.show_all()


if __name__ == "__main__":
    main()