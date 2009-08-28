import scenery
import util
import logger
import constants
from vector2d import Vector2D

import sys
import os

## The SceneryManager class handles loading scenery configuration and 
# selection of scenery items depending on terrain.
class SceneryManager:
    def __init__(self):
        ## Maps scenery names to their configuration information.
        # \todo This dict is a huge mess (just check out selectScenery()).
        self.sceneryConfigCache = dict()

    ## Choose an item from the set available for the given terrain, 
    # picking only from items that can be 
    # "planted" on blocks with the given adjacency signature.
    def selectScenery(self, terrain, signature):
        if terrain not in self.sceneryConfigCache:
            # Load the scenery config into the config cache first
            filename = os.path.join(constants.spritePath, 'terrain', 
                    terrain.zone, terrain.region, 'scenery', 'sceneryConfig')
            filename = filename.replace(os.sep, '.')
            module = None
            try:
                module = __import__(filename, globals(), locals(), ['scenery'])
            except Exception, e:
                logger.fatal("Unable to load",filename,":",e.message)
            
            sceneryMap = module.scenery
            self.sceneryConfigCache[terrain] = dict()
            self.sceneryConfigCache[terrain]['nameToAnchorMap'] = dict()
            keyToSceneryWeightsMap = dict()
            for sceneryType, scenerySettings in sceneryMap.iteritems():
                anchor = Vector2D(scenerySettings['anchor'])
                # Reverse the anchors to represent the offset we need to add to 
                # properly plant the item at a given block location
                anchor = anchor.multiply(-1)
                self.sceneryConfigCache[terrain]['nameToAnchorMap'][sceneryType] = anchor
                keys = util.adjacencyArrayToSignatures(scenerySettings['map'])
                for key in keys:
                    if key not in keyToSceneryWeightsMap:
                        keyToSceneryWeightsMap[key] = dict()
                    keyToSceneryWeightsMap[key][sceneryType] = scenerySettings['weight']
            logger.debug("Keys for terrain",terrain,"are",keyToSceneryWeightsMap.keys())

            self.sceneryConfigCache[terrain]['signatureToWeightsMap'] = keyToSceneryWeightsMap

        # Select an item given the adjacency signature for the block it'll be 
        # on.
        if signature in self.sceneryConfigCache[terrain]['signatureToWeightsMap']:
            sceneryType = util.pickWeightedOption(self.sceneryConfigCache[terrain]['signatureToWeightsMap'][signature])
            if sceneryType[0] is None or sceneryType[1] is None:
                return None
            anchor = self.sceneryConfigCache[terrain]['nameToAnchorMap'][sceneryType]
            newItem = scenery.Scenery(anchor, terrain, sceneryType[0], sceneryType[1])
            return newItem
        # No matching scenery item
        return None


    ## Clear the cache.
    def reset(self):
        self.sceneryConfigCache = dict()

