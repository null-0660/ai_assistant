import pygame
import math
import random

W, H = 600, 800
FPS = 60

BG_TOP = (0, 50, 100)
BG_BOT = (0, 20, 50)
FISH_COLORS = [(255, 100, 100), (255, 200, 100), (100, 255, 200), (200, 100, 255)]
BUBBLE = (150, 200, 255)
TREASURE = (255, 215, 0)

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
        self.x += math.sin(self.wobble) * 20 * dt
        if self.y < -20:
            self.y = H + 20
            self.x = random.randint(0, W)
    
    def draw(self, screen):
        pygame.draw.circle(screen, BUBBLE, (int(self.x), int(self.y)), self.size, 2)

class Fish:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(100, H - 100)
        self.speed = random.uniform(20, 60) * random.choice([-1, 1])
        self.color = random.choice(FISH_COLORS)
        self.size = random.randint(15, 30)
        self.wobble = random.uniform(0, 6.28)
    
    def update(self, dt):
        self.x += self.speed * dt
        self.wobble += dt * 5
        self.y += math.sin(self.wobble) * 10 * dt
        if self.x < -50 or self.x > W + 50:
            self.x = -50 if self.speed > 0 else W + 50
    
    def draw(self, screen):
        f = 1 if self.speed > 0 else -1
        pygame.draw.ellipse(screen, self.color, (self.x - self.size, self.y - self.size//2, self.size*2, self.size))
        pygame.draw.polygon(screen, self.color, [
            (self.x - f * self.size, self.y),
            (self.x - f * self.size * 1.8, self.y - self.size//2),
            (self.x - f * self.size * 1.8, self.y + self.size//2)
        ])
        eye_x = self.x + f * self.size // 2
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(self.y - 3)), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye_x + f*2), int(self.y - 3)), 2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Подводный Мир")
        self.clock = pygame.time.Clock()
        self.bubbles = [Bubble() for _ in range(30)]
        self.fishes = [Fish() for _ in range(8)]
        self.state = "normal"  # normal | treasure
        self.t = 0
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
    
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE and self.state == "normal":
                        self.state = "treasure"
                        self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()
            
            if self.state == "treasure" and self.t > 5:
                self.state = "normal"
                self.t = 0
            
            for b in self.bubbles:
                b.update(dt)
            for f in self.fishes:
                f.update(dt)
            
            self.draw()
            pygame.display.flip()
    
    def draw(self):
        # Градиентный фон
        for y in range(H):
            t = y / H
            col = (
                int(BG_TOP[0] * (1-t) + BG_BOT[0] * t),
                int(BG_TOP[1] * (1-t) + BG_BOT[1] * t),
                int(BG_TOP[2] * (1-t) + BG_BOT[2] * t),
            )
            pygame.draw.line(self.screen, col, (0, y), (W, y))
        
        for b in self.bubbles:
            b.draw(self.screen)
        for f in self.fishes:
            f.draw(self.screen)
        
        # Сундук
        if self.state == "treasure":
            pulse = 0.5 + 0.5 * math.sin(self.t * 5)
            glow_radius = int(80 + pulse * 40)
            glow = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 215, 0, 80), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow, (W//2 - glow_radius, H - 200 - glow_radius))
            
            pygame.draw.rect(self.screen, (150, 80, 30), (W//2 - 60, H - 200, 120, 80))
            pygame.draw.rect(self.screen, TREASURE, (W//2 - 60, H - 200, 120, 15))
            text = self.font.render("С ДНЁМ РОЖДЕНИЯ!", True, TREASURE)
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))
        else:
            text = self.font.render("Нажми ПРОБЕЛ, чтобы найти клад", True, (150, 200, 255))
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))

if __name__ == "__main__":
    Game().run()