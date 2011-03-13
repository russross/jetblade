import straight
import util
from vector2d import Vector2D

import random

## Size of rooms in comparison to width of tunnels.
roomSizeMultiplier = 1.6

def getClassName():
    return 'Room'

class Room(straight.StraightTunnel):
    ## Just like carving a straight tunnel, except we create a big 
    # open space in the middle of the tunnel.
    def carveTunnel(self):
        straight.StraightTunnel.carveTunnel(self)

        start = self.sector.start.loc
        end = self.sector.end.loc
        distance = end.distance(start)
        delta = end.sub(start).normalize().multiply(distance/4.0)
        
        center = start.average(end)
        size = self.sector.getTunnelWidth() * roomSizeMultiplier

        self.map.plantSeed(center, self.sector, size)
        self.map.plantSeed(center.add(delta), self.sector, size)
        self.map.plantSeed(center.sub(delta), self.sector, size)


    def shouldCheckAccessibility(self):
        return True

