import furniture
import game
import constants
import util
import logger
from vector2d import Vector2D

import random
import os

## Maps direction names to vectors describing those directions
directionToVectorMap = {
    'up' : Vector2D(0, -1),
    'down' : Vector2D(0, 1),
    'left' : Vector2D(-1, 0),
    'right' : Vector2D(1, 0),
}

## Much like SceneryManager, this class loads the furnitureConfig files that
# describe what furniture to place and how.
class FurnitureManager:
    def __init__(self):
        ## Maps terrain to furniture config for that terrain.
        self.furnitureConfigCache = dict()


    ## Return a Furniture instance that matches the provided terrain and local
    # surface normal. Or return None if there's no good match.
    def pickFurniture(self, terrain, loc, surfaceNormal):
        # Map the local surface normal to a direction string
        direction = 'down'
        if abs(surfaceNormal.x) > abs(surfaceNormal.y):
            if surfaceNormal.x > 0:
                direction = 'left'
            else:
                direction = 'right'
        elif surfaceNormal.y < 0:
            direction = 'up'
        if terrain not in self.furnitureConfigCache:
            ## Load the config file
            filename = os.path.join(constants.spritePath, 'terrain', 
                    terrain.zone, terrain.region, 'furniture', 
                    'furnitureConfig')
            module = game.dynamicClassManager.loadModuleItems(filename, ['furniture'])
            furnitureMap = module.furniture
            furnitureConfig = dict()
            for furnitureNames, furnitureData in furnitureMap.iteritems():
                for direction in furnitureData['embedDirections']:
                    if direction not in furnitureConfig:
                        furnitureConfig[direction] = dict()
                    depths = tuple(furnitureData['embedDepths'])
                    furnitureConfig[direction][(furnitureNames, depths)] = furnitureData['weight']
            self.furnitureConfigCache[terrain] = furnitureConfig
        if direction not in self.furnitureConfigCache[terrain]:
            return None
        (type, embedDepths) = util.pickWeightedOption(self.furnitureConfigCache[terrain][direction])
        if type[0] is not None:
            depth = random.choice(embedDepths)
            offset = directionToVectorMap[direction].multiply(-depth)
            # \todo Figure out why we have to add a half-block to the location.
            furnitureLoc = loc.add(offset).toRealspace().addScalar(constants.blockSize / 2.0)
            return furniture.Furniture(furnitureLoc, terrain, type[0], type[1])
        return None
            
