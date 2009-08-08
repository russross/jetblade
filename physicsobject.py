import sprite
import constants
import logger
import game
import collisiondata
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
defaultGravity = Vector2D(0, 0)
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
        ## Unique object ID
        self.id = constants.globalId
        constants.globalId += 1
        ## Name of object, used to look up the sprite.
        self.name = name
        ## Location of the object
        self.loc = loc
        ## Current velocity of the object
        self.vel = Vector2D(0, 0)
        ## True if gravity should be applied during the update cycle.
        self.isGravityOn = True
        ## Acceleration due to gravity, added to self.vel each update cycle.
        self.gravity = defaultGravity.copy()
        ## Maximum velocity in X and Y directions (handled separately)
        self.maxVel = defaultMaxVel.copy()
        ## Direction object is facing (1: right, -1: left)
        self.facing = 1
        ## Sprite for animations and bounding polygons
        self.sprite = sprite.Sprite(name, self, self.loc)
        ## List of collisions received since the last update cycle.
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
        self.checkTerrain()
        self.postCollisionUpdate()
        self.sprite.update(self.loc)
        return True


    ## Make whatever state changes the AI/player control calls for.
    def AIUpdate(self):
        pass


    ## Called right before self.handleCollisions(), to prepare.
    def preCollisionUpdate(self):
        pass


    ## Called after self.handleCollisions(), to do any necessary cleanup.
    def postCollisionUpdate(self):
        pass


    ## React to colliding with terrain by killing velocity and backing out
    # until we are not intersecting again.
    def checkTerrain(self):
        self.collisions = []
        collision = game.map.collidePolygon(self.sprite.getPolygon(), self.loc)
        numTries = 0
        while collision.vector is not None and numTries < maxCollisionRetries:
            numTries += 1
            self.processCollision(collision)
            collision = game.map.collidePolygon(self.sprite.getPolygon(), self.loc)
        if numTries == maxCollisionRetries:
            # We got stuck in a loop somehow. Eject upwards.
            self.loc = self.loc.add(zipAmount)


    ## Hit a non-terrain object. 
    def hitObject(self, alt):
        (overlap, vector) = alt.getPolygon().runSAT(alt.loc,
                                                    self.getPolygon(), self.loc)
        if vector is not None:
            collision = collisiondata.CollisionData(vector, overlap, alt.name, alt)
            logger.debug("Object",self.id,"at",self.loc,"hit",alt.id,"at", 
                         alt.loc,":",collision)
            self.processCollision(collision)


    ## Handle running into something.
    # Use self.adjustCollision() to modify ejection vectors and distances;
    # use self.hit[Floor|Wall|Ceiling] to react to running into terrain of 
    # those types.
    # \todo Currently assumes all collisions are with terrain.
    def processCollision(self, collision):
        collision = self.adjustCollision(collision)
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
            self.loc = self.loc.add(collision.vector.multiply(collision.distance))



    ## Perform any necessary tweaks to the collision vector or distance.
    def adjustCollision(self, collision):
        return collision


    ## React to hitting any terrain.
    def hitTerrain(self, collision):
        return True


    ## React to hitting a wall.
    def hitWall(self, collision):
        self.vel = Vector2D(0, self.vel.y)
        return True


    ## React to hitting the ceiling
    def hitCeiling(self, collision):
        self.vel = Vector2D(self.vel.x, 0)
        return True


    ## React to hitting the floor.
    def hitFloor(self, collision):
        self.vel = Vector2D(self.vel.x, 0)
        return True


    ## Passthrough to Sprite.draw()
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, None, scale)


    ## Passthrough to Sprite.getDrawLoc()
    def getDrawLoc(self, progress):
        return self.sprite.getDrawLoc(progress)


    ## Passthrough to Sprite.getBounds()
    def getBounds(self):
        return self.sprite.getBounds(self.loc)


    ## Passthrough to Sprite.getPolygon()
    def getPolygon(self):
        return self.sprite.getPolygon(self.loc)


    ## Return a string representing the facing of the object
    def getFacingString(self):
        if self.facing < 0:
            return 'l'
        return 'r'

    ## Handle completion of animations.
    def completeAnimation(self, animation):
        self.loc = self.loc.add(animation.getMoveOffset())
        return self.loc

