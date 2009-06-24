import polygon
import sprite
import animation
import constants
import util

import pygame


## Sprites are display classes for handling dynamic game objects like creatures.
# Each sprite contains a set of Animation instances, and tracks the "parent
# object's" locations as of the last two physics updates so that drawing can
# smoothly interpolate between those points.
class Sprite:

    def __init__(self, name, owner):
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
        ## Previous location of the parent object, for interpolation of drawing
        # location.
        self.prevLoc = owner.loc
        ## Current location of the parent object, for interpolation of drawing
        # location.
        self.curLoc = owner.loc


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
        util.debug("Sprite",self.name,"setting animation",action)
        if action != self.currentAnimation:
            if shouldResetAnimation:
                self.animations[self.currentAnimation].reset()
            self.prevAnimation = self.currentAnimation
            self.currentAnimation = action


    ## Set the current animation to what the previous one was.
    def setPreviousAnimation(self, shouldResetAnimation = True):
        util.debug("Returning to previous animation",self.prevAnimation)
        self.setAnimation(self.prevAnimation, False, shouldResetAnimation)

    ## Reset the currently-running animation.
    def resetAnimation(self):
        self.animations[self.currentAnimation].reset()

    ## Update the displayed animation. If the animation has finished, apply
    # whatever closing logic is necessary. 
    def update(self):
        curAnim = self.animations[self.currentAnimation]
        if curAnim.update(self.owner):
            util.debug("Finishing animation",curAnim.name)
            # Animation finished, so wrap up.
            curAnim.completeAnimation(self.owner)
            self.owner.completeAnimation(self.getCurrentAnimation())
            if (abs(curAnim.moveOffset[0]) > constants.EPSILON or 
                    abs(curAnim.moveOffset[1]) > constants.EPSILON):
                util.debug("Teleporting due to move offset",curAnim.moveOffset)
                # Ending the animation moved the player, possibly arbitrarily,
                # so our interpolation points are no longer valid.
                self.prevLoc = tuple(self.owner.loc)
                self.curLoc = self.prevLoc
        self.prevLoc = (self.curLoc[0], self.curLoc[1])
        self.curLoc = tuple(self.owner.loc)
        util.debug(self.prevLoc,self.curLoc)


    ## Draw the current animation frame.
    def draw(self, screen, camera, progress, scale = 1):
        drawLoc = self.getDrawLoc(progress)
        self.animations[self.currentAnimation].draw(screen, camera, drawLoc, scale)


    ## Interpolate between self.prevLoc and self.curLoc, using progress to 
    # weight the two locations.
    def getDrawLoc(self, progress):
        return util.interpolatePoints(self.prevLoc, self.curLoc, progress)


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

    ## Do collision detection against the provided polygon, which is at
    # the provided location.
    def collidePolygon(self, polygon, loc):
        return self.animations[self.currentAnimation].getPolygon().runSAT(self.owner.loc, polygon, loc)


## A cache of animation data, to prevent redundant loading of modules.
animationsCache = {}
## Load information on the named animation. 
# \param name The path to a directory containing directories of image files
# (individual animations) and a sprite.py file that holds information on those
# animations.
def loadAnimations(name):
    
    # Special case: static terrain shares one file since they're just 
    # different skins over the same polygons.
    # \todo This is a hack and could probably be handled better, perhaps by 
    # having a heirarchy of sprite configuration modules.
    moduleName = name
    if name.find('terrain') != -1:
        moduleName = 'terrain'

    if name in sprite.animationsCache:
        return sprite.animationsCache[name]

    path = moduleName
    path = path.replace('/', '.')
    path += '.spriteConfig'
    util.debug("Loading animations for",name,"with path",path)
    spriteModule = __import__(path, globals(), locals(), ['sprites'])

    animations = {}
    for animationName, data in spriteModule.sprites.iteritems():
        animPolygon = polygon.Polygon(data['polygon'])
        shouldLoop = True
        if 'loop' in data:
            shouldLoop = data['loop']
        updateRate = 1
        if 'updateRate' in data:
            updateRate = data['updateRate']
        updateFunc = None
        if 'updateFunc' in data:
            updateFunc = data['updateFunc']
        drawOffset = (0, 0)
        if 'drawOffset' in data:
            drawOffset = data['drawOffset']
        moveOffset = (0, 0)
        if 'moveOffset' in data:
            moveOffset = data['moveOffset']
        animations[animationName] = animation.Animation(name, animationName, 
                    animPolygon, shouldLoop, updateRate, updateFunc, 
                    drawOffset, moveOffset)

    sprite.animationsCache[name] = animations
    return animations

    
    
