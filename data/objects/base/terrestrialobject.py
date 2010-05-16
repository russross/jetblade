import physicsobject
from terrestrialstates import groundedstate
import logger
import constants
import game
import range1d
from vector2d import Vector2D

## Default acceleration to use on the ground
defaultRunAcceleration = 2
## Default deceleration to use on the ground
defaultRunDeceleration = 4
## Default acceleration to use in the air
defaultAirAcceleration = 1
## Default deceleration to use in the air
defaultAirDeceleration = 1
## Default speed when crawling
defaultCrawlSpeed = 3
## Default speed at the start of a jump
defaultJumpSpeed = -20
## Default number of frames that creature can ignore gravity by "holding the 
# jump button" to adjust jump height.
defaultMaxJumpRiseFrames = 10
## Default value for whether the creature can hang from ledges.
defaultCanHang = False


## Terrestrial objects are ones that walk around on the ground and can jump.
# \todo The logic dealing with crawling (and, in particular, forcing crawls
# when there's no headroom) is rather convoluted and should be improved.
class TerrestrialObject(physicsobject.PhysicsObject):
    ## Instantiate a TerrestrialObject
    def __init__(self, loc, name):
        physicsobject.PhysicsObject.__init__(self, loc, name)
        ## Rate at which running (moving while grounded) adds to velocity.
        self.runAcceleration = defaultRunAcceleration
        ## Rate at which slowing to a stop on the ground detracts from velocity.
        self.runDeceleration = defaultRunDeceleration
        ## Rate at which air control (moving while in air) adds to velocity.
        self.airAcceleration = defaultAirAcceleration
        ## Rate at which air control deceleration detracts from velocity.
        self.airDeceleration = defaultAirDeceleration
        ## Speed when crawling (no acceleration)
        self.crawlSpeed = defaultCrawlSpeed
        ## Vertical speed at the start of a jump.
        self.jumpSpeed = defaultJumpSpeed
        ## Speed cap to apply when on the ground
        self.maxGroundVel = self.maxVel.copy()
        ## Speed cap to apply when in the air
        self.maxAirVel = self.maxVel.copy()
        ## Maximum number of frames that gravity can be negated by holding the
        # jump action.
        self.maxJumpRiseFrames = defaultMaxJumpRiseFrames
        ## Whether or not the creature can hang from ledges.
        self.canHang = defaultCanHang
        ## Used to signal that the creature has started a jump. Set this in 
        # your AI routines to jump.
        self.shouldJump = False
        ## Used to signal that the creature has stopped hanging.
        self.shouldReleaseHang = False
        ## Used to signal that the creature has started climbing from a hanging
        # position.
        self.shouldClimb = False
        ## Used to signal that the creature should try to crawl.
        self.shouldCrawl = False
        ## Direction creature is trying to move in. Set this to -1 to move
        # left, 0 to not move, or 1 to move right.
        self.runDirection = -1
        ## ObjectState derivative that handles our movement logic.
        self.state = groundedstate.GroundedState(self)


    ## Update to perform before doing collision detection.
    def preCollisionUpdate(self):
        self.state.preCollisionUpdate()
        self.shouldJump = False
        self.shouldClimb = False
        self.shouldReleaseHang = False
       

    ## Fix the "toe-stubbing" problem (of running horizontally 
    # into a block at foot level) by reversing gravity.
    # Recognize this situation because we're on the ground, getting
    # ejected straight horizontally by a block at foot level that has no
    # block above it.
    def adjustFootCollision(self, collision):
        if collision.type == 'solid':
            block = collision.altObject
            if (not game.map.getBlockAtGridLoc(block.gridLoc.addY(-1)) and
                    abs(collision.vector.y) < constants.EPSILON and
                    self.blockIsAtFootLevel(block)):
                collision.distance = self.gravity.y
                collision.vector = Vector2D(0, -1)

            # Convert sideways displacement into vertical displacement if there
            # is any vertical component, to prevent sliding down slopes.
            if collision.vector.y < -constants.EPSILON:
                collision.vector = Vector2D(0, collision.vector.y +
                        abs(collision.vector.x) * cmp(collision.vector.y, 0))
        return collision


    ## Return true if we are in position to grab the top of a block. We can
    # only grab blocks that do not have other blocks above them. 
    # There are two possible blocks we can grab: the top of a square block, 
    # or the bottom of a triangular one.
    def canGrabLedge(self):
        headLoc = self.getHeadLoc()
        # Round headLoc to the nearest column in the self.facing direction; 
        # this gets us the right column of blocks to try to grab.
        headLoc = headLoc.setX(
            int(
                headLoc.x / constants.blockSize + .5 * self.facing
               ) * constants.blockSize
        )
        headGridLoc = headLoc.toGridspace()
        locs = [headGridLoc.addY(-i) for i in [0, 1, 2]]
        blocks = [game.map.getBlockAtGridLoc(loc) for loc in locs]
        headRange = range1d.Range1D(headLoc.y - self.vel.y, headLoc.y)
#        logger.debug("Head is at",headLoc,"grid",headGridLoc,"range",headRange,"and blocks are",blocks)
        for i in [0, 1]:
            if blocks[i] and not blocks[i+1]:
                top = blocks[i].getBlockCorner(Vector2D(-self.facing, -1))
                if headRange.contains(top.y):
#                    logger.debug("Can grab block",blocks[i],"with top at",top)
                    return True
        return False

    ## Return the "foot" of this object, which is the bottom vertex of the 
    # bounding polygon that is furthest in our direction of travel.
    def getFootLoc(self, shouldUseBack = False):
        return self.getExtremalPoint(self.sprite.getPolygon().lowerRight.y, shouldUseBack)


    ## As getFootLoc, but applies to the top of the object instead of the
    # bottom.
    def getHeadLoc(self, shouldUseBack = False):
        return self.getExtremalPoint(self.sprite.getPolygon().upperLeft.y, shouldUseBack)


    ## Return the point on the polygon that matches the target height and is
    # on the given side.
    def getExtremalPoint(self, targetHeight, shouldUseBack = False):
        direction = self.facing
        if shouldUseBack:
            direction *= -1
        polygon = self.sprite.getPolygon()
        point = polygon.getPointAtHeight(targetHeight, direction)
        return point.add(self.loc)
        

    ## Return true if the given block is near our foot level.
    def blockIsAtFootLevel(self, block):
        footLoc = self.getFootLoc()
        blockTop = block.getBlockCorner(Vector2D(-1 * cmp(self.vel.x, 0), -1))
#        logger.debug("Foot is at",footLoc,"compare block at",blockTop,
#                   "velocity is",self.vel,"distance",footLoc.distance(blockTop),
#                   "magnitude",self.vel.magnitude())
        return footLoc.distance(blockTop) < self.vel.magnitude() + constants.EPSILON


    ## Move according to input, using the provided acceleration or deceleration
    # depending on the direction pressed, our own velocity, and our facing.
    def applyMovement(self, accelFactor, decelFactor):
        accelDirection = self.runDirection
        if (not self.runDirection or
                (self.runDirection != self.facing and
                 abs(self.vel.x) > constants.EPSILON)):
            accelDirection = -self.facing

        velocityMod = None
        if (self.runDirection and
                (accelDirection == self.facing or
                 abs(self.vel.x) < constants.EPSILON)):
            # Accelerate
            velocityMod = accelFactor
        else:
            # Decelerate, coming to a stop if appropriate.
            velocityMod = decelFactor
            if abs(velocityMod) > abs(self.vel.x):
                velocityMod = abs(self.vel.x)
        self.vel = self.vel.addX(accelDirection * velocityMod)
        if abs(self.vel.x) > constants.EPSILON:
            self.facing = cmp(self.vel.x, 0)

