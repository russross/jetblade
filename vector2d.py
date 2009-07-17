import constants

import math


## This class represents a two-dimensional vector. Many functions are provided
# that allow modification of Vector2Ds; however, none of them alter the 
# specific instance (instead returning new Vector2D instances that you can
# assign to variables). Equality and inequality operators are provided;
# though they do a fuzzy match and so cost more than you might otherwise
# expect.
# \todo While using these instead of tuples/lists makes the code much cleaner,
# it's also much slower. Convert this module into a C module for more speed.
class Vector2D:
    ## Instantiate a new vector. We accept either one or two arguments. If 
    # one, we assume the argument is a tuple whose first two elements are 
    # the values we want. Otherwise we use the two arguments as our values.
    # If you want to make a Vector2D from another Vector2D, use the copy()
    # function.
    def __init__(self, first, second = None):
        if second is None:
            self.x = first[0]
            self.y = first[1]
        else:
            self.x = first
            self.y = second


    ## Return a copy of us.
    def copy(self):
        return Vector2D(self.x, self.y)


    ## Return a tuple of our values.
    def tuple(self):
        return (self.x, self.y)


    ## Add alt to us. Return a copy of ourselves.
    def add(self, alt):
        x = self.x + alt.x
        y = self.y + alt.y
        return Vector2D(x, y)


    ## Add a scalar to both x and y.
    def addScalar(self, addend):
        x = self.x + addend
        y = self.y + addend
        return Vector2D(x, y)


    ## As add, but subtract instead
    def sub(self, alt):
        x = self.x - alt.x
        y = self.y - alt.y
        return Vector2D(x, y)


    ## As add, but multiply by a scalar
    def multiply(self, multiplicand):
        x = self.x * multiplicand
        y = self.y * multiplicand
        return Vector2D(x, y)


    ## As add, but divide by a scalar.
    def divide(self, divisor):
        x = self.x / divisor
        y = self.y / divisor
        return Vector2D(x, y)


    ## As add, but average instead.
    def average(self, alt):
        x = (self.x + alt.x) / 2.0
        y = (self.y + alt.y) / 2.0
        return Vector2D(x, y)


    ## Return the result of rounding us to the nearest int.
    def round(self):
        return Vector2D(int(self.x + .5), int(self.y + .5))


    ## Flatten to ints
    def int(self):
        return Vector2D(int(self.x), int(self.y))


    ## Return the distance from us to alt.
    def distance(self, alt):
        return math.sqrt((self.x - alt.x)**2 + (self.y - alt.y)**2)


    ## Return the distance if moving diagonally counts the same as moving
    # horizontally (generates square "circles").
    def distanceSquare(self, alt):
        return max(abs(self.x - alt.x), abs(self.y - alt.y))


    ## Return our magnitude
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)


    ## Return the magnitude squared, to avoid the sqrt call when it's not needed
    def magnitudeSquared(self):
        return self.x**2 + self.y**2


    ## Return our normalized form
    def normalize(self):
        return self.divide(self.magnitude())


    ## Return the inverted form
    def invert(self):
        return Vector2D(-self.y, self.x)


    ## Return our slope
    def slope(self):
        if abs(self.x) < constants.EPSILON:
            return constants.BIGNUM * cmp(self.y, 0)
        return self.y / self.x


    ## Return our angle
    def angle(self):
        return math.atan2(self.y, self.x)


    ## Return the project of ourselves onto the given vector
    def projectOnto(self, alt):
        if abs(alt.x) < constants.EPSILON:
            # alt is vertical
            return Vector2D(0, self.y)
        slope = alt.slope()
        x = (slope * self.y + self.x) / (slope**2 + 1)
        y = (slope**2 + self.y + slope * self.x) / (slope**2 + 1)
        return Vector2D(x, y)


    ## Interpolate between us and alt with the given bias
    def interpolate(self, alt, altWeight):
        delta = alt.sub(self).multiply(altWeight)
        return self.add(delta)


    ## Clamp our values to the given maximal component magnitudes
    def clamp(self, clamp):
        (x, y) = (self.x, self.y)
        if abs(self.x) > clamp.x:
            x = clamp.x * cmp(x, 0)
        if abs(self.y) > clamp.y:
            y = clamp.y * cmp(self.y, 0)
        return Vector2D(x, y)


    ## Convert to gridspace from realspace
    def toGridspace(self):
        x = int(self.x / constants.blockSize)
        y = int(self.y / constants.blockSize)
        return Vector2D(x, y)


    ## Convert to realspace from gridspace
    def toRealspace(self):
        x = self.x * constants.blockSize
        y = self.y * constants.blockSize
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
        return "<" + str(self.x) + ", " + str(self.y) + ">"


    ## For use in dicts. For now this is short and simple and error-prone.
    # \todo Look up a good hash function to prevent collisions here.
    def __hash__(self):
        return int(self.x * constants.BIGNUM + self.y)


    ## Equality operator. Uses abs and subtraction instead of 
    # Vector2D.distance() to avoid the sqrt invocation; informal tests have
    # shown this to be faster.
    def __eq__(self, alt):
        return (abs(self.x - alt.x) < constants.EPSILON and 
                abs(self.y - alt.y) < constants.EPSILON)


    ## Inequality operator
    def __ne__(self, alt):
        return not self.__eq__(alt)


## List of offsets in North, East, West, South directions. Used for iterating 
# over spaces adjacent to a given space in the map.
NEWSPerimeterOrder = [Vector2D(0, -1), Vector2D(1, 0),
                      Vector2D(-1, 0), Vector2D(0, 1)]
## List of offsets in all 8 directions. Used for iterating over spaces adjacent
# to a given space in the map.
perimeterOrder = [Vector2D(0, -1), Vector2D(1, -1), Vector2D(1, 0),
                  Vector2D(1, 1), Vector2D(0, 1), Vector2D(-1, 1),
                  Vector2D(-1, 0), Vector2D(-1, -1)]

