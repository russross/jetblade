import sprite
import constants
import jetblade
import util

## Magnitude of the horizontal portion of a normalized vector, past which we 
# consider the vector to be the normal of a wall.
wallHorizontalVectorComponent = .8
## Maximum attempts to disentangle an object from a wall before we give up 
# and start zipping it.
maxCollisionRetries = 15
## Distance to zip if we fail to pull an object out of the terrain.
zipAmount = constants.blockSize

## Default acceleration due to gravity, in X and Y directions
defaultGravity = (0, 2)
## Default maximum velocity, in X and Y directions
defaultMaxVel = (20, 30)

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
        self.vel = [0, 0]
        self.isGravityOn = True
        self.gravity = list(defaultGravity)
        self.maxVel = list(defaultMaxVel)
        self.facing = 1
        self.sprite = sprite.Sprite(name, self)
        self.collisionVectors = []


    ## Apply gravity to velocity and velocity to location, then run collision
    # detection.
    def update(self):
        self.AIUpdate()
        self.preCollisionUpdate()
        if self.isGravityOn:
            self.vel = util.clampVector(util.addVectors(self.vel, self.gravity), self.maxVel)
        self.loc = util.addVectors(self.loc, self.vel)
        self.handleCollisions()
        self.postCollisionUpdate()
        self.sprite.update()


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
        self.collisionVectors = []
        (distance, vector, block) = jetblade.map.collidePolygon(self.sprite.getPolygon(), self.loc)
        numTries = 0
        while vector is not None and numTries < maxCollisionRetries:
            numTries += 1

            (vector, distance) = self.adjustCollision(block, vector, distance)
            util.debug("Collision modified to",(distance, vector))
            util.debug("Block at",block.loc,"has polygon",block.sprite.getPolygon())
            self.collisionVectors.append(vector)

            shouldReactToCollision = self.hitTerrain(block, vector, distance)
            if vector[1] > constants.EPSILON:
                if not self.hitCeiling(block, vector, distance):
                    shouldReactToCollision = False
            elif vector[1] < -constants.EPSILON:
                if not self.hitFloor(block, vector, distance):
                    shouldReactToCollision = False

            # Hit a wall
            if (abs(vector[0]) > wallHorizontalVectorComponent and
                    cmp(self.vel[0], 0) != cmp(vector[0], 0)):
                if not self.hitWall(block, vector, distance):
                    shouldReactToCollision = False

            if shouldReactToCollision:
                util.debug("Updating location from",self.loc,)
                self.loc[0] += vector[0] * distance
                self.loc[1] += vector[1] * distance
                util.debug("to",self.loc)
            else:
                util.debug("Told to ignore collision")

            (distance, vector, block) = jetblade.map.collidePolygon(self.sprite.getPolygon(), self.loc)
            util.debug("Retry collision data is",distance,vector,block)
        if numTries == maxCollisionRetries:
            # We got stuck in a loop somehow. Eject upwards.
            util.debug("Hit a collision loop. Whoops.")
            self.loc[1] -= zipAmount


    ## Perform any necessary tweaks to the collision vector or distance.
    def adjustCollision(self, block, vector, distance):
        return (vector, distance)


    ## React to hitting any terrain.
    def hitTerrain(self, block, vector, distance):
        util.debug("Object",self.name,"hit terrain at",block.gridLoc)
        return True


    ## React to hitting a wall.
    def hitWall(self, block, vector, distance):
        util.debug("Object",self.name,"hit wall at",block.gridLoc)
        self.vel[0] = 0
        return True


    ## React to hitting the ceiling
    def hitCeiling(self, block, vector, distance):
        util.debug("Object",self.name,"hit ceiling at",block.gridLoc)
        self.vel[1] = 0
        return True


    ## React to hitting the floor.
    def hitFloor(self, block, vector, distance):
        util.debug("Object",self.name,"hit floor at",block.gridLoc)
        self.vel[1] = 0
        return True


    ## Passthrough to Sprite.draw()
    def draw(self, screen, camera, progress):
        util.debug("Drawing",self.name,"at",self.getDrawLoc(progress),"from",self.sprite.prevLoc,"and",self.sprite.curLoc)
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

