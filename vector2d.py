import constants

import math


## This class represents a two-dimensional vector. Many functions are provided
# that allow modification of Vector2Ds; however, none of them alter the 
# specific instance (instead returning new Vector2D instances that you can
# assign to variables). Equality and inequality operators are provided;
# though they do a fuzzy match and so cost more than you might otherwise
# expect.
class Vector2D(tuple):
    __slots__ = []

    ## Instantiate a Vector2D. We accept either two coordinates, or a single
    # argument which is assumed to be a tuple or list with at least two 
    # elements. 
    def __new__(cls, first, second = None):
        self = None
        if second is None:
            self = tuple.__new__(cls, (first[0], first[1]))
        else:
            self = tuple.__new__(cls, (first, second))
        return self


    ## Return a copy of us.
    def copy(self):
        return Vector2D(self[0], self[1])


    ## Access the first element (used by the x property)
    def _getX_(self):
        return self[0]


    ## Access the second element (used by the y property)
    def _getY_(self):
        return self[1]


    ## Clean-looking way of accessing the first element. This is marginally 
    # slower than using [0] but makes for easier-to-read code.
    x = property(_getX_)
    ## As x property, for second element.
    y = property(_getY_)


    ## Add alt to us. Return a copy of ourselves.
    def add(self, alt):
        x = self[0] + alt[0]
        y = self[1] + alt[1]
        return Vector2D(x, y)


    ## Add a scalar to both x and y.
    def addScalar(self, addend):
        x = self[0] + addend
        y = self[1] + addend
        return Vector2D(x, y)


    ## Add a scalar to just X
    def addX(self, addend):
        return Vector2D(self[0] + addend, self[1])

    
    ## Add a scalar to just Y
    def addY(self, addend):
        return Vector2D(self[0], self[1] + addend)


    ## As add, but subtract instead
    def sub(self, alt):
        x = self[0] - alt[0]
        y = self[1] - alt[1]
        return Vector2D(x, y)


    ## As add, but multiply by a scalar
    def multiply(self, multiplicand):
        x = self[0] * multiplicand
        y = self[1] * multiplicand
        return Vector2D(x, y)


    ## As add, but divide by a scalar.
    def divide(self, divisor):
        x = self[0] / divisor
        y = self[1] / divisor
        return Vector2D(x, y)


    ## Return a Vector2D instance that is us with the desired X component
    def setX(self, xVal):
        return Vector2D(xVal, self.y)


    ## As setX for the Y component
    def setY(self, yVal):
        return Vector2D(self.x, yVal)


    ## As add, but average instead.
    def average(self, alt):
        x = (self[0] + alt[0]) / 2.0
        y = (self[1] + alt[1]) / 2.0
        return Vector2D(x, y)


    ## Return the result of rounding us to the nearest int.
    def round(self):
        return Vector2D(int(self[0] + .5), int(self[1] + .5))


    ## Flatten to ints
    def int(self):
        return Vector2D(int(self[0]), int(self[1]))


    ## Return the distance from us to alt.
    def distance(self, alt):
        return math.sqrt((self[0] - alt[0])**2 + (self[1] - alt[1])**2)


    ## Return the distance if moving diagonally counts the same as moving
    # horizontally (generates square "circles").
    def distanceSquare(self, alt):
        return max(abs(self[0] - alt[0]), abs(self[1] - alt[1]))


    ## Return our magnitude
    def magnitude(self):
        return math.sqrt(self[0]**2 + self[1]**2)


    ## Return the magnitude squared, to avoid the sqrt call when it's not needed
    def magnitudeSquared(self):
        return self[0]**2 + self[1]**2


    ## Return our normalized form
    def normalize(self):
        return self.divide(self.magnitude())


    ## Return the inverted form
    def invert(self):
        return Vector2D(-self[1], self[0])


    ## Return our slope
    def slope(self):
        if abs(self[0]) < constants.EPSILON:
            return constants.BIGNUM * cmp(self[1], 0)
        return self[1] / self[0]


    ## Return our angle
    def angle(self):
        return math.atan2(self[1], self[0])


    ## Return the project of ourselves onto the given vector
    def projectOnto(self, alt):
        if abs(alt[0]) < constants.EPSILON:
            # alt is vertical
            return Vector2D(0, self[1])
        slope = alt.slope()
        x = (slope * self[1] + self[0]) / (slope**2 + 1)
        y = (slope**2 + self[1] + slope * self[0]) / (slope**2 + 1)
        return Vector2D(x, y)


    ## Interpolate between us and alt with the given bias
    def interpolate(self, alt, altWeight):
        delta = alt.sub(self).multiply(altWeight)
        return self.add(delta)


    ## Clamp our values to the given maximal component magnitudes
    def clamp(self, clamp):
        (x, y) = (self[0], self[1])
        if abs(self[0]) > clamp[0]:
            x = clamp[0] * cmp(x, 0)
        if abs(self[1]) > clamp[1]:
            y = clamp[1] * cmp(self[1], 0)
        return Vector2D(x, y)


    ## Convert to gridspace from realspace
    def toGridspace(self):
        x = int(self[0] / constants.blockSize)
        y = int(self[1] / constants.blockSize)
        return Vector2D(x, y)


    ## Convert to realspace from gridspace
    def toRealspace(self):
        x = self[0] * constants.blockSize
        y = self[1] * constants.blockSize
        return Vector2D(x, y)


    ## Determine if any of the given points are close to us
    def fuzzyMatchList(self, alts):
        for alt in alts:
            if self.distance(alt) < constants.DELTA:
                return True
        return False


    ## Provide iteration over all 8 adjacent locations.
    def perimeter(self):
        for offset in perimeterOrder:
            yield self.add(offset)


    ## Provide iteration over the 4 immediately adjacent locations
    def NEWSPerimeter(self):
        for offset in NEWSPerimeterOrder:
            yield self.add(offset)


    ## Convert to string
    def __str__(self):
        return "<" + str(self[0]) + ", " + str(self[1]) + ">"


## List of offsets in North, East, West, South directions. Used for iterating 
# over spaces adjacent to a given space in the map.
NEWSPerimeterOrder = [Vector2D(0, -1), Vector2D(1, 0),
                      Vector2D(-1, 0), Vector2D(0, 1)]
## List of offsets in all 8 directions. Used for iterating over spaces adjacent
# to a given space in the map.
perimeterOrder = [Vector2D(0, -1), Vector2D(1, -1), Vector2D(1, 0),
                  Vector2D(1, 1), Vector2D(0, 1), Vector2D(-1, 1),
                  Vector2D(-1, 0), Vector2D(-1, -1)]

