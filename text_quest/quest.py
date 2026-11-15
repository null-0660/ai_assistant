# Текстовый квест — v4: квест, амулет, финал

import random


class Hero:
    def __init__(self, name="Странник"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.gold = 20
        self.inventory = []
        self.has_amulet = False

    def show_stats(self):
        print(f"\n--- {self.name} ---")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Золото: {self.gold}")
        if self.inventory:
            print(f"Инвентарь: {', '.join(self.inventory)}")
        else:
            print("Инвентарь: пусто")
        if self.has_amulet:
            print("🔮 Амулет: ЕСТЬ")
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

    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def add_item(self, item):
        self.inventory.append(item)
        print(f"🎒 Получен предмет: {item}")

    def is_alive(self):
        return self.hp > 0


class NPC:
    def __init__(self, name, dialogue, is_enemy=False, hp=20, dmg=5):
        self.name = name
        self.dialogue = dialogue
        self.is_enemy = is_enemy
        self.hp = hp
        self.max_hp = hp
        self.dmg = dmg

    def show(self):
        if self.is_enemy:
            print(f"👹 {self.name} (HP: {self.hp}/{self.max_hp}, урон: {self.dmg})")
        else:
            print(f"🧑 {self.name}: «{self.dialogue}»")

    def attack(self, hero):
        print(f"{self.name} атакует!")
        hero.take_damage(self.dmg)

    def take_damage(self, dmg):
        self.hp -= dmg
        print(f"⚔ {self.name} получает {dmg} урона. HP: {max(0, self.hp)}")

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
            "desc": "Тёмно, сыро, откуда-то капает вода. Кто-то рычит в темноте...",
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
        self.npcs = {
            "forest": [NPC("Лесник", "Говорят, в пещере гоблин охраняет древний амулет. Принеси его в деревню — старейшина щедро наградит.")],
            "cave": [NPC("Гоблин", "Гр-р-р! Не отдам амулет!", is_enemy=True, hp=35, dmg=8)],
            "village": [NPC("Старейшина", "Найди амулет в пещере, и я награжу тебя.")],
        }
        self.quest_complete = False

    def print_location(self):
        loc = self.LOCATIONS[self.location]
        print("\n" + "=" * 40)
        print(f"📍 {loc['name']}")
        print("=" * 40)
        print(loc["desc"])
        if loc["exits"]:
            print("\nВыходы:", ", ".join(loc["exits"].keys()))
        if self.npcs.get(self.location):
            for npc in self.npcs[self.location]:
                npc.show()

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

    def talk_or_fight(self):
        if not self.npcs.get(self.location):
            print("Тут никого нет.")
            return

        npc = self.npcs[self.location][0]

        if npc.is_enemy:
            print(f"\n⚔ Бой с {npc.name}!")
            self.combat(npc)
        else:
            print(f"\n{npc.name} говорит: «{npc.dialogue}»")
            if npc.name == "Старейшина" and self.hero.has_amulet:
                print("🧓 Старейшина: «Ты нашёл амулет! Спасибо тебе, путник!»")
                print("🏆 КВЕСТ ЗАВЕРШЁН! Ты победил!")
                self.quest_complete = True
                self.running = False
            elif npc.name == "Старейшина":
                print("🧓 Старейшина: «Сначала найди амулет в пещере.»")

    def combat(self, npc):
        while npc.is_alive() and self.hero.is_alive():
            print(f"\n{self.hero.name} HP: {self.hero.hp} | {npc.name} HP: {npc.hp}")
            print("1. Атаковать")
            print("2. Бежать")
            choice = input("> ").strip()

            if choice == "1":
                dmg = random.randint(8, 15)
                npc.take_damage(dmg)
                if npc.is_alive():
                    npc.attack(self.hero)
            elif choice == "2":
                print("Ты убегаешь!")
                return
            else:
                print("Неизвестная команда.")

        if not npc.is_alive():
            print(f"\n🏆 Ты победил {npc.name}!")
            self.hero.add_gold(15)
            self.npcs[self.location].remove(npc)
            if npc.name == "Гоблин":
                print("🔮 Из гоблина выпал древний амулет!")
                self.hero.has_amulet = True
                self.hero.add_item("Амулет")
        elif not self.hero.is_alive():
            print("💀 Ты пал в бою.")

    def play(self):
        print("🌲 Добро пожаловать в Тёмный Лес!")
        print("Ты — Странник. Твоя цель: найти амулет в пещере и принести его старейшине.")

        while self.running and self.hero.is_alive():
            self.hero.show_stats()
            self.print_location()

            print("\nЧто будешь делать?")
            print("1. Осмотреться")
            print("2. Идти (north/south/east/west)")
            print("3. Поговорить / Атаковать")
            print("4. Выход")
            choice = input("> ").strip().lower()

            if choice == "1":
                self.look_around()
            elif choice == "2":
                direction = input("Куда идти? (north/south/east/west): ").strip().lower()
                self.move(direction)
            elif choice == "3":
                self.talk_or_fight()
            elif choice == "4":
                print("Конец игры.")
                self.running = False
            else:
                print("Неизвестная команда.")

        if self.quest_complete:
            print("\n🏆 ПОБЕДА! Ты завершил квест.")
        elif not self.hero.is_alive():
            print("💀 Game Over.")


if __name__ == "__main__":
    game = Game()
    game.play()