# Expense Tracker — v5: сохранение в JSON

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'expenses.json')
expenses = []


def load_data():
    """Загружает расходы из файла, если он есть."""
    global expenses
    if not os.path.exists(DATA_FILE):
        expenses = []
        return

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            expenses = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Ошибка чтения файла. Начинаем с пустого списка.")
        expenses = []


def save_data():
    """Сохраняет расходы в файл."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(expenses, f, ensure_ascii=False, indent=2)
    except OSError:
        print("Ошибка сохранения файла.")


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
    save_data()
    print(f"Добавлено: {amount} ({category})")


def show_all():
    if not expenses:
        print("Список пуст.")
        return
    print()
    print("--- Все расходы ---")
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. {exp['amount']} — {exp['category']}")
    print(f"Всего записей: {len(expenses)}")


def show_total():
    if not expenses:
        print("Список пуст.")
        return
    total = 0
    for exp in expenses:
        total += exp['amount']
    print(f"Общая сумма: {total}")


def show_by_category():
    if not expenses:
        print("Список пуст.")
        return
    summary = {}
    for exp in expenses:
        cat = exp['category']
        summary[cat] = summary.get(cat, 0) + exp['amount']
    print()
    print("--- По категориям ---")
    for cat, total in summary.items():
        print(f"{cat}: {total}")


def main():
    load_data()
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
            show_total()
        elif choice == '4':
            show_by_category()
        else:
            print("Неверный выбор.")


main()