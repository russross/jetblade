import util
import game
import constants
import logger

import os

## Animations are sequences of images and the logic needed to know when, where, 
# and how to display them. Every animation is tied to a single polygon for 
# collision detection. Animations may loop, may change the location of the 
# animated object after completing, and may have specialized logic for
# when to change animation frames.
class Animation:
    ## Create a new Animation instance.
    def __init__(self, group, name, polygon, shouldLoop,
                 updateRate, updateFunc, drawOffset, moveOffset, frameActions):
        
        ## The collection of animations that this one is a part of. For example,
        # in "player/run-l" the group would be "player"
        self.group = group
        
        ## The specific animation name, e.g. "run-l"
        self.name = name

        ## The polygon that is used for all frames of the animation.
        self.polygon = polygon

        ## If true, the animation will automatically loop when it runs out of
        # frames, and will therefore never complete.
        # If false, then once the final frame is reached, the animation will
        # stay on that frame indefinitely.
        self.shouldLoop = shouldLoop

        ## If this is not None, then it specifies how rapidly animation frames
        # update in terms of physics updates (1 => 1 frame advanced per 
        # physics update).
        self.updateRate = updateRate

        ## If this is not None, then it specifies a function that accepts the
        # object being animated and returns the number of frames to advace the
        # animation.
        self.updateFunc = updateFunc

        ## A positional offset used when drawing.
        self.drawOffset = drawOffset

        ## The amount to move the animated object after the animation completes.
        # This value is never used if the animation is set to loop, as the
        # animation never completes.
        self.moveOffset = moveOffset

        ## Actions to take on specific frames of the animation
        self.frameActions = frameActions

        ## Individual frames of the animation.
        self.frames = game.imageManager.loadAnimation(
                os.path.join(self.group, self.name)
        )
        ## Current frame of animation; an index into self.frames.
        self.frame = 0

        ## Previous frame as of the last update
        self.prevFrame = 0
        
        ## Tracks if we've reached the end of the animation.
        self.isComplete = False


    ## Create a blank copy of this animation set.
    def copy(self):
        return Animation(self.group, self.name, self.polygon, self.shouldLoop,
                         self.updateRate, self.updateFunc,
                         self.drawOffset, self.moveOffset, self.frameActions)


    ## Advance self.frames. If self.updateFunc is specified, use that;
    # otherwise, use self.updateRate. Return True if the animation is complete,
    # False otherwise.
    def update(self, owner):
        self.prevFrame = self.frame
        if not self.isComplete or self.shouldLoop:
            if self.updateFunc is not None:
                self.frame += self.updateFunc(owner)
            else:
                self.frame += self.updateRate
        if (int(self.prevFrame) != int(self.frame) and 
                int(self.frame) in self.frameActions):
            self.frameActions[int(self.frame)](owner, game)
        if (not self.shouldLoop and not self.isComplete and 
                (self.frame >= len(self.frames) or
                 self.frame < 0)):
            # Animation done
            self.isComplete = True
            return True
        return False


    ## Draw the animation to screen, taking self.drawOffset into account.
    def draw(self, loc, progress):
        drawLoc = loc
        if self.drawOffset.magnitudeSquared() > constants.EPSILON:
            drawLoc = loc.add(self.drawOffset).round()
        frame = int(self.prevFrame + (self.frame - self.prevFrame) * progress)
        if self.isComplete:
            frame = len(self.frames) - 1
        surface = self.frames[int(frame) % len(self.frames)]
        game.imageManager.drawGameObjectAt(surface, drawLoc)
        if logger.getLogLevel() == logger.LOG_DEBUG:
            # Draw the bounding polygon and location information
            self.polygon.draw(loc)
            gridLoc = loc.toGridspace()
            game.fontManager.drawText('MODENINE', 12,
                    ['%d' % gridLoc.x,
                     '%d' % gridLoc.y,
                     '%d' % loc.x,
                     '%d' % loc.y],
                    loc = drawLoc.addScalar(25),
                    isPositioningAbsolute = False
            )


    ## Reset internal state so the animation can be cleanly re-run.
    def reset(self):
        self.frame = 0
        self.prevFrame = 0
        self.isComplete = False
    

    def setPolygon(self, newPolygon):
        self.polygon = newPolygon
    
    
    def getPolygon(self):
        return self.polygon
    

    def getMoveOffset(self):
        return self.moveOffset


    def getFrame(self, index = None):
        if index is None:
            index = self.frame
        return self.frames[index]


    ## Return True if the animation completed by running through all its frames,
    # or False if it completed by running backwards.
    def getCompletedSuccessfully(self):
        return self.frame > self.prevFrame


    def __str__(self):
        return '[Animation ' + self.name + ' at frame ' + str(self.frame) + ']'
