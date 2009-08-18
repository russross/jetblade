import constants

import pygame
import os
import random

## This class handles loading and playing of sound effects.
class SoundManager:

    ## Load all sounds. 
    # \todo: Make this configurable.
    def __init__(self):
        pygame.mixer.quit()
        pygame.mixer.init(22050, -16, 1, 1024)
        ## Maps individual sound names (i.e. their paths) to PyGame Sound 
        # instances.
        self.nameToSoundMap = dict()
        ## Maps names of sound directories to lists of the PyGame Sound
        # instances found in those directories.
        self.nameToSoundListMap = dict()
        self.loadSoundDirectory(constants.soundPath)


    ## Load an entire directory of sounds. Recurse if we encounter more
    # directories.
    def loadSoundDirectory(self, directory):
        newSounds = []
        for file in os.listdir(directory):
            filePath = os.path.join(directory, file)
            if os.path.isdir(filePath):
                self.nameToSoundListMap[file] = self.loadSoundDirectory(filePath)
                newSounds.extend(self.nameToSoundListMap[file])
            else:
                self.nameToSoundMap[file] = pygame.mixer.Sound(filePath)
                newSounds.append(self.nameToSoundMap[file])
        return newSounds


    ## Play an individual sound by its name.
    def playSound(self, soundName):
        if soundName in self.nameToSoundMap:
            self.nameToSoundMap[soundName].play()
        elif soundName in self.nameToSoundListMap:
            random.choice(self.nameToSoundListMap[soundName]).play()
        else:
            logger.fatal("Invalid sound name",soundName)

