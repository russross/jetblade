import constants
import objectstate
import game
from vector2d import Vector2D

import jumpingstate
import crawlingstate
import fallingstate

## This class handles objects that are standing on the ground.
# Possible transitions: 
# Jump -> JumpingState
# Crawl -> CrawlingState
# Fall off of terrain -> FallingState
class GroundedState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'grounded'
        self.owner = owner
        self.isGrounded = True
        self.owner.sprite.setAnimation('idle')


    ## Check input for state transitions; perform them if the terrain allows.
    def preCollisionUpdate(self):
        if self.owner.shouldCrawl:
            # Check if there's room to crawl
            crawlPolygon = self.owner.getPolygonForAnimation('crawl')
            crawlCollision = game.map.collidePolygon(crawlPolygon, self.owner.loc)
            if crawlCollision is not None:
                # See if pushing us away from the offending wall would give us
                # room to crawl.
                offset = crawlCollision.vector.multiply(crawlCollision.distance)
                crawlCollision = game.map.collidePolygon(crawlPolygon, self.owner.loc.add(offset))
            if crawlCollision is None:
                # There's room to crawl.
                self.owner.setState(crawlingstate.CrawlingState(self.owner))
                return
        elif self.owner.shouldJump:
            self.owner.setState(jumpingstate.JumpingState(self.owner))
            return
        self.owner.applyMovement(self.owner.runAcceleration, self.owner.runDeceleration)
        if abs(self.owner.vel.x) > constants.EPSILON:
            if self.owner.runDirection == self.owner.facing:
                self.owner.sprite.setAnimation('run')
            else:
                self.owner.sprite.setAnimation('runstop')
        elif not self.owner.runDirection:
            self.owner.sprite.setAnimation('idle')
        # By unsetting self.isGrounded right before the update, we'll know 
        # if we're still on the ground after the end (because hitFloor sets
        # self.isGrounded).
        self.isGrounded = False


    ## Adjust collisions. Since we're on the ground, we need to fix the 
    # toe-stubbing problem.
    def adjustCollision(self, collision):
        return self.owner.adjustFootCollision(collision)


    ## Hit a floor. Reset self.isGrounded.
    def hitFloor(self, collision):
        self.isGrounded = True
        return True


    ## Hit a ceiling. Transition to a crawling animation.
    def hitCeiling(self, collision):
        self.owner.setState(crawlingstate.CrawlingState(self.owner))
        return True


    ## Update state after all collisions are done. Check to see if we ran out
    # of ground.
    def postCollisionUpdate(self):
        if not self.isGrounded:
            # Ran out of ground. Either we start falling, or we look for a 
            # block below us and try to hug it. 
            footLoc = self.owner.getFootLoc(True) # Get rear foot location
            belowLoc = footLoc.addY(abs(self.owner.vel.x) + 1)
            if (game.map.getBlockAtGridLoc(footLoc.toGridspace()) or
                    game.map.getBlockAtGridLoc(belowLoc.toGridspace())):
                # Either rear foot is already in the same space as a block, 
                # or there's a block there if we move down a bit.
                self.owner.loc = self.owner.loc.addY(abs(self.owner.vel.x) + 1)
                self.isGrounded = True
                game.gameObjectManager.checkObjectAgainstTerrain(self.owner)
            else:
                # Start freefall
                self.owner.setState(fallingstate.FallingState(self.owner))

