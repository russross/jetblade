import straight
import util
import random

def getClassName():
    return 'Room'

class Room(straight.StraightTunnel):
    ## Just like carving a straight tunnel, except we create a big 
    # open space in the middle of the tunnel.
    def carveTunnel(self):
        straight.StraightTunnel.carveTunnel(self)

        start = self.sector.parent.loc
        end = self.sector.loc
        
        center = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
        (dx, dy) = util.getNormalizedVector(start, end)
        distance = util.pointPointDistance(start, end)

        size = self.sector.getRoomSize()
        self.map.plantSeed(center, self.sector, size)
        self.map.plantSeed([center[0] + dx*distance/4.0, center[1] + dy*distance/4.0], self.sector, size)
        self.map.plantSeed([center[0] - dx*distance/4.0, center[1] - dy*distance/4.0], self.sector, size)


    def shouldCheckAccessibility(self):
        return True

