import jetblade
import util

## This class manages the different map feature modules in data/mapgen/features.
class FeatureManager:
    ## Instantiate the manager
    def __init__(self):
        self.featureCache = dict()


    ## Instantiate a class from the named module using the provided 
    # sector, and return it.
    def loadFeature(self, name, sector):
        if name in self.featureCache:
            return self.featureCache[name](jetblade.map, sector)
        modulePath = 'features.' + name
        self.featureCache[name] = util.loadDynamicClass(modulePath)
        return self.featureCache[name](jetblade.map, sector)
