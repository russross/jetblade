import constants
from .. import objectstate

import hangingstate
import groundedstate

## This class handles objects that are in freefall.
# Possible transitions: 
# Hit terrain from the side -> HangingState
# Land -> GroundedState
class FallingState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'fall'
        self.owner = owner
        self.owner.isGravityOn = True
        oldTop = self.owner.getHeadLoc()
        oldAnim = self.owner.sprite.getCurrentAnimation()
        if abs(self.owner.vel.x) < constants.EPSILON or oldAnim == 'standjump':
            self.owner.sprite.setAnimation('standfall')
        else:
            self.owner.sprite.setAnimation('fall')
        if oldAnim == 'crawl':
            # Assume that crawling animations have a different "top"
            # than other animations, and thus we need to move the sprite
            # down.
            # \todo This is a fairly nasty hack as it makes assumptions
            # about the shapes of bounding polygons for various actions.
            newTop = self.owner.getHeadLoc()
            self.owner.loc = self.owner.loc.addY(oldTop.y - newTop.y)


    ## Adjust velocity.
    def preCollisionUpdate(self):
        self.owner.applyMovement(self.owner.airAcceleration, self.owner.airDeceleration)

    
    ## Hit a floor. Transition to grounded state.
    def hitFloor(self, collision):
        self.owner.setState(groundedstate.GroundedState(self.owner))
        return True


    ## Hit a wall. Check to see if we can hang from the obstruction.
    def hitWall(self, collision):
        if self.owner.canHang and self.owner.canGrabLedge():
            self.owner.setState(hangingstate.HangingState(self.owner))
        return True
