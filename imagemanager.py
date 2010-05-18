import constants
import util
import logger

import os
import pygame

## This class handles loading and display of images. 
# \todo Switch this over from creating and using SDL Surfaces to OpenGL 
# textured quads.
class ImageManager:
    ## Load fonts, and prepare the image caches. 
    def __init__(self):
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


    ## Load a single surface. 
    def loadSurface(self, name, has_alpha = True):
        if name in self.surfaces:
            return self.surfaces[name]
        path = os.path.join(constants.spritePath, name + '.png')
        logger.debug("Loading image file",path)
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
        rect.topleft = loc.tuple()
        screen.blit(surface, rect)
        return rect

