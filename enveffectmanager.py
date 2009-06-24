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
        modulePath = 'environments.' + name
        try:
            print "Loading environment effect",name
            # In order to allow arbitrary naming of these classes, we first 
            # import a function that tells us the name of the class, then we 
            # import the class itself.
            # \todo: seems like this could be done better somehow.
            nameFuncModule = __import__(modulePath, globals(), locals(), ['getClassName'])
            className = nameFuncModule.getClassName()
            envModule = __import__(modulePath, globals(), locals(), [className])
            initFunc = getattr(envModule, className)
            classInstance = initFunc(name)
            self.envMap[name] = classInstance
            return classInstance

        except Exception, e:
            print "Failed to load module",modulePath,":",e
            sys.exit()

    ## Clear our cache
    def reset(self):
        self.envMap = dict()
