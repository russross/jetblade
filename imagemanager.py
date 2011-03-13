import constants
import util
import logger
from vector2d import Vector2D

import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU

## This is a simple container class for holding metadata on image frames.
class Frame:
    def __init__(self, surface, textureId, name):
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.textureId = textureId
        self.name = name

    def __str__(self):
        return "[Frame %s with dimensions %dx%d]" % (self.name, self.width, self.height)

## This class handles loading and display of images. 
# \todo Switch this over from creating and using SDL Surfaces to OpenGL 
# textured quads.
class ImageManager:
    ## Load fonts, and prepare the image caches. 
    def __init__(self):
        ## Maps animation group names to sets of animations. Typically an 
        # animation group is all of the animations for a single creature.
        self.animationSets = dict()
        ## Maps animation names to sequences of texture IDs.
        self.animations = dict()
        ## Maps surface names to Frame instances
        self.frames = dict()


    ## Load the named animation set, either from our cache or by loading each
    # individual animation in the set.
    def loadAnimationSet(self, name):
        if name in self.animationSets:
            return self.animationSets[name]
        result = dict()
        for entry in os.listdir(os.path.join(constants.spritePath, name)):
            if entry.find(constants.spriteFilename) == -1:
                result[entry] = self.loadAnimation(os.path.join(name, entry))
        self.animationSets[name] = result
        return result


    ## Load all of the surfaces in a given named animation. 
    def loadAnimation(self, name):
        if name in self.animations:
            return self.animations[name]
        result = []
        files = os.listdir(os.path.join(constants.spritePath, name))
        for file in files:
            filename, extension = file.split('.')
            result.append(self.loadSurface(os.path.join(name, filename)))
        self.animations[name] = result
        return result


    ## Load a single surface, process it into a texture for OpenGL, and
    # store it in a Frame instance.
    # \todo This assumes all image names end in ".png". Pretty brittle.
    def loadSurface(self, name, has_alpha = True):
        if name in self.frames:
            return self.frames[name]
        path = os.path.join(constants.spritePath, name + '.png')
        surface = pygame.image.load(path)
        if has_alpha:
            surface = surface.convert_alpha()

        texture = self.createTextureFromSurface(surface, has_alpha)
        self.frames[name] = Frame(surface, texture, name)
        return self.frames[name]


    def createTextureFromSurface(self, surface, has_alpha = True):
        texture = GL.glGenTextures(1)
        modeFlag = GL.GL_RGB
        modeString = "RGB"
        if has_alpha:
            modeFlag = GL.GL_RGBA
            modeString = "RGBA"
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GLU.gluBuild2DMipmaps(GL.GL_TEXTURE_2D, modeFlag, 
                surface.get_width(), surface.get_height(), 
                modeFlag, GL.GL_UNSIGNED_BYTE, 
                pygame.image.tostring(surface, modeString))
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, 
                GL.GL_NEAREST_MIPMAP_NEAREST)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, 
                GL.GL_NEAREST)
        return texture


    ## Clear the screen to black.
    def drawBackground(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)


    ## Draw an object relative to the camera. 
    # \todo This function is obsolete, just a passthrough now. Remove it.
    def drawGameObjectAt(self, frame, loc):
        self.drawObjectAt(frame, loc)


    ## Draw an object at a specific location on the screen (e.g. for HUD 
    # elements). Apply any scaling or alpha blending needing. 
    def drawObjectAt(self, frame, loc):
        bottomRight = loc.add(Vector2D(frame.width, frame.height))
        GL.glBindTexture(GL.GL_TEXTURE_2D, frame.textureId)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex3f(loc.x, -loc.y, 0)
        GL.glTexCoord2f(1, 0)
        GL.glVertex3f(bottomRight.x, -loc.y, 0)
        GL.glTexCoord2f(1, 1)
        GL.glVertex3f(bottomRight.x, -bottomRight.y, 0)
        GL.glTexCoord2f(0, 1)
        GL.glVertex3f(loc.x, -bottomRight.y, 0)
        GL.glEnd()


    ## Create a display list of the provided set of loc-frame pairs.
    def createDisplayList(self, objects):
        list = GL.glGenLists(1)
        GL.glNewList(list, GL.GL_COMPILE)
        for frame, loc in objects:
            self.drawObjectAt(frame, loc)
        GL.glEndList()
        return list


    ## Draw the provided list
    def drawList(self, list):
        GL.glCallList(list)


    ## Convert an SDL-style surface into an OpenGL texture and blit it.
    def blitSurface(self, surface, rect, cameraLoc):
        logger.debug("Pretending to blit surface", surface, "with rect", rect)
        texture = self.createTextureFromSurface(surface)
        size = Vector2D(rect.width, rect.height)
        topLeft = Vector2D(rect.left, rect.top).add(cameraLoc).sub(size.multiply(.5))
        bottomRight = topLeft.add(size)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex3f(topLeft.x, -topLeft.y, 0)
        GL.glTexCoord2f(1, 0)
        GL.glVertex3f(bottomRight.x, -topLeft.y, 0)
        GL.glTexCoord2f(1, 1)
        GL.glVertex3f(bottomRight.x, -bottomRight.y, 0)
        GL.glTexCoord2f(0, 1)
        GL.glVertex3f(topLeft.x, -bottomRight.y, 0)
        GL.glEnd()
        GL.glDeleteTextures(1, texture)


