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
        ## Maximal width and height
        self.maxDims = [0, 0]
        ## Mapping of characters to textures of those characters
        self.charTextures = dict()
        for char in string.printable:
            width, height = self.font.size(char)
            self.maxDims[0] = max(self.maxDims[0], width)
            self.maxDims[1] = max(self.maxDims[1], height)
            charSurface = self.font.render(char, True, (255, 255, 255))
            self.charTextures[char] = game.imageManager.createTextureFromSurface(charSurface)
        ## Cache of recently-rendered strings; maps text of string to 
        # (display list ID, access time)
        self.renderCache = dict()


    ## Draw some white text to the screen at the specified location.
    # \param texts A list of strings. Each string is drawn on a separate line.
    # \param loc Vector2D location to draw the text.
    # \param isPositioningAbsolute If true, loc is an offset from the top-left
    #        corner of the screen; otherwise, it is a location in realspace.
    # \todo Most of these parameters are not used at the moment.
    def drawText(self, texts, loc, isPositioningAbsolute = True, 
                 align = TEXT_ALIGN_LEFT, 
                 color = (255, 255, 255, 255)):
        if not isPositioningAbsolute:
            loc = util.adjustLocForCenter(loc, game.camera.getDrawLoc(), game.screen.get_rect())
        # Calculate widths of each line, needed for alignment
        textWidths = [self.maxDims[0] * len(t) for t in texts]
        maxWidth = max(textWidths)
            
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glPushMatrix()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glOrtho(0, constants.sw, constants.sh, 0, 0, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        yOffset = 0
        for index, text in enumerate(texts):
            if text not in self.renderCache:
                # Generate a display list to render the text.
                newList = GL.glGenLists(1)
                GL.glNewList(newList, GL.GL_COMPILE)
                xOffset = 0
                for char in text:
                    left = xOffset
                    top = 0
                    right = left + self.maxDims[0]
                    bottom = self.maxDims[1]
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
                    xOffset += self.maxDims[0]
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
                xAdjustment = maxWidth - textWidths[index]
            elif align == TEXT_ALIGN_CENTER:
                xAdjustment = (maxWidth - textWidths[index]) / 2.0
            GL.glPushMatrix()
            GL.glLoadIdentity()
            GL.glTranslatef(loc.x + xAdjustment, loc.y + yOffset, 0)
            GL.glCallList(self.renderCache[text][1])
            GL.glPopMatrix()
            
            # Update last-used time
            self.renderCache[text][0] = time.time()            
            yOffset += self.maxDims[1]

        # Clean up the stack
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()
        GL.glEnable(GL.GL_DEPTH_TEST)

