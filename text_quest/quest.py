# Текстовый квест — v1: классы Hero и Game


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


class Game:
    def __init__(self):
        self.hero = Hero()
        self.running = True
        self.location = "forest"

    def print_location(self):
        print("\n" + "=" * 40)
        print(f"Локация: {self.location}")
        print("=" * 40)

    def play(self):
        print("🌲 Добро пожаловать в Тёмный Лес!")
        print("Ты — Странник. Впереди тебя ждут испытания.")
        self.hero.show_stats()

        while self.running:
            self.print_location()
            
            print("Что будешь делать?")
            print("1. Осмотреться")
            print("2. Выход")
            choice = input("> ").strip()

            if choice == "1":
                print("Ты видишь только деревья и туман.")
            elif choice == "2":
                print("Ты покидаешь лес. Конец.")
                self.running = False
            else:
                print("Неизвестная команда.")


if __name__ == "__main__":
    game = Game()
    game.play()