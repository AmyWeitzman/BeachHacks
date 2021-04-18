import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, TRASH_PATH
import os

# Import pygame.locals for special constants
from pygame.locals import (
    RLEACCEL  # render display more quickly 
)

class Trash(pygame.sprite.Sprite):
    def __init__(self):
        super(Trash, self).__init__()
        trashOptions = list(os.listdir(TRASH_PATH))
        trashSelected = random.choice(trashOptions)
        self.image = TRASH_PATH + trashSelected
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

        self.speed = random.randint(4, 8)  # set speed of trash to random number

    # Update position of trash based on speed
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()  # once trash reach left edge of screen, remove it