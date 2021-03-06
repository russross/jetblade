import util
import constants
import logger
import game

import pygame
import os
import time
import string
import OpenGL.GL as GL

## Number of strings to keep cached.
TEXT_CACHE_SIZE = 64

## Alignment strings
[TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT] = range(3)

## Represents a single font. This class loads the font information from a TTF
# file, and draws the font to screen.
class Font:
    ## Instantiate a Font instance
    def __init__(self, name, size):
        self.name = name + '.TTF'
        try:
            self.font = pygame.font.Font(os.path.join(constants.fontPath, self.name), size)
        except Exception, e:
            logger.fatal("Unable to load font named %s: [%s]" % (self.name, e))
        ## Mapping of characters to textures of those characters
        self.charTextures = dict()
        self.charSizes = dict()
        self.maxWidth = 0
        for char in string.printable:
            self.charSizes[char] = self.font.size(char)
            self.maxWidth = max(self.maxWidth, self.charSizes[char][0])
            charSurface = self.font.render(char, True, (255, 255, 255))
            self.charTextures[char] = game.imageManager.createTextureFromSurface(charSurface)
        ## Cache of recently-rendered strings; maps text of string to 
        # (display list ID, access time)
        self.renderCache = dict()


    ## Draw some white text to the screen at the specified location.
    # \param texts A list of strings. Each string is drawn on a separate line.
    # \param loc Vector2D location to draw the text. If using left-alignment,
    #        this is the upper-left corner of the text. If using
    #        center-alignment, it's the upper-middle. If using right-alignment,
    #        it's the upper-right corner. 
    # \param isPositioningAbsolute If true, loc is an offset from the top-left
    #        corner of the screen; otherwise, it is a location in realspace.
    # \todo Most of these parameters are not used at the moment.
    def drawText(self, texts, loc, isPositioningAbsolute = True, 
                 align = TEXT_ALIGN_LEFT, 
                 color = (255, 255, 255, 255)):
        if not isPositioningAbsolute:
            loc = util.adjustLocForCenter(loc, game.camera.getDrawLoc(), game.screen.get_rect())
        # Calculate widths of each line, needed for alignment
        textWidths = [self.maxWidth * len(t) for t in texts]
        maxWidth = max(textWidths)

        GL.glColor4fv([i / 255.0 for i in color])

        GL.glDisable(GL.GL_DEPTH_TEST)
        util.setOrtho()
        
        yOffset = 0
        for index, text in enumerate(texts):
            if text not in self.renderCache:
                # Generate a display list to render the text.
                newList = GL.glGenLists(1)
                GL.glNewList(newList, GL.GL_COMPILE)
                xOffset = 0
                for char in text:
                    width, height = self.charSizes[char]
                    left = int(xOffset)
                    top = 0
                    right = int(left + width)
                    bottom = int(height)
                    GL.glBindTexture(GL.GL_TEXTURE_2D, self.charTextures[char])
                    GL.glBegin(GL.GL_QUADS)
                    GL.glTexCoord2f(0, 0)
                    GL.glVertex3f(left, top, 0)
                    GL.glTexCoord2f(1, 0)
                    GL.glVertex3f(right, top, 0)
                    GL.glTexCoord2f(1, 1)
                    GL.glVertex3f(right, bottom, 0)
                    GL.glTexCoord2f(0, 1)
                    GL.glVertex3f(left, bottom, 0)
                    GL.glEnd()
                    # Enforce "fixed-width" offsets
                    xOffset += int(self.maxWidth)
                GL.glEndList()
                self.renderCache[text] = [time.time(), newList]
                if len(self.renderCache) > TEXT_CACHE_SIZE:
                    # Find the least recently-used string and delete it.
                    oldestTime = None
                    oldestText = None
                    for itemText, (useTime, temp) in self.renderCache.iteritems():
                        if oldestTime is None or useTime < oldestTime:
                            oldestTime = useTime
                            oldestText = itemText
                    GL.glDeleteLists(self.renderCache[oldestText][1], 1)
                    del self.renderCache[oldestText]
                    
            # Translate to where the text should be drawn, and draw it
            xAdjustment = 0
            if align == TEXT_ALIGN_RIGHT:
                xAdjustment = -textWidths[index]
            elif align == TEXT_ALIGN_CENTER:
                xAdjustment = (maxWidth - textWidths[index]) / 2.0
            GL.glPushMatrix()
            GL.glLoadIdentity()
            # \todo Either come up with an explanation for why we need to add
            # .5 to keep the text from going fuzzy, or rework things so we
            # don't.
            GL.glTranslatef(int(loc.x + xAdjustment) + .375, 
                            int(loc.y + yOffset) + .375, 0)
            GL.glCallList(self.renderCache[text][1])
            GL.glPopMatrix()
            
            # Update last-used time
            self.renderCache[text][0] = time.time()            
            yOffset += self.font.get_height()

        # Clean up the stack
        util.clearOrtho()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glColor4f(1, 1, 1, 1)

