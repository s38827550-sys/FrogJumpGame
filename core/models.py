# core/models.py
import random
import pygame
from .constants import SCREEN_WIDTH, MAX_JUMP_HEIGHT
from .assets import create_glow_surface

class Fly:
    def __init__(self, fly_origin, ground_y):
        self.big = random.random() < 0.15
        self.size = 70 if self.big else random.randint(35, 50)
        self.image = pygame.transform.scale(fly_origin, (self.size, self.size)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        
        self.ground_y = ground_y
        min_y = ground_y - MAX_JUMP_HEIGHT
        max_y = ground_y - self.rect.height - 10
        self.rect.y = random.randint(min_y, max_y)

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        speed = 0.8 if self.big else 1.2
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)

        if self.big:
            glow_radius = self.size // 2 + 12
            self.glow = create_glow_surface(glow_radius, color=(255, 220, 100), alpha=130)
        else:
            self.glow = None

    def update(self):
        min_y = self.ground_y - MAX_JUMP_HEIGHT
        max_y = self.ground_y - self.rect.height - 10

        self.fx += self.vx
        self.fy += self.vy

        if self.fx < 0:
            self.fx = 0
            self.vx *= -1
        elif self.fx > SCREEN_WIDTH - self.rect.width:
            self.fx = SCREEN_WIDTH - self.rect.width
            self.vx *= -1

        if self.fy < min_y:
            self.fy = min_y
            self.vy *= -1
        elif self.fy > max_y:
            self.fy = max_y
            self.vy *= -1

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)
