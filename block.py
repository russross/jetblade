import util
import sprite

## These block types do not have square polygons. HACK; ideally we wouldn't
# need this.
nonSquareBlockOrientations = ['upleft', 'upright', 'downleft', 'downright']

## Blocks are solid, nonmoving bits of terrain. 
class Block:

    ## Create a new Block instance.
    def __init__(self, loc, orientation, adjacencySignature, terrain, flavor):

        ## Location in realspace
        self.loc = loc

        ## Location in gridspace
        self.gridLoc = util.realspaceToGridspace(self.loc)

        ## There are currently 20 different block orientations, most of which
        # have a square collision polygon.
        self.orientation = orientation

        ## Adjacency signatures are a short way of indicating which of the 8
        # neighboring spaces are occupied by blocks. 
        self.adjacencySignature = adjacencySignature

        ## Which large-scale grouping this block falls into, e.g. "jungle " or
        # "hotzone".
        self.terrain = terrain

        ## The specific sub-type of terrain, e.g. "grass", or "lava".
        self.flavor = flavor
        
        imagePath = 'terrain/' + self.terrain + '/' + self.flavor + '/blocks'
        ## To allow blocks to be animated, we use Sprites for drawing them.
        self.sprite = sprite.Sprite(imagePath, self)
        self.sprite.setAnimation(self.orientation, False)


    ## Get the location of the top of the block on the edge in the given 
    # direction (-1: left, 1: right)
    def getBlockTop(self, direction):
        poly = self.sprite.getPolygon()
        targetX = poly.lowerRight[0]
        if direction < 0:
            targetX = poly.upperLeft[0]
        return util.addVectors(self.loc, poly.getPointAtX(targetX, -1))


    ## As getBlockTop, but for the bottom of the block
    def getBlockBottom(self, direction):
        poly = self.sprite.getPolygon()
        targetX = poly.lowerRight[0]
        if direction < 0:
            targetX = poly.upperLeft[0]
        return util.addVectors(self.loc, poly.getPointAtX(targetX, 1))
        

    ## Draw the block.
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, scale)


    ## Perform collision detection against an incoming polygon.
    def collidePolygon(self, polygon, loc):
        return self.sprite.collidePolygon(polygon, loc)


    ## Return a scalar indicating which spaces adjacent to this block are 
    # occupied.
    def getAdjacencySignature(self):
        return self.adjacencySignature


    ## Convert to string for output
    def __str__(self):
        return "Block at " + str(self.gridLoc) + " realspace " + str(self.loc) + " orientation " + str(self.orientation) + " type " + str(self.terrain) + " " + str(self.flavor)

