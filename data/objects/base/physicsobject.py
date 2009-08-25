import sprite
import constants
import logger
import game
import collisiondata
from vector2d import Vector2D

import objectstate

## Magnitude of the horizontal portion of a normalized vector, past which we 
# consider the vector to be the normal of a wall.
wallHorizontalVectorComponent = .8

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
        ## Faction of object, for use in reacting to collisions
        self.faction = name
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
        ## Controls if we limit self.vel to be less than self.maxVel
        self.shouldApplyVelocityCap = True
        ## Direction object is facing (1: right, -1: left)
        self.facing = 1
        ## Sprite for animations and bounding polygons
        self.sprite = sprite.Sprite(name, self, self.loc)
        ## List of collisions received since the last update cycle.
        self.collisions = []
        ## Damage to do to other objects on contact.
        self.touchDamage = 0
        ## Damage that can be sustained before discorporating
        self.health = constants.BIGNUM
        ## Current state for movement logic
        self.state = objectstate.ObjectState(self)


    ## Set a new state for our movement logic.
    def setState(self, state):
        logger.debug("Setting new state on",self.name,":",state.name)
        self.state = state


    ## Make whatever state changes the AI/player control calls for.
    def AIUpdate(self):
        self.state.AIUpdate()


    ## Apply gravity to velocity and velocity to location.
    def applyPhysics(self):
        if self.isGravityOn:
            self.vel = self.vel.add(self.gravity)
        if self.shouldApplyVelocityCap:
            self.vel = self.vel.clamp(self.maxVel)
        self.loc = self.loc.add(self.vel)


    ## Called right before self.handleCollisions(), to prepare.
    def preCollisionUpdate(self):
        self.state.preCollisionUpdate()


    ## Called after self.handleCollisions(), to do any necessary cleanup.
    def postCollisionUpdate(self):
        self.state.postCollisionUpdate()


    ## Return if we are alive. Returning false here causes the object to be 
    # removed from the game.
    def getIsAlive(self):
        return self.health > 0


    ## Perform any actions required on death, e.g. explosions, dropping items,
    # etc.
    def die(self):
        pass

    
    ## Return true if collisions against the given faction type should be 
    # performed.
    def shouldCollideAgainstFaction(self, faction):
        return True


    ## Hit a non-terrain object. 
    def hitObject(self, alt):
        (overlap, vector) = alt.getPolygon().runSAT(alt.loc,
                                                    self.getPolygon(), self.loc)
        if vector is not None:
            collision = collisiondata.CollisionData(vector, overlap, alt.faction, alt)
            self.processCollision(collision)


    ## Handle running into something.
    # Use self.adjustCollision() to modify ejection vectors and distances;
    # use self.hit[Floor|Wall|Ceiling] to react to running into terrain of 
    # those types.
    def processCollision(self, collision):
        if collision.type == 'solid':
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
        return self.state.adjustCollision(collision)


    ## React to hitting any terrain.
    def hitTerrain(self, collision):
        return self.state.hitTerrain(collision)


    ## React to hitting a wall.
    def hitWall(self, collision):
        logger.debug("Object",self.id,"with velocity",self.vel,"hit a wall")
        self.vel = self.vel.setX(0)
        return self.state.hitWall(collision)


    ## React to hitting the ceiling
    def hitCeiling(self, collision):
        logger.debug("Object",self.id,"with velocity",self.vel,"hit a ceiling")
        self.vel = self.vel.setY(0)
        return self.state.hitCeiling(collision)


    ## React to hitting the floor.
    def hitFloor(self, collision):
        logger.debug("Object",self.id,"with velocity",self.vel,"hit a floor")
        self.vel = self.vel.setY(0)
        return self.state.hitFloor(collision)


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
        return self.sprite.getPolygon()


    ## Passthrough to Sprite.getPolygonForAnimation()
    def getPolygonForAnimation(self, animationName):
        return self.sprite.getPolygonForAnimation(animationName)


    ## Return a string representing the facing of the object
    def getFacingString(self):
        if self.facing < 0:
            return 'l'
        return 'r'

    ## Handle completion of animations.
    def completeAnimation(self, animation):
        self.loc = self.loc.add(animation.getMoveOffset())
        self.state.completeAnimation(animation)
        return self.loc

