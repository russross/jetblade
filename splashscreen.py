import splashscreen
import constants

import pygame

## This class handles the splash screen display at the start of the game. As
# such, it has very few dependencies (and in fact, duplicates some code found
# in the ImageManager and Font classes to avoid having to import them early).
# Note that it is in this class that PyGame is initialized.
class SplashScreen:
    def __init__(self):
        pygame.init()
        self.splashSurface = pygame.image.load(constants.otherPath + '/splashscreen.png')
        self.font = pygame.font.Font(constants.fontPath + '/MODENINE.TTF', 18)
        self.screen = pygame.display.set_mode((constants.sw, constants.sh))
        self.splashRect = self.splashSurface.get_rect()
        self.splashRect.topleft = (0, 0)


    ## Draw a new status message.
    def updateMessage(self, message):
        self.screen.blit(self.splashSurface, self.splashRect)
        messageSurface = self.font.render(message, True, (255, 255, 255))
        messageRect = messageSurface.get_rect()
        messageRect.topleft = (20, 20)
        self.screen.blit(messageSurface, messageRect)
        pygame.display.update()

## Module-global singleton
splashscreen.splashScreen = SplashScreen()

## Passthrough to SplashScreen.updateMessage
def updateMessage(message):
    splashscreen.splashScreen.updateMessage(message)

## Since SplashScreen has the main PyGame screen surface, we need to be able 
# to retrieve it.
def getScreen():
    return splashscreen.splashScreen.screen

## Unset the singleton so that we can stop sending log messages to it.
def completeLoading():
    splashscreen.splashScreen = None

def getIsDoneLoading():
    return splashscreen.splashScreen == None
