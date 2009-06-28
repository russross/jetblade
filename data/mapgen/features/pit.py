import straight
import jetblade
import map
import constants
import util

import random

def getClassName():
    return 'Pit'

tunnelWidthFactor = 2
pitDepthFactor = .2

## When horizontal, this tunnel type puts a pit trap at the bottom and fills it
# with something unpleasant. 
# Because part of the tunnel is meant to be avoided, this tunnel type is wider
# than normal.
class Pit(straight.StraightTunnel):

    def carveTunnel(self):
        width = int(self.sector.getTunnelWidth() * tunnelWidthFactor)
        straight.StraightTunnel.carveTunnel(self, width)

    
    def createFeature(self):
        if abs(self.sector.getSlope()) > constants.DELTA:
            return
        
        (start, end) = self.sector.getStartAndEndLoc()
        if start is None or end is None:
            util.error("Unable to make pit for",self.sector.id,"from",self.sector.loc,"to",self.sector.parent.loc)
            return
        
        if start[0] > end[0]:
            (start, end) = (end, start)
        width = int(self.sector.getTunnelWidth() * tunnelWidthFactor / constants.blockSize)
        
        surfaceY = int(start[1] + width * pitDepthFactor)
        bottomY = int(start[1] + (width / 2) + 1)

        # Set up walls to contain the bottom of the pit.
        for y in range(surfaceY, bottomY + 1):
            self.map.blocks[start[0]][y] = 2
            self.map.blocks[end[0]][y] = 2

#        self.map.markLoc = ((start[0] + end[0]) / 2, surfaceY)
#        self.map.drawStatus()

        # Now fill the pit with stuff.
        # \todo Make this more variable. For now, just add water.
        water = jetblade.envEffectManager.loadEnvEffect('water')
        for x in range(start[0], end[0] + 1):
            for y in range(surfaceY, bottomY + 1):
                water.addSpace((x, y), self.map)

        # Now add platforms across the pit.
        # \todo Add a variety of platform types. Keep in mind the ceiling may
        # be low.
        for x in range(start[0], end[0] + 1, map.minHorizDistToOtherPlatforms):
            top = random.choice(range(surfaceY - 2, surfaceY + 1))
            for y in range(top, bottomY):
                self.map.blocks[x][y] = 2

