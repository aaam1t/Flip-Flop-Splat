import pygame
from os import path
import csv
import random
from settings import *
from .player import *
from .world import *
from .camera import *
from .bullet import *
from .save import *
from .pygame_textinput import *
from .sound import *

class Runtime():
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        pygame.display.set_caption(TITLE)

        icondir= path.dirname(path.dirname(path.abspath(__file__)))
        icondir = path.join(icondir, "Assets")
        icondir = path.join(icondir, "Visual")
        icondir = path.join(icondir, "Icon.png")
        icon = pygame.image.load(icondir).convert_alpha()       # loading and setting the window icon
        iconSurf = pygame.Surface((32, 32))
        iconSurf.blit(icon, (0, 0))
        iconSurf.set_colorkey(BLACK)
        pygame.display.set_icon(iconSurf)

        self.clock = pygame.time.Clock()

        self.fontdir = path.dirname(path.dirname(path.abspath(__file__)))
        self.fontdir = path.join(self.fontdir, "Assets")
        self.fontdir = path.join(self.fontdir, "Pixeboy.ttf")       # this font will be used whenever printing text
        self.pixeboy = pygame.font.Font(self.fontdir, 40)

        self.world = World()
        self.save = Save()
        self.music = Music()
        self.sfx = SFX()

        self.header()

        self.bgSurf = pygame.Surface((600, 400))

        self.frameCounter = 0
        self.creditCount = 0

        self.running = True
        self.playing = False
        self.isPaused = False

    def start(self):
        self.allSprites = pygame.sprite.Group()
        self.finishSprite = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.backgrounds = pygame.sprite.Group()        # creating separate groups for each sprite type
        self.bullets = pygame.sprite.Group()
        self.playerBullets = pygame.sprite.Group()
        self.enemyBullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.mainmenu()

    def run(self):
        if self.doPlay:
            self.playing = True
        
            while self.playing:
                self.clock.tick(FPS)
                self.events()
                self.update()
                self.draw()

            self.save.saveData()        # saving the game upon quitting

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player.isDead == False:     # spawn a bullet whenever the spacebar is pressed
                    if self.player.g1 > 0:
                        bullet = Bullet(self.player.rect.x, self.player.rect.y + 12, self.player.vel.x)
                    else:
                        bullet = Bullet(self.player.rect.x, self.player.rect.bottom - 13, self.player.vel.x)
                    self.sfx.play(1)
                    self.playerBullets.add(bullet)
                    self.bullets.add(bullet)
                    self.allSprites.add(bullet)
                    self.player.isShooting = True
                elif event.key == pygame.K_ESCAPE:      # pause the game when the escape key is pressed
                    self.music.pause()
                    self.pauseMenu()
            elif event.type == self.music.SONG_END:     # start the next song whenever background music stops
                self.music.next()

    def update(self):
        if self.frameCounter == 59:
            self.frameCounter = 0       # keeping track of current frame for timekeeping (used to control various actions i.e. enemy shooting)
        else:
            self.frameCounter += 1

        self.allSprites.update()
        self.camera.update(self.player)

        if self.save.level == 6 and self.frameCounter == 59:
            if self.creditCount == 2:
                self.creditCount = 0
            else:
                self.creditCount += 1       # when on the credits, update the background every three seconds

            if self.creditCount == 2:
                self.updateCredits()

        hits1 = pygame.sprite.spritecollide(self.player, self.finishSprite, False)
        if hits1:
            self.music.next()
            self.clear()
            self.sfx.play(3)

            self.save.level += 1        # progress to next level when the player collides with the chequered flag
            self.save.saveData()
            self.load(self.save.level, True)

        hits2 = pygame.sprite.groupcollide(self.bullets, self.platforms, False, False)
        for hit in hits2:
            if hits2[hit]:
                self.bulletSound(hit)       # explode bullets when colliding with a platform
                hit.explode(hit.rect.x)

        hits3 = pygame.sprite.groupcollide(self.playerBullets, self.enemies, False, False)
        for hit in hits3:
            if hits3[hit]:
                self.bulletSound(hit)       
                hit.explode(hit.rect.x)

                for kill in hits3[hit]:
                    if kill.isDead == False:        # check if enemy is alive, kill them if so
                        kill.die()
                        
                        if kill.isDead == True:
                            self.sfx.play(6)
                            self.save.kills += 1

        hits4 = pygame.sprite.groupcollide(self.playerBullets, self.enemyBullets, False, False)
        for hit in hits4:
            if hits4[hit]:
                self.bulletSound(hit)       # collision between bullets
                hit.explode(hit.rect.x)

                for collide in hits4[hit]:
                    self.bulletSound(collide)
                    collide.explode(collide.rect.x)

        hits5 = pygame.sprite.spritecollideany(self.player, self.enemyBullets)
        if hits5:
            if self.player.isDead == False:     # killing the player if colliding with an enemy's bullet(s)
                self.sfx.play(2)

            self.player.isDead = True

        hits6 = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits6:
            if self.player.isDead == False:     # kill the player if they collide with an enemy
                self.sfx.play(2)

            self.player.isDead = True

        if self.player.flipChange:
            self.save.flips += 1

            if self.player.g1 > 0:
                self.sfx.play(5)
            else:
                self.sfx.play(4)

        if self.player.pos.y > HEIGHT or self.player.rect.bottom < 0:
            if self.player.isDead == False:
                self.sfx.play(2)

            self.save.deaths += 1       # the player is considered dead when they are off the screen,
            self.clear()                # a bullet hitting the player makes the player fall down and off the screen
            self.save.saveData()
            self.deathScreen()

        for enemy in self.enemies:
            if enemy.isDead == False:
                if self.frameCounter == enemy.shootDelay1 or self.frameCounter == enemy.shootDelay2:
                    if abs(enemy.rect.centery - self.player.rect.centery) <= 25:
                        if abs(enemy.rect.centerx - self.player.pos.x) <= 300:
                            if enemy.rect.centerx - self.player.pos.x > 0:
                                bullet = Bullet(enemy.rect.x - 20, enemy.rect.y + 12, -1)       # enemies will shoot at the player once
                                enemy.shoot(-1)                                                 # they are in range
                            else:
                                bullet = Bullet(enemy.rect.x + 40, enemy.rect.y + 12, 1)
                                enemy.shoot(1)

                            self.sfx.play(0)
                            self.enemyBullets.add(bullet)
                            self.bullets.add(bullet)
                            self.allSprites.add(bullet)
        
    def draw(self):
        if self.save.level == 6:
            self.display.blit(self.bgSurf, (0, 0))
        else:
            for img in self.backgrounds:
                self.display.blit(img.image, self.camera.pan(img))

        for sprite in self.allSprites:
            self.display.blit(sprite.image, self.camera.pan(sprite))

        pygame.display.flip()
        
    def loadMap(self, level):
        self.mapData = []
        level = str(level)

        mapFile = (f"level{level}.csv")

        self.dir = path.dirname(path.dirname(path.abspath(__file__)))
        self.dir = path.join(self.dir, "Assets")
        self.dir = path.join(self.dir, "Level Data")        # loading in the tilemap csv
        self.map = path.join(self.dir, mapFile)

        for row in range(ROWS):
            r = [-1] * COLNS
            self.mapData.append(r)
        
        with open(self.map, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')         # taking the data from the csv and loading it into a local dictionary
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.mapData[x][y] = int(tile)

    def load(self, level, header):
        self.loadMap(level)
        self.player, self.finish, self.enemies = self.world.loadWorld(self.mapData, self.save.control)
        self.allSprites.add(self.player, self.finish)
        self.finishSprite.add(self.finish)

        for sprite in self.enemies:
            self.allSprites.add(sprite)


        for tile in self.world.obstacleList:
            platform = Platform(tile[0], tile[1])
            self.platforms.add(platform)
            self.allSprites.add(platform)

        if self.save.level == 6:
            self.BG = 4
            self.BGimg, self.BGw = self.world.loadBG(self.BG)       # if on the credits 'level', load the custom credits into the background
            bgRect = pygame.Rect(0, 0, self.BGw, 400)               # instead of the city background
            bg = Platform(self.BGimg, bgRect)
            self.backgrounds.add(bg)
            self.credits()
        else:
            self.BG = random.randrange(0, BACKGROUNDS - 1)
            self.BGimg, self.BGw = self.world.loadBG(self.BG)
            i = 0
            while i * self.BGw < 1800:
                bgRect = pygame.Rect(i * self.BGw, 0, self.BGw, 400)        # repeat the background to fill the entire level
                bg = Platform(self.BGimg, bgRect)
                self.backgrounds.add(bg)
                i += 1

        self.camera = Camera(1800, 400)

        self.music.resume()

        if header:
            self.displayHeader()

    def clear(self):
        self.world.clear()

        self.allSprites.empty()
        self.finishSprite.empty()
        self.platforms.empty()
        self.backgrounds.empty()        # kill all sprites
        self.playerBullets.empty()
        self.enemyBullets.empty()
        self.bullets.empty()
        self.enemies.empty()

        self.music.pause()

    def loadScreen(self, screen):
        screenFile = (f"{str(screen)}.png")
        dir = path.dirname(path.dirname(path.abspath(__file__)))        # every screen for the main/pause/death menus are pre-made images
        dir = path.join(dir, "Assets")
        dir = path.join(dir, "Visual")
        dir = path.join(dir, "Menu")
        dir = path.join(dir, screenFile)
        screen = pygame.image.load(dir).convert_alpha()

        return screen

    def mainmenu(self):
        self.menuState = 0
        self.currentMenu = 0
        self.hover = 0

        self.music.next()

        self.contButt = pygame.Rect(236, 196, 126, 24)
        self.newButt = pygame.Rect(239, 253, 121, 23)
        self.optionsButt = pygame.Rect(206, 309, 187, 22)       # define the locations of each button
        self.quitButt = pygame.Rect(264, 364, 70, 23)
        self.arrowButt = pygame.Rect(252, 342, 131, 19)
        self.wasdButt = pygame.Rect(436, 342, 131, 19)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.playing = False
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menuState == 2:
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)      # start a new game
                        self.sfx.play(8)
                        self.doPlay = True
                        self.getName()
                        self.save.newSave()
                        self.load(self.save.level, True)
                        self.music.next()
                        self.run()
                        return False
                    elif self.menuState == 1 and self.save.username != "noname":
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)      # continue game
                        self.sfx.play(8)
                        self.load(self.save.level, True)
                        self.doPlay = True
                        self.music.next()
                        self.run()
                    elif self.menuState == 3:       # go to options/help screen
                        self.sfx.play(8)
                        self.menuState = 5
                    elif self.menuState == 4:       # quit game
                        self.sfx.play(8)
                        self.running = False
                        self.playing = False
                        return False
                    elif self.menuState == 5 or self.menuState == 6:
                        if self.hover == 1:
                            self.sfx.play(8)
                            self.save.control = 0       # change control scheme to arrow keys
                            self.save.saveData()
                        elif self.hover == 2:
                            self.sfx.play(8)
                            self.save.control = 1       # change control scheme to wasd
                            self.save.saveData()
                elif event.type == self.music.SONG_END:
                    self.music.next()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menuState = 0

            if self.playing == False and self.running == False:
                return False

            self.menuSelect()

            self.display.blit(self.loadScreen(self.menuState), (0, 0))
            pygame.display.flip()

            self.clock.tick(FPS / 4)        # while the game normally runs at 60 fps, when paused/on a menu screen, it clocks down to 15 fps

    def menuSelect(self):
        mouse = pygame.mouse.get_pos()

        if self.menuState <= 4:
            if self.contButt.collidepoint(mouse):
                self.menuState = 1
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif self.newButt.collidepoint(mouse):
                self.menuState = 2
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)       # set which menu screen to display by checking if the cursor
            elif self.optionsButt.collidepoint(mouse):                          # is colliding with any button
                self.menuState = 3
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif self.quitButt.collidepoint(mouse):
                self.menuState = 4
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                self.menuState = 0
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if self.menuState != 0:
                if self.menuState != self.currentMenu:
                    self.sfx.play(7)
            self.currentMenu = self.menuState

        else:
            if self.save.control == 0:
                self.menuState = 5
            else:
                self.menuState = 6

            if self.arrowButt.collidepoint(mouse):
                self.hover = 1
                if self.save.control == 1:
                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif self.wasdButt.collidepoint(mouse):
                self.hover = 2
                if self.save.control == 0:
                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            else:
                self.hover = 0
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def deathScreen(self):
        self.menuState = 0
        self.currentMenu = 7
        
        self.retryButt = pygame.Rect(41, 310, 211, 29)      # the death screen functions almost identically to the main menu
        self.menuButt = pygame.Rect(387, 310, 171, 29)

        tip = random.randrange(0, TIPS)     # pick a random tip to display on the death screen

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sfx.play(8)
                    self.running = False
                    self.playing = False
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menuState == 8:
                        self.sfx.play(8)
                        self.music.resume()
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        self.load(self.save.level, False)
                        self.doPlay = True
                        self.run()
                        return False
                    elif self.menuState == 9:
                        self.sfx.play(8)
                        self.clear()
                        self.mainmenu()
                        return False

            self.deathScreenSelect()

            deathText = (f"{self.save.username}?")
            deathName = pygame.font.Font.render(self.pixeboy, deathText, False, WHITE)
            deathSize = pygame.font.Font.size(self.pixeboy, deathText)

            self.display.blit(self.loadScreen(self.menuState), (0, 0))
            self.display.blit(deathName, ((WIDTH - deathSize[0]) / 2, 84))
            self.display.blit(self.tipsList[tip], (33, 154))
            pygame.display.flip()

            self.clock.tick(FPS / 4)

    def deathScreenSelect(self):
        mouse = pygame.mouse.get_pos()

        if self.retryButt.collidepoint(mouse):
            self.menuState = 8
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.menuButt.collidepoint(mouse):
            self.menuState = 9
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            self.menuState = 7
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.menuState != 7:
            if self.menuState != self.currentMenu:
                self.sfx.play(7)
        self.currentMenu = self.menuState

    def pauseMenu(self):
        self.sfx.play(9)
        self.menuState = 10

        self.resumeButt = pygame.Rect(249, 180, 101, 50)        # again, using the same menu function for the pause menu
        self.returnButt = pygame.Rect(249, 264, 101, 50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sfx.play(8)
                    self.running = False
                    self.playing = False
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menuState == 12:
                        self.sfx.play(8)
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        self.music.resume()
                        return False
                    elif self.menuState == 11:
                        self.sfx.play(8)
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        self.clear()
                        self.mainmenu()
                        return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                        self.music.resume()
                        return False

            self.pauseScreenSelect()

            self.display.blit(self.loadScreen(self.menuState), (193, 40))
            pygame.display.flip()

            self.clock.tick(FPS / 4)

    def pauseScreenSelect(self):
        mouse = pygame.mouse.get_pos()

        if self.resumeButt.collidepoint(mouse):
            self.menuState = 12
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.returnButt.collidepoint(mouse):
            self.menuState = 11
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            self.menuState = 10
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.menuState != 10:
            if self.menuState != self.currentMenu:
                self.sfx.play(7)
        self.currentMenu = self.menuState

    def getName(self):
        self.menuState = 13
        textbox = TextInput("", self.fontdir, 35, False, (255, 255, 255), (255, 255, 255), 400, 35, 10)     # using the pygame textinput
                                                                                                            # module by Nearoo
        while True:
            eventlist = pygame.event.get()
            for event in eventlist:
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False
                    self.doPlay = False
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and textbox.get_text() and textbox.get_text() != "noname":
                        self.save.username = textbox.get_text()
                        return False

            if textbox.get_text() and textbox.get_text() != "noname":
                self.menuState = 14
            else:
                self.menuState = 13

            textbox.update(eventlist)

            self.display.blit(self.loadScreen(self.menuState), (0, 0))
            self.display.blit(textbox.get_surface(), (232, 190))
            pygame.display.flip()

            self.clock.tick(FPS / 4)

    def credits(self):
        creditDir= path.dirname(path.dirname(path.abspath(__file__)))
        creditDir = path.join(creditDir, "Assets")
        creditDir = path.join(creditDir, "Visual")
        creditDir = path.join(creditDir, "Credits")     # load in the screens (backgrounds) for the credits/achievements 'stage'

        self.creditList = []
        self.creditIter = 0
        self.achieveCount = 0

        for i in range(0, 30):
            screendir = path.join(creditDir, f"{i}.png")
            screen = pygame.image.load(screendir)
            self.creditList.append(screen)

        self.bgSurf.fill(WHITE)

    def updateCredits(self):
        self.bgSurf.blit(self.creditList[self.creditIter], (0, 0))

        if self.creditIter == 7:
            name = pygame.font.Font.render(self.pixeboy, str(self.save.username), False, GREY)      # if on the 7th screen, display stats
            kills = pygame.font.Font.render(self.pixeboy, str(self.save.kills), False, GREY)        # for the current player
            deaths = pygame.font.Font.render(self.pixeboy, str(self.save.deaths), False, GREY)
            flips = pygame.font.Font.render(self.pixeboy, str(self.save.flips), False, GREY)

            self.bgSurf.blit(name, (317, 79))
            self.bgSurf.blit(kills, (251, 179))
            self.bgSurf.blit(deaths, (271, 229))
            self.bgSurf.blit(flips, (251, 279))

        elif self.creditIter == 9:
            if self.save.kills >= 100:
                self.bgSurf.blit(self.creditList[24], (0, 0))       # for the achievements, the achievement is displayed first,
                self.achieveCount += 1                              # then either locked/unlocked if it has been achieved

        elif self.creditIter == 11:
            if self.save.kills >= 200:
                self.bgSurf.blit(self.creditList[25], (0, 0))
                self.achieveCount += 1

        elif self.creditIter == 13:
            if self.save.flips >= 1000:
                self.bgSurf.blit(self.creditList[26], (0, 0))
                self.achieveCount += 1

        elif self.creditIter == 15:
            if self.save.flips >= 2000:
                self.bgSurf.blit(self.creditList[27], (0, 0))
                self.achieveCount += 1

        elif self.creditIter == 17:
            if self.save.deaths >= 100:
                self.bgSurf.blit(self.creditList[28], (0, 0))
                self.achieveCount += 1

        elif self.creditIter == 19:
            if self.save.deaths >= 200:
                self.bgSurf.blit(self.creditList[29], (0, 0))
                self.achieveCount += 1

        elif self.creditIter == 21:
            achieve = pygame.font.Font.render(self.pixeboy, str(self.achieveCount), False, GREY)        # display the total number of
            self.bgSurf.blit(achieve, (280, 245))                                                       # achievements unlocked

        if self.creditIter <= 22:
            self.creditIter += 1

    def header(self):
        visualDir= path.dirname(path.dirname(path.abspath(__file__)))
        visualDir = path.join(visualDir, "Assets")
        visualDir = path.join(visualDir, "Visual")
        headerDir = path.join(visualDir, "Headers")     # load in the level titles
        tipsDir = path.join(visualDir, "Tips")          # and tips

        self.headerList = []
        self.tipsList = []

        for i in range(1, 7):
            screenDir = path.join(headerDir, f"{i}.png")
            headerScreen = pygame.image.load(screenDir)
            self.headerList.append(headerScreen)

        for i in range(1, (TIPS + 1)):
            screenDir = path.join(tipsDir, f"{i}.png")
            tipsScreen = pygame.image.load(screenDir)
            self.tipsList.append(tipsScreen)

    def displayHeader(self):
        if self.running:
            self.display.blit(self.headerList[self.save.level - 1], (0, 0))     # display the level title for 3 seconds
            pygame.display.flip()
            pygame.time.wait(3000)

    def bulletSound(self, bullet):
        if bullet.doExplode == False:       # if a bullet has not started its explosion animation,
            self.sfx.play(10)               # play the explosion sound effect when this function is called