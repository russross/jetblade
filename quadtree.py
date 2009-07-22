import constants
import util
import logger
from vector2d import Vector2D

import pygame

## Minimum cell width/height, to prevent dicing up the quadtree too far.
minCellDim = 1000

## Number of objects in a node before we try to push objects down into the tree.
maxObjectsPerNode = 6

## QuadTree instances are nodes in a recursive quad tree used to hold 2D
# objects. They are useful for spatial partitioning for efficient collision
# detection involving dynamic or irregularly-placed objects. Note that we don't
# shove the map grid into a quadtree, as the grid itself handles spacial
# partitioning for us.
class QuadTree:

    def __init__(self, rect, parent = None, depth = 0):
        self.id = constants.globalId
        constants.globalId += 1
        ## Bounding box for the node; unless the node is the root of the tree,
        # no objects in the node will extend beyond the bounds.
        self.rect = rect
        ## List of children of this node. Empty if this node is a leaf, but
        # leaves may extend themselves if objects are added.
        self.children = []
        ## Parent node. If this is the root, then parent is None.
        self.parent = parent
        ## Depth in the tree.
        self.depth = depth
        ## List of objects in this node.
        self.objects = []

        if (not self.children and 
                self.rect.width > minCellDim):
            self.extendTree()


    ## Add an object to the node. Rebalance the tree afterwards if needed.
    def addObject(self, object):
        rect = object.getBounds()
        for child in self.children:
            if child.canAcceptObject(object):
                child.addObject(object)
                return
        logger.debug("Adding object",object,"with bounds",object.getBounds(),"to quadtree at depth",self.depth)
        self.objects.append(object)
        if len(self.objects) > maxObjectsPerNode:
            self.rebalanceTree()


    ## Add many objects by iteratively calling self.addObject().
    def addObjects(self, objects):
        for object in objects:
            self.addObject(object)


    ## Push objects in this level down into deeper levels of the tree, if 
    # possible.
    def rebalanceTree(self):
        newObjects = []
        for object in self.objects:
            didPutObjectInChild = 0
            for child in self.children:
                if child.canAcceptObject(object):
                    child.addObject(object)
                    didPutObjectInChild = 1
                    break
            if not didPutObjectInChild:
                newObjects.append(object)
        self.objects = newObjects


    ## Create four children for this node.
    def extendTree(self):
        dims = (self.rect.width / 2.0, self.rect.height / 2.0)
        childRects = [
            pygame.rect.Rect(self.rect.topleft, dims),
            pygame.rect.Rect(self.rect.midtop, dims),
            pygame.rect.Rect(self.rect.midleft, dims),
            pygame.rect.Rect(self.rect.center, dims)
        ]
        for rect in childRects:
            self.children.append(QuadTree(rect, self, self.depth + 1))


    ## Update all objects in the tree. Rebalance as we go, by returning all 
    # objects that we cannot hold any longer, and pushing down objects that
    # can fit into one of our children.
    def update(self):
        displacedObjects = []
        newObjects = []
        for object in self.objects:
            if object.update():
                if not self.canAcceptObject(object):
                    displacedObjects.append(object)
                else:
                    newObjects.append(object)
            else:
                logger.debug("Object",object,"is dead")
        
        for child in self.children:
            for object in child.update():
                if not self.canAcceptObject(object):
                    displacedObjects.append(object)
                else:
                    newObjects.append(object)
        self.objects = []
        self.addObjects(newObjects)
        if self.parent is None:
            self.addObjects(displacedObjects)
        else:
            return displacedObjects



    ## Draw the objects in this node and all children, that intersect with the 
    # current view.
    def draw(self, screen, camera, progress, scale = 1):
        screenRect = screen.get_rect()
        screenRect.center = camera
        for object in self.objects:
            objectRect = object.getBounds()
            objectRect.width *= scale
            objectRect.height *= scale
            objectRect.topleft = (objectRect.topleft[0] * scale, objectRect.topleft[1] * scale)
            if objectRect.colliderect(screenRect):
                object.draw(screen, camera, progress, scale)
        for child in self.children:
            if child.rect.colliderect(screenRect):
                child.draw(screen, camera, progress, scale)

        if logger.getLogLevel() == logger.LOG_DEBUG:
            # Draw our bounding rect, inset by a pixel for each level of depth.
            drawRect = pygame.Rect(Vector2D(1, 1).multiply(self.depth).add(self.rect.topleft),
                                   Vector2D(-2, -2).multiply(self.depth).add(self.rect.size))
            drawRect.center = util.adjustLocForCenter(Vector2D(self.rect.center), camera, screen.get_rect())
            pygame.draw.rect(screen, (0, 0, 255), drawRect, 1)
            


    ## Return all objects in this node and any child nodes.
    def getObjects(self):
        result = [object for object in self.objects]
        for child in self.children:
            result.extend(child.getObjects())
        return result


    ## Return all objects whose bounding rects intersect the given rect, in
    # this node and any child nodes.
    def getObjectsIntersectingRect(self, rect):
        result = [object for object in self.objects if rect.colliderect(object.getBounds())]
        for child in self.children:
            result.extend(child.getObjectsIntersectingRect(rect))
        return result


    ## Return true if this node can fully contain the given object.
    def canAcceptObject(self, object):
        return self.rect.contains(object.getBounds())
        
