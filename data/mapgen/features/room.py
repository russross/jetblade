import straight
import util
import random

## @package room Just like carving a straight tunnel, except we create a big 
# open space in the middle of the tunnel.
def carveTunnel(map, sector):
    straight.carveTunnel(map, sector)

    start = sector.parent.loc
    end = sector.loc
    
    center = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
    (dx, dy) = util.getNormalizedVector(start, end)
    distance = util.pointPointDistance(start, end)

    size = sector.getRoomSize()
    map.plantSeed(center, sector, size)
    map.plantSeed([center[0] + dx*distance/4.0, center[1] + dy*distance/4.0], sector, size)
    map.plantSeed([center[0] - dx*distance/4.0, center[1] - dy*distance/4.0], sector, size)

def createFeature(map, sector):
    pass

def shouldCheckAccessibility(sector):
    return True

