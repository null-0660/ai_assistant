import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG = (5, 5, 20)
STAR_COLORS = [(255, 255, 255), (200, 200, 255), (255, 255, 200)]
PLANET = (80, 40, 120)
PLANET_GLOW = (120, 60, 180)
RING = (180, 120, 220)
SHIP = (100, 255, 150)
PORTAL = (100, 200, 255)
NEBULA = [(100, 50, 150), (50, 100, 200), (150, 50, 100)]


class Star:
    def __init__(self, layer=1):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.layer = layer
        self.speed = random.uniform(0.5, 3.5) * layer
        self.size = random.randint(1, 3) * layer
        self.color = random.choice(STAR_COLORS)
        self.twinkle = random.uniform(0, 6.28)

    def update(self, dt):
        self.y += self.speed * 20 * dt
        self.twinkle += dt * 5
        if self.y > H:
            self.y = -10
            self.x = random.randint(0, W)

    def draw(self, screen):
        b = 0.6 + 0.4 * math.sin(self.twinkle)
        col = (int(self.color[0] * b), int(self.color[1] * b), int(self.color[2] * b))
        pygame.draw.circle(screen, col, (int(self.x), int(self.y)), self.size)


class Comet:
    def __init__(self):
        self.x = random.randint(-100, W + 100)
        self.y = random.randint(-100, 200)
        self.vx = random.uniform(150, 300)
        self.vy = random.uniform(100, 200)
        self.life = 0
        self.max_life = 3.0
        self.size = random.randint(2, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life += dt

    def draw(self, screen):
        if self.life < self.max_life:
            fade = 1 - (self.life / self.max_life)
            for i in range(10):
                dx = self.x - self.vx * 0.02 * i
                dy = self.y - self.vy * 0.02 * i
                r = int(self.size * (1 - i / 10) * fade)
                if r > 0:
                    pygame.draw.circle(screen, (255, 200 - i * 15, 100), (int(dx), int(dy)), r)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Космический Гость")
        self.clock = pygame.time.Clock()

        self.stars = [Star(random.choice([1, 1, 2, 3])) for _ in range(200)]
        self.comets = [Comet() for _ in range(2)]
        self.state = "intro"
        self.t = 0
        self.time = 0
        self.ship_angle = 0
        self.portal_scale = 0
        self.portal_alpha = 0
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
                    if e.key == pygame.K_SPACE and self.state == "wait":
                        self.state = "teleporting"
                        self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()

            if self.state == "intro" and self.t > 3:
                self.state = "wait"
                self.t = 0

            if self.state == "teleporting":
                self.ship_angle += dt * 10
                self.portal_scale = min(1.0, self.portal_scale + dt * 1.5)
                self.portal_alpha = min(1.0, self.portal_alpha + dt * 3)
                if self.t > 4:
                    self.state = "done"
                    self.t = 0

            for s in self.stars: s.update(dt)
            for c in self.comets: c.update(dt)
            self.comets = [c for c in self.comets if c.life < c.max_life]
            if random.random() < 0.005:
                self.comets.append(Comet())

            self.draw()
            pygame.display.flip()

    def draw(self):
        # Фон
        for y in range(H):
            t = y / H
            col = (int(5 + 15 * t), int(5 + 10 * t), int(20 + 40 * t))
            pygame.draw.line(self.screen, col, (0, y), (W, y))

        # Туманность
        for i, col in enumerate(NEBULA):
            alpha = 20 + 15 * math.sin(self.time * 0.5 + i)
            neb = pygame.Surface((300, 200), pygame.SRCALPHA)
            pygame.draw.ellipse(neb, (*col, int(alpha)), (0, 0, 300, 200))
            self.screen.blit(neb, (W//2 - 150 + i * 30 - 60, 100 + i * 50))

        for s in self.stars: s.draw(self.screen)
        for c in self.comets: c.draw(self.screen)

        # Планета с атмосферой
        planet_y = H + 100
        for r in range(350, 250, -10):
            alpha = int(20 * (1 - (350 - r) / 100))
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*PLANET_GLOW, alpha), (r, r), r)
            self.screen.blit(s, (W//2 - r, planet_y - r))
        pygame.draw.circle(self.screen, PLANET, (W//2, planet_y), 250)
        pygame.draw.ellipse(self.screen, RING, (W//2 - 320, planet_y - 60, 640, 120), 6)

        # Корабль
        ship_y = H//2 + 150
        if self.state == "teleporting":
            ship_y -= self.t * 80
        ship_x = W//2
        angle = self.ship_angle if self.state == "teleporting" else 0

        ship = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.polygon(ship, SHIP, [(20, 0), (0, 50), (20, 40), (40, 50)])
        pygame.draw.circle(ship, (255, 255, 200), (20, 15), 5)
        ship = pygame.transform.rotate(ship, math.degrees(angle))
        self.screen.blit(ship, ship.get_rect(center=(ship_x, int(ship_y))))

        # Портал
        if self.state == "teleporting":
            for i in range(8):
                r = int(80 * self.portal_scale * (1 + i * 0.15))
                if r > 0:
                    alpha = int(80 * self.portal_alpha * (1 - i / 8))
                    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*PORTAL, alpha), (r, r), r, 4)
                    self.screen.blit(s, (ship_x - r, int(ship_y) - r))

        # Текст
        if self.state == "intro":
            a = min(1.0, self.t / 0.5)
            surf = self.font_big.render("Прибытие на планету...", True, (200, 200, 255))
            surf.set_alpha(int(255 * a))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 80))
        elif self.state == "wait":
            pulse = 0.5 + 0.5 * math.sin(self.time * 3)
            surf = self.font.render("Нажми ПРОБЕЛ для телепорта", True, (int(200*pulse), 255, 255))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 80))
        elif self.state == "teleporting":
            surf = self.font_big.render("ТЕЛЕПОРТ...", True, (100, 255, 255))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 80))
        elif self.state == "done":
            surf = self.font_big.render("С ДНЁМ РОЖДЕНИЯ!", True, (255, 200, 100))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 80))


if __name__ == "__main__":
    Game().run()