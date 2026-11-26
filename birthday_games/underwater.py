import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG_TOP = (20, 80, 140)
BG_BOT = (5, 15, 40)
FISH_COLORS = [(255, 100, 100), (255, 200, 100), (100, 255, 200), (200, 100, 255), (255, 150, 200)]
BUBBLE = (150, 200, 255)
TREASURE = (255, 215, 0)
LIGHT_RAY = (100, 200, 255)


class Fish:
    def __init__(self):
        self.x = random.uniform(-100, W + 100)
        self.y = random.uniform(150, H - 150)
        self.speed = random.uniform(20, 60) * random.choice([-1, 1])
        self.color = random.choice(FISH_COLORS)
        self.size = random.randint(15, 30)
        self.wobble = random.uniform(0, 6.28)
        self.tail_phase = random.uniform(0, 6.28)

    def update(self, dt):
        self.x += self.speed * dt
        self.wobble += dt * 3
        self.tail_phase += dt * 8
        self.y += math.sin(self.wobble) * 15 * dt

        if self.x < -100:
            self.x = W + 100
            self.y = random.uniform(150, H - 150)
        elif self.x > W + 100:
            self.x = -100
            self.y = random.uniform(150, H - 150)

    def draw(self, screen):
        f = 1 if self.speed > 0 else -1
        tail_wag = math.sin(self.tail_phase) * 0.3

        # Хвост
        tail_x = self.x - f * self.size * 1.5
        tail_pts = [
            (self.x - f * self.size, self.y),
            (tail_x + f * self.size * 0.3 * tail_wag, self.y - self.size * 0.6),
            (tail_x + f * self.size * 0.3 * tail_wag, self.y + self.size * 0.6),
        ]
        pygame.draw.polygon(screen, self.color, tail_pts)

        # Тело
        pygame.draw.ellipse(screen, self.color,
                            (self.x - self.size, self.y - self.size * 0.5, self.size * 2, self.size))

        # Глаз
        eye_x = self.x + f * self.size * 0.6
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(self.y - 3)), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye_x + f*2), int(self.y - 3)), 2)


class Jellyfish:
    def __init__(self):
        self.x = random.uniform(0, W)
        self.y = random.uniform(-100, H)
        self.speed = random.uniform(15, 30)
        self.size = random.randint(20, 40)
        self.pulse = random.uniform(0, 6.28)
        self.color = random.choice([(200, 100, 255), (255, 100, 200), (150, 100, 255)])

    def update(self, dt):
        self.y -= self.speed * dt
        self.pulse += dt * 2
        if self.y < -80:
            self.y = H + 80
            self.x = random.uniform(0, W)

    def draw(self, screen):
        s = self.size + math.sin(self.pulse) * 5
        alpha = int(80 + 40 * math.sin(self.pulse))
        col = (*self.color, alpha)
        surf = pygame.Surface((int(s*2), int(s*2)), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, col, (0, s, s*2, s*0.8))
        for i in range(5):
            tx = s + (i - 2) * s * 0.4
            ty = s + s * 0.7
            pygame.draw.line(surf, col, (tx, ty), (tx, ty + s * 1.2), 3)
        screen.blit(surf, (self.x - s, self.y - s))


class Bubble:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = H + random.randint(0, 200)
        self.speed = random.uniform(30, 80)
        self.size = random.randint(3, 10)
        self.wobble = random.uniform(0, 6.28)

    def update(self, dt):
        self.y -= self.speed * dt
        self.wobble += dt * 2
        self.x += math.sin(self.wobble) * 30 * dt
        if self.y < -20:
            self.y = H + 20
            self.x = random.randint(0, W)

    def draw(self, screen):
        pygame.draw.circle(screen, BUBBLE, (int(self.x), int(self.y)), self.size, 2)
        # Блик
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - self.size*0.3), int(self.y - self.size*0.3)), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Подводный Мир")
        self.clock = pygame.time.Clock()

        self.bubbles = [Bubble() for _ in range(40)]
        self.fishes = [Fish() for _ in range(10)]
        self.jellyfish = [Jellyfish() for _ in range(4)]
        self.state = "normal"
        self.t = 0
        self.time = 0
        self.font_big = pygame.font.SysFont("Arial", 36, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self.time += dt

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE and self.state == "normal":
                        self.state = "treasure"
                        self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()

            if self.state == "treasure" and self.t > 6:
                self.state = "normal"
                self.t = 0

            for b in self.bubbles: b.update(dt)
            for f in self.fishes: f.update(dt)
            for j in self.jellyfish: j.update(dt)

            self.draw()
            pygame.display.flip()

    def draw(self):
        # Градиент
        for y in range(H):
            t = y / H
            col = (
                int(BG_TOP[0] * (1-t) + BG_BOT[0] * t),
                int(BG_TOP[1] * (1-t) + BG_BOT[1] * t),
                int(BG_TOP[2] * (1-t) + BG_BOT[2] * t),
            )
            pygame.draw.line(self.screen, col, (0, y), (W, y))

        # Световые лучи
        for i in range(5):
            x = 100 + i * 100 + math.sin(self.time + i) * 30
            alpha = 20 + 15 * math.sin(self.time * 1.5 + i)
            surf = pygame.Surface((80, H), pygame.SRCALPHA)
            pygame.draw.polygon(surf, (*LIGHT_RAY, int(alpha)), [(0, 0), (80, 0), (50, H), (30, H)])
            self.screen.blit(surf, (x, 0))

        # Волны сверху
        for i in range(W):
            wave_y = 20 + math.sin(self.time * 2 + i * 0.05) * 10
            pygame.draw.circle(self.screen, (100, 200, 255), (i, int(wave_y)), 1)

        for b in self.bubbles: b.draw(self.screen)
        for j in self.jellyfish: j.draw(self.screen)
        for f in self.fishes: f.draw(self.screen)

        # Сундук
        if self.state == "treasure":
            pulse = 0.5 + 0.5 * math.sin(self.t * 5)
            glow_r = int(100 + pulse * 60)
            glow = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*TREASURE, 100), (glow_r, glow_r), glow_r)
            self.screen.blit(glow, (W//2 - glow_r, H - 220 - glow_r))

            pygame.draw.rect(self.screen, (120, 60, 20), (W//2 - 70, H - 220, 140, 90))
            pygame.draw.rect(self.screen, TREASURE, (W//2 - 70, H - 220, 140, 15))
            pygame.draw.rect(self.screen, (80, 40, 10), (W//2 - 70, H - 220, 140, 90), 3)

            surf = self.font_big.render("С ДНЁМ РОЖДЕНИЯ!", True, TREASURE)
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 100))
        else:
            surf = self.font.render("Нажми ПРОБЕЛ, чтобы найти клад", True, (150, 200, 255))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 100))


if __name__ == "__main__":
    Game().run()