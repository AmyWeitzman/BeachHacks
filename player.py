import pygame
from utils import SCREEN_WIDTH, SCREEN_HEIGHT

# Import pygame.locals for special constants
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    RLEACCEL  # render display more quickly 
)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.currentImg = "./imgs/players/stick_figure.png"
        self.surface = pygame.image.load(self.currentImg).convert()
        self.surface = pygame.transform.scale(self.surface, (int(SCREEN_WIDTH / 8), int(SCREEN_HEIGHT / 4)))
        self.surface.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surface.get_rect()
        self.speed = 5
        self.points = 0

    # Move Player based on keys pressed (direction)
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)

        # Make sure player stays on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    # Get player's points
    def getPts(self):
      return self.points

    # Increment player's points
    def incPts(self, numPts):
      self.points += numPts