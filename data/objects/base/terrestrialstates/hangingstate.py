import constants
import objectstate
from vector2d import Vector2D

import fallingstate
import climbingstate
import jumpingstate

## This class handles objects that are hanging from a ledge.
# Possible transitions: 
# Release grip -> FallingState
# Jump -> JumpingState
# Climb -> ClimbingState
class HangingState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'hang'
        self.owner = owner
        self.owner.isGravityOn = False
        self.owner.vel = Vector2D(0, 0)
        # Lock position to match the block.
        self.owner.loc = self.owner.loc.setY(
            int(
                (self.owner.loc.y - self.owner.vel.y) /
                constants.blockSize + .5
               ) * constants.blockSize
        )
        self.owner.sprite.setAnimation('hang')
        self.owner.maxVel = self.owner.maxGroundVel


    ## Check for climbing
    def preCollisionUpdate(self):
        if self.owner.shouldClimb:
            self.owner.setState(climbingstate.ClimbingState(self.owner))
        elif self.owner.shouldReleaseHang:
            self.owner.isGravityOn = True
            self.owner.setState(fallingstate.FallingState(self.owner))
        elif self.owner.shouldJump:
            self.owner.isGravityOn = True
            self.owner.setState(jumpingstate.JumpingState(self.owner))
