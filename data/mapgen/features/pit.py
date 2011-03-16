import straight
import game
import mapgen.generator
import constants
import logger
from vector2d import Vector2D

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
            logger.error("Unable to make pit for",self.sector.id,"from",self.sector.start.loc,"to",self.sector.end.loc)
            return
        
        if start.x > end.x:
            (start, end) = (end, start)
        width = int(self.sector.getTunnelWidth() * tunnelWidthFactor / constants.blockSize)
        
        surfaceY = int(start.y + width * pitDepthFactor)
        bottomY = int(start.y + (width / 2) + 1)

        # Set up walls to contain the bottom of the pit.
        for y in range(surfaceY, bottomY + 1):
            self.map.blocks[start.ix][y] = mapgen.generator.BLOCK_WALL
            self.map.blocks[end.ix][y] = mapgen.generator.BLOCK_WALL

        # Now fill the pit with stuff.
        # \todo Make this more variable. For now, just add water.
        water = game.envEffectManager.loadEnvEffect('water')
        for x in range(start.ix, end.ix + 1):
            for y in range(surfaceY, bottomY + 1):
                water.addSpace(Vector2D(x, y), self.map)

        # Now add platforms across the pit.
        # \todo Add a variety of platform types. Keep in mind the ceiling may
        # be low.
        for x in range(start.ix, end.ix + 1, mapgen.generator.minHorizDistToOtherPlatforms):
            top = int(random.uniform(surfaceY - 2, surfaceY + 1))
            for y in range(top, bottomY):
                self.map.blocks[x][y] = mapgen.generator.BLOCK_WALL

