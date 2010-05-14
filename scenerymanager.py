import game
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
    def selectScenery(self, gridLoc, terrain, signature):
        if terrain not in self.sceneryConfigCache:
            self.loadSceneryConfig(terrain)
        # Select an item given the adjacency signature for the block it'll be 
        # on.
        if signature in self.sceneryConfigCache[terrain]['signatureToWeightsMap']:
            sceneryType = util.pickWeightedOption(self.sceneryConfigCache[terrain]['signatureToWeightsMap'][signature])
            if sceneryType[0] is None or sceneryType[1] is None:
                return None
            newItem = scenery.Scenery(gridLoc, terrain, sceneryType[0], sceneryType[1])
            return newItem
        # No matching scenery item
        return None


    ## Load scenery configuration information for a specified terrain.
    def loadSceneryConfig(self, terrain):
        filename = os.path.join(constants.spritePath, 'terrain', 
                terrain.zone, terrain.region, 'scenery', 'sceneryConfig')
        module = game.dynamicClassManager.loadModuleItems(filename, ['scenery'])
        
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


    ## Get the anchor for the specified terrain/group/item combination.
    def getAnchorForScenery(self, terrain, group, item):
        if terrain not in self.sceneryConfigCache:
            self.loadSceneryConfig(terrain)
        if (group, item) not in self.sceneryConfigCache[terrain]['nameToAnchorMap']:
            logger.error("Invalid scenery type", (group, item), "for terrain",
                         terrain)
            logger.error("Valid types are",self.sceneryConfigCache[terrain]['nameToAnchorMap'].keys())
        return self.sceneryConfigCache[terrain]['nameToAnchorMap'][(group, item)]


    ## Clear the cache.
    def reset(self):
        self.sceneryConfigCache = dict()

