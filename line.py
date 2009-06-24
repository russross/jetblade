import constants
import pygame

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
        width = abs(start[0] - end[0])
        height = abs(start[1] - end[1])
        upperLeft = (min(start[0], end[0]), min(start[1], end[1]))
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
                if point[0] == altPoint[0] and point[1] == altPoint[1]:
                    doesMatch = 1
            if not doesMatch:
                result.append(point)
        return result

    ## Return the relationship between ourself and another line: 
    # no intersection, crossing, coincident, or parallel but not coincident.
    # Logic pulled from http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
    def lineLineIntersect(self, alt):
        p1 = self.start
        p2 = self.end
        p3 = alt.start
        p4 = alt.end

        denominator = (p4[1] - p3[1])*(p2[0] - p1[0]) - (p4[0] - p3[0])*(p2[1] - p1[1])
        uaNumerator = ((p4[0] - p3[0])*(p1[1] - p3[1]) - (p4[1] - p3[1])*(p1[0] - p3[0]))
        ubNumerator = ((p2[0] - p1[0])*(p1[1] - p3[1]) - (p2[1] - p1[1])*(p1[0] - p3[0]))
        if abs(denominator) < constants.DELTA:
            if (abs(uaNumerator) < constants.DELTA and
                abs(ubNumerator) < constants.DELTA):
                # Lines are coincident
                return LINE_COINCIDENT
            # Parallel lines, so don't worry.
            return LINE_PARALLEL
        ua = uaNumerator / denominator
        ub = ubNumerator / denominator
        if ua > 0 and ua < 1 and ub > 0 and ub < 1:
            # Line segments intersect.
            return LINE_INTERSECT
        return LINE_NO_COLLISION


    def __str__(self):
        return '[Line ' + str(self.start) + ', ' + str(self.end) + ']'


    def getBounds(self):
        return self.rect

