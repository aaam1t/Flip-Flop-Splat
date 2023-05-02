import pygame
import random
from os import path
from settings import *

class Music():
    def __init__(self):
        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in music files
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Audio")
        self.dir = path.join(self.dir, "Music")

        self.current = 0

    def next(self):
        i = self.current
        while i == self.current:
            i = random.randrange(0, 3)      # pick a random song that is not the song currently playing

        self.current = i
        song = path.join(self.dir, f"{self.current}.ogg")       # load in and play ogg file
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()      # pause playback
        
    def resume(self):
        pygame.mixer.music.unpause()        # resume playback

class SFX():
    def __init__(self):
        pygame.mixer.set_num_channels(64)       # increase number of channels to allow for spammed bullets and prevent audio cutting

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # load in sfx
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Audio")
        self.dir = path.join(self.dir, "SFX")

        self.bullet1 = pygame.mixer.Sound((path.join(self.dir, "bullet1.ogg")))
        self.bullet2 = pygame.mixer.Sound((path.join(self.dir, "bullet2.ogg")))
        self.death = pygame.mixer.Sound((path.join(self.dir, "death.ogg")))
        self.finish = pygame.mixer.Sound((path.join(self.dir, "finish.ogg")))       # load in each sound file
        self.flip1 = pygame.mixer.Sound((path.join(self.dir, "flip1.ogg")))
        self.flip2 = pygame.mixer.Sound((path.join(self.dir, "flip2.ogg")))
        self.kill = pygame.mixer.Sound((path.join(self.dir, "kill.ogg")))
        self.menu1 = pygame.mixer.Sound((path.join(self.dir, "menu1.ogg")))
        self.menu2 = pygame.mixer.Sound((path.join(self.dir, "menu2.ogg")))
        self.pause = pygame.mixer.Sound((path.join(self.dir, "pause.ogg")))
        self.explosion = pygame.mixer.Sound((path.join(self.dir, "explosion.ogg")))

    def play(self, sound):
        if sound == 0:
            self.bullet1.play()
        elif sound == 1:
            self.bullet2.play()
        elif sound == 2:
            self.death.play()
        elif sound == 3:
            self.finish.play()
        elif sound == 4:
            self.flip1.play()       # play selected sound file
        elif sound == 5:
            self.flip2.play()
        elif sound == 6:
            self.kill.play()
        elif sound == 7:
            self.menu1.play()
        elif sound == 8:
            self.menu2.play()
        elif sound == 9:
            self.pause.play()
        elif sound == 10:
            self.explosion.play()