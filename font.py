import util
import constants
import logger

import pygame
import os

## Identifiers for text alignment
(TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT) = range(1, 4)

## Represents a single font. This class loads the font information from a TTF
# file, and draws the font to screen.
class Font:

    ## Instantiate a Font instance
    def __init__(self, name, sizes):
        self.name = name + '.TTF'
        self.fonts = dict()
        for size in sizes:
            self.fonts[size] = pygame.font.Font(
                    os.path.join(constants.fontPath, self.name), size)


    ## Draw some text to the screen at the specified location.
    # \param texts A list of strings. Each string is drawn on a separate line.
    # \param fontSize Font size to use. If we haven't already loaded that size,
    #                 then load it first.
    # \param align: Text alignment. See the TEXT_ALIGN_* constants.
    # \param color: PyGame-style color tuple, with alpha. 
    def drawText(self, screen, texts, loc, fontSize, 
                 align = TEXT_ALIGN_LEFT, color = (255, 255, 255, 255)):
        if fontSize not in self.fonts:
            self.fonts[fontSize] = pygame.font.Font(
                    os.path.join(constants.fontPath, self.name), fontSize)
        drawColor = (color[0], color[1], color[2])
        alpha = color[3]
        yOffset = 0
        for text in texts:
            textSurface = self.fonts[fontSize].render(text, True, drawColor)
            textRect = textSurface.get_rect()
            if align == TEXT_ALIGN_LEFT:
                textRect.x = loc.x
            elif align == TEXT_ALIGN_CENTER:
                textRect.centerx = loc.x
            elif align == TEXT_ALIGN_RIGHT:
                textRect.right = loc.x
            textRect.centery = loc.y + yOffset
            yOffset += self.fonts[fontSize].get_linesize()
            if alpha != 255:
                util.fadeAlpha(textSurface, alpha)
            screen.blit(textSurface, textRect)
