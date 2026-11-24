import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG = (10, 10, 25)
CITY = (30, 30, 50)
WINDOW_ON = (255, 220, 100)
MOON = (240, 240, 200)
CAR = (255, 80, 80)
TEXT_COLOR = (255, 200, 100)

class Building:
    def __init__(self, x, w, h):
        self.x = x
        self.w = w
        self.h = h
        self.windows = []
        for y in range(20, h - 20, 30):
            for wx in range(10, w - 10, 20):
                if random.random() > 0.3:
                    self.windows.append((wx, y))
    
    def draw(self, screen, lights_on):
        pygame.draw.rect(screen, CITY, (self.x, H - self.h, self.w, self.h))
        for wx, wy in self.windows:
            col = WINDOW_ON if (lights_on and random.random() > 0.2) else (20, 20, 30)
            pygame.draw.rect(screen, col, (self.x + wx, H - self.h + wy, 8, 12))

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
        
        self.state = "night"  # night | day
        self.t = 0
        self.lights_on = False
        self.cars = []
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
    
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        if self.state == "night":
                            self.state = "day"
                            self.lights_on = True
                            self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()
            
            if self.state == "day" and self.t > 5:
                self.state = "night"
                self.lights_on = False
                self.t = 0
            
            # Машины
            if random.random() < 0.02:
                self.cars.append({"x": random.randint(0, W), "speed": random.uniform(100, 200)})
            for c in self.cars:
                c["x"] += c["speed"] * dt
            self.cars = [c for c in self.cars if c["x"] < W + 50]
            
            self.draw()
            pygame.display.flip()
    
    def draw(self):
        self.screen.fill(BG)
        
        # Луна
        pygame.draw.circle(self.screen, MOON, (W - 100, 100), 40)
        
        # Здания
        for b in self.buildings:
            b.draw(self.screen, self.lights_on)
        
        # Машины
        for c in self.cars:
            pygame.draw.rect(self.screen, CAR, (c["x"], H - 20, 30, 10))
            pygame.draw.circle(self.screen, (255, 255, 200), (c["x"] + 30, H - 15), 4)
        
        # Текст
        if self.state == "night":
            text = self.font.render("Нажми ПРОБЕЛ, чтобы зажечь огни", True, (150, 150, 200))
            self.screen.blit(text, (W//2 - text.get_width()//2, 50))
        else:
            text = self.font.render("С ДНЁМ РОЖДЕНИЯ!", True, TEXT_COLOR)
            self.screen.blit(text, (W//2 - text.get_width()//2, 200))
        
        hint = self.font_small.render("R — заново", True, (80, 80, 100))
        self.screen.blit(hint, (20, H - 30))

if __name__ == "__main__":
    Game().run()