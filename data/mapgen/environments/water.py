import mapgen.generator
import enveffect
import logger
from vector2d import Vector2D
import constants

import random

def getClassName():
    return 'Water'


##  This class defines an environmental effect that creates pools of water 
# on the map. Such pools may occupy multiple sectors of the map but cannot 
# touch sectors that belong to a different region than the region they 
# start in. 
# \todo Make water pools affect physics.
class Water(enveffect.EnvEffect):

    ## Instantiate the Water class. There is only one instance for the entire
    # map; thus, create some "global" variables now.
    def __init__(self, name):
        ## This is a bit of a misnomer; water will not fill more than this
        # many spaces _from its starting point_, but it will fill down from
        # that point to an arbitrary depth.
        self.maxWaterDepth = 12
        ## Contains all locations that have the water effect.
        self.globalWaterSpaces = dict()
        enveffect.EnvEffect.__init__(self, name)


    ## Try to create a pool of water starting in the given sector. Keep adding
    # depth to the pool until either we hit maxWaterDepth or the next layer
    # would intrude into another region.
    def createRegion(self, gameMap, sector):
        waterSpaces = dict()
        # Find the midpoint of this tunnel.
        center = sector.start.loc.average(sector.end.loc).toGridspace()
        
        # Find the floor of the tunnel
        while gameMap.getBlockAtGridLoc(center) == 0:
            center = center.addY(1)

        # Try to floodfill out from this point. Give up if we run in to another
        # zone or if we're already underwater. Otherwise, raise the water level 
        # and try again.
        waterDepth = 0
        fillBlocks = set()
        topLayer = set()
        topLayer.add(center)
        while waterDepth < self.maxWaterDepth and len(topLayer):
            fillBlocks.update(topLayer)
            newWaterSpaces = dict()
            didFailFill = False

            while fillBlocks:
                block = fillBlocks.pop()
                # If we run into a block that isn't open space, isn't in our
                # region, or is part of a different pond, then give up on this
                # layer of the pond. 
                # Preventing the connection of two ponds saves us from having to
                # worry about some thorny merge issues, making for simpler 
                # code; it's arguable if we'd be better off being able to 
                # handle merges.
                if (gameMap.getTerrainInfoAtGridLoc(block) != sector.getTerrainInfo() or
                        block in self.globalWaterSpaces):
                    didFailFill = True
                    break

                newWaterSpaces[block] = True
                for neighbor in block.NEWSPerimeter():
                    if gameMap.getBlockAtGridLoc(neighbor) == mapgen.generator.BLOCK_EMPTY:
                        if neighbor.y < center.y - waterDepth:
                            # Neighbor is above the current water line, so add 
                            # it to the top layer
                            topLayer.add(neighbor)
                        elif (neighbor in fillBlocks or 
                                neighbor in newWaterSpaces or 
                                neighbor in waterSpaces or
                                gameMap.getBlockAtGridLoc(neighbor) != mapgen.generator.BLOCK_EMPTY):
                            # Space is invalid or already enqueued
                            continue
                        else:
                            fillBlocks.add(neighbor)

            if didFailFill:
                break
            waterDepth += 1
            waterSpaces.update(newWaterSpaces)

        if waterDepth > 0:
            for block in waterSpaces.keys():
                self.addSpace(block, gameMap)
                self.globalWaterSpaces[block] = True
                # Add the blocks on either side, to make a clean look where
                # slopes are involved.
                for offset in [-1, 1]:
                    tmp = Vector2D(block.x - offset, block.y)
                    if tmp not in self.globalWaterSpaces and tmp not in waterSpaces:
                        self.addSpace(tmp, gameMap)
                        self.globalWaterSpaces[tmp] = True


