# Текстовый квест — v5: русский интерфейс, удобное управление

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
        print(f"\n┌{'─' * 30}┐")
        print(f"│ 👤 {self.name:<25} │")
        print(f"│ ❤️  HP: {self.hp}/{self.max_hp:<17} │")
        print(f"│ 🪙 Золото: {self.gold:<18} │")
        if self.inventory:
            inv_str = ', '.join(self.inventory)
            print(f"│ 🎒 Инвентарь: {inv_str[:16]:<14} │")
        else:
            print(f"│ 🎒 Инвентарь: пусто           │")
        if self.has_amulet:
            print(f"│ 🔮 Амулет: ЕСТЬ               │")
        print(f"└{'─' * 30}┘")

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
            "exits": {"Север (Пещера)": "cave", "Восток (Деревня)": "village"},
        },
        "cave": {
            "name": "Пещера",
            "desc": "Тёмно, сыро, откуда-то капает вода. Кто-то рычит в темноте...",
            "exits": {"Юг (Лес)": "forest"},
        },
        "village": {
            "name": "Деревня",
            "desc": "Небольшая деревня. Тут есть рынок и трактир.",
            "exits": {"Запад (Лес)": "forest"},
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
        print(f"\n╔{'═' * 40}╗")
        print(f"║ 📍 {loc['name']:<35} ║")
        print(f"╚{'═' * 40}╝")
        print(loc["desc"])
        
        if self.npcs.get(self.location):
            print("\n👥 Кто здесь:")
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
        print(f"\n🔍 {text}")
        action()

    def move(self):
        loc = self.LOCATIONS[self.location]
        exits = list(loc["exits"].keys())
        
        print("\n🚶 Куда идти?")
        for i, exit_name in enumerate(exits, 1):
            print(f"{i}. {exit_name}")
        print(f"{len(exits) + 1}. Остаться на месте")
        
        choice = input("> ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(exits):
                destination = exits[choice_idx]
                self.location = loc["exits"][destination]
                print(f"Ты идёшь: {destination}...")
            elif choice_idx == len(exits):
                pass
            else:
                print("Неверный выбор.")
        except ValueError:
            print("Введи цифру.")

    def talk_or_fight(self):
        if not self.npcs.get(self.location):
            print("\nТут никого нет.")
            return

        npc = self.npcs[self.location][0]

        if npc.is_enemy:
            print(f"\n⚔ Начинается бой с {npc.name}!")
            self.combat(npc)
        else:
            print(f"\n🗣 {npc.name} говорит: «{npc.dialogue}»")
            if npc.name == "Старейшина" and self.hero.has_amulet:
                print("\n🧓 Старейшина: «Ты нашёл амулет! Спасибо тебе, путник!»")
                print("🏆 КВЕСТ ЗАВЕРШЁН! Ты победил!")
                self.quest_complete = True
                self.running = False
            elif npc.name == "Старейшина":
                print("🧓 Старейшина: «Сначала найди амулет в пещере.»")

    def combat(self, npc):
        while npc.is_alive() and self.hero.is_alive():
            print(f"\n⚔ БОЙ: {self.hero.name} (HP: {self.hero.hp}) vs {npc.name} (HP: {npc.hp})")
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
                print("Неверный выбор.")

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

            print("\n📋 Что будешь делать?")
            print("1. Осмотреться")
            print("2. Идти")
            print("3. Поговорить / Атаковать")
            print("4. Выход")
            choice = input("> ").strip().lower()

            if choice == "1":
                self.look_around()
            elif choice == "2":
                self.move()
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