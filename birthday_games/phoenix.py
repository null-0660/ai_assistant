import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG_DARK = (20, 10, 20)
BG_DAWN = (80, 40, 30)
EGG = (240, 220, 180)
CRACK = (80, 40, 20)
FIRE = [(255, 80, 0), (255, 150, 50), (255, 220, 100), (255, 100, 50)]
PHOENIX = (255, 100, 50)
PHOENIX_DARK = (200, 50, 20)
TEXT = (255, 220, 120)


class Spark:
    def __init__(self, x, y, spread=100, upward=True):
        self.x = x
        self.y = y
        angle = random.uniform(0, 6.28) if not upward else random.uniform(-2.5, -0.5)
        speed = random.uniform(50, spread)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.5, 1.5)
        self.age = 0
        self.color = random.choice(FIRE)
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 80 * dt
        self.vx *= 0.98

    def draw(self, screen):
        if self.age < self.life:
            alpha = 1 - self.age / self.life
            col = (
                int(min(255, self.color[0] * alpha + 50)),
                int(self.color[1] * alpha),
                int(self.color[2] * alpha)
            )
            pygame.draw.circle(screen, col, (int(self.x), int(self.y)), self.size)

    def done(self):
        return self.age >= self.life


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Огненный Феникс")
        self.clock = pygame.time.Clock()

        self.state = "egg"
        self.t = 0
        self.time = 0
        self.sparks = []
        self.cracks = 0
        self.font_big = pygame.font.SysFont("Arial", 42, bold=True)
        self.font = pygame.font.SysFont("Arial", 22)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self.time += dt

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        if self.state == "egg":
                            self.state = "hatching"
                            self.t = 0
                        elif self.state == "hatching":
                            self.cracks += 1
                            for _ in range(20):
                                self.sparks.append(Spark(W//2, H//2 + 50, 150))
                            if self.cracks >= 3:
                                self.state = "flying"
                                self.t = 0
                                for _ in range(80):
                                    self.sparks.append(Spark(W//2, H//2, 250))
                    if e.key == pygame.K_r:
                        self.__init__()

            if self.state == "hatching":
                # Искры от яйца
                if random.random() < 0.3:
                    self.sparks.append(Spark(W//2 + random.uniform(-60, 60), H//2 + 50, 80, upward=True))
                if self.t > 4:
                    self.state = "flying"
                    self.t = 0

            if self.state == "flying":
                # След феникса
                for _ in range(4):
                    self.sparks.append(Spark(
                        W//2 + random.uniform(-40, 40),
                        H//2 + math.sin(self.t * 3) * 20 + random.uniform(-20, 20),
                        50, upward=True
                    ))

            for s in self.sparks: s.update(dt)
            self.sparks = [s for s in self.sparks if not s.done()]

            self.draw()
            pygame.display.flip()

    def draw(self):
        # Фон меняется
        if self.state == "flying":
            progress = min(1.0, self.t / 4)
            bg = tuple(int(BG_DARK[i] * (1-progress) + BG_DAWN[i] * progress) for i in range(3))
        else:
            bg = BG_DARK

        self.screen.fill(bg)

        # Искры (рисуются за яйцом)
        for s in self.sparks:
            s.draw(self.screen)

        # Яйцо
        if self.state in ("egg", "hatching"):
            egg_y = H//2 + 100
            pulse = 1 + 0.05 * math.sin(self.time * 4) if self.state == "hatching" else 1
            ew, eh = int(160 * pulse), int(200 * pulse)

            # Свечение
            glow = pygame.Surface((ew*2, eh*2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 150, 50, 60), (0, 0, ew*2, eh*2))
            self.screen.blit(glow, (W//2 - ew, egg_y - eh))

            pygame.draw.ellipse(self.screen, EGG, (W//2 - ew//2, egg_y - eh, ew, eh))

            # Трещины
            for i in range(self.cracks):
                start_x = W//2 - 40 + i * 30
                start_y = egg_y - 80
                for j in range(5):
                    x1 = start_x + random.randint(-8, 8) + j * 8
                    y1 = start_y + j * 25
                    x2 = x1 + random.randint(-15, 15)
                    y2 = y1 + 25
                    pygame.draw.line(self.screen, CRACK, (x1, y1), (x2, y2), 3)

            if self.state == "egg":
                pulse_t = 0.5 + 0.5 * math.sin(self.time * 2)
                surf = self.font.render("Нажми ПРОБЕЛ, чтобы разбить яйцо", True, (200, 200, 200))
                self.screen.blit(surf, (W//2 - surf.get_width()//2, 100))
            else:
                surf = self.font.render(f"Трещина {self.cracks}/3 — ЖМИ!", True, (255, 200, 100))
                self.screen.blit(surf, (W//2 - surf.get_width()//2, 100))

        # Феникс
        if self.state == "flying":
            float_y = H//2 + math.sin(self.t * 3) * 30
            wing_angle = math.sin(self.t * 8) * 0.5

            # Огненное свечение
            glow_r = 150
            glow = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 50, 80), (glow_r, glow_r), glow_r)
            self.screen.blit(glow, (W//2 - glow_r, int(float_y) - glow_r))

            # Левое крыло
            left_wing = [
                (W//2 - 20, float_y),
                (W//2 - 120, float_y - 60 + wing_angle * 30),
                (W//2 - 140, float_y + 20 + wing_angle * 30),
                (W//2 - 80, float_y + 40),
            ]
            pygame.draw.polygon(self.screen, PHOENIX_DARK, left_wing)
            pygame.draw.polygon(self.screen, PHOENIX, [
                (W//2 - 20, float_y),
                (W//2 - 100, float_y - 40 + wing_angle * 25),
                (W//2 - 110, float_y + 10 + wing_angle * 25),
                (W//2 - 70, float_y + 30),
            ])

            # Правое крыло
            right_wing = [
                (W//2 + 20, float_y),
                (W//2 + 120, float_y - 60 + wing_angle * 30),
                (W//2 + 140, float_y + 20 + wing_angle * 30),
                (W//2 + 80, float_y + 40),
            ]
            pygame.draw.polygon(self.screen, PHOENIX_DARK, right_wing)
            pygame.draw.polygon(self.screen, PHOENIX, [
                (W//2 + 20, float_y),
                (W//2 + 100, float_y - 40 + wing_angle * 25),
                (W//2 + 110, float_y + 10 + wing_angle * 25),
                (W//2 + 70, float_y + 30),
            ])

            # Тело
            pygame.draw.ellipse(self.screen, PHOENIX, (W//2 - 30, float_y - 40, 60, 80))

            # Голова
            pygame.draw.circle(self.screen, PHOENIX, (W//2, int(float_y - 50)), 20)

            # Глаза
            pygame.draw.circle(self.screen, (255, 255, 100), (W//2 - 8, int(float_y - 55)), 4)
            pygame.draw.circle(self.screen, (255, 255, 100), (W//2 + 8, int(float_y - 55)), 4)

            # Хвост
            tail_swing = math.sin(self.t * 4) * 20
            pygame.draw.polygon(self.screen, PHOENIX_DARK, [
                (W//2 - 20, float_y + 40),
                (W//2 - 40 + tail_swing, float_y + 150),
                (W//2, float_y + 130),
                (W//2 + 40 + tail_swing, float_y + 150),
                (W//2 + 20, float_y + 40),
            ])

            surf = self.font_big.render("С ДНЁМ РОЖДЕНИЯ!", True, TEXT)
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 80))


if __name__ == "__main__":
    Game().run()