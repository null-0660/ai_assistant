import pygame
import math
import random
import sys

W, H = 600, 800
FPS = 60

# Цвета
BG = (10, 10, 30)
STAR = (255, 255, 255)
PLANET = (100, 50, 150)
RING = (200, 150, 250)
SHIP = (100, 255, 100)
PORTAL = (100, 200, 255)

class Star:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.speed = random.uniform(0.5, 3)
        self.size = random.randint(1, 2)
    
    def update(self):
        self.y += self.speed
        if self.y > H:
            self.y = 0
            self.x = random.randint(0, W)
    
    def draw(self, screen):
        pygame.draw.circle(screen, STAR, (int(self.x), int(self.y)), self.size)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Космический Гость")
        self.clock = pygame.time.Clock()
        self.stars = [Star() for _ in range(150)]
        self.state = "intro"  # intro | wait | teleported
        self.t = 0
        self.portal_scale = 0
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
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
                        if self.state == "wait":
                            self.state = "teleported"
                            self.t = 0
                    if e.key == pygame.K_r:
                        self.__init__()
            
            if self.state == "intro" and self.t > 3:
                self.state = "wait"
                self.t = 0
            
            if self.state == "teleported":
                self.portal_scale = min(1.0, self.portal_scale + dt * 2)
                if self.portal_scale >= 1.0 and self.t > 2:
                    self.state = "intro"
                    self.t = 0
                    self.portal_scale = 0
            
            for s in self.stars:
                s.update()
            
            self.draw()
            pygame.display.flip()
    
    def draw(self):
        self.screen.fill(BG)
        for s in self.stars:
            s.draw(self.screen)
        
        # Планета
        pygame.draw.circle(self.screen, PLANET, (W//2, H - 100), 250)
        pygame.draw.ellipse(self.screen, RING, (W//2 - 300, H - 160, 600, 120), 5)
        
        # Корабль
        ship_y = H - 200 + math.sin(self.t * 2) * 10
        pygame.draw.polygon(self.screen, SHIP, [
            (W//2, ship_y - 30),
            (W//2 - 20, ship_y + 20),
            (W//2 + 20, ship_y + 20)
        ])
        
        # Портал
        if self.state == "teleported":
            for i in range(5):
                radius = int(50 * self.portal_scale * (1 + i * 0.2))
                alpha = 100 - i * 20
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*PORTAL, alpha), (radius, radius), radius, 3)
                self.screen.blit(s, (W//2 - radius, ship_y - radius - 50))
        
        # Текст
        if self.state == "intro":
            text = self.font.render("Прибытие на планету...", True, (255, 255, 255))
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))
        elif self.state == "wait":
            pulse = 0.5 + 0.5 * math.sin(self.t * 3)
            text = self.font.render("Нажми ПРОБЕЛ для телепорта", True, (int(255*pulse), 255, 255))
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))
        elif self.state == "teleported":
            text = self.font.render("Возвращение домой...", True, (100, 255, 255))
            self.screen.blit(text, (W//2 - text.get_width()//2, 100))
        
        hint = self.font_small.render("R — заново", True, (100, 100, 150))
        self.screen.blit(hint, (20, H - 30))

if __name__ == "__main__":
    Game().run()