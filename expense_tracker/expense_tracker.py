# Expense Tracker — v3: показать все расходы

expenses = []


def show_menu():
    print()
    print("=== EXPENSE TRACKER ===")
    print("1. Добавить расход")
    print("2. Показать все расходы")
    print("3. Показать сумму")
    print("4. Показать по категориям")
    print("5. Выход")
    print()


def add_expense():
    amount_str = input("Сумма: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Ошибка: сумма должна быть числом.")
        return
    if amount <= 0:
        print("Ошибка: сумма должна быть больше нуля.")
        return

    category = input("Категория: ").strip().lower()
    if not category:
        print("Ошибка: категория не может быть пустой.")
        return

    expenses.append({'amount': amount, 'category': category})
    print(f"Добавлено: {amount} ({category})")


def show_all():
    """Печатает все расходы с номерами."""
    if not expenses:
        print("Список пуст.")
        return

    print()
    print("--- Все расходы ---")
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. {exp['amount']} — {exp['category']}")
    print(f"Всего записей: {len(expenses)}")


def main():
    while True:
        show_menu()
        choice = input("Выбери пункт (1-5): ").strip()

        if choice == '5':
            print("Выход.")
            break
        elif choice == '1':
            add_expense()
        elif choice == '2':
            show_all()
        elif choice == '3':
            print("(пока не работает)")
        elif choice == '4':
            print("(пока не работает)")
        else:
            print("Неверный выбор.")


main()