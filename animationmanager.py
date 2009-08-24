import polygon
import animation
import constants
import logger
from vector2d import Vector2D

import pygame
import os
import copy

## The AnimationManager class handles loading and instantiating Animations and 
# their Polygons.
class AnimationManager:
    def __init__(self):
        ## A cache of animation data, to prevent redundant loading of modules.
        self.animationsCache = dict()

    
    ## Load information on the named animation. 
    # \param name The path to a directory containing directories of image files
    # (individual animations) and a spriteConfig.py file that holds 
    # information on those animations.
    # \param shouldCreateCopy True if the animation needs to be a copy of the 
    # cached version, false otherwise. If it isn't a copy, then we'll end up 
    # with multiple references to the same animation...but this doesn't matter
    # for things like terrain, and having each terrain block have its own
    # animation is slow.
    def loadAnimations(self, spriteName, shouldCreateCopy = True):
        if spriteName in self.animationsCache:
            if shouldCreateCopy:
                return self.copy(spriteName)
            return self.animationsCache[spriteName]
        
        # Search for a file named 'spriteConfig.py' through the path specified 
        # in spriteName. Use the deepest one we find. This lets us share 
        # spriteConfigs for similar sprites.
        directories = spriteName.split(os.sep)
        modulePath = ''
        path = constants.spritePath
        for directory in directories:
            path += os.sep + directory
            if os.path.exists(os.path.join(path, constants.spriteFilename + '.py')):
                modulePath = path

        modulePath = modulePath.replace(os.sep, '.') + '.' + constants.spriteFilename
        spriteModule = __import__(modulePath, globals(), locals(), ['sprites'])

        animations = {}
        for animationName, data in spriteModule.sprites.iteritems():
            animPolygon = polygon.Polygon([Vector2D(point) for point in data['polygon']])
            shouldLoop = True
            if 'loop' in data:
                shouldLoop = data['loop']
            updateRate = 1
            if 'updateRate' in data:
                updateRate = data['updateRate']
            updateFunc = None
            if 'updateFunc' in data:
                updateFunc = data['updateFunc']
            drawOffset = Vector2D(0, 0)
            if 'drawOffset' in data:
                drawOffset = Vector2D(data['drawOffset'])
            moveOffset = Vector2D(0, 0)
            if 'moveOffset' in data:
                moveOffset = Vector2D(data['moveOffset'])
            frameActions = dict()
            if 'frameActions' in data:
                frameActions = data['frameActions']
            animations[animationName] = animation.Animation(
                        spriteName, animationName, 
                        animPolygon, shouldLoop, updateRate, 
                        updateFunc, drawOffset, moveOffset, frameActions
            )

        self.animationsCache[spriteName] = animations
        if shouldCreateCopy:
            return self.copy(spriteName)
        return self.animationsCache[spriteName]
    
    
    ## Create a copy of the given dict (including copies of the animations 
    # involved) and return it.
    def copy(self, name):
        result = dict()
        for animationName in self.animationsCache[name]:
            result[animationName] = self.animationsCache[name][animationName].copy()
        return result

