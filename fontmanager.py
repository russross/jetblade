import font
import logger
import constants
import game

import os

## This class handles loading fonts and making them available for rendering.
class FontManager:

    ## Instantiate the manager and load all the fonts in the config file.
    def __init__(self):
        ## Maps names of fonts to Font instances
        self.fontNameToFontMap = dict()
        configPath = os.path.join(constants.fontPath, constants.fontFilename)
        fontModule = game.dynamicClassManager.loadModuleItems(configPath, ['fonts'])
        for fontName, fontConfig in fontModule.fonts.iteritems():
            fontSizes = []
            if 'sizes' in fontConfig:
                fontSizes = fontConfig['sizes']
            self.fontNameToFontMap[fontName] = font.Font(fontName, fontSizes)
    

    ## Tell a font to draw some text
    def drawText(self, fontName, *entries):
        if fontName not in self.fontNameToFontMap:
            logger.fatal("Invalid font name",fontName)
        self.fontNameToFontMap[fontName].drawText(*entries)

