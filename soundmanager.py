import constants

import pygame
import os

## This class handles loading and playing of sound effects.
class SoundManager:

    ## Load all sounds. 
    # \todo: Make this configurable.
    def __init__(self):
        pygame.mixer.quit()
        pygame.mixer.init(22050, -16, 1, 1024)
        self.soundNameToSoundMap = dict()
        self.loadSoundDirectory(constants.soundPath)


    ## Load an entire directory of sounds. Recurse if we encounter more
    # directories.
    def loadSoundDirectory(self, directory):
        for file in os.listdir(directory):
            filePath = os.path.join(directory, file)
            if os.path.isdir(filePath):
                self.loadSoundDirectory(filePath)
            else:
                self.soundNameToSoundMap[file] = pygame.mixer.Sound(filePath)


    ## Play an individual sound by its name.
    def playSound(self, soundName):
        if soundName not in self.soundNameToSoundMap:
            logger.fatal("Invalid sound name",soundName)
        self.soundNameToSoundMap[soundName].play()

