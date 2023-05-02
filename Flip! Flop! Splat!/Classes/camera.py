import pygame
from settings import *

class Camera():
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)      # creating a virtual 'camera' to show part of a level at a time
        self.width = width
        self.height = height

    def pan(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        if WIDTH - target.rect.centerx <= 0:
            if 2 * WIDTH - target.rect.centerx <= 0:        # scroll to the appropriate part of the level based on the position
                self.scroll(2)                              # of the player
            else:
                self.scroll(1)
        else:
            self.scroll(0)

    def scroll(self, screen):
        if screen == 2:
            if self.camera.x != -(2 * WIDTH):               # pan the camera to the next area over a few seconds,
                self.camera.x -= SCROLL_SPEED               # rather than instantaneuosly
        elif screen == 1:
            if self.camera.x < -WIDTH:
                self.camera.x += SCROLL_SPEED
            elif self.camera.x > -WIDTH:
                self.camera.x -= SCROLL_SPEED               # all visuals are blitted to the screen with a certain x offset,
        else:                                               # determined by the location of the camera
            if self.camera.x != 0:                          # the game believes everything is still in the same location,
                self.camera.x += SCROLL_SPEED               # but they are just being blitted to a different x position on the display
