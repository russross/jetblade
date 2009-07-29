import game
import constants

## This class manages the different map feature modules in data/mapgen/features.
class FeatureManager:
    ## Instantiate the manager
    def __init__(self):
        self.featureCache = dict()


    ## Instantiate a class from the named module using the provided 
    # sector, and return it.
    def loadFeature(self, name, sector):
        if name in self.featureCache:
            return self.featureCache[name](game.map, sector)
        modulePath = constants.mapPath + '/features/' + name
        modulePath = modulePath.replace('/', '.')
        self.featureCache[name] = game.dynamicClassManager.loadDynamicClass(modulePath)
        return self.featureCache[name](game.map, sector)

