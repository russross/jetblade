import logger
import sprite

## Blocks are solid, nonmoving bits of terrain. 
class Block:

    ## Create a new Block instance.
    def __init__(self, loc, orientation, adjacencySignature, terrain):

        ## Location in realspace
        self.loc = loc

        ## Location in gridspace
        self.gridLoc = self.loc.toGridspace()

        ## There are currently 20 different block orientations, most of which
        # have a square collision polygon.
        self.orientation = orientation

        ## Adjacency signatures are a short way of indicating which of the 8
        # neighboring spaces are occupied by blocks. 
        self.adjacencySignature = adjacencySignature

        ## TerrainInfo instance to let the block know what it looks like.
        self.terrain = terrain

        imagePath = 'terrain/' + self.terrain.zone + '/' + self.terrain.region + '/blocks'
        ## To allow blocks to be animated, we use Sprites for drawing them.
        self.sprite = sprite.Sprite(imagePath, self, self.loc, False)
        self.sprite.setAnimation(self.orientation, False)

        ## Bounding rect
        self.rect = self.sprite.getBounds(self.loc)


    ## Return the location of the vertex in the block's polygon that is 
    # furthest in the given direction.
    def getBlockCorner(self, direction):
        poly = self.sprite.getPolygon()
        targetX = poly.lowerRight.x
        if direction.x < 0:
            targetX = poly.upperLeft.x
        return self.loc.add(poly.getPointAtX(targetX, direction.y))


    ## Draw the block.
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, self.loc, scale)


    ## Perform collision detection against an incoming polygon.
    def collidePolygon(self, polygon, loc):
        return self.sprite.getPolygon().runSAT(self.loc, polygon, loc)


    ## Return the bounding polygon
    def getPolygon(self):
        return self.sprite.getPolygon()


    ## Get our bounding polygon. We assume that blocks don't move once created,
    # so their bounding rectangles are fixed.
    def getBounds(self):
        return self.rect


    ## Return a scalar indicating which spaces adjacent to this block are 
    # occupied.
    def getAdjacencySignature(self):
        return self.adjacencySignature


    ## Convert to string for output
    def __str__(self):
        return "Block at " + str(self.gridLoc) + " realspace " + str(self.loc) + " orientation " + str(self.orientation) + " type " + str(self.terrain)

