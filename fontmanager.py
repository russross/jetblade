import font
import logger
import constants
import game

import os

## This class handles loading fonts and making them available for rendering.
class FontManager:

    ## Instantiate the manager and load all the fonts in the config file.
    def __init__(self):
        ## Maps (fontName, fontSize) to Font instances
        self.fontMap = dict()
        configPath = os.path.join(constants.fontPath, constants.fontFilename)
        fontModule = game.dynamicClassManager.loadModuleItems(configPath, ['fonts'])
        for fontName, fontConfig in fontModule.fonts.iteritems():
            fontSizes = []
            if 'sizes' in fontConfig:
                fontSizes = fontConfig['sizes']
            for size in fontSizes:
                self.fontMap[(fontName, size)] = font.Font(fontName, size)
    

    ## Tell a font to draw some text
    def drawText(self, fontName, fontSize, *args, **kwargs):
        if (fontName, fontSize) not in self.fontMap:
            self.fontMap[(fontName, fontSize)] = font.Font(fontName, fontSize)
        self.fontMap[(fontName, fontSize)].drawText(*args, **kwargs)

