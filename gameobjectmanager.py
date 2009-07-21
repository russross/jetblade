import jetblade
import quadtree
import constants
import logger

## This class handles all dynamic (i.e. not part of the map grid) objects during
# gameplay.
class GameObjectManager:
    ## Instantiate a manager
    def __init__(self):
        ## QuadTree that holds all dynamic objects
        self.objectTree = quadtree.QuadTree(jetblade.map.getBounds())
    

    ## Update all objects
    def update(self):
        self.objectTree.update()


    ## Draw all objects
    def draw(self, screen, camera, progress, scale = 1):
        self.objectTree.draw(screen, camera, progress, scale)


    ## Add the given object to the tree.
    def addObject(self, obj):
        self.objectTree.addObject(obj)


    ## Instantiate a new object of the given name and add it to the tree
    def addNewObject(self, objectName, *args):
        logger.inform("Adding object named",objectName,"with args",*args)
        objectPath = constants.objectsPath + '/' + objectName
        objectPath = objectPath.replace('/', '.')
        objectFunc = jetblade.dynamicClassManager.loadDynamicClass(objectPath)
        newObject = objectFunc(*args)
        self.objectTree.addObject(newObject)
