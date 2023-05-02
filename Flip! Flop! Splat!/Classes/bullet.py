import pygame
from os import path
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in explosion spritesheet
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Visual")
        self.dir = path.join(self.dir, "Sprites")
        self.dir = path.join(self.dir, "explosionspritesheet.png")
        self.explodeSheet= pygame.image.load(self.dir).convert_alpha()

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in bullet sprite image
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Visual")
        self.dir = path.join(self.dir, "Sprites")
        self.dir = path.join(self.dir, "bulletsprite.png")
        self.image = pygame.image.load(self.dir).convert_alpha()

        self.rect = self.image.get_rect()       # get bullet rect
        self.rect.y = y

        self.xPos = x
        self.yPos = y

        if direction > 0:
            self.rect.x = x + 25
            self.speed = BULLETSPEED        # determine direction of bullet
        else:
            self.rect.x = x - 5
            self.speed = -BULLETSPEED

        self.doExplode = False
        self.explodeImages = []     # define variables to be used throughout class
        self.loadImages()
        self.frameIter = 0
        self.explodeIter = 0

    def update(self):
        if self.frameIter == 3:
            self.frameIter = 1
        else:
            self.frameIter += 1

        if self.doExplode == True:
            if self.frameIter == 3:
                if self.explodeIter < 4:
                    self.image = self.explodeImages[self.explodeIter]       # animate bullet explosion, copied from player class
                    self.rect = self.image.get_rect()
                    self.rect.x = self.xPos
                    self.rect.y = self.yPos
                    self.explodeIter += 1
                else:
                    self.kill()

        else:
            self.rect.x += self.speed

            if self.rect.x > 3 * WIDTH or self.rect.x < 0:      # kill the sprite if it exceeds the bounds of the level
                self.kill()

    def explode(self, x):
        if self.doExplode == False:
            self.xPos = x - 16
            self.yPos = self.rect.y - 16        # move the location of the bullet before exploding,
            self.doExplode = True               # to adjust for a difference in size between bullet and explosion images

    def getImage(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.explodeSheet, (0, 0), (x, y, width, height))        # return portion of spritesheet
        return image

    def loadImages(self):
        for i in range(4):
            self.explodeImages.append(self.getImage(i * 33, 0, 33, 33))     # collate bullet explosion images
        for f in self.explodeImages:
            f.set_colorkey(BLACK)