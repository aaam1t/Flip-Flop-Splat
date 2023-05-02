import pygame
from settings import *
from Classes.runtime import *

r = Runtime()
while r.running:
    r.start()           # begin the game!

pygame.quit()