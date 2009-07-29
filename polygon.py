import constants
import util
import logger
import range1d
from vector2d import Vector2D

import pygame
import os

## Maximum number of already-calculated projections onto vectors that we 
# should cache for this polygon.
maxCachedProjections = 30

## The Polygon class represents convex bounding polygons used for collision 
# detection.
class Polygon:
    def __init__(self, points):
        ## Array of points in the polygon. 
        self.points = points
        
        upperLeft = [constants.BIGNUM, constants.BIGNUM]
        lowerRight = [-constants.BIGNUM, -constants.BIGNUM]
        for point in self.points:
            upperLeft[0] = min(upperLeft[0], point.x)
            upperLeft[1] = min(upperLeft[1], point.y)
            lowerRight[0] = max(lowerRight[0], point.x)
            lowerRight[1] = max(lowerRight[1], point.y)
        ## Upper-left corner of the polygon's bounding box.
        self.upperLeft = Vector2D(upperLeft)

        ## Lower-right corner of the polygon's bounding box.
        self.lowerRight = Vector2D(lowerRight)

        ## Bounding box rectangle
        self.rect = pygame.Rect(self.upperLeft.tuple(), self.lowerRight.sub(self.upperLeft).tuple())

        # Detect if the points we're given make a concave polygon, by looking
        # to see if any of the interior angles go in the wrong direction.
        polygonDirection = None
        for i in range(0, len(self.points)):
            p1 = self.points[(i-1) % len(self.points)]
            p2 = self.points[i]
            p3 = self.points[(i+1) % len(self.points)]
            # Get the direction of the angle via cross product.
            a = p2.sub(p1)
            b = p3.sub(p2)
            angleDirection = cmp(a.x * b.y - a.y * b.x, 0)
            if polygonDirection is None:
                polygonDirection = angleDirection
            if angleDirection != polygonDirection:
                # This angle has the wrong sign.
                logger.fatal("Polygon",self.points,"is not convex; angle at",p2,"is invalid")

        ## For debugging purposes, when we collide with another polygon, we 
        # set this to True for 1 frame.
        self.hit = False
        
        ## A list of all vectors we'll want to project the polygon onto when 
        # applying SAT. Each vector is perpendicular to one of the 
        # polygon's edges.
        self.projectionVectors = []
        prevPoint = self.points[-1]
        for point in self.points:
            vector = prevPoint.sub(point).normalize().invert()
            self.projectionVectors.append(vector)
            prevPoint = point
        ## Cache of vectors we've been projected onto in the past.
        self.vectorToProjectionCache = dict()
        ## Incrementing counter to track how old elements in the cache are.
        self.projectionCacheUseCounter = 0


    ## Use the Separating Axis Theorem to collide two convex polygons.
    # See http://www.metanetsoftware.com/technique/tutorialA.html
    def runSAT(self, myLoc, alt, altLoc):
        projectionVectors = self.getProjectionVectors()

        smallestOverlap = constants.BIGNUM
        overlapVector = None
        for vector in projectionVectors:
            range1 = self.projectOntoVector(myLoc, vector)
            range2 = alt.projectOntoVector(altLoc, vector)
            overlap = range1.getOverlap(range2)
            if overlap < constants.EPSILON:
                # Non-overlap means no collision
                return (0, None)
            if overlap < smallestOverlap:
                smallestOverlap = overlap
                overlapVector = vector
        if overlapVector is not None:
            self.hit = True
            alt.hit = True
            # The projection vectors may be pointing in the wrong direction; 
            # flip the vector if needed. Check by comparing the overlap 
            # if we move alt along overlapVector to the overlap we've already
            # obtained.
            displacedLoc = altLoc.add(overlapVector)
            range1 = self.projectOntoVector(myLoc, overlapVector)
            range2 = alt.projectOntoVector(displacedLoc, overlapVector)
            if range1.getOverlap(range2) > smallestOverlap:
                # overlapVector points in the wrong direction.
                overlapVector = overlapVector.multiply(-1)

        return (smallestOverlap, overlapVector)


    def getProjectionVectors(self):
        return self.projectionVectors


    ## Project us onto the given vector assuming we are at loc. Return the 
    # range (min, max) along the vector formed by that projection.
    def projectOntoVector(self, loc, vector):
        if vector in self.vectorToProjectionCache:
            result = self.vectorToProjectionCache[vector]['result']
            return result.addScalar(loc.getComponentOn(vector))
        result = range1d.Range1D()
        for point in self.points:
            distanceFromOrigin = point.getComponentOn(vector)
            if distanceFromOrigin < result.min:
                result.min = distanceFromOrigin
            if distanceFromOrigin > result.max:
                result.max = distanceFromOrigin
        
        self.vectorToProjectionCache[vector] = {
            'use' : self.projectionCacheUseCounter,
            'result' : result
        }
        self.projectionCacheUseCounter += 1
        if len(self.vectorToProjectionCache) > maxCachedProjections:
            logger.inform("Cache has grown too big")
            oldestProjectionVector = None
            oldestUse = self.projectionCacheUseCounter
            for key, projectionData in self.vectorToProjectionCache.iteritems():
                if projectionData['use'] < oldestUse:
                    oldestUse = projectionData['use']
                    oldestProjectionVector = key
            logger.inform("Removing entry for",oldestProjectionVector)
            del self.vectorToProjectionCache[oldestProjectionVector]
        return result.addScalar(loc.getComponentOn(vector))
        return result


    ## Return the ejection distance of the given polygon out of ourselves along
    # the provided vector.
    def getEjectionDistanceAlongVector(self, vector, myLoc, alt, altLoc):
        myProj = self.projectOntoVector(myLoc, vector)
        altProj = alt.projectOntoVector(altLoc, vector)
        distance = myProj.getOverlap(altProj)
        logger.debug("Overlap along",vector,"is",distance,"from ranges",myProj,altProj)
        return distance

    ## Draw the polygon, for debugging purposes only. Polygons that have been
    # hit turn red for 1 frame.
    def draw(self, screen, loc, camera):
        drawColor = (0, 255, 0)
        if self.hit:
            drawColor = (255, 0, 0)
        drawPoints = []
        for point in self.points:
            drawPoints.append(util.adjustLocForCenter(point.add(loc), camera, screen.get_rect()).tuple())
        pygame.draw.lines(screen, drawColor, 1, drawPoints, 4)
        self.hit = False


    ## Return the center, as the average of all points in the polygon.
    def getCenter(self):
        center = Vector2D(0, 0)
        for point in self.points:
            center = center.add(point)
        center = center.divide(len(self.points))
        return center


    ## Return the point on the polygon that matches the given Y coordinate and 
    # is furthest in the specified direction
    def getPointAtHeight(self, targetY, direction):
        currentPoint = None
        for point in self.points:
            if abs(point.y - targetY) < constants.EPSILON:
                if currentPoint is None or cmp(point.x - currentPoint.x, 0) == direction:
                    currentPoint = point
        return currentPoint


    ## Return the point on the polygon that matches the given X coordinate and
    # is highest or lowest (depending on direction)
    # Just a tweaked version of getPointAtHeight
    def getPointAtX(self, targetX, direction):
        currentPoint = None
        for point in self.points:
            if abs(point.x - targetX) < constants.EPSILON:
                if currentPoint is None or cmp(point.y - currentPoint.y, 0) == direction:
                    currentPoint = point
        return currentPoint


    ## Return the point on the polygon that is furthest in the specified 
    # direction and is between the specified heights.
    def getPointBetweenHeights(self, targetRange, direction):
        currentPoint = None
        for point in self.points:
            if (currentPoint is None or 
                    (targetRange.contains(point.y) and 
                        cmp(point.x - currentPoint.x, 0) == direction)):
                currentPoint = point
        return currentPoint


    ## Return a PyGame rect describing our boundary at the given location.
    def getBounds(self, loc):
        result = pygame.Rect(self.rect)
        result.topleft = loc.add(self.upperLeft).tuple()
        return result


    def __str__(self):
        result = 'polygon ['
        for point in self.points:
            result += str(point) + ', '
        result += ']'
        return result

#    def printAdjusted(self, loc):
#        for point in self.points: # 'print' <--- to trigger my vim commands
#            print '(', point[0] + loc[0], ',', point[1] + loc[1], ')',
#        print ''


