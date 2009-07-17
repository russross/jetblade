import straight
import map
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
        # Only if the angle from us to our parent is shallow enough
        slope = self.sector.getSlope()
        if abs(slope) > maxSlope or abs(slope) < minSlope:
            return
        intercept = (self.sector.loc.y - self.sector.loc.x * slope) / constants.blockSize


        touchedColumns = set()
        for loc in self.sector.spaces:
            if (loc.x not in touchedColumns and 
                    self.map.blocks[loc.x][loc.y + 1] == map.BLOCK_WALL and 
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
                        self.map.blocks[currentLoc.x][currentLoc.y] = map.BLOCK_WALL
                    currentLoc.y += 1


