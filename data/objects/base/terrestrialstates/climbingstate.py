import objectstate
from vector2d import Vector2D

import crawlingstate

## This class handles objects that are climbing up from a ledge.
# Possible transitions: 
# Finish climb -> CrawlingState
class ClimbingState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'climb'
        self.owner = owner
        self.owner.sprite.setAnimation('climb')


    ## Finish the climbing animation.
    def completeAnimation(self, animation):
        action = animation.name[:-2]
        if action == 'climb':
            self.owner.isGravityOn = True
            self.owner.setState(crawlingstate.CrawlingState(self.owner))

