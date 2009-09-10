import objectstate
import game
from vector2d import Vector2D

import fallingstate

## This class handles creatures that are flinching after getting hit. To know
# what direction to flinch in, they need to have the object that was touched.
# Additionally the calling object should have the fields flinchFrames and 
# mercyInvincibilityFrames.
# Possible transitions: 
# Finish flinch -> FallingState
class FlinchState(objectstate.ObjectState):
    def __init__(self, owner, altObject):
        self.name = 'flinch'
        self.owner = owner
        self.owner.isGravityOn = False
        self.owner.shouldApplyVelocityCap = False
        self.owner.invincibilityTimer = self.owner.mercyInvincibilityFrames
        self.owner.health -= altObject.touchDamage
        self.owner.sprite.setAnimation('flinch')
        self.flinchVel = Vector2D(self.owner.flinchVel.x * cmp(altObject.loc.x, self.owner.loc.x), 
                                  self.owner.flinchVel.y)
        self.flinchFrames = 0


    ## Check if we're done flinching.
    def preCollisionUpdate(self):
        self.owner.vel = self.flinchVel
        self.flinchFrames += 1
        if self.flinchFrames >= self.owner.flinchFrames:
            self.owner.isGravityOn = True
            self.owner.shouldApplyVelocityCap = True
            self.owner.setState(fallingstate.FallingState(self.owner))

