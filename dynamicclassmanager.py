import logger

## This class handles loading dynamic classes out of the data directory.
class DynamicClassManager:
    ## Instantiate the manager.
    # \todo Load all dynamic classes at this time instead of waiting for them
    # to be needed.
    def __init__(self):
        ## Maps class names to their creation functions so we don't have to 
        # call __import__ every time we want a given class.
        self.classPathToClassMap = dict()


    ## Load a class from the named module. Assumes that the module includes a
    # function getClassName() that indicates the name of the class to load.
    def loadDynamicClass(self, path):
        if path in self.classPathToClassMap:
            return self.classPathToClassMap[path]
        try:
            logger.debug("Loading module",path)
            # In order to allow arbitrary naming of these classes, we first 
            # import a function that tells us the name of the class, then we 
            # import the class itself.
            # \todo: seems like this could be done better somehow.
            nameFuncModule = __import__(path, globals(), locals(), ['getClassName'])
            className = nameFuncModule.getClassName()
            classModule = __import__(path, globals(), locals(), [className])
            initFunc = getattr(classModule, className)
            self.classPathToClassMap[path] = initFunc
            return initFunc
        except Exception, e:
            logger.fatal("Failed to load module",path,":",e)
