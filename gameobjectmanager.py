import game
import quadtree
import constants
import logger

import os

## This class handles all dynamic (i.e. not part of the map grid) objects during
# gameplay.
class GameObjectManager:
    ## Instantiate a manager
    def __init__(self):
        ## QuadTree that holds all dynamic objects. Delay instantiating this
        # until the game map is ready.
        self.objectTree = None

  
    ## Set up our tree now that the map's done being made.
    def setup(self):
        if self.objectTree is None:
            self.objectTree = quadtree.QuadTree(game.map.getBounds())


    ## Update all objects
    def update(self):
        if logger.getLogLevel() == logger.LOG_DEBUG:
            logger.debug("Updating",len(self.objectTree.getObjects()),"objects")
        self.objectTree.prepObjects()
        self.objectTree.runObjectCollisionDetection()
        self.objectTree.runTerrainCollisionDetection()
        self.objectTree.cleanupObjects()


    ## Run an object against terrain collision detection.
    def checkObjectAgainstTerrain(self, object):
        game.map.collideObject(object)


    ## Draw all objects
    def draw(self, progress):
        self.objectTree.draw(progress)


    ## Add the given object to the tree.
    def addObject(self, obj):
        self.objectTree.addObject(obj)


    ## Instantiate a new object of the given name and add it to the tree
    def addNewObject(self, objectName, *args):
        if logger.getLogLevel() >= logger.LOG_INFORM:
            numObjects = len(self.objectTree.getObjects()) + 1
            logger.inform("Adding",numObjects,"th object named",objectName,"with args",*args)
        objectPath = os.path.join(constants.objectsPath, objectName)
        objectPath = objectPath.replace(os.sep, '.')
        objectFunc = game.dynamicClassManager.loadDynamicClass(objectPath)
        newObject = objectFunc(*args)
        self.objectTree.addObject(newObject)
        return newObject

