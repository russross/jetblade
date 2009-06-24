import pygame

## This class handles loading and playing of sound effects.
class SoundManager:

    ## Load all sounds. 
    # \todo: Make this configurable.
    def __init__(self):
        pygame.mixer.quit()
        pygame.mixer.init(22050, -16, 1, 1024)
#        self.newBombSfx = self.loadSound('newbomb')
#        self.bigExplosionSfx = self.loadSound('bigexplosion')
#        self.smallExplosionSfx = self.loadSound('smallexplosion')
#        self.menuToneSfx = self.loadSound('menutone')

    ## Load an individual sound by its path.
    def loadSound(self, name):
        return pygame.mixer.Sound(constants.sfxPath + '/' + name + '.ogg')

    ## Play an individual sound by its name.
    def playSound(self, sound):
        pass
#        if bulletml.configManager.getConfigValue('sound'):
#                self.newBombSfx.play()

