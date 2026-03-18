# core/assets.py
import os
import pygame
from .constants import ASSETS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT

def load_img(name: str):
    return pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()

def scale_img_to_screen(img, smooth=True):
    if smooth:
        return pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

def create_glow_surface(radius, color, alpha=120):
    size = radius * 2
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, (*color, alpha), (radius, radius), radius)
    return surface

class AssetManager:
    def __init__(self):
        self.background = load_img("background_mygame2.png")
        self.prologue_bg = scale_img_to_screen(load_img("background_mygame_Prologue.png"))
        self.start_bg = scale_img_to_screen(load_img("background_mygame_start.PNG"))
        self.name_entry_bg = scale_img_to_screen(load_img("name_entry.png"))

        self.frog_normal = load_img("frog_normal.png")
        self.frog_jump = load_img("frog_jump.png")
        self.frog_prepare = load_img("frog_prepare_jump.png")
        self.frog_left = load_img("frog_left.png")
        self.frog_right = load_img("frog_right.png")
        self.fly_origin = load_img("fly.png")
