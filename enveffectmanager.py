import constants
import game

import sys

## This class handles loading and caching information on enviromental effects.
class EnvEffectManager:
    def __init__(self):
        ## Maps names to EnvEffect instances
        envMap = dict()

    ## Load the code for a single environmental effect, and instantiate the 
    # class for it. Then store it in the envMap cache.
    def loadEnvEffect(self, name):
        if name in self.envMap:
            return self.envMap[name]
        modulePath = constants.mapPath + '/environments/' + name
        modulePath = modulePath.replace('/', '.')
        initFunc = game.dynamicClassManager.loadDynamicClass(modulePath)
        classInstance = initFunc(name)
        self.envMap[name] = classInstance
        return classInstance


    ## Clear our cache
    def reset(self):
        self.envMap = dict()

