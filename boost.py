import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, BOOSTS_PATH
import os

# Import pygame.locals for special constants
from pygame.locals import (
    RLEACCEL  # render display more quickly 
)

class Boost(pygame.sprite.Sprite):
    def __init__(self):
        super(Boost, self).__init__()
        boostOptions = list(os.listdir(BOOSTS_PATH))
        boostSelected = random.choice(boostOptions)
        self.image = BOOSTS_PATH + boostSelected
        self.surface = pygame.image.load(self.image)
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 10), int(SCREEN_HEIGHT / 10)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)

        # set position to be random location on right edge of screen
        self.rect = self.surface.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    # Update position of boost with constant speed
    def update(self):
        self.rect.move_ip(-3, 0)
        if self.rect.right < 0:
            self.kill()  # once boost reach left edge of screen, remove it