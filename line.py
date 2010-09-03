import constants
from vector2d import Vector2D

import pygame
import math

## These are the possible return values of lineLineIntersect()
LINE_NO_COLLISION = 0
LINE_INTERSECT = 1
LINE_COINCIDENT = 2
LINE_PARALLEL = 3

## Lines are simple pairs of points. 
class Line:
    def __init__(self, start, end):
        ## Start point
        self.start = start
        ## End point
        self.end = end
        width = abs(start.x - end.x)
        height = abs(start.y - end.y)
        upperLeft = (min(start.x, end.x), min(start.y, end.y))
        ## Bounding box
        self.rect = pygame.rect.Rect(upperLeft, (width, height))


    ## Return the endpoints we don't have in common with altLine.
    def getUnsharedPoints(self, alt):
        ourPoints = [self.start, self.end]
        altPoints = [alt.start, alt.end]
        result = []
        for point in ourPoints:
            doesMatch = 0
            for altPoint in altPoints:
                if point.x == altPoint.x and point.y == altPoint.y:
                    doesMatch = 1
            if not doesMatch:
                result.append(point)
        return result

    ## Get the point of intersection between us and another line, or one of 
    # a few possible alternate results:
    #  - LINE_COINCIDENT: lines lie on top of each other.
    #  - LINE_PARALLEL: lines are parallel and non-coincident
    #  - LINE_NO_COLLISION: Lines are not parallel but do not intersect
    # Logic pulled from http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
    def lineLineIntersect(self, alt):
        (possibleResult, values) = self.getIntersectValues(alt)
        if possibleResult is not None:
            return possibleResult
        (ua, ub) = values
        if ua > 0 and ua < 1 and ub > 0 and ub < 1:
            p1 = self.start
            p2 = self.end
            p3 = alt.start
            p4 = alt.end
            # Line segments intersect.
            return LINE_INTERSECT
        return LINE_NO_COLLISION


    ## As lineLineIntersect, but treats both us and alt as being infinite, 
    # and returns either no intersection or a Vector2D of the intersection
    # point.
    # \todo We should change this so lineLineIntersect calls this function
    # and then verifies that the result is on the line segments.
    def infiniteLineIntersect(self, alt):
        (possibleResult, values) = self.getIntersectValues(alt)
        if possibleResult is not None:
            return possibleResult
        (ua, ub) = values
        p1 = self.start
        p2 = self.end
        p3 = alt.start
        p4 = alt.end
        return Vector2D(p1.x + ua * (p2.x - p1.x),
                        p1.y + ua * (p2.y - p1.y))


    ## Does some calculations common to lineLineIntersect and 
    # infiniteLineIntersect
    def getIntersectValues(self, alt):
        p1 = self.start
        p2 = self.end
        p3 = alt.start
        p4 = alt.end

        denominator = (p4.y - p3.y)*(p2.x - p1.x) - (p4.x - p3.x)*(p2.y - p1.y)
        uaNumerator = ((p4.x - p3.x)*(p1.y - p3.y) - (p4.y - p3.y)*(p1.x - p3.x))
        ubNumerator = ((p2.x - p1.x)*(p1.y - p3.y) - (p2.y - p1.y)*(p1.x - p3.x))
        if abs(denominator) < constants.DELTA:
            if (abs(uaNumerator) < constants.DELTA and
                abs(ubNumerator) < constants.DELTA):
                # Lines are coincident
                return (LINE_COINCIDENT, None)
            # Parallel lines, so don't worry.
            return (LINE_PARALLEL, None)
        ua = uaNumerator / denominator
        ub = ubNumerator / denominator
        return (None, (ua, ub))

    ## Return the distance from the point to the line. Logic taken from
    # http://www.codeguru.com/forum/printthread.php?t=194400
    def pointDistance(self, point):
        cx = point.x
        cy = point.y
        ax = self.start.x
        ay = self.start.y
        bx = self.end.x
        by = self.end.y
        # In short: project our endpoint onto the line, then determine how
        # far along that projection we are, then deal with endpoints.

        rNumerator = (cx-ax)*(bx-ax) + (cy-ay)*(by-ay)
        rDenominator = (bx-ax)*(bx-ax) + (by-ay)*(by-ay)
        r = rNumerator / rDenominator

        px = ax + r * (bx - ax) # Projecting onto line
        py = ay + r * (by - ay) # Ditto

        # This is the distance if the line were infinite instead of a 
        # segment
        s = ((ay - cy)*(bx - ax) - (ax - cx)*(by - ay)) / rDenominator
        distance = abs(s) * math.sqrt(rDenominator)

        # x, y is the point on the line closest to (cx, cy)
        x = px
        y = py
        if r < 0 or r > 1:
            # The projection is not on the line, so look at endpoint
            # distances.
            dist1 = (cx - ax)*(cx - ax) + (cy - ay)*(cy - ay)
            dist2 = (cx - bx)*(cx - bx) + (cy - by)*(cy - by)
            if dist1 < dist2:
                x = ax
                y = ay
                distance = math.sqrt(dist1)
            else:
                x = bx
                y = by
                distance = math.sqrt(dist2)

        return distance


    ## Convert to string
    def __str__(self):
        return '[Line ' + str(self.start) + ', ' + str(self.end) + ']'


    def getBounds(self):
        return self.rect

