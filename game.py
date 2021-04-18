import pygame
import pygame_menu
from player import Player
from obstacle import Obstacle
from trash import Trash
from boost import Boost
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, AUDIO_PATH, TRASH_PATH, LOGO_PATH
from random import randint, choices
import time
import threading
import os

# Import pygame.locals for special constants
from pygame.locals import (
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
    RLEACCEL
)

class Game():
  def __init__(self):
    pass   # initialize in separate method to make it easier to play again

  def initGame(self):
    self.gameTitle = 'Beach Cleanup'
    self.pointsForTrashCollected = 20
    self.pointsForBoostCollected = 100
    self.scorePos = SCREEN_WIDTH - 100
    self.topMenuBarWidth = 350
    self.topMenuBarPos = self.scorePos - self.topMenuBarWidth - 100
    self.topMenuRewardWidth = int(SCREEN_WIDTH / 14)
    self.topMenuRewardHeight = int(SCREEN_HEIGHT / 14)
    self.totalTime = 0
    self.collisionDelta = 30
    self.clock = None
    self.screen = None
    self.playMusic = True
    self.playSounds = True
    self.sounds = {}
    self.settingsMenu = None
    self.gameOverMenu = None

    pygame.mixer.init()   # for sounds, use default configuration
    pygame.init()
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # create screen object with size SCREEN_WIDTH x SCREEN_HEIGHT
    pygame.display.set_caption(self.gameTitle)    # set window title
    gameLogo = pygame.image.load(LOGO_PATH)       # load game logo
    pygame.display.set_icon(gameLogo)  

    # Create custom events for adding new obstacles/trash
    self.ADD_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(self.ADD_OBSTACLE, randint(1000, 3000))  # add new obstacles at random interval
    self.ADD_TRASH = pygame.USEREVENT + 2
    pygame.time.set_timer(self.ADD_TRASH, randint(1000, 3000))    # add new trash at random interval
    self.ADD_BOOST = pygame.USEREVENT + 3
    pygame.time.set_timer(self.ADD_BOOST, randint(5000, 10000))    # add boost at random interval

    # Sprites
    self.player = Player()  
    self.obstacles = pygame.sprite.Group() 
    self.trash = pygame.sprite.Group()
    self.boosts = pygame.sprite.Group()
    self.allSprites = pygame.sprite.Group()
    self.allSprites.add(self.player)

    self.gameOver = False             # keep track of whether game over
    self.startTime = None      
    self.clock = pygame.time.Clock()  # set up clock for good frame rate

    # Sounds
    pygame.mixer.music.load(AUDIO_PATH + 'waves.wav')   # background music
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(loops=-1)                  # -1 = loop forever
    
    collect_trash_sound = pygame.mixer.Sound(AUDIO_PATH + "collect_trash.wav")   # sound effect when collect trash
    pygame.mixer.Sound.set_volume(collect_trash_sound, 0.8)
    self.sounds['collect_trash_sound'] = collect_trash_sound
    
    collect_boost_sound = pygame.mixer.Sound(AUDIO_PATH + "collect_boost.wav")   # sound effect when collect boost
    pygame.mixer.Sound.set_volume(collect_boost_sound, 0.8)
    self.sounds['collect_boost_sound'] = collect_boost_sound

    game_over_sound = pygame.mixer.Sound(AUDIO_PATH + "game_over.wav")           # sound effect when game over
    pygame.mixer.Sound.set_volume(game_over_sound, 0.2)
    self.sounds['game_over_sound'] = game_over_sound

  def changeMusicSetting(self, val):
    self.playMusic = not self.playMusic
    if self.playMusic:
      pygame.mixer.music.play(loops=-1)  
    else:
      pygame.mixer.music.stop()  
    
  def changeSoundSetting(self, val):
    self.playSounds = not self.playSounds

  def startGame(self):
    self.settingsMenu.disable()  # close settings menu and begin game
    self.gameLoop()

  def showSettings(self):
    self.settingsMenu = pygame_menu.Menu(
      width=int(SCREEN_WIDTH * 0.75), 
      height=int(SCREEN_HEIGHT * 0.75), 
      title='Settings', 
      theme=pygame_menu.themes.THEME_BLUE
    )
    self.settingsMenu.add.image(LOGO_PATH, image_id='settings_logo', margin=(0, 10), scale=(0.5, 0.5))
    self.settingsMenu.add.toggle_switch('Background Music', True, toggleswitch_id='music_setting', onchange=self.changeMusicSetting).set_selection_effect(None)
    self.settingsMenu.add.toggle_switch('Sound Effects', True, toggleswitch_id='sound_setting', onchange=self.changeSoundSetting).set_border(0, None).set_selection_effect(None)
    self.settingsMenu.add.button('Play', self.startGame, button_id='play_btn').set_background_color((212, 195, 171))  # light brown
    self.settingsMenu.mainloop(self.screen)   # start by showing settings menu before continuing game

  def drawSprites(self):
    # want to keep sprites layered in specific order
    orderedSprites = []
    orderedSprites.extend([x for x in self.obstacles])
    orderedSprites.extend([x for x in self.trash])
    orderedSprites.extend([x for x in self.boosts])
    orderedSprites.extend([self.player])

    for sprite in orderedSprites:
      self.screen.blit(sprite.surface, sprite.rect)  

  def drawScore(self):
    font = pygame.font.SysFont("Arial", 50)  # font family, font size
    text_surface = font.render('Score: ' + str(self.player.getPts()), True, (0, 0, 0))  
    text_rect = text_surface.get_rect()
    text_rect.midtop = (self.scorePos, 20)
    self.screen.blit(text_surface, text_rect)

  def updateTime(self):  
    curTime = int(time.time() - self.startTime)
    self.totalTime = curTime
    return curTime

  def drawTime(self, curTime):
    font = pygame.font.SysFont("Arial", 50)  # font family, font size
    text_surface = font.render('Time: ' + str(curTime)+'s', True, (0, 0, 0)) 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 60)
    self.screen.blit(text_surface, text_rect)

  def drawAllSprites(self):
    self.drawSprites()
    self.drawScore()
    self.drawTime(self.updateTime())

  def updateSpritePos(self, pressed_keys):
    self.player.update(pressed_keys)
    self.obstacles.update()
    self.trash.update()
    self.boosts.update()

  def setBackground(self):
    bg_image = pygame.image.load('./imgs/sand_bg.jpg')
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_rect = bg_image.get_rect()
    bg_rect.left, bg_rect.top = [0, 0]
    self.screen.fill([255, 255, 255])
    self.screen.blit(bg_image, bg_rect)

  def checkXCollision(self, leftSprite, rightSprite):
    return ((leftSprite.rect.right > rightSprite.rect.left) and ((leftSprite.rect.right - rightSprite.rect.left) >= self.collisionDelta))

  def checkYCollision(self, leftSprite, rightSprite):
    return self.checkTopCollision(leftSprite, rightSprite) or self.checkBottomCollision(leftSprite, rightSprite)

  def checkTopCollision(self, leftSprite, rightSprite):
    return ((leftSprite.rect.bottom > rightSprite.rect.top) and ((leftSprite.rect.bottom - rightSprite.rect.top) >= self.collisionDelta)) and ((leftSprite.rect.bottom - rightSprite.rect.top) <= (leftSprite.rect.height - self.collisionDelta))

  def checkBottomCollision(self, leftSprite, rightSprite):
    return ((rightSprite.rect.bottom > leftSprite.rect.top) and ((rightSprite.rect.bottom - leftSprite.rect.top) >= self.collisionDelta)) and ((rightSprite.rect.bottom - leftSprite.rect.top) <= (leftSprite.rect.height - self.collisionDelta))

  def checkCollision(self, leftSprite, rightSprite):
    # only count as collision is bounding boxes overlap by certain amount
    if self.checkXCollision(leftSprite, rightSprite) and self.checkYCollision(leftSprite, rightSprite):
      return True
    return False

  def handleTrashCollision(self):
    trashCollected = pygame.sprite.spritecollide(self.player, self.trash, True)     # True = remove from trash
    if trashCollected:  
      self.player.incPts(self.pointsForTrashCollected * len(trashCollected))  # add points for each piece of trash collected
      if self.playSounds:
        self.sounds['collect_trash_sound'].play()

  def handleBoostsCollision(self):
    boostsCollected = pygame.sprite.spritecollide(self.player, self.boosts, True)   # True = remove from boosts
    if boostsCollected:
      self.player.incPts(self.pointsForBoostCollected * len(boostsCollected))
      if self.playSounds:
        self.sounds['collect_boost_sound'].play()

  def collisionDetection(self):
    for obstacle in self.obstacles:
      if self.checkCollision(self.player, obstacle):
        if self.playSounds:
          self.sounds['game_over_sound'].play()
          while pygame.mixer.get_busy():     # wait for sound to finish playing 
            pass
        self.gameOver = True
        return   # obstacle collision: game over
    self.handleTrashCollision()
    self.handleBoostsCollision()
    
  def handleEvents(self):
    for event in pygame.event.get():
      if event.type == KEYDOWN:        # player pressed key
        if event.key == K_ESCAPE:      # key was ESC
          self.gameOver = True         # end game
      elif event.type == QUIT:                # player closed game
          self.gameOver = True                # end game
      elif event.type == self.ADD_OBSTACLE:   # add new obstacle
        newObstacle = Obstacle()
        self.obstacles.add(newObstacle)
        self.allSprites.add(newObstacle)
      elif event.type == self.ADD_TRASH:     # add new piece of trash
        newTrash = Trash()
        self.trash.add(newTrash)
        self.allSprites.add(newTrash)
      elif event.type == self.ADD_BOOST:    # add boost
        addBoost = choices([0, 1], cum_weights=(70, 30))   # 30% chance of boost
        if addBoost:
          newBoost = Boost()
          self.boosts.add(newBoost)
          self.allSprites.add(newBoost)

  def gameLoop(self):
    # Run game loop
    self.startTime = time.time()
    while not self.gameOver:
      self.handleEvents()  # process events

      # Check keys pressed and update sprites
      pressed_keys = pygame.key.get_pressed()  # array of keys pressed, empty if none
      self.updateSpritePos(pressed_keys)       # update sprite positions
      self.setBackground()
      self.collisionDetection()  # collision detection: if player hits obstacle, game over; if player hits trash/boost, earn points
      self.drawAllSprites()  # draw all sprites

      pygame.display.flip()  # update screen
      self.clock.tick(30)    # maintain rate of 30 frames per second
    
    self.showGameOverMenu()  # game over

  def showGameOverMenu(self):
    self.gameOverMenu = pygame_menu.Menu(
      width=int(SCREEN_WIDTH * 0.75), 
      height=int(SCREEN_HEIGHT * 0.75), 
      title='Game Over', 
      theme=pygame_menu.themes.THEME_BLUE
    )
    self.gameOverMenu.add.label('Thanks for playing!', label_id='thanks_label')
    self.gameOverMenu.add.label('Score: ' + str(self.player.getPts()), label_id='score_label')
    self.gameOverMenu.add.label('Time: ' + str(self.totalTime) + 's', label_id='time_label')
    self.gameOverMenu.add.button('Play Again', self.playAgain).set_background_color((30, 159, 199))  # mid-light blue
    self.gameOverMenu.mainloop(self.screen)   

  def playAgain(self):
      self.gameOverMenu.disable()
      self.run()

  def run(self):
    self.initGame()
    self.showSettings()
