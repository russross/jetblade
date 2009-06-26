import straight
import constants

## Minimum distance to the ceiling for stairs to be added.
stairsMinimumClearance = 6
## Height of each step of the staircase
stairsHeight = 4
## Allowed slopes for stairs to be made (beyond this, we just make a straight
# tunnel).
stairsSlopeRange = [-2, 2]

def carveTunnel(map, sector):
    straight.carveTunnel(map, sector)

## @package stairs Augment the floor of the tunnel with extra blocks to 
# create a staircase.
def createFeature(map, sector):
    # Only if the angle from us to our parent is shallow enough
    if abs(sector.loc[0] - sector.parent.loc[0]) < constants.EPSILON:
        return
    slope = (sector.loc[1] - sector.parent.loc[1]) / (sector.loc[0] - sector.parent.loc[0])
    intercept = (sector.loc[1] - sector.loc[0] * slope) / constants.blockSize
    if slope < stairsSlopeRange[0] or slope > stairsSlopeRange[1]:
        return 
    
    for x in range(0, map.numCols):
        for y in range(1, map.numRows):
            if (map.blocks[x][y] == 2 and map.blocks[x][y-1] == 0 and
                    y > x * slope + intercept and (x, y-1) in map.deadSeeds and
                    map.deadSeeds[(x, y-1)].node == sector):
                distToCeiling = sector.getDistToCeiling((x, y))
                if distToCeiling < stairsMinimumClearance:
                    continue
                targetY = (int(y / stairsHeight)) * stairsHeight
                if targetY > y:
                    targetY -= stairsHeight

                for curY in range(targetY, y):
                    if sector.getIsOurSpace((x, curY)):
                        map.blocks[x][curY] = 2

def shouldCheckAccessibility(sector):
    return straight.shouldCheckAccessibility(sector)

