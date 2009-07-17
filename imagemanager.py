import constants
import util
import logger

import os
import pygame

## This class handles loading and display of images and fonts. 
class ImageManager:
    ## Load fonts, and prepare the image caches. 
    def __init__(self):
        ## Maps font names to font sizes to PyGame Font instances.
        self.fonts = dict()
        for fontName in constants.fontNames:
            self.fonts[fontName] = dict()
            for size in constants.fontSizes:
                self.fonts[fontName][size] = pygame.font.Font(constants.fontPath + '/' + fontName, size)
        ## Maps animation group names to sets of animations. Typically an 
        # animation group is all of the animations for a single creature.
        self.animationSets = dict()
        ## Maps animation names to sequences of surfaces.
        self.animations = dict()
        ## Individual loaded surfaces.
        self.surfaces = dict()


    ## Load the named animation set, either from our cache or by loading each
    # individual animation in the set.
    def loadAnimationSet(self, name):
        if name in self.animationSets:
            return self.animationSets[name]
        result = dict()
        for entry in os.listdir(constants.imagePath + '/' + name):
            if entry.find(constants.spriteFilename) == -1:
                result[entry] = self.loadAnimation(name + '/' + entry)
        self.animationSets[name] = result
        return result        


    ## Load all of the surfaces in a given named animation. 
    def loadAnimation(self, name):
        if name in self.animations:
            return self.animations[name]
        result = []
        files = os.listdir(constants.imagePath + '/' + name)
        for file in files:
            filename, extension = file.split('.')
            result.append(self.loadSurface(name + '/' + filename))
        self.animations[name] = result
        return result


    ## Load a single surface. 
    def loadSurface(self, name, has_alpha = 1):
        if name in self.surfaces:
            return self.surfaces[name]
        path = constants.imagePath + '/' + name + '.png'
        logger.debug("Loading file",path)
        surface = pygame.image.load(path)
        if has_alpha:
            surface = surface.convert_alpha()
        self.surfaces[name] = surface
        return surface


    ## Clear the screen to black.
    def drawBackground(self, screen):
        screen.fill((0, 0, 0), None)


    ## Draw an object relative to the camera. 
    def drawGameObjectAt(self, screen, surface, loc, center, scale = 1):
        drawLoc = util.adjustLocForCenter(loc, center, screen.get_rect())
        self.drawObjectAt(screen, surface, drawLoc, 255, scale)


    ## Draw an object at a specific location on the screen (e.g. for HUD 
    # elements). Apply any scaling or alpha blending needing. 
    def drawObjectAt(self, screen, surface, loc, alpha = 255, scale = 1):
        if alpha < 255:
            surface = surface.copy()
            pixels_alpha = pygame.surfarray.pixels_alpha(surface)
            pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(Numeric.UInt8)
            del pixels_alpha
        if scale != 1:
            surface = pygame.transform.rotozoom(surface, 0, scale)
        rect = surface.get_rect()
        rect.topleft = (loc.x, loc.y)
        screen.blit(surface, rect)
        return rect


    ## Draw some text to the screen at the specified location.
    # \param texts A list of strings. Each string is drawn on a separate line.
    # \param fontNameNum Index into constants.fontNames
    # \param fontSize Integer. Must be one of the values in constants.fontSizes.
    # \param align: Text alignment.
    # \param color: PyGame-style color tuple, with alpha. 
    def drawText(self, screen, texts, loc, fontNameNum, fontSize, 
                 align = constants.TEXT_ALIGN_LEFT, color = (255, 255, 255, 255)):
        drawColor = (color[0], color[1], color[2])
        alpha = color[3]
        if fontNameNum < 0 or fontNameNum > len(constants.fontNames):
            logger.fatal("Invalid font selection:",fontNameNum)
        fontName = constants.fontNames[fontNameNum]
        if fontSize not in self.fonts[fontName]:
            logger.fatal("Invalid font size for font",fontName,":",fontSize)
        yOffset = 0
        for text in texts:
            textSurface = self.fonts[fontName][fontSize].render(text, True, drawColor)
            textRect = textSurface.get_rect()
            if align == constants.TEXT_ALIGN_LEFT:
                textRect.x = loc.x
            elif align == constants.TEXT_ALIGN_CENTER:
                textRect.centerx = loc.x
            elif align == constants.TEXT_ALIGN_RIGHT:
                textRect.right = loc.x
            textRect.centery = loc.y + yOffset
            yOffset += constants.textLineVerticalOffsetMultiplier * fontSize
            self.fadeAlpha(textSurface, alpha)
            screen.blit(textSurface, textRect)


    ## Fade the given surface by the given alpha amount. 
    def fadeAlpha(self, surface, alpha):
        if alpha < 255:
            if alpha < 0:
                alpha = 0
            # \todo: This is TERRIBLE. Figure out why pixels_alpha occasionally
            # throws an exception
            try:
                pixels_alpha = pygame.surfarray.pixels_alpha(surface)
                pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(Numeric.UInt8)
                del pixels_alpha
            except Exception, e:
                return

