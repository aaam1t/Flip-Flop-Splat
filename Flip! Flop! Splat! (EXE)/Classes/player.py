import pygame
from os import path
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms, controls):
        pygame.sprite.Sprite.__init__(self)

        self.frameIter = 0
        self.idleImageIter = 0
        self.runImageIter = 0       # these variables will be used to keep track of animations
        self.shootImageIter = 0
        self.animFrames = [3, 6, 9]
        self.isShooting = False

        self.spriteSheet = PlayerImg()
        self.image = self.spriteSheet.getImage(0, 0, 23, 38)        # get player image
        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()
        self.width = self.image.get_width()     # set player rect
        self.height = self.image.get_height()
        self.rect.center = (x, y)

        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)        # all player movement is based on vectors
        self.acc = pygame.math.Vector2(0, 0)

        self.g1 = GRAVITY
        self.flipChange = False

        self.platforms = platforms      # loading in platforms to calculate collision

        self.isDead = False

        self.controlScheme = controls
        self.upState = False

    def update(self):
        self.keys = pygame.key.get_pressed()

        if self.isDead == False:
            self.move()
        else:
            self.vel.x = 0
            self.vel.y = 0
            self.acc.x = 0      # if player has been hit, move the player down until they are off the screen
            self.acc.y = 0

            self.pos.y += 5

        self.animate()

    def move(self):

        self.acc = pygame.math.Vector2(0, self.g1)
        if self.controlScheme == 0:
            if self.keys[pygame.K_LEFT]:
                self.acc.x = -PLAYER_ACC        # setting acceleration when movement keys are pressed
            if self.keys[pygame.K_RIGHT]:
                self.acc.x = PLAYER_ACC
        else:
            if self.keys[pygame.K_a]:
                self.acc.x = -PLAYER_ACC
            if self.keys[pygame.K_d]:
                self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRIC      # equations of motion
        self.vel += self.acc
        self.pos += self.vel + self.acc / 2

        self.hitY = False

        self.rect.centerx = self.pos.x      # check for collision in x and y axis
        self.collide("x")
        self.rect.bottom = self.pos.y
        self.collide("y")

        self.flipChange = False     # used to count flips for achievements
        if self.hitY:
            self.flip()

    def collide(self, dir):
        if dir == "x":
            hits = pygame.sprite.spritecollide(self, self.platforms, False)     # collision system from reddit post (see logbook)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.width / 2 - 1
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + self.width / 2 + 1
                self.vel.x = 0
                self.rect.centerx = self.pos.x
        if dir == "y":
            hits = pygame.sprite.spritecollide(self, self.platforms, False)     # check for collision for each tile,
            if hits:                                                            # then check which side(s) collided,
                if self.vel.y > 0:                                              # then move the player back in the opposite direction
                    self.pos.y = hits[0].rect.top
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.height
                self.vel.y = 0
                self.rect.bottom = self.pos.y
                self.hitY = True

    def flip(self):
        if self.controlScheme == 0:
            if self.upState == False:
                if self.keys[pygame.K_UP] or self.keys[pygame.K_DOWN]:      # change sign of gravity when the flip key is pressed,
                    self.upState = True                                     # and the player is touching the ground
                    self.g1 = -self.g1
                    self.flipChange = True

            elif not self.keys[pygame.K_UP] and not self.keys[pygame.K_DOWN]:
                self.upState = False
        else:
            if self.upState == False:
                if self.keys[pygame.K_w] or self.keys[pygame.K_s]:
                    self.upState = True
                    self.g1 = -self.g1
                    self.flipChange = True

            elif not self.keys[pygame.K_w] and not self.keys[pygame.K_s]:
                self.upState = False

    def animate(self):
        if self.frameIter == 9:     # idle animation iterates through images every 10 frames
            self.frameIter = 0
        else:
            self.frameIter += 1

        if self.g1 > 0:
            if self.isShooting == True:
                if self.vel.x > 0:
                    self.image = self.spriteSheet.shootImagesR[self.shootImageIter]     # animate the player by iterating through a list
                                                                                        # of images; the list changes if the player is:
                    if self.shootImageIter == 8:
                        self.shootImageIter = 0
                        self.isShooting = False
                    else:
                        self.shootImageIter += 1

                else:
                    self.image = self.spriteSheet.shootImagesL[self.shootImageIter]     # shooting

                    if self.shootImageIter == 8:
                        self.shootImageIter = 0
                        self.isShooting = False
                    else:
                        self.shootImageIter += 1

            elif abs(self.vel.x) < 0.5:
                if self.frameIter == 9:
                    self.image = self.spriteSheet.idleImages[self.idleImageIter]        # stationary
            
                    if self.idleImageIter == 5:
                        self.idleImageIter = 0
                    else:
                        self.idleImageIter += 1

            elif self.vel.x > 0.5:
                if self.frameIter in self.animFrames:
                    self.image = self.spriteSheet.runImagesR[self.runImageIter]     # running

                    if self.runImageIter == 6:
                        self.runImageIter = 0
                    else:
                        self.runImageIter += 1

            elif self.vel.x < -0.5:
                if self.frameIter in self.animFrames:
                    self.image = self.spriteSheet.runImagesL[self.runImageIter]

                    if self.runImageIter == 6:
                        self.runImageIter = 0
                    else:
                        self.runImageIter += 1

        else:
            if self.isShooting == True:
                if self.vel.x > 0:
                    self.image = self.spriteSheet.shootImagesRF[self.shootImageIter]        # images are flipped if gravity is flipped

                    if self.shootImageIter == 8:
                        self.shootImageIter = 0
                        self.isShooting = False
                    else:
                        self.shootImageIter += 1

                else:
                    self.image = self.spriteSheet.shootImagesLF[self.shootImageIter]

                    if self.shootImageIter == 8:
                        self.shootImageIter = 0
                        self.isShooting = False
                    else:
                        self.shootImageIter += 1

            elif self.vel.x < 0.5 and self.vel.x > -0.5:
                if self.frameIter == 9:
                    self.image = self.spriteSheet.idleImagesF[self.idleImageIter]
            
                    if self.idleImageIter == 5:
                        self.idleImageIter = 0
                    else:
                        self.idleImageIter += 1

            elif self.vel.x > 0.5:
                if self.frameIter in self.animFrames:
                    self.image = self.spriteSheet.runImagesRF[self.runImageIter]

                    if self.runImageIter == 6:
                        self.runImageIter = 0
                    else:
                        self.runImageIter += 1

            elif self.vel.x < -0.5:
                if self.frameIter in self.animFrames:
                    self.image = self.spriteSheet.runImagesLF[self.runImageIter]

                    if self.runImageIter == 6:
                        self.runImageIter = 0
                    else:
                        self.runImageIter += 1

        self.rect.midbottom = self.pos

    def die(self):
        if self.isDead == False:        # since the bullet will collide with the player over multiple frames,
            self.isDead = True          # we must make sure that only one death is counted

class PlayerImg():
    def __init__(self):
        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in player spritesheet
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Visual")
        self.dir = path.join(self.dir, "Sprites")
        self.spritesheet = path.join(self.dir, "playerspritesheet.png")
        self.spritesheet = pygame.image.load(self.spritesheet).convert_alpha()

        self.loadImages()

    def getImage(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))     # return a specified portion of the spritesheet
        return image

    def loadImages(self):
        self.idleImages = []
        for i in range(6):
            self.idleImages.append(self.getImage(i * 32, 0, 23, 38))        # create a separate list collating images from the spritesheet,
                                                                            # based on if the player is:
        for f in self.idleImages:
            f.set_colorkey(WHITE)

        self.runImagesR = []
        for i in range(7):
            self.runImagesR.append(self.getImage(i * 32 + 192, 0, 22, 38))      # running to the right

        self.runImagesL = []
        for f in self.runImagesR:
            f.set_colorkey(WHITE)
            self.runImagesL.append(pygame.transform.flip(f, True, False))       # running to the left

        self.idleImagesF = []
        for f in self.idleImages:
            self.idleImagesF.append(pygame.transform.flip(f, False, True))      # stationary + upside-down

        self.runImagesRF = []
        for f in self.runImagesR:
            self.runImagesRF.append(pygame.transform.flip(f, False, True))      # running to the right + upside-down

        self.runImagesLF = []
        for f in self.runImagesL:
            self.runImagesLF.append(pygame.transform.flip(f, False, True))      # running to the left + upside-down

        self.shootImagesR = []
        for i in range(9):
            self.shootImagesR.append(self.getImage(i * 32 + 416, 0, 30, 38))    # shooting to the right

        self.shootImagesRF = []
        for f in self.shootImagesR:
            f.set_colorkey(WHITE)
            self.shootImagesRF.append(pygame.transform.flip(f, False, True))        # shooting to the right + upside-down

        self.shootImagesL = []
        for f in self.shootImagesR:
            self.shootImagesL.append(pygame.transform.flip(f, True, False))     # shooting to the left

        self.shootImagesLF = []
        for f in self.shootImagesL:
            self.shootImagesLF.append(pygame.transform.flip(f, False, True))        # shooting to the left + upside-down