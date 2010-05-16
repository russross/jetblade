import objectstate
import game
import logger

import jumpingstate
import groundedstate
import fallingstate

## This class handles objects that are crawling on the ground. It's very similar
# to GroundedState except that you can't jump and your movement speed is fixed.
# Possible transitions: 
# Release crawl -> GroundedState
# Fall off of terrain -> FallingState
class CrawlingState(objectstate.ObjectState):
    def __init__(self, owner):
        self.name = 'crawl'
        self.owner = owner
        self.isGrounded = True
        self.owner.sprite.setAnimation('crawl')
        self.owner.maxVel = self.owner.maxGroundVel


    ## Check input for state transitions; perform them if the terrain allows.
    def preCollisionUpdate(self):
        if not self.owner.shouldCrawl:
            # Check if there's room to stand.
            standingPolygon = self.owner.getPolygonForAnimation('idle')
            standingCollision = game.map.collidePolygon(standingPolygon, self.owner.loc)
            if standingCollision is None:
                self.owner.setState(groundedstate.GroundedState(self.owner))
                return
            else:
                logger.debug("No room to stand")
        if (self.owner.facing == self.owner.runDirection and 
                self.owner.sprite.getCurrentAnimation() != 'crawlturn'):
            self.owner.sprite.setAnimation('crawl')
            self.owner.vel = self.owner.vel.setX(self.owner.crawlSpeed * self.owner.runDirection)
        else:
            self.owner.vel = self.owner.vel.setX(0)
            if self.owner.runDirection:
                self.owner.sprite.setAnimation('crawlturn')
        # By unsetting self.isGrounded right before the update, we'll know if
        # we're still on the ground after the end (because hitFloor sets
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


    ## Hit a ceiling. This should not be possible under ordinary circumstances.
    # Treat it as a wall on the assumption that we've run into a narrowing
    # tunnel.
    def hitCeiling(self, collision):
        self.owner.vel = self.owner.vel.setX(0)
        return True


    ## Update state after all collisions are done. Check to see if we ran out
    # of ground.
    # \todo This is duplicated code (compare GroundedState's version).
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


    ## Complete an animation. The only relevant one is crawlturn.
    def completeAnimation(self, animation):
        action = animation.name[:-2]
        if action == 'crawlturn':
            if animation.getCompletedSuccessfully():
                self.owner.facing *= -1
            self.owner.sprite.setAnimation('crawl')

