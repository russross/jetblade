import constants
import objectstate

import fallingstate

## This class handles objects that have jumped into the air.
# Possible transitions: 
# Hit ceiling, or run out of jump time -> FallingState
class JumpingState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'jump'
        self.owner = owner
        self.jumpFrames = 0
        if abs(self.owner.vel.x) < constants.EPSILON:
            self.owner.sprite.setAnimation('standjump')
        else:
            self.owner.sprite.setAnimation('jump')
        self.owner.vel = self.owner.vel.setY(self.owner.jumpSpeed)
        self.owner.isGravityOn = False


    ## Check input for state transitions; perform them if the terrain allows.
    def preCollisionUpdate(self):
        self.owner.applyMovement(self.owner.airAcceleration, self.owner.airDeceleration)
        if self.owner.shouldJump and self.jumpFrames <= self.owner.maxJumpRiseFrames:
            self.jumpFrames += 1
        else:
            self.owner.isGravityOn = True
            self.owner.setState(fallingstate.FallingState(self.owner))
   
    
    ## Hit a ceiling; start falling.
    def hitCeiling(self, collision):
        self.owner.setState(fallingstate.FallingState(self.owner))
        return True
