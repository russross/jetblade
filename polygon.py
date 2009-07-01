import constants
import util
import range1D

import pygame
import os

## The Polygon class represents convex bounding polygons used for collision 
# detection.
class Polygon:
    def __init__(self, points):
        self.id = constants.globalId
        constants.globalId += 1

        ## Array of points in the polygon. 
        self.points = points
        
        ## Upper-left corner of the polygon's bounding box.
        self.upperLeft = [constants.BIGNUM, constants.BIGNUM]

        ## Lower-right corner of the polygon's bounding box.
        self.lowerRight = [-constants.BIGNUM, -constants.BIGNUM]
        for point in self.points:
            self.upperLeft[0] = min(self.upperLeft[0], point[0])
            self.upperLeft[1] = min(self.upperLeft[1], point[1])
            self.lowerRight[0] = max(self.lowerRight[0], point[0])
            self.lowerRight[1] = max(self.lowerRight[1], point[1])

        # Detect if the points we're given make a concave polygon, by looking
        # to see if any of the interior angles go in the wrong direction.
        polygonDirection = None
        for i in range(0, len(self.points)):
            p1 = self.points[(i-1) % len(self.points)]
            p2 = self.points[i]
            p3 = self.points[(i+1) % len(self.points)]
            # Get the direction of the angle via cross product.
            a = (p2[0] - p1[0], p2[1] - p1[1])
            b = (p3[0] - p2[0], p3[1] - p2[1])
            angleDirection = cmp(a[0] * b[1] - a[1] * b[0], 0)
            if polygonDirection is None:
                polygonDirection = angleDirection
            if angleDirection != polygonDirection:
                # This angle has the wrong sign.
                util.fatal("Polygon",self.points,"is not convex; angle at",p2,"is invalid")

        ## For debugging purposes, when we collide with another polygon, we 
        # set this to True for 1 frame.
        self.hit = False
        
        ## A list of all vectors we'll want to project the polygon onto when 
        # applying SAT. Each vector is perpendicular to one of the 
        # polygon's edges.
        self.projectionVectors = []
        prevPoint = self.points[-1]
        for point in self.points:
            vector = util.getNormalizedVector(prevPoint, point)
            vector = (-vector[1], vector[0])
            self.projectionVectors.append(vector)
            prevPoint = point

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
            displacedLoc = [altLoc[0] + overlapVector[0], altLoc[1] + overlapVector[1]]
            range1 = self.projectOntoVector(myLoc, overlapVector)
            range2 = alt.projectOntoVector(displacedLoc, overlapVector)
            if range1.getOverlap(range2) > smallestOverlap:
                # overlapVector points in the wrong direction.
                overlapVector = [-overlapVector[0], -overlapVector[1]]

        return (smallestOverlap, overlapVector)


    def getProjectionVectors(self):
        return self.projectionVectors


    ## Project the polygon onto the given vector. Return the range (min, max)
    # along the vector formed by that projection.
    def projectOntoVector(self, loc, vector):
        result = range1D.Range1D()
        for point in self.points:
            adjustedPoint = util.addVectors(point, loc)
            projectedPoint = util.projectPointOntoVector(adjustedPoint, vector)
            distanceFromOrigin = None
            if abs(vector[0]) > constants.EPSILON:
                distanceFromOrigin = projectedPoint[0] / vector[0]
            else:
                distanceFromOrigin = projectedPoint[1] / vector[1]
            if distanceFromOrigin < result.min:
                result.min = distanceFromOrigin
            if distanceFromOrigin > result.max:
                result.max = distanceFromOrigin
        return result


    ## Return the ejection distance of the given polygon out of ourselves along
    # the provided vector.
    def getEjectionDistanceAlongVector(self, vector, myLoc, alt, altLoc):
        myProj = self.projectOntoVector(myLoc, vector)
        altProj = alt.projectOntoVector(altLoc, vector)
        distance = myProj.getOverlap(altProj)
        util.debug("Overlap along",vector,"is",distance,"from ranges",myProj,altProj)
        return distance

    ## Draw the polygon, for debugging purposes only. Polygons that have been
    # hit turn red for 1 frame.
    def draw(self, screen, loc, camera):
        drawColor = (0, 255, 0)
        if self.hit:
            drawColor = (255, 0, 0)
        drawPoints = []
        for point in self.points:
            drawPoints.append(util.adjustLocForCenter(util.addVectors(point, loc), camera, screen.get_rect()))
        pygame.draw.lines(screen, drawColor, 1, drawPoints, 4)
        self.hit = False


    ## Return the center, as the average of all points in the polygon.
    def getCenter(self):
        center = [0, 0]
        for point in self.points:
            center[0] += point[0]
            center[1] += point[1]
        center[0] /= len(self.points)
        center[1] /= len(self.points)
        return center


    ## Return the point on the polygon that matches the given Y coordinate and 
    # is furthest in the specified direction
    def getPointAtHeight(self, targetY, direction):
        currentPoint = None
        for point in self.points:
            if abs(point[1] - targetY) < constants.EPSILON:
                if currentPoint is None or cmp(point[0] - currentPoint[0], 0) == direction:
                    currentPoint = point
        return currentPoint


    ## Return the point on the polygon that matches the given X coordinate and
    # is highest or lowest (depending on direction)
    # Just a tweaked version of getPointAtHeight
    def getPointAtX(self, targetX, direction):
        currentPoint = None
        for point in self.points:
            if abs(point[0] - targetX) < constants.EPSILON:
                if currentPoint is None or cmp(point[1] - currentPoint[1], 0) == direction:
                    currentPoint = point
        return currentPoint


    ## Return the point on the polygon that is furthest in the specified 
    # direction and is between the specified heights.
    def getPointBetweenHeights(self, targetRange, direction):
        currentPoint = None
        for point in self.points:
            if (currentPoint is None or 
                    (targetRange.contains(point[1]) and 
                        cmp(point[0] - currentPoint[0], 0) == direction)):
                currentPoint = point
        return currentPoint


    def __str__(self):
        str = 'polygon ['
        for point in self.points:
            str += '(%f, %f)' % (point[0], point[1])
        str += ']'
        return str

#    def printAdjusted(self, loc):
#        for point in self.points: # 'print' <--- to trigger my vim commands
#            print '(', point[0] + loc[0], ',', point[1] + loc[1], ')',
#        print ''


