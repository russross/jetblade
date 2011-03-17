import straight
import mapgen.generator
import constants
from vector2d import Vector2D

## Minimum distance to the ceiling for stairs to be added.
stairsMinimumClearance = 6
## Height of each step of the staircase
stairsHeight = 4
## Maximum slope for stairs to be made (otherwise make a straight tunnel)
maxSlope = 2
## Minimume slope for stairs to be made (otherwise don't bother)
minSlope = .4

def getClassName():
    return 'StairsTunnel'

## Augment the floor of the tunnel with extra blocks to 
# create a staircase.
class StairsTunnel(straight.StraightTunnel):
    def createFeature(self):
        # Only if the angle from start to end is shallow enough
        slope = self.sector.getSlope()
        if abs(slope) > maxSlope or abs(slope) < minSlope:
            return
        intercept = (self.sector.start.y - self.sector.start.x * slope) / constants.blockSize


        touchedColumns = set()
        for loc in self.sector.spaces:
            if (loc.x not in touchedColumns and 
                    self.map.blocks[loc.ix][loc.iy + 1] == mapgen.generator.BLOCK_WALL and 
                    loc.y > loc.x * slope + intercept):
                touchedColumns.add(loc.x)
                distToCeiling = self.sector.getDistToCeiling(loc)
                if distToCeiling < stairsMinimumClearance:
                    continue
                # Quantize the Y location
                targetY = (int(loc.y / stairsHeight)) * stairsHeight

                currentLoc = Vector2D(loc.x, targetY)
                while currentLoc.y <= loc.y:
                    if self.sector.getIsOurSpace(currentLoc):
                        self.map.blocks[currentLoc.ix][currentLoc.iy] = mapgen.generator.BLOCK_WALL
                    currentLoc = currentLoc.addY(1)


