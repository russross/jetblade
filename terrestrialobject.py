import physicsobject
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
## Default gravity
defaultGravity = Vector2D(0, 2)
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
        self.gravity = defaultGravity
        ## When grounded, we apply running acceleration, can jump, and
        # can crouch if the creature has that ability.
        self.isGrounded = True
        ## Used when checking for the floor during collision detection. True
        # if, before collision detection, the creature was grounded.
        self.wasGrounded = True
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
        ## Used to signal that the creature has started a jump. Set this in 
        # your AI routines to jump.
        self.justJumped = False
        ## Vertical speed at the start of a jump.
        self.jumpSpeed = defaultJumpSpeed
        ## Number of frames that the jump action has been "held". Holding the 
        # jump action negates gravity so that jump height can be controlled.
        self.jumpFrames = None
        ## Maximum number of frames that gravity can be negated by holding the
        # jump action.
        self.maxJumpRiseFrames = defaultMaxJumpRiseFrames
        ## Signals if the creature has the ability to hang from ledges. 
        self.canHang = defaultCanHang
        ## Used when the creature is hanging from a ledge. Negates gravity
        # and limits available controls.
        self.isHanging = False
        ## Used to signal that the creature has stopped hanging.
        self.justStoppedHanging = False
        ## Used to signal that the creature has started climbing from a hanging
        # position.
        self.justStartedClimbing = False
        ## Used to signal that the creature should try to crawl.
        self.shouldCrawl = False
        ## Indicates that the creature is currently crawling.
        self.isCrawling = False
        ## Indicates if the creature was crawling on the previous frame. Used
        # to detect when there's no room to crawl (or no room to stand).
        self.wasCrawling = False
        ## Direction creature is trying to move in. Set this to -1 to move
        # left, 0 to not move, or 1 to move right.
        self.runDirection = -1
        ## Indicates that we've already tried changing the player's current
        # action this frame. This is used when "trying out" different actions
        # to see if there's room e.g. to stand up from a crawl. 
        # \todo Seems like there should be a better way to handle this.
        self.haveChangedAction = False


    ## Apply acceleration if the creature is moving; start jumps and negate 
    # gravity as needed if the creature is in the air.
    def preCollisionUpdate(self):
#        logger.debug("At beginning of update, loc is",self.loc,"and vel",self.vel,"and action",self.sprite.getCurrentAnimation(False))
        # We need to start out with self.jumpFrames = self.maxJumpRiseFrames
        # but can't do this in the constructor because inheritors from this
        # code might override self.maxJumpRiseFrames.
        if self.jumpFrames is None:
            self.jumpFrames = self.maxJumpRiseFrames

        # Update crawling state.
        self.wasCrawling = self.isCrawling
        if self.shouldCrawl and not self.isCrawling:
            self.isCrawling = True
            self.sprite.setAnimation('crawl', True, False)
        elif not self.shouldCrawl and self.isCrawling:
            self.isCrawling = False
            logger.debug("Standing from a crawl")
            self.sprite.setAnimation('idle', True, False)

        if not self.isHanging and not self.wasCrawling:
            # Apply horizontal acceleration or deceleration as needed.
            accelFactor = 1
            accelDirection = self.getAccelDirection()
            if (self.runDirection and 
                    (accelDirection == self.facing or 
                     abs(self.vel.x) < constants.EPSILON)):
                # Accelerate
                if self.isGrounded:
                    accelFactor = self.runAcceleration
                else:
                    accelFactor = self.airAcceleration
            else:
                # Decelerate
                if self.isGrounded:
                    accelFactor = self.runDeceleration
                else:
                    accelFactor = self.airDeceleration
                if abs(accelFactor) > abs(self.vel.x):
                    accelFactor = abs(self.vel.x)
            self.vel = self.vel.addX(accelDirection * accelFactor)
        elif self.wasCrawling:
            if self.runDirection == self.facing:
                self.vel = self.vel.setX(self.crawlSpeed * self.runDirection)
            else:
                # No inertia while crawling.
                self.vel = self.vel.setX(0)

        if abs(self.vel.x) > constants.EPSILON:
            # This conditional ensures that we do not reset the creature's
            # facing when they come to a stop but do not turn around.
            self.facing = cmp(self.vel.x, 0)


        if self.justJumped and self.jumpFrames <= self.maxJumpRiseFrames and not self.isCrawling:
            if self.isGrounded or self.isHanging:
                # Commence a jump
                logger.debug("Commencing jump")
                self.isGrounded = False
                self.isHanging = False
                self.vel = self.vel.setY(self.jumpSpeed)
                self.jumpFrames = 0
                self.isGravityOn = False
                if self.isHanging or abs(self.vel.x) < constants.EPSILON:
                    self.sprite.setAnimation('standjump')
                else:
                    self.sprite.setAnimation('jump')
            else:
                # Still in the rising phase of the jump
#                logger.debug("Going up")
                self.jumpFrames += 1
        elif not self.isHanging:
            self.isGravityOn = True
            if not self.isGrounded and self.vel.y > 0:
                # In the air, but we can't keep rising. Make us fall.
                if self.sprite.getCurrentAnimation() in ['standjump', 'standfall']:
                    self.sprite.setAnimation('standfall')
                else:
                    self.sprite.setAnimation('fall')

        if self.isHanging:
            if self.justStartedClimbing:
                self.sprite.setAnimation('climb')
            elif self.justStoppedHanging:
                self.isHanging = False
                self.isGravityOn = True
                self.sprite.setAnimation('standfall')

        self.justJumped = False
        self.justStartedClimbing = False
        self.justStoppedHanging = False
        self.haveChangedAction = False
        
        # By unsetting self.isGrounded right before the update, we'll know if
        # we're still on the ground after the end (because hitFloor sets
        # self.isGrounded).
        self.wasGrounded = self.isGrounded
        self.isGrounded = False

    
    ## Handle updating the creature's state after collision detection is done.
    # Enter freefall if we didn't hit a floor; set sprite animations.
    def postCollisionUpdate(self):
        if not self.isGrounded and self.wasGrounded:
            # Ran out of ground. Either we start falling, or we look for a 
            # block below us and try to hug it. 
            footLoc = self.getFootLoc(True) # Get rear foot location
            belowLoc = footLoc.addY(abs(self.vel.x) + 1)
            if (game.map.getBlockAtGridLoc(footLoc.toGridspace()) or
                    game.map.getBlockAtGridLoc(belowLoc.toGridspace())):
                # Either rear foot is already in the same space as a block, 
                # or there's a block there if we move down a bit.
#                logger.debug("Pushing self down to hug the ground")
                self.loc = self.loc.addY(abs(self.vel.x) + 1)
                self.isGrounded = True
                game.gameObjectManager.checkObjectAgainstTerrain(self)
            else:
                ## Commence freefall
#                logger.debug("Ran out of ground; commencing freefall")
                self.jumpFrames = self.maxJumpRiseFrames
                oldTop = self.getHeadLoc()
                self.sprite.setAnimation('fall')
                if self.isCrawling:
                    self.isCrawling = False
                    # Assume that crawling animations have a different "top"
                    # than other animations, and thus we need to move the sprite
                    # down.
                    # \todo This is a fairly nasty hack as it makes assumptions
                    # about the shapes of bounding polygons for various actions.
                    newTop = self.getHeadLoc()
                    self.loc = self.loc.addY(oldTop.y - newTop.y)


        if self.isGrounded:
            if not self.isCrawling:
                accelDirection = self.getAccelDirection()
                if accelDirection == self.facing:
                    self.sprite.setAnimation('run')
                elif abs(self.vel.x) > constants.EPSILON:
                    self.sprite.setAnimation('runstop')
                elif not self.runDirection:
                    self.sprite.setAnimation('idle')
            else: # Crawling
                if self.runDirection:
                    if self.runDirection == self.facing:
                        self.sprite.setAnimation('crawl')
                    else:
                        self.sprite.setAnimation('crawlturn')
                elif self.sprite.getCurrentAnimation() not in ['crawl', 'crawlturn']:
                    self.sprite.setAnimation('crawl')
#        logger.debug("At end of update, loc is",self.loc,"and vel",self.vel,"and action",self.sprite.getCurrentAnimation(True))


    ## Adjust collision detection inputs so that we can properly track the
    # terrain.
    # Note: we use self.wasGrounded instead of self.isGrounded here because 
    # self.isGrounded is invalidated before collision detection starts.
    def adjustCollision(self, collision):
        # Fix the "toe-stubbing" problem (of running horizontally 
        # into a block at foot level) by reversing gravity.
        # Recognize this situation because we're on the ground, getting
        # ejected straight horizontally by a block at foot level that has no
        # block above it.
        if collision.type == 'solid':
            block = collision.altObject
            if (not game.map.getBlockAtGridLoc(block.gridLoc.addY(-1)) and 
                    self.wasGrounded and 
                    abs(collision.vector.y) < constants.EPSILON and
                    self.blockIsAtFootLevel(block)):
                collision.distance = self.gravity.y
                collision.vector = Vector2D(0, -1)

            # Convert sideways displacement into vertical displacement if there
            # is any vertical component, to prevent sliding down slopes.
            # Also lets us slide along ceilings at full speed when jumping.
            if self.wasGrounded and collision.vector.y < -constants.EPSILON:
                collision.vector = Vector2D(0, collision.vector.y +
                        abs(collision.vector.x) * cmp(collision.vector.y, 0))

            # If we just tried to stand up, force all vertical ejection 
            # directions from blocks above our feet to be downwards. 
            # We do this because the act of standing can badly 
            # embed us into a block, causing it to be confused about which 
            # direction we should be ejected in. Without this, we can get 
            # ejected upwards through a block that, last frame, we were 
            # crawling beneath.
            if (self.wasCrawling and not self.shouldCrawl and 
                    collision.vector.y < 0 and 
                    self.getFootLoc().y > block.getBlockCorner(Vector2D(self.facing, 1)).y):
                collision.vector = Vector2D(collision.vector.x, -collision.vector.y)

        return collision


    ## Basic logic for hitting any terrain at all. 
    # The only thing we care about is that if we hit a block with a 
    # non-upwards ejection vector and we're trialling standing, or if we hit 
    # a block with a horizontal ejection vector and we're trialling crawling,
    # then we need to give up on the trial.
    def hitTerrain(self, collision):
        physicsobject.PhysicsObject.hitTerrain(self, collision)
        if self.wasGrounded:
            shouldChangeAction = False
            if (self.shouldCrawl and not self.wasCrawling and
                    abs(collision.vector.x) > 0):
                # Hit a wall when we tried to crouch, so force us to stand
#                logger.debug("Forcing to stand")
                self.isCrawling = False
                shouldChangeAction = True
            elif (not self.shouldCrawl and self.wasCrawling and 
                    collision.vector.y >= 0):
                # Hit our heads on the ceiling or a wall when we tried to 
                # stand, so force a crouch.
#                logger.debug("Forcing into a crawl")
                self.isCrawling = True
                self.wasCrawling = True
                shouldChangeAction = True
            if shouldChangeAction and not self.haveChangedAction:
                self.haveChangedAction = True
                if self.shouldCrawl ^ self.isCrawling:
                    # Tried to crawl, but couldn't because of terrain. Or, 
                    # tried to stand, but couldn't. Revert to our previous 
                    # action.
                    self.sprite.setPreviousAnimation()
                elif collision.vector.y >= 0:
                    self.sprite.setAnimation('crawl')
                else:
                    self.sprite.setAnimation('idle')
                return False
        return True

    ## Hitting the ceiling when jumping forces us to start freefall.
    def hitCeiling(self, collision):
        physicsobject.PhysicsObject.hitCeiling(self, collision)
        if not self.wasGrounded:
#            logger.debug("Bopped our heads while jumping")
            # We were in the middle of rising, so we need to turn gravity back 
            # on.
            self.isGravityOn = True
            self.jumpFrames = self.maxJumpRiseFrames
            if self.sprite.getCurrentAnimation() == 'standjump':
                self.sprite.setAnimation('standfall')
            else:
                self.sprite.setAnimation('fall')
        return True


    ## Hitting the floor makes us grounded.
    def hitFloor(self, collision):
        physicsobject.PhysicsObject.hitFloor(self, collision)
        self.isGrounded = True
        if not self.wasGrounded:
            # Reduce runspeed on landing
            self.vel = self.vel.setX(self.vel.x / 2.0)
        self.jumpFrames = 0
        return True


    ## Hitting the wall makes us stop moving, and may let us hang.
    def hitWall(self, collision):
        physicsobject.PhysicsObject.hitWall(self, collision)
        if self.canHang and self.canGrabLedge():
            # Lock location to the top of the ledge
            # \todo Incorporate some kind of offset here?
            self.loc = self.loc.setY(
                int(
                    (self.loc.y - self.vel.y) / 
                    constants.blockSize + .5
                   ) * constants.blockSize
            )
            self.vel = Vector2D(0, 0)
            self.isHanging = True
            self.jumpFrames = 0
            self.sprite.setAnimation('hang')
            self.isGravityOn = False
        return True


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


    ## Wrap up after finishing a climb.
    def completeAnimation(self, animation):
        action = animation.name[:-2]
        if action == 'climb':
            self.isHanging = False
            self.isCrawling = True
            self.wasCrawling = True
            self.isGrounded = True
            self.isGravityOn = True
            self.sprite.setAnimation('crawl')
            game.soundManager.playSound('player')
        elif action == 'crawlturn':
            self.facing *= -1
            self.sprite.setAnimation('crawl')
        elif self.isGrounded:
            self.sprite.setAnimation('idle')
        return physicsobject.PhysicsObject.completeAnimation(self, animation)


    ## Determine direction of acceleration.
    def getAccelDirection(self):
        accelDirection = self.runDirection
        if (not self.runDirection or 
                (self.runDirection != self.facing and
                 abs(self.vel.x) > constants.EPSILON)):
            accelDirection = -self.facing
#        logger.debug("Accel direction is",accelDirection,"from",self.runDirection,self.facing,self.vel)
        return accelDirection
