import constants
import copy
import math

def getClassName():
    return 'StraightTunnel'

## The basic tunnel type -- a straight tunnel from point A to point B.
class StraightTunnel:
    def __init__(self, map, sector):
        self.map = map
        self.sector = sector

    ## Lay down seeds for Map.expandSeeds -- in other words, we mark a point 
    # on the map and say "At this point, I want the distance to the walls to 
    # be X in all directions", and the map will try to accomodate all these 
    # requests to the best of its ability.
    # In this specific case, we simply lay down a set of seeds along the line 
    # connecting the sector to its parent, with each seed having the same 
    # radius.
    def carveTunnel(self):
        start = self.sector.parent.loc
        end = self.sector.loc
        
        # Proceed along the line from start to end, clearing out 
        # blocks that are too close to that line.
        dy = end[1] - start[1]
        dx = end[0] - start[0]
        if abs(dx) < constants.EPSILON:
            # This algorithm doesn't handle verticals well, so use a different
            # one.
            self.carveVerticalTunnel()
            return

        width = self.sector.getTunnelWidth()
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
            self.map.plantSeed(currentLoc, self.sector, width)
            currentLoc = [currentLoc[0] + blockDx, currentLoc[1] + blockDy]


    ## As carveTunnel, but only for vertical situations. 
    def carveVerticalTunnel(self):
        start = self.sector.parent.loc
        end = self.sector.loc
        width = self.sector.getTunnelWidth()

        currentLoc = [start[0], start[1]]
        endLoc = [end[0], end[1]]
        if currentLoc[1] > end[1]:
            tmp = currentLoc
            currentLoc = endLoc
            endLoc = tmp

        while currentLoc[1] < endLoc[1]:
            self.map.plantSeed(currentLoc, self.sector, width)
            currentLoc[1] += 1

    ## Perform any extra actions needed to flesh out the tunnel.
    def createFeature(self):
        pass


    ## Return true if it's necessary to check the tunnel for accessibility.
    def shouldCheckAccessibility(self, minSlope = 2):
        return abs(self.sector.getSlope()) > minSlope

