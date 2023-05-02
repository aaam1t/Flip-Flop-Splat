import pygame
from os import path
from settings import *
from .player import *
from .enemy import *

class World():
    def __init__(self):
        self.obstacleList = []
        self.loadImg()
        self.loadBGList()

    def loadWorld(self, map, controls):
        self.enemies = pygame.sprite.Group()

        for y, row in enumerate(map):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = self.images[tile]
                    imgRect = img.get_rect()        # reading in the tilemap csv
                    imgRect.x = x * TILESIZE
                    imgRect.y = y * TILESIZE
                    tileData = (img, imgRect)

                    if tile == 0:
                        self.obstacleList.append(tileData)
                    elif tile == 1:
                        enemy = Enemy(x * TILESIZE, y * TILESIZE, "enemy")
                        self.enemies.add(enemy)
                    elif tile == 2:
                        enforcer = Enemy(x * TILESIZE, y * TILESIZE, "enforcer")        # each csv value corresponds to a different entity
                        self.enemies.add(enforcer)
                    elif tile == 3:
                        finish = Finish(img, x * TILESIZE, y * TILESIZE)
                        finish.image.set_colorkey(BLUE)
                    elif tile == 4:
                        playerx = (x * TILESIZE)
                        playery = (y * TILESIZE)
        
        self.platforms = pygame.sprite.Group()
        for tile in self.obstacleList:
            platform = Platform(tile[0], tile[1])       # add all platform tiles to a dedicated sprite group
            self.platforms.add(platform)

        player = Player(playerx, playery, self.platforms, controls)

        return player, finish, self.enemies

    def loadImg(self):
        self.images = []

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in the images for each entity
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Level Data")

        for i in range(TILETYPES):
            imgPath = path.join(self.dir, (f"{i}.png"))
            imgL = pygame.image.load(imgPath)
            self.images.append(imgL)

    def loadBGList(self):
        self.BGList = []

        self.dir2 = path.dirname(path.dirname(path.abspath(__file__)))      # load in level backgrounds
        self.dir2 = path.join(self.dir2, "Assets")
        self.dir2 = path.join(self.dir2, "Visual")
        self.dir2 = path.join(self.dir2, "Background")

        for i in range(BACKGROUNDS):
            imgPath = path.join(self.dir2, (f"{i}.png"))
            imgL = pygame.image.load(imgPath)
            self.BGList.append(imgL)

    def loadBG(self, i):
        return self.BGList[i], self.BGList[i].get_rect().width

    def clear(self):
        self.platforms.empty()      # clear all sprite groups and lists before loading a new level
        self.enemies.empty()
        self.obstacleList.clear()

class Platform(pygame.sprite.Sprite):
    def __init__(self, img, dim):
        pygame.sprite.Sprite.__init__(self)     # platforms and the finish are just basic stationary sprites with no attributes/functions
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = dim.x, dim.y

class Finish(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y