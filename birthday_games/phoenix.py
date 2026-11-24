import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG = (20, 10, 20)
EGG = (240, 220, 180)
FIRE = [(255, 100, 0), (255, 150, 50), (255, 200, 100)]
PHOENIX = (255, 100, 50)
TEXT = (255, 200, 100)

class Spark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-150, 0)
        self.life = random.uniform(0.5, 1.5)
        self.age = 0
        self.color = random.choice(FIRE)
    
    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 100 * dt
    
    def draw(self, screen):
        if self.age < self.life:
            alpha = 1 - self.age / self.life
            r = int(self.color[0] * alpha)
            g = int(self.color[1] * alpha)
            b = int(self.color[2] * alpha)
            pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), 3)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Огненный Феникс")
        self.clock = pygame.time.Clock()
        self.state = "egg"  # egg | hatching | flying
        self.t = 0
        self.sparks = []
        self.cracks = 0
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
    
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            
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
                            self.t = 0
                            if self.cracks >= 3:
                                self.state = "flying"
                                self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()
            
            if self.state == "hatching" and self.t > 2:
                self.state = "flying"
                self.t = 0
            
            if self.state == "flying":
                for _ in range(5):
                    self.sparks.append(Spark(W//2, H//2))
                for s in self.sparks:
                    s.update(dt)
                self.sparks = [s for s in self.sparks if s.age < s.life]
            
            self.draw()
            pygame.display.flip()
    
    def draw(self):
        self.screen.fill(BG)
        
        # Яйцо
        if self.state in ("egg", "hatching"):
            egg_y = H//2 + 100
            pygame.draw.ellipse(self.screen, EGG, (W//2 - 80, egg_y - 120, 160, 200))
            
            for i in range(self.cracks):
                pygame.draw.line(self.screen, (100, 50, 20),
                                 (W//2 - 40 + i * 30, egg_y - 80),
                                 (W//2 - 20 + i * 30, egg_y + 40), 3)
            
            if self.state == "egg":
                text = self.font.render("Нажми ПРОБЕЛ, чтобы разбить яйцо", True, (200, 200, 200))
                self.screen.blit(text, (W//2 - text.get_width()//2, 100))
            else:
                text = self.font.render(f"Ещё {3 - self.cracks} нажатия!", True, (255, 200, 100))
                self.screen.blit(text, (W//2 - text.get_width()//2, 100))
        
        # Феникс
        if self.state == "flying":
            for s in self.sparks:
                s.draw(self.screen)
            
            float_y = H//2 + math.sin(self.t * 3) * 20
            pygame.draw.polygon(self.screen, PHOENIX, [
                (W//2, float_y),
                (W//2 - 60, float_y - 30),
                (W//2 - 40, float_y + 30)
            ])
            pygame.draw.polygon(self.screen, PHOENIX, [
                (W//2, float_y),
                (W//2 + 60, float_y - 30),
                (W//2 + 40, float_y + 30)
            ])
            pygame.draw.circle(self.screen, (255, 255, 100), (W//2 - 10, float_y - 5), 5)
            pygame.draw.circle(self.screen, (255, 255, 100), (W//2 + 10, float_y - 5), 5)
            
            text = self.font.render("С ДНЁМ РОЖДЕНИЯ!", True, TEXT)
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))

if __name__ == "__main__":
    Game().run()