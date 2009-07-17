import constants
from vector2d import Vector2D

import math

## Magnitude of slope past which we use a vertical tunnel algorithm.
verticalTunnelSlopeRequirement = 200

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
    def carveTunnel(self, width = None, start = None, end = None):
        if start is None or end is None:
            start = self.sector.parent.loc
            end = self.sector.loc
        
        delta = end.sub(start)
        slope = delta.slope()
        if abs(slope) > verticalTunnelSlopeRequirement:
            # This algorithm doesn't handle vertical tunnels well, so use a 
            # different one for steeply-sloped tunnels.
            self.carveVerticalTunnel()
            return

        # Always want to be proceeding left-to-right along the line, so
        # adjust sign of slope and endpoints
        currentLoc = start.copy()
        endLoc = end.copy()
        if currentLoc.x > endLoc.x:
            (currentLoc, endLoc) = (endLoc, currentLoc)

        magnitude = math.sqrt(1+slope**2)
        blockDelta = Vector2D(1.0, slope)
        blockDelta.multiply(constants.blockSize / magnitude)
        if width is None:
            width = self.sector.getTunnelWidth()
        if self.sector.id == 232:
            print "Going from",currentLoc,"to",endLoc,"with delta",blockDelta
            print "Slope is",slope,"delta",delta
        # Iterate over a series of points blockSize apart along the line.
        while currentLoc.x < endLoc.x:
            self.map.plantSeed(currentLoc, self.sector, width)
            currentLoc = currentLoc.add(blockDelta)


    ## As carveTunnel, but only for vertical situations. 
    def carveVerticalTunnel(self):
        start = self.sector.parent.loc
        end = self.sector.loc
        width = self.sector.getTunnelWidth()

        currentLoc = start.copy()
        endLoc = end.copy()
        if currentLoc.y > endLoc.y:
            (currentLoc, endLoc) = (endLoc, currentLoc)
        delta = endLoc.sub(currentLoc).normalize().multiply(constants.blockSize)

        while currentLoc.y < endLoc.y:
            self.map.plantSeed(currentLoc, self.sector, width)
            currentLoc = currentLoc.add(delta)

    ## Perform any extra actions needed to flesh out the tunnel.
    def createFeature(self):
        pass


    ## Return true if it's necessary to check the tunnel for accessibility.
    def shouldCheckAccessibility(self, minSlope = 2):
        return abs(self.sector.getSlope()) > minSlope

