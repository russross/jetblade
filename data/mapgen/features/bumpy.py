import straight
import util
import math
import random

## Number of subsegments of the tunnel to create
bumpyTunnelNumSubtunnels = 4
## Degree to which a single tunnel can vary in direction from the previous.
# Making this higher allows for bumpier tunnels, but making it too high can
# cause the tunnel to interfere with other tunnels and create inaccessible maps.
bumpyTunnelDirectionVariance = math.pi / 16.0

## @package bumpy Create a series of short tunnel segments connecting the 
# start and ends of the sector.
def carveTunnel(map, sector):
    start = sector.parent.loc
    end = sector.loc
    # Create a series of short straight tunnels that connect start and end
    totalDist = util.pointPointDistance(start, end)
    totalDirection = math.atan2(end[1] - start[1], end[0] - start[0])
    tunnelDist = totalDist / bumpyTunnelNumSubtunnels
    currentLoc = start
    for i in range(0, bumpyTunnelNumSubtunnels):
        if i == bumpyTunnelNumSubtunnels - 1:
            straight.carveTunnel(map, sector)
        else:
            subDirection = random.uniform(totalDirection - bumpyTunnelDirectionVariance, totalDirection + bumpyTunnelDirectionVariance)
            targetLoc = [currentLoc[0] + math.cos(subDirection) * tunnelDist,
                         currentLoc[1] + math.sin(subDirection) * tunnelDist]
            straight.carveTunnel(map, sector)
            currentLoc = targetLoc

def createFeature(map, sector):
    pass

def shouldCheckAccessibility(sector):
    return 1

