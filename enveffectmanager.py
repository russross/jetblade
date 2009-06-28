import sys
import util

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
        modulePath = 'environments.' + name
        try:
            initFunc = util.loadDynamicClass(modulePath)
            classInstance = initFunc(name)
            self.envMap[name] = classInstance
            return classInstance

        except Exception, e:
            util.fatal("Failed to load module",modulePath,":",e)

    ## Clear our cache
    def reset(self):
        self.envMap = dict()
