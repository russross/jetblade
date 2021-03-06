import logger
import sprite

import os
import random

## Blocks are solid, nonmoving bits of terrain. 
class Block:

    ## Create a new Block instance.
    def __init__(self, gridLoc, terrain, orientation, subType = None):

        ## Location in gridspace
        self.gridLoc = gridLoc

        ## Location in realspace
        self.loc = gridLoc.toRealspace()

        ## There are currently 20 different block orientations, most of which
        # have a square collision polygon.
        self.orientation = orientation

        ## TerrainInfo instance to let the block know what it looks like.
        self.terrain = terrain

        imagePath = os.path.join('terrain', self.terrain.zone, 
                                 self.terrain.region, 'blocks')
        ## To allow blocks to be animated, we use Sprites for drawing them.
        self.sprite = sprite.Sprite(imagePath, self, self.loc, False)
        self.sprite.setAnimation(self.orientation, False)
        ## Purely graphical variation on the block.
        self.subType = subType
        if self.subType is None:
            anim = self.sprite.getCurrentAnimationObject()
            self.subType = random.choice(range(0, len(anim.frames) + 1))

        ## Bounding rect
        self.rect = self.sprite.getBounds(self.loc)


    ## Return an identical copy of us.
    def copy(self, gridLoc = None):
        if gridLoc is None:
            gridLoc = self.gridLoc
        return Block(gridLoc, self.terrain, self.orientation, self.subType)


    ## Update our positional information.
    def moveTo(self, newRealspaceLoc):
        self.loc = newRealspaceLoc
        self.gridLoc = newRealspaceLoc.toGridspace()
        self.rect = self.sprite.getBounds(self.loc)


    ## Return the location of the vertex in the block's polygon that is 
    # furthest in the given direction.
    def getBlockCorner(self, direction):
        poly = self.sprite.getPolygon()
        targetX = poly.lowerRight.x
        if direction.x < 0:
            targetX = poly.upperLeft.x
        return self.loc.add(poly.getPointAtX(targetX, direction.y))


    ## Draw the block. Ignore the "progress" parameter because we use 
    # animation frames for block variants.
    def draw(self, progress):
        # \todo This is a hacky way to force display of the proper frame.
        anim = self.sprite.getCurrentAnimationObject()
        anim.frame = self.subType
        anim.prevFrame = self.subType
        self.sprite.draw(0, self.loc)


    ## Perform collision detection against an incoming polygon.
    def collidePolygon(self, polygon, loc):
        return self.sprite.getPolygon().runSAT(self.loc, polygon, loc)


    ## Return the bounding polygon
    def getPolygon(self):
        return self.sprite.getPolygon()


    ## Get our bounding rectangle. We assume that blocks don't move once 
    # created, so their bounding rectangles are fixed.
    def getBounds(self):
        return self.rect


    ## Get our specific frame of "animation"
    def getFrame(self):
        return self.sprite.getCurrentAnimationObject().getFrame()


    ## Convert to string for output
    def __str__(self):
        return ("[Block at " + str(self.gridLoc) + " realspace " + 
                str(self.loc) + " orientation " + str(self.orientation) + 
                " type " + str(self.terrain) + "]")

