# Текстовый квест — v2: локации и переходы

import random


class Hero:
    def __init__(self, name="Странник"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.gold = 0
        self.inventory = []

    def show_stats(self):
        print(f"\n--- {self.name} ---")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Золото: {self.gold}")
        if self.inventory:
            print(f"Инвентарь: {', '.join(self.inventory)}")
        else:
            print("Инвентарь: пусто")
        print("-------------------")

    def take_damage(self, dmg):
        self.hp -= dmg
        print(f"💥 Ты потерял {dmg} HP.")
        if self.hp <= 0:
            print("💀 Ты погиб...")
            self.hp = 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"💚 Восстановлено {amount} HP.")

    def add_gold(self, amount):
        self.gold += amount
        print(f"💰 +{amount} золота.")

    def add_item(self, item):
        self.inventory.append(item)
        print(f"🎒 Получен предмет: {item}")

    def is_alive(self):
        return self.hp > 0


class Game:
    LOCATIONS = {
        "forest": {
            "name": "Тёмный Лес",
            "desc": "Деревья шелестят, туман стелется по земле.",
            "exits": {"north": "cave", "east": "village"},
        },
        "cave": {
            "name": "Пещера",
            "desc": "Тёмно, сыро, откуда-то капает вода.",
            "exits": {"south": "forest"},
        },
        "village": {
            "name": "Деревня",
            "desc": "Небольшая деревня. Тут есть рынок и трактир.",
            "exits": {"west": "forest"},
        },
    }

    def __init__(self):
        self.hero = Hero()
        self.running = True
        self.location = "forest"

    def print_location(self):
        loc = self.LOCATIONS[self.location]
        print("\n" + "=" * 40)
        print(f"📍 {loc['name']}")
        print("=" * 40)
        print(loc["desc"])
        if loc["exits"]:
            print("\nВыходы:", ", ".join(loc["exits"].keys()))

    def look_around(self):
        events = [
            ("Ты находишь монету на земле.", lambda: self.hero.add_gold(5)),
            ("На тебя нападает волк!", lambda: self.hero.take_damage(10)),
            ("Ты находишь травы, восстанавливающие силы.", lambda: self.hero.heal(15)),
            ("Ничего интересного.", lambda: None),
        ]
        text, action = random.choice(events)
        print(text)
        action()

    def move(self, direction):
        loc = self.LOCATIONS[self.location]
        if direction in loc["exits"]:
            self.location = loc["exits"][direction]
            print(f"Ты идёшь на {direction}...")
        else:
            print("Туда пройти нельзя.")

    def play(self):
        print("🌲 Добро пожаловать в Тёмный Лес!")
        print("Ты — Странник. Впереди тебя ждут испытания.")

        while self.running and self.hero.is_alive():
            self.hero.show_stats()
            self.print_location()

            print("\nЧто будешь делать?")
            print("1. Осмотреться")
            print("2. Идти (north/south/east/west)")
            print("3. Выход")
            choice = input("> ").strip().lower()

            if choice == "1":
                self.look_around()
            elif choice == "2":
                direction = input("Куда идти? (north/south/east/west): ").strip().lower()
                self.move(direction)
            elif choice == "3":
                print("Конец игры.")
                self.running = False
            else:
                print("Неизвестная команда.")

        if not self.hero.is_alive():
            print("💀 Game Over.")


if __name__ == "__main__":
    game = Game()
    game.play()