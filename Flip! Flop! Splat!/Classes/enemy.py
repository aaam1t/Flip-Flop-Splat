import pygame
from os import path
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)

        self.enemytype = type

        self.spriteSheet = EnemyImg(self.enemytype)
        self.image = self.spriteSheet.getImage(0, 0, 23, 38)        # load enemy image

        if self.enemytype == "enemy":
            self.image.set_colorkey(WHITE)
        else:
            self.image.set_colorkey(BLACK)      # key out background of enemy sprite

        self.xPos = x
        self.yPos = y + 2

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.xPos, self.yPos)      # get enemy rect

        self.isDead = False
        self.isShooting = False     # variables to be used throughout class
        self.shootDir = 0
        self.hitCount = 0

        self.idleAdv = random.randrange(0, 10)      # idle animation updates every ten frames
        self.shootDelay1 = random.randrange(0, 30)      # since the game runs at 60 fps, two random integers are generated for each enemy,
        self.shootDelay2 = random.randrange(30, 59)     # one between 0 - 29, and the other between 30 - 59,
                                                        # if the player is within range of the enemy, and the current frame is one of these
        self.frameIter = 0                              # two random integers, the enemy will shoot
        self.idleImageIter = 0
        self.shootImageIter = 0

    def update(self):
        if self.isDead == True:
            self.yPos += 5

        if self.rect.y > HEIGHT:        # similar to the player, when dying, the sprite moves down and is killed
            self.kill()                 # once off screen

        self.animate()

    def animate(self):
        if self.frameIter == 9:
            self.frameIter = 0
        else:
            self.frameIter += 1

        if self.isShooting == True:
            if self.shootDir > 0:
                self.image = self.spriteSheet.shootImagesR[self.shootImageIter]     # iterate through images, identically to player
                self.rect = self.image.get_rect()                                   # shoot to the right
                self.rect.topleft = (self.xPos, self.yPos)

                if self.shootImageIter == 8:
                    self.shootImageIter = 0
                    self.isShooting = False
                else:
                    self.shootImageIter += 1

            else:
                self.image = self.spriteSheet.shootImagesL[self.shootImageIter]     # shoot to the left
                self.rect = self.image.get_rect()
                self.rect.topleft = (self.xPos - 10, self.yPos)

                if self.shootImageIter == 8:
                    self.shootImageIter = 0
                    self.isShooting = False
                else:
                    self.shootImageIter += 1

        else:
            self.image = self.spriteSheet.idleImages[self.idleImageIter]        # idle

            if self.frameIter == self.idleAdv:
                if self.idleImageIter == 5:
                    self.idleImageIter = 0
                else:
                    self.idleImageIter += 1

            self.rect = self.image.get_rect()
            self.rect.topleft = (self.xPos, self.yPos)

    def die(self):
        if self.enemytype == "enemy":
            if self.isDead == False:
                self.isDead = True
        else:
            self.hitCount += 1

            if self.hitCount >= 40:     # the enforcer type takes multiple shots to kill
                self.isDead = True      # each bullet collides with the enemy for approximately 10 frames

    def shoot(self, dir):
        if self.isShooting == False:
            self.isShooting = True

        if dir > 0:
            self.shootDir = 1       # determine which direction to shoot
        else:
            self.shootDir = 0

class EnemyImg():
    def __init__(self, enemytype):
        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # copied from player class
        self.dir = path.join(self.dir, "Assets")                            # load in spritesheet
        self.dir = path.join(self.dir, "Visual")
        self.dir = path.join(self.dir, "Sprites")

        if enemytype == "enemy":
            self.spritesheet = path.join(self.dir, "enemyspritesheet.png")
        else:
            self.spritesheet = path.join(self.dir, "enforcerspritesheet.png")

        self.spritesheet = pygame.image.load(self.spritesheet).convert_alpha()

        self.loadImages(enemytype)

    def getImage(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))     # return section of spritesheet
        return image

    def loadImages(self, enemytype):
        self.idleImages = []
        for i in range(6):
            self.idleImages.append(self.getImage(i * 32 + 9, 0, 23, 38))        # collate idle animation frames;

        for f in self.idleImages:
            if enemytype == "enemy":
                f.set_colorkey(WHITE)
            else:
                f.set_colorkey(BLACK)

        self.shootImagesL = []
        for i in range(9):
            self.shootImagesL.append(self.getImage(i * 32 + 192, 0, 30, 38))        # shoot to the left

        self.shootImagesR = []
        for f in self.shootImagesL:
            if enemytype == "enemy":
                f.set_colorkey(WHITE)
            else:
                f.set_colorkey(BLACK)
            self.shootImagesR.append(pygame.transform.flip(f, True, False))     # shoot to the right