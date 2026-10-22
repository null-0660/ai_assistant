# Expense Tracker — v1: меню и выход

def show_menu():
    print()
    print("=== EXPENSE TRACKER ===")
    print("1. Добавить расход")
    print("2. Показать все расходы")
    print("3. Показать сумму")
    print("4. Показать по категориям")
    print("5. Выход")
    print()


def main():
    while True:
        show_menu()
        choice = input("Выбери пункт (1-5): ").strip()

        if choice == '5':
            print("Выход.")
            break
        elif choice == '1':
            print("(пока не работает)")
        elif choice == '2':
            print("(пока не работает)")
        elif choice == '3':
            print("(пока не работает)")
        elif choice == '4':
            print("(пока не работает)")
        else:
            print("Неверный выбор.")


main()