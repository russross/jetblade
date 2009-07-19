import font
import logger
import constants

## Default ratio of line height in pixels to font size
defaultLineHeightMultiplier = .85

## This class handles loading fonts and making them available for rendering.
class FontManager:

    ## Instantiate the manager and load all the fonts in the config file.
    def __init__(self):
        ## Maps names of fonts to Font instances
        self.fontNameToFontMap = dict()
        configPath = constants.fontPath + '/' + constants.fontFilename
        configPath = configPath.replace('/', '.')
        fontModule = __import__(configPath, globals(), locals(), ['fonts'])
        for fontName, fontConfig in fontModule.fonts.iteritems():
            fontSizes = []
            if 'sizes' in fontConfig:
                fontSizes = fontConfig['sizes']
            lineHeightMultiplier = defaultLineHeightMultiplier
            if 'lineHeightMultiplier' in fontConfig:
                lineHeightMultiplier = fontConfig['lineHeightMultiplier']
            self.fontNameToFontMap[fontName] = font.Font(fontName, fontSizes, lineHeightMultiplier)
    

    ## Tell a font to draw some text
    def drawText(self, fontName, *entries):
        if fontName not in self.fontNameToFontMap:
            logger.fatal("Invalid font name",fontName)
        self.fontNameToFontMap[fontName].drawText(*entries)
