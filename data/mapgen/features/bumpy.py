import straight
import util
from vector2d import Vector2D

import math
import random

def getClassName():
    return 'BumpyTunnel'

## Number of subsegments of the tunnel to create
bumpyTunnelNumSubtunnels = 8
## Degree to which a single tunnel can vary in direction from the previous.
# Making this higher allows for bumpier tunnels, but making it too high can
# cause the tunnel to interfere with other tunnels and create inaccessible maps.
bumpyTunnelDirectionVariance = math.pi / 12.0

class BumpyTunnel(straight.StraightTunnel):
    ## Create a series of short tunnel segments connecting the 
    # start and ends of the sector.
    def carveTunnel(self):
        start = self.sector.start.loc
        end = self.sector.end.loc
        totalDist = start.distance(end)
        directionVector = end.sub(start).normalize()
        totalDirection = math.atan2(directionVector.y, directionVector.x)
        tunnelDist = totalDist / bumpyTunnelNumSubtunnels
        currentLoc = start
        for i in range(0, bumpyTunnelNumSubtunnels):
            width = self.sector.getTunnelWidth()
            if i == bumpyTunnelNumSubtunnels - 1:
                straight.StraightTunnel.carveTunnel(self, width, 
                                                    currentLoc, end)
            else:
                subDirection = random.uniform(totalDirection - bumpyTunnelDirectionVariance, totalDirection + bumpyTunnelDirectionVariance)
                targetLoc = Vector2D(currentLoc.x + math.cos(subDirection) * tunnelDist,
                             currentLoc.y + math.sin(subDirection) * tunnelDist)
                straight.StraightTunnel.carveTunnel(self, width, 
                                                    currentLoc, targetLoc)
                currentLoc = targetLoc
