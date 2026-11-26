import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG = (10, 10, 25)
CITY = (25, 25, 45)
WINDOW_ON = (255, 220, 100)
MOON = (240, 240, 200)
CAR = (255, 80, 80)
RAIN = (150, 150, 200)
CLOUD = (40, 40, 60)
TEXT_COLOR = (255, 200, 100)


class Window:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.on = random.random() > 0.3
        self.timer = random.uniform(0, 5)
        self.state = self.on

    def update(self, dt, all_on):
        if all_on:
            self.state = True
        else:
            self.timer -= dt
            if self.timer <= 0:
                self.state = not self.state
                self.timer = random.uniform(2, 8)

    def draw(self, screen):
        col = WINDOW_ON if self.state else (20, 20, 30)
        pygame.draw.rect(screen, col, (self.x, self.y, 8, 12))


class Building:
    def __init__(self, x, w, h):
        self.x = x
        self.w = w
        self.h = h
        self.windows = []
        for wy in range(20, h - 20, 30):
            for wx in range(10, w - 10, 20):
                self.windows.append(Window(self.x + wx, H - self.h + wy))

    def update(self, dt, all_on):
        for w in self.windows:
            w.update(dt, all_on)

    def draw(self, screen):
        pygame.draw.rect(screen, CITY, (self.x, H - self.h, self.w, self.h))
        for w in self.windows:
            w.draw(screen)


class Car:
    def __init__(self, direction=1):
        self.x = -50 if direction == 1 else W + 50
        self.y = H - random.randint(30, 80)
        self.direction = direction
        self.speed = random.uniform(100, 200)

    def update(self, dt):
        self.x += self.speed * dt * self.direction

    def draw(self, screen):
        col = CAR if self.direction == 1 else (80, 80, 255)
        pygame.draw.rect(screen, col, (self.x - 15, self.y - 8, 30, 12))
        # Фары
        light_x = self.x + 15 * self.direction
        pygame.draw.circle(screen, (255, 255, 200), (int(light_x), self.y - 2), 6)

    def off_screen(self):
        return self.x < -60 or self.x > W + 60


class Raindrop:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(-50, H)
        self.speed = random.uniform(400, 700)
        self.length = random.randint(8, 16)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > H:
            self.y = -20
            self.x = random.randint(0, W)

    def draw(self, screen):
        pygame.draw.line(screen, RAIN, (self.x, self.y), (self.x, self.y + self.length), 1)


class Firework:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.particles = []
        for _ in range(50):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(50, 200)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(1, 2),
                "age": 0,
            })
        self.color = color

    def update(self, dt):
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 150 * dt
            p["age"] += dt
        self.particles = [p for p in self.particles if p["age"] < p["life"]]

    def draw(self, screen):
        for p in self.particles:
            alpha = 1 - p["age"] / p["life"]
            col = (int(self.color[0] * alpha), int(self.color[1] * alpha), int(self.color[2] * alpha))
            pygame.draw.circle(screen, col, (int(p["x"]), int(p["y"])), 3)

    def done(self):
        return len(self.particles) == 0


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Ночной Город")
        self.clock = pygame.time.Clock()

        self.buildings = []
        x = 0
        while x < W:
            w = random.randint(60, 120)
            h = random.randint(150, 500)
            self.buildings.append(Building(x, w, h))
            x += w + random.randint(5, 20)

        self.cars = []
        self.rain = [Raindrop() for _ in range(80)]
        self.fireworks = []
        self.clouds = [{"x": random.randint(0, W), "y": random.randint(50, 150)} for _ in range(5)]
        self.state = "night"
        self.t = 0
        self.time = 0
        self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
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
                    if e.key == pygame.K_SPACE and self.state == "night":
                        self.state = "day"
                        self.t = 0
                        for _ in range(5):
                            self.fireworks.append(Firework(
                                random.randint(100, W - 100),
                                random.randint(100, 300),
                                (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                            ))
                    if e.key == pygame.K_r:
                        self.__init__()

            if self.state == "day" and self.t > 6:
                self.state = "night"
                self.t = 0

            # Логика
            all_on = self.state == "day"

            for b in self.buildings:
                b.update(dt, all_on)

            if random.random() < 0.03:
                self.cars.append(Car(random.choice([1, -1])))
            for c in self.cars: c.update(dt)
            self.cars = [c for c in self.cars if not c.off_screen()]

            for r in self.rain: r.update(dt)

            for c in self.clouds:
                c["x"] += 20 * dt
                if c["x"] > W + 100:
                    c["x"] = -100

            for f in self.fireworks: f.update(dt)
            self.fireworks = [f for f in self.fireworks if not f.done()]

            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill(BG)

        # Луна
        pygame.draw.circle(self.screen, MOON, (W - 100, 100), 40)
        pygame.draw.circle(self.screen, (200, 200, 180), (W - 110, 90), 8)
        pygame.draw.circle(self.screen, (200, 200, 180), (W - 90, 110), 6)

        # Облака
        for c in self.clouds:
            s = pygame.Surface((150, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*CLOUD, 150), (0, 0, 150, 60))
            self.screen.blit(s, (c["x"], c["y"]))

        # Здания
        for b in self.buildings:
            b.draw(self.screen)

        # Машины
        for c in self.cars:
            c.draw(self.screen)

        # Дождь
        for r in self.rain:
            r.draw(self.screen)

        # Салют
        for f in self.fireworks:
            f.draw(self.screen)

        # Текст
        if self.state == "night":
            surf = self.font.render("Нажми ПРОБЕЛ, чтобы зажечь огни", True, (150, 150, 200))
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 20))
        else:
            surf = self.font_big.render("С ДНЁМ РОЖДЕНИЯ!", True, TEXT_COLOR)
            self.screen.blit(surf, (W//2 - surf.get_width()//2, 30))


if __name__ == "__main__":
    Game().run()