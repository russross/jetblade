import polygon
import sprite
import animation
import constants
import logger
from vector2d import Vector2D

import pygame
import os

## Amount to add to drawing location to prevent visual jitter
drawRoundAmount = .000005

## Sprites are display classes for handling dynamic game objects like creatures.
# Each sprite contains a set of Animation instances, and tracks the "parent
# object's" locations as of the last two physics updates so that drawing can
# smoothly interpolate between those points.
class Sprite:

    ## Instantiate a Sprite.
    def __init__(self, name, owner, loc = None):
        ## Name of the sprite, a.k.a. the path to the directory containing the 
        # animations in the sprite.
        self.name = name
        ## Mapping of animation names to Animation instances. 
        self.animations = loadAnimations(name)
        ## Current active animation. 
        self.currentAnimation = self.animations.keys()[0]
        ## Previous animation. Sometimes we need to know what we were just
        # doing. 
        self.prevAnimation = self.currentAnimation
        ## Object this is a sprite for. 
        self.owner = owner
        ## Drawing location as of previous physics update, for location
        # interpolation.
        self.prevLoc = loc
        ## Drawing location as of most recent physics update, for location
        # interpolation
        self.curLoc = loc


    ## Set the current animation for the sprite.
    # \param shouldUseFacing If true, the actual animation name used has
    # -l or -r appended, depending on self.owner.facing
    # \param shouldResetAnimation If true, the frame of the animation is 
    # reset; otherwise it is preserved. 
    # \todo shouldResetAnimation should be handled better. Currently we need
    # it so we can "try out" different polygons for collision detection (c.f.
    # TerrestrialObject crawl logic) without interfering with smooth animation.
    def setAnimation(self, action, shouldUseFacing = True, shouldResetAnimation = True):
        if shouldUseFacing:
            if self.owner.facing < 0:
                action += '-l'
            else:
                action += '-r'
        logger.debug("Sprite",self.name,"setting animation",action)
        if action != self.currentAnimation:
            if shouldResetAnimation:
                self.animations[self.currentAnimation].reset()
            self.prevAnimation = self.currentAnimation
            self.currentAnimation = action


    ## Set the current animation to what the previous one was.
    def setPreviousAnimation(self, shouldResetAnimation = True):
        logger.debug("Returning to previous animation",self.prevAnimation)
        self.setAnimation(self.prevAnimation, False, shouldResetAnimation)

    ## Reset the currently-running animation.
    def resetAnimation(self):
        self.animations[self.currentAnimation].reset()

    ## Update the displayed animation. If the animation has finished, apply
    # whatever closing logic is necessary. 
    # \param loc The location of the sprite as of this update. This is 
    # technically optional if you are going to specify a drawing location every
    # time you call Sprite.draw().
    def update(self, loc = None):
        curAnim = self.animations[self.currentAnimation]
        if curAnim.update(self.owner):
            logger.debug("Finishing animation",curAnim.name)
            # Animation finished, so wrap up.
            newLoc = self.owner.completeAnimation(self.animations[self.currentAnimation])
            if newLoc != loc:
                logger.debug("Teleporting due to move offset",
                             curAnim.moveOffset,"from",loc,"to",newLoc)
                # Ending the animation moved the player, possibly arbitrarily,
                # so our interpolation points are no longer valid.
                self.prevLoc = newLoc.copy()
                self.curLoc = newLoc.copy()
            loc = newLoc
        self.prevLoc = self.curLoc.copy()
        self.curLoc = loc.copy()


    ## Draw the current animation frame.
    # \param drawLoc The location to draw the sprite. This is optional; if it
    # is not provided, then the sprite will derive its own draw location based
    # on its locations at the previous two physics updates.
    def draw(self, screen, camera, progress, drawLoc = None, scale = 1):
        if drawLoc is None:
            drawLoc = self.getDrawLoc(progress)
        self.animations[self.currentAnimation].draw(screen, camera, drawLoc, scale)


    ## Interpolate between self.prevLoc and self.curLoc, using progress to 
    # weight the two locations.
    # Round drawing locations to the nearest hundred-thousandth to prevent 
    # visual jittering caused by very minor positional variation.
    def getDrawLoc(self, progress):
        loc = self.prevLoc.interpolate(self.curLoc, progress)
        loc = loc.addScalar(drawRoundAmount).int()
        return loc


    ## Retrieve the current animation's polygon, or the previous animation's
    # polygon if needed.
    def getPolygon(self, shouldUsePrevAnimation = False):
        action = self.currentAnimation
        if shouldUsePrevAnimation:
            action = self.prevAnimation
        return self.animations[action].getPolygon()


    ## Return the current animation, defaulting to not including the facing
    # if any.
    # \todo Assumes that the facing is the last two characters of the string.
    #       Probably a better way to handle this.
    def getCurrentAnimation(self, shouldIncludeFacing = False):
        if shouldIncludeFacing:
            return self.currentAnimation
        else:
            return self.currentAnimation[:-2]


## A cache of animation data, to prevent redundant loading of modules.
animationsCache = {}
## Load information on the named animation. 
# \param name The path to a directory containing directories of image files
# (individual animations) and a sprite.py file that holds information on those
# animations.
def loadAnimations(name):

    if name in sprite.animationsCache:
        return sprite.animationsCache[name]
    
    # Search for a file named 'spriteConfig.py' through the path specified in
    # name. Use the deepest one we find. This lets us share spriteConfigs for
    # similar sprites.
    directories = name.split('/')
    modulePath = ''
    path = constants.imagePath
    for directory in directories:
        path += '/' + directory
        if os.path.exists(path + '/spriteConfig.py'):
            modulePath = path

    modulePath = modulePath.replace('/', '.') + '.spriteConfig'
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
        animations[animationName] = animation.Animation(name, animationName, 
                    animPolygon, shouldLoop, updateRate, updateFunc, 
                    drawOffset, moveOffset)

    sprite.animationsCache[name] = animations
    return animations

    
    
