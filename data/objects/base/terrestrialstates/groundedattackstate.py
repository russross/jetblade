from .. import objectstate
from vector2d import Vector2D

import groundedstate

## This class handles objects that are attacking while on the ground.
# Possible transitions:
# Complete attack animation -> GroundedState
class GroundedAttackState(objectstate.ObjectState):
    def __init__(self, owner, attackName):
        self.owner = owner
        self.name = attackName
        self.owner.sprite.setAnimation(self.name)
        self.owner.vel = Vector2D(0, 0)
        self.owner.isGravityOn = False


    def completeAnimation(self, animation):
        self.owner.isGravityOn = True
        self.owner.setState(groundedstate.GroundedState(self.owner))
