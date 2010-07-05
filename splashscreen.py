import splashscreen
import constants

import pygame
import pygame.locals
import os
import OpenGL.GL as GL
import OpenGL.GLU as GLU

## This class handles the splash screen display at the start of the game. As
# such, it has very few dependencies (and in fact, duplicates some code found
# in the ImageManager and Font classes to avoid having to import them early).
# Note that it is in this class that PyGame is initialized and the main 
# display is set up.
class SplashScreen:
    def __init__(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.locals.GL_SWAP_CONTROL, 0)
        self.screen = pygame.display.set_mode((constants.sw, constants.sh),
                pygame.locals.OPENGL | pygame.locals.DOUBLEBUF)
        GL.glViewport(0, 0, constants.sw, constants.sh)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, float(constants.sw) / constants.sh, .1, 10000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(0, 0, 0, 0)
        GL.glClearDepth(1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)

        self.splashSurface = pygame.image.load(os.path.join(constants.otherPath, 'splashscreen.png'))
        self.texture = self.makeTextureFromSurface(self.splashSurface)
        
        self.font = pygame.font.Font(os.path.join(constants.fontPath, 'MODENINE.TTF'), 18)
        self.messageTextureId = None

    ## Copied from ImageManager's version. Can't import ImageManager at this
    # stage, though.
    # \todo Find a better approach.
    def makeTextureFromSurface(self, surface):
        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GLU.gluBuild2DMipmaps(GL.GL_TEXTURE_2D, GL.GL_RGBA,
                surface.get_width(), surface.get_height(),
                GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
                pygame.image.tostring(surface, 'RGBA'))
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                GL.GL_NEAREST_MIPMAP_NEAREST)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                GL.GL_NEAREST)
        return texture


    # Update the display of the splash screen; redraw the background image
    # and draw a new status message.
    def updateMessage(self, message):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GLU.gluOrtho2D(0, constants.sw, 0, constants.sh)
        GL.glScalef(1, -1, 1)
        GL.glTranslatef(0, -constants.sh, 0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        # Draw the backdrop
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex3f(0, 0, 0)
        GL.glTexCoord2f(0, 1)
        GL.glVertex3f(0, constants.sh, 0)
        GL.glTexCoord2f(1, 1)
        GL.glVertex3f(constants.sw, constants.sh, 0)
        GL.glTexCoord2f(1, 0)
        GL.glVertex3f(constants.sw, 0, 0)
        GL.glEnd()
        
        # Draw the message
        messageSurface = self.font.render(message, True, (255, 255, 255))
        messageRect = messageSurface.get_rect()
        if self.messageTextureId is not None:
            GL.glDeleteTextures(self.messageTextureId)
        self.messageTextureId = self.makeTextureFromSurface(messageSurface)
        
        topLeft = [20, 20]

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.messageTextureId)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex3f(topLeft[0], topLeft[1], 1)
        GL.glTexCoord2f(1, 0)
        GL.glVertex3f(topLeft[0] + messageRect.width, topLeft[1], 1)
        GL.glTexCoord2f(1, 1)
        GL.glVertex3f(topLeft[0] + messageRect.width, 
                      topLeft[1] + messageRect.height, 1)
        GL.glTexCoord2f(0, 1)
        GL.glVertex3f(topLeft[0], topLeft[1] + messageRect.height, 1)
        GL.glEnd()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)

        pygame.display.flip()

## Module-global singleton
splashscreen.splashScreen = SplashScreen()

## Passthrough to SplashScreen.updateMessage
def updateMessage(message):
    splashscreen.splashScreen.updateMessage(message)

## Since SplashScreen has the main PyGame screen surface, we need to be able 
# to retrieve it.
def getScreen():
    return splashscreen.splashScreen.screen

## Unset the singleton so that we can stop sending log messages to it.
def completeLoading():
    splashscreen.splashScreen = None

def getIsDoneLoading():
    return splashscreen.splashScreen == None
