import straight
import util
import math
import random

def getClassName():
    return 'BumpyTunnel'

## Number of subsegments of the tunnel to create
bumpyTunnelNumSubtunnels = 4
## Degree to which a single tunnel can vary in direction from the previous.
# Making this higher allows for bumpier tunnels, but making it too high can
# cause the tunnel to interfere with other tunnels and create inaccessible maps.
bumpyTunnelDirectionVariance = math.pi / 16.0

class BumpyTunnel(straight.StraightTunnel):
    ## Create a series of short tunnel segments connecting the 
    # start and ends of the sector.
    def carveTunnel(self):
        start = self.sector.parent.loc
        end = self.sector.loc
        # Create a series of short straight tunnels that connect start and end
        totalDist = util.pointPointDistance(start, end)
        totalDirection = math.atan2(end[1] - start[1], end[0] - start[0])
        tunnelDist = totalDist / bumpyTunnelNumSubtunnels
        currentLoc = start
        for i in range(0, bumpyTunnelNumSubtunnels):
            if i == bumpyTunnelNumSubtunnels - 1:
                straight.StraightTunnel.carveTunnel(self)
            else:
                subDirection = random.uniform(totalDirection - bumpyTunnelDirectionVariance, totalDirection + bumpyTunnelDirectionVariance)
                targetLoc = [currentLoc[0] + math.cos(subDirection) * tunnelDist,
                             currentLoc[1] + math.sin(subDirection) * tunnelDist]
                straight.StraightTunnel.carveTunnel(self)
                currentLoc = targetLoc
