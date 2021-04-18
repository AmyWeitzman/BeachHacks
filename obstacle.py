import random
import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, OBSTACLES_PATH
import os

# Import pygame.locals for special constants
from pygame.locals import (
    RLEACCEL  # render display more quickly 
)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super(Obstacle, self).__init__()
        obstacleOptions = list(os.listdir(OBSTACLES_PATH))
        self.image = OBSTACLES_PATH + random.choice(obstacleOptions)
        self.surface = pygame.image.load(self.image)
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 9), int(SCREEN_HEIGHT / 8)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)

        # set position to be random location on right edge of screen
        self.rect = self.surface.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

        self.speed = random.randint(4, 10)  # set speed of obstacle to random number

    # Update position of obstacle based on speed
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()  # once obstacle reach left edge of screen, remove it