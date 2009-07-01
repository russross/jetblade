import enveffect
import util
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
        ## Contains all (x, y) tuples that have the water effect.
        self.globalWaterSpaces = dict()
        enveffect.EnvEffect.__init__(self, name)


    ## Try to create a pool of water starting in the given sector. Keep adding
    # depth to the pool until either we hit maxWaterDepth or the next layer
    # would intrude into another region.
    def createRegion(self, map, sector):
        util.debug("Creating a water region at",sector)
        waterSpaces = dict()
        # Find the midpoint of this tunnel.
        center = list(sector.loc)
        center[0] += (sector.parent.loc[0] - sector.loc[0]) / 2.0
        center[1] += (sector.parent.loc[1] - sector.loc[1]) / 2.0
        center = util.realspaceToGridspace(center)
        
        # Find the floor of the tunnel
        while map.getBlockAtGridLoc(center) == 0:
            center[1] += 1

        # Try to floodfill out from this point. Give up if we run in to another
        # zone or if we're already underwater. Otherwise, raise the water level 
        # and try again.
        waterDepth = 0
        fillBlocks = dict()
        topLayer = {tuple(center) : True}
        while waterDepth < self.maxWaterDepth and len(topLayer):
            fillBlocks.update(topLayer)
            topLayer = dict()
            newWaterSpaces = dict()
            didFailFill = False

            while fillBlocks:
                block = fillBlocks.keys()[0]
                del fillBlocks[block]
                # If we run into a block that isn't open space, isn't in our
                # region, or is part of a different pond, then give up on this
                # layer of the pond. 
                # Preventing the connection of two ponds saves us from having to
                # worry about some thorny merge issues, making for simpler 
                # code; it's arguable if we'd be better off being able to 
                # handle merges.
                if (block not in map.deadSeeds or 
                        map.deadSeeds[block].node.getTerrainInfo() != sector.getTerrainInfo() or
                        block in self.globalWaterSpaces):
                    didFailFill = True
                    break

                newWaterSpaces[block] = True
                for offset in constants.NEWSPerimeterOrder:
                    neighbor = (block[0] + offset[0], block[1] + offset[1])
                    if map.getBlockAtGridLoc(neighbor) == 0:
                        if neighbor[1] < center[1] - waterDepth:
                            # Neighbor is above the current water line, so add it
                            # to the top layer
                            topLayer[neighbor] = True
                        elif (neighbor in fillBlocks or 
                                neighbor in newWaterSpaces or 
                                neighbor in waterSpaces or
                                map.getBlockAtGridLoc(neighbor) != 0):
                            # Space is invalid or already enqueued
                            continue
                        else:
                            fillBlocks[neighbor] = True

            if didFailFill:
                break
            waterDepth += 1
            waterSpaces.update(newWaterSpaces)

        if waterDepth > 0:
            (zone, flavor) = sector.getTerrainInfo()
            for block in waterSpaces.keys():
                self.addSpace(block, map)
                self.globalWaterSpaces[block] = True
                # Add the blocks on either side, to make a clean look where
                # slopes are involved.
                for offset in [-1, 1]:
                    tmp = (block[0] - offset, block[1])
                    if tmp not in self.globalWaterSpaces and tmp not in waterSpaces:
                        self.addSpace(tmp, map)
                        self.globalWaterSpaces[tmp] = True


