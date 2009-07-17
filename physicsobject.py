import sprite
import constants
import jetblade
import logger
from vector2d import Vector2D

## Magnitude of the horizontal portion of a normalized vector, past which we 
# consider the vector to be the normal of a wall.
wallHorizontalVectorComponent = .8
## Maximum attempts to disentangle an object from a wall before we give up 
# and start zipping it.
maxCollisionRetries = 15
## Distance to zip if we fail to pull an object out of the terrain.
zipAmount = Vector2D(0, -constants.blockSize)

## Default acceleration due to gravity, in X and Y directions
defaultGravity = Vector2D(0, 2)
## Default maximum velocity, in X and Y directions
defaultMaxVel = Vector2D(20, 30)

## PhysicsObject is the base class for objects that need to interact with 
# other objects, like creatures, mechanisms, etc. It handles collision 
# detection and provides a framework for more complex behaviors and AI. 
class PhysicsObject:

    ## Instantiate a new object.
    # \param loc The location in realspace coordinates of the object.
    # \param name The name of the object; also the path to its animations 
    #             (e.g. 'data/images/maleplayer').
    def __init__(self, loc, name):
        self.name = name
        self.loc = loc
        self.vel = Vector2D(0, 0)
        self.isGravityOn = True
        self.gravity = defaultGravity.copy()
        self.maxVel = defaultMaxVel.copy()
        self.facing = 1
        self.sprite = sprite.Sprite(name, self, self.loc)
        self.collisions = []


    ## Apply gravity to velocity and velocity to location, then run collision
    # detection.
    def update(self):
        self.AIUpdate()
        self.preCollisionUpdate()
        if self.isGravityOn:
            self.vel = self.vel.add(self.gravity)
        self.vel = self.vel.clamp(self.maxVel)
        self.loc = self.loc.add(self.vel)
        self.handleCollisions()
        self.postCollisionUpdate()
        self.sprite.update(self.loc)


    ## Make whatever state changes the AI/player control calls for.
    def AIUpdate(self):
        pass


    ## Called right before self.handleCollisions(), to prepare.
    def preCollisionUpdate(self):
        pass


    ## Called after self.handleCollisions(), to do any necessary cleanup.
    def postCollisionUpdate(self):
        pass


    ## React to colliding with objects by killing velocity and backing out
    # until we are not intersecting again.
    # Use self.adjestCollision() to modify ejection vectors and distances;
    # use self.hit[Floor|Wall|Ceiling] to react to running into terrain of 
    # those types.
    # \todo Currently assumes all collisions are with terrain.
    def handleCollisions(self):
        self.collisions = []
        collision = jetblade.map.collidePolygon(self.sprite.getPolygon(), self.loc)
        numTries = 0
        while collision.vector is not None and numTries < maxCollisionRetries:
            numTries += 1

            collision = self.adjustCollision(collision)
            logger.debug("Collision modified to",(collision.vector, collision.distance))
            logger.debug("Hit object",collision.altObject)
            self.collisions.append(collision)

            shouldReactToCollision = self.hitTerrain(collision)
            if collision.vector.y > constants.EPSILON:
                if not self.hitCeiling(collision):
                    shouldReactToCollision = False
            elif collision.vector.y < -constants.EPSILON:
                if not self.hitFloor(collision):
                    shouldReactToCollision = False

            # Hit a wall
            if (abs(collision.vector.x) > wallHorizontalVectorComponent and
                    cmp(self.vel.x, 0) != cmp(collision.vector.x, 0)):
                if not self.hitWall(collision):
                    shouldReactToCollision = False

            if shouldReactToCollision:
                logger.debug("Updating location from",self.loc)
                self.loc = self.loc.add(collision.vector.multiply(collision.distance))
                logger.debug("to",self.loc)
            else:
                logger.debug("Told to ignore collision")

            collision = jetblade.map.collidePolygon(self.sprite.getPolygon(), self.loc)
            logger.debug("Retry collision data is",collision)
        if numTries == maxCollisionRetries:
            # We got stuck in a loop somehow. Eject upwards.
            logger.debug("Hit a collision loop. Whoops.")
            self.loc = self.loc.add(zipAmount)


    ## Perform any necessary tweaks to the collision vector or distance.
    def adjustCollision(self, collision):
        return collision


    ## React to hitting any terrain.
    def hitTerrain(self, collision):
        logger.debug("Object", self.name, "hit terrain at", 
                   collision.altObject.loc.toGridspace())
        return True


    ## React to hitting a wall.
    def hitWall(self, collision):
        logger.debug("Object", self.name, "hit wall at",
                   collision.altObject.loc.toGridspace()) 
        self.vel = Vector2D(0, self.vel.y)
        return True


    ## React to hitting the ceiling
    def hitCeiling(self, collision):
        logger.debug("Object", self.name, "hit ceiling at",
                   collision.altObject.loc.toGridspace()) 
        self.vel = Vector2D(self.vel.x, 0)
        return True


    ## React to hitting the floor.
    def hitFloor(self, collision):
        logger.debug("Object", self.name, "hit floor at",
                   collision.altObject.loc.toGridspace()) 
        self.vel = Vector2D(self.vel.x, 0)
        return True


    ## Passthrough to Sprite.draw()
    def draw(self, screen, camera, progress):
        logger.debug("Drawing",self.name,"at",self.getDrawLoc(progress),"from",self.sprite.prevLoc,"and",self.sprite.curLoc)
        self.sprite.draw(screen, camera, progress)


    ## Passthrough to Sprite.getDrawLoc()
    def getDrawLoc(self, progress):
        return self.sprite.getDrawLoc(progress)


    ## Return a string representing the facing of the object
    def getFacingString(self):
        if self.facing < 0:
            return 'l'
        return 'r'

    ## Handle completion of animations.
    def completeAnimation(self):
        pass

