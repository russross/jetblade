import game
import logger

import pygame

## Amount to add to drawing location to prevent visual jitter
drawRoundAmount = .000005

## Sprites are display classes for handling dynamic game objects like creatures.
# Each sprite contains a set of Animation instances, and tracks the "parent
# object's" locations as of the last two physics updates so that drawing can
# smoothly interpolate between those points.
class Sprite:

    ## Instantiate a Sprite.
    # \param shouldCreateCopy Passthrough argument for 
    # AnimationManager.loadAnimations. \todo Find a better way to handle this
    # so the passthrough isn't needed.
    def __init__(self, name, owner, loc = None, shouldCreateCopy = True):
        ## Name of the sprite, a.k.a. the path to the directory containing the 
        # animations in the sprite.
        self.name = name
        ## Mapping of animation names to Animation instances. 
        self.animations = game.animationManager.loadAnimations(name, shouldCreateCopy)
        ## Current active animation. 
        self.currentAnimation = self.animations.keys()[0]
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
    # Return True if we succeed in changing the animation; false otherwise.
    # Currently animation setting always succeeds (no checks for e.g. 
    # terrain intersection problems with the new animation are performed). 
    def setAnimation(self, action, shouldUseFacing = True):
        curAnim = self.animations[self.currentAnimation]
        if shouldUseFacing:
            if self.owner.facing < 0:
                action += '-l'
            else:
                action += '-r'
        if action != self.currentAnimation:
            curAnim.reset()
            self.currentAnimation = action
        return True


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
        animFacing = 1 if self.currentAnimation[-2:] == '-r' else -1
        if animFacing != self.owner.facing:
            # We're facing the wrong way. Turn around, but keep the same current
            # frame.
            curFrame = curAnim.frame
            self.setAnimation(self.getCurrentAnimation())
            curAnim = self.animations[self.currentAnimation]
            curAnim.frame = curFrame
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
    def draw(self, progress, drawLoc = None):
        if drawLoc is None:
            drawLoc = self.getDrawLoc(progress)
        self.animations[self.currentAnimation].draw(drawLoc, progress)


    ## Interpolate between self.prevLoc and self.curLoc, using progress to 
    # weight the two locations.
    # Round drawing locations to the nearest hundred-thousandth to prevent 
    # visual jittering caused by very minor positional variation.
    def getDrawLoc(self, progress):
        loc = self.prevLoc.interpolate(self.curLoc, progress)
        loc = loc.addScalar(drawRoundAmount).toInt()
        return loc


    ## Return a PyGame Rect describing our bounding box.
    def getBounds(self, loc):
        polygon = self.animations[self.currentAnimation].getPolygon()
        return polygon.getBounds(loc)


    ## Set the animation to use the provided polygon instead of the one it's
    # currently using.
    def overridePolygon(self, newPolygon):
        self.animations[self.currentAnimation].setPolygon(newPolygon)


    ## Retrieve the current animation's polygon, or the previous animation's
    # polygon if needed.
    def getPolygon(self):
        return self.animations[self.currentAnimation].getPolygon()


    ## Retrieve the polygon for the named animation.
    def getPolygonForAnimation(self, animationName):
        return self.animations[animationName + '-' + self.getFacingString()].getPolygon()


    ## Return a string representing the facing of the object
    def getFacingString(self):
        if self.owner.facing < 0:
            return 'l'
        return 'r'


    ## Return the current animation name, defaulting to not including the facing
    # if any.
    # \todo Assumes that the facing is the last two characters of the string.
    #       Probably a better way to handle this.
    def getCurrentAnimation(self, shouldIncludeFacing = False):
        if shouldIncludeFacing:
            return self.currentAnimation
        else:
            return self.currentAnimation[:-2]


    ## Return the current Animation object
    def getCurrentAnimationObject(self):
        return self.animations[self.currentAnimation]

