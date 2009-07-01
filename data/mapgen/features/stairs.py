import straight
import map
import constants

## Minimum distance to the ceiling for stairs to be added.
stairsMinimumClearance = 6
## Height of each step of the staircase
stairsHeight = 4
## Maximum slope for stairs to be made (otherwise make a straight tunnel)
maxSlope = 2

def getClassName():
    return 'StairsTunnel'

## Augment the floor of the tunnel with extra blocks to 
# create a staircase.
class StairsTunnel(straight.StraightTunnel):
    def createFeature(self):
        # Only if the angle from us to our parent is shallow enough
        slope = self.sector.getSlope()
        if abs(slope) > maxSlope
            return
        intercept = (self.sector.loc[1] - self.sector.loc[0] * slope) / constants.blockSize
        
        for x in range(0, self.map.numCols):
            for y in range(1, self.map.numRows):
                if (self.map.blocks[x][y] == map.BLOCK_WALL and 
                        self.map.blocks[x][y-1] == map.BLOCK_EMPTY and
                        y > x * slope + intercept and (x, y-1) in self.map.deadSeeds and
                        self.map.deadSeeds[(x, y-1)].node == self.sector):
                    distToCeiling = self.sector.getDistToCeiling((x, y))
                    if distToCeiling < stairsMinimumClearance:
                        continue
                    targetY = (int(y / stairsHeight)) * stairsHeight
                    if targetY > y:
                        targetY -= stairsHeight

                    for curY in range(targetY, y):
                        if self.sector.getIsOurSpace((x, curY)):
                            self.map.blocks[x][curY] = map.BLOCK_WALL


