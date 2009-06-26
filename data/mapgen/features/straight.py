import constants
import verticalTunnel
import copy
import math


## @package straight The basic tunnel-carving algorithm. 
# "Carving a tunnel" means laying down
# seeds for Map.expandSeeds -- in other words, we mark a point on the map and
# say "At this point, I want the distance to the walls to be X in all 
# directions", and the map will try to accomodate all these requests to the best
# of its ability.
# In this specific case, we simply lay down a set of seeds along the line 
# connecting the sector to its parent, with each seed having the same radius.
def carveTunnel(map, sector):
    start = sector.parent.loc
    end = sector.loc
    
    # Proceed along the line from start to end, clearing out 
    # blocks that are too close to that line.
    dy = end[1] - start[1]
    dx = end[0] - start[0]
    if abs(dx) < constants.EPSILON:
        # This algorithm doesn't handle verticals well, so use a different
        # one.
        verticalTunnel.carveTunnel(map, sector)
        return

    width = sector.getTunnelWidth()
    slope = dy / float(dx)

    # Always want to be proceeding left-to-right along the line, so
    # adjust sign of slope and endpoints
    currentLoc = copy.copy(start)
    endLoc = copy.copy(end)
    if currentLoc[0] > endLoc[0]:
        tmp = currentLoc
        currentLoc = endLoc
        endLoc = tmp

    magnitude = math.sqrt(1+slope**2)
    blockDx = constants.blockSize / magnitude
    blockDy = constants.blockSize * slope / magnitude
    # Iterate over a series of points blockSize apart along the line.
    while currentLoc[0] < endLoc[0]:
        map.plantSeed(currentLoc, sector, width)
        currentLoc = [currentLoc[0] + blockDx, currentLoc[1] + blockDy]

def createFeature(map, sector):
    pass

def shouldCheckAccessibility(sector):
    return abs(sector.getSlope()) > 2

