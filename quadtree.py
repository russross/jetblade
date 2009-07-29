import constants
import util
import logger
import range1d
from vector2d import Vector2D

import pygame

## Minimum cell width/height, to prevent dicing up the quadtree too far.
minCellDim = 1000

## Number of objects in a node before we try to push objects down into the tree.
maxObjectsPerNode = 12

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


    ## Add an object to the node. Rebalance the tree afterwards if needed.
    def addObject(self, object, shouldRebalance = True):
        if self.parent is None and len(self.objects) == 11:
            logger.debug("Before rebalancing, tree is:")
            self.printTree()
        if len(self.objects) < maxObjectsPerNode - 1:
            logger.debug("Adding object",object,"with bounds",object.getBounds(),"to quadtree at depth",self.depth)
            self.objects.append(object)
        else:
            # Adding the object here would put us at the limit per node, so 
            # try pushing it down deeper.
            
            if not self.tryAddObjectToChildren(object):
                self.objects.append(object)
                logger.debug("Unable to push object", object, 
                             "deeper into tree, so it must stay at depth",
                             self.depth, "where we have", 
                             len(self.objects), "objects")
                if shouldRebalance:
                    self.rebalanceTree()
        if self.parent is None:
            logger.debug("After rebalancing, tree is:")
            self.printTree()


    ## Add many objects by iteratively calling self.addObject().
    def addObjects(self, objects):
        for object in objects:
            self.addObject(object, False)
        self.rebalanceTree(True)


    ## Try to push the given object down to our children. Return true on 
    # success, false on failure
    def tryAddObjectToChildren(self, object):
        if not len(self.children):
            return False
        rect = object.getBounds()
        horizRange = range1d.Range1D(rect.left, rect.right)
        vertRange = range1d.Range1D(rect.top, rect.bottom)
        nodeCenter = self.rect.center
        if (horizRange.contains(nodeCenter[0]) or
                vertRange.contains(nodeCenter[1])):
            # The object's bounding rect crosses a midpoint, so children
            # couldn't possibly hold it.
            return False
        else:
            for child in self.children:
                if child.canAcceptObject(object):
                    child.addObject(object)
                    return True


    ## Push objects in this level down into deeper levels of the tree, if 
    # possible.
    def rebalanceTree(self, shouldRecurse = False):
        if len(self.objects) > maxObjectsPerNode:
            newObjects = []
            for object in self.objects:
                if not self.tryAddObjectToChildren(object):
                    newObjects.append(object)
            self.objects = newObjects
        if shouldRecurse:
            for child in self.children:
                child.rebalanceTree()


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
        screenRect.center = camera.tuple()
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
            drawRect = pygame.Rect(Vector2D(1, 1).multiply(self.depth).add(self.rect.topleft).tuple(),
                                   Vector2D(-2, -2).multiply(self.depth).add(self.rect.size).tuple())
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
        

    ## Recursively print the tree
    def printTree(self):
        logger.debug(self)
        for child in self.children:
            child.printTree()


    ## Convert to string, non-recursively.
    def __str__(self):
        nodeTypeStr = ' (leaf) '
        if len(self.children):
            nodeTypeStr = ''
        return ('[Quadtree ID ' + str(self.id)  + ' at depth ' + 
                str(self.depth) + nodeTypeStr + ' bounds ' + 
                str(Vector2D(self.rect.topleft)) + ' to ' + 
                str(Vector2D(self.rect.bottomright)) +
                ' with ' + str(len(self.objects)) + ' objects here and ' + 
                str(len(self.getObjects())) + ' objects overall')
