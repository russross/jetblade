import constants

import math

## This class represents a two-dimensional vector. Many functions are provided
# that allow modification of Vector2Ds; however, none of them alter the 
# specific instance (instead returning new Vector2D instances that you can
# assign to variables). Equality and inequality operators are provided;
# though they do a fuzzy match and so cost more than you might otherwise
# expect.
cdef class Vector2D:

    ## Instantiate a Vector2D. We accept either two coordinates, or a single
    # argument which is assumed to be a tuple or list with at least two 
    # elements. If you want to make a Vector2D from another Vector2D, 
    # use the copy function.
    def __new__(self, first, second = None, magnitude = -1):
        if second is None:
            self.x = first[0]
            self.y = first[1]
        else:
            self.x = first
            self.y = second
        ## Cached copy of our magnitude.
        self.cachedMagnitude = magnitude


    ## Return a copy of us.
    def copy(self):
        return Vector2D(self.x, self.y, self.cachedMagnitude)


    ## Allows easy casting to an int
    property ix:
        def __get__(self):
            return int(self.x)
        def __set__(self, value):
            self.x = int(value)


    ## Allows easy casting to an int
    property iy:
        def __get__(self):
            return int(self.y)
        def __set__(self, value):
            self.y = int(value)


    ## Add alt to us. Return a copy of ourselves.
    cpdef public Vector2D add(Vector2D self, Vector2D alt):
        return Vector2D(self.x + alt.x, self.y + alt.y)


    ## Add a scalar to both x and y.
    cpdef public Vector2D addScalar(Vector2D self, double addend):
        return Vector2D(self.x + addend, self.y + addend)


    ## Add a scalar to just X
    cpdef public Vector2D addX(Vector2D self, double addend):
        return Vector2D(self.x + addend, self.y)

    
    ## Add a scalar to just Y
    cpdef public Vector2D addY(Vector2D self, double addend):
        return Vector2D(self.x, self.y + addend)


    ## As add, but subtract instead
    cpdef public Vector2D sub(Vector2D self, Vector2D alt):
        return Vector2D(self.x - alt.x, self.y - alt.y)


    ## As add, but multiply by a scalar
    cpdef public Vector2D multiply(Vector2D self, double multiplicand):
        return Vector2D(self.x * multiplicand, self.y * multiplicand)


    ## As add, but divide by a scalar.
    cpdef public Vector2D divide(Vector2D self, double divisor):
        return Vector2D(self.x / divisor, self.y / divisor)


    ## Return a Vector2D instance that is us with the desired X component
    cpdef public Vector2D setX(Vector2D self, double xVal):
        return Vector2D(xVal, self.y)


    ## As setX for the Y component
    cpdef public Vector2D setY(Vector2D self, double yVal):
        return Vector2D(self.x, yVal)


    ## As add, but average instead.
    cpdef public Vector2D average(Vector2D self, Vector2D alt):
        return Vector2D((self.x + alt.x) / 2.0, (self.y + alt.y) / 2.0)


    ## Return the result of rounding us to the nearest int.
    cpdef public Vector2D round(Vector2D self):
        return Vector2D(int(self.x + .5), int(self.y + .5))


    ## Flatten to ints
    cpdef public Vector2D toInt(Vector2D self):
        return Vector2D(int(self.x), int(self.y))


    ## Rotate by the specified angle, about the origin
    cpdef public Vector2D rotate(Vector2D self, double angle):
        cpdef double curAngle = self.angle()
        cpdef double magnitude = self.magnitude()
        return Vector2D(magnitude * math.cos(angle + curAngle),
                        magnitude * math.sin(angle + curAngle))


    ## Return the distance from us to alt.
    cpdef public double distance(Vector2D self, Vector2D alt):
        return math.sqrt((self.x - alt.x)**2 + (self.y - alt.y)**2)


    ## Return the distance from us to alt, squared.
    cpdef public double distanceSquared(Vector2D self, Vector2D alt):
        return (self.x - alt.x)**2 + (self.y - alt.y)**2


    ## Return the distance if moving diagonally counts the same as moving
    # horizontally (generates square "circles").
    cpdef public double gridDistance(Vector2D self, Vector2D alt):
        return max(abs(self.x - alt.x), abs(self.y - alt.y))


    ## Return our magnitude
    cpdef public double magnitude(Vector2D self):
        if self.cachedMagnitude == -1:
            self.cachedMagnitude = math.sqrt(self.x**2 + self.y**2)
        return self.cachedMagnitude


    ## Return the magnitude squared, to avoid the sqrt call when it's not needed
    cpdef public double magnitudeSquared(Vector2D self):
        return self.x**2 + self.y**2


    ## Return our normalized form
    cpdef public Vector2D normalize(Vector2D self):
        return self.divide(self.magnitude())


    ## Return the inverted form
    cpdef public Vector2D invert(Vector2D self):
        return Vector2D(-self.y, self.x)


    ## Return our slope
    cpdef public double slope(Vector2D self):
        if abs(self.x) < constants.EPSILON:
            return constants.BIGNUM * cmp(self.y, 0)
        return self.y / self.x


    ## Return our angle
    cpdef public double angle(Vector2D self):
        return math.atan2(self.y, self.x)


    ## Return the angle made with the alternate vector.
    cpdef public double angleWithVector(Vector2D self, Vector2D alt):
        return math.acos(alt.normalize().dot(self.normalize()))


    ## Return the project of ourselves onto the given vector
    cpdef public Vector2D projectOnto(Vector2D self, Vector2D alt):
        if abs(alt.x) < constants.EPSILON:
            # alt is vertical
            return Vector2D(0, self.y)
        cdef double slope = alt.slope()
        cdef double x = (slope * self.y + self.x) / (slope**2 + 1)
        cdef double y = (slope**2 + self.y + slope * self.x) / (slope**2 + 1)
        return Vector2D(x, y)


    ## Return the multiplier of the given vector that gets it closest to us.
    # In other words, project us onto the given vector, and get the distance
    # from that projection to the origin.
    cpdef public double getComponentOn(Vector2D self, Vector2D vector):
        cdef Vector2D projection = self.projectOnto(vector)
        if abs(vector.x) > constants.EPSILON:
            return projection.x / vector.x
        return projection.y / vector.y


    ## Perform a dot product.
    cpdef public double dot(Vector2D self, Vector2D alt):
        return self.x * alt.x + self.y * alt.y


    ## Interpolate between us and alt with the given bias
    cpdef public Vector2D interpolate(Vector2D self, Vector2D alt, double altWeight):
        delta = alt.sub(self).multiply(altWeight)
        return self.add(delta)


    ## Clamp our values to the given maximal component magnitudes
    cpdef public Vector2D clamp(Vector2D self, Vector2D clamp):
        cdef double x = self.x
        cdef double y = self.y
        if abs(self.x) > clamp.x:
            x = clamp.x * cmp(x, 0)
        if abs(self.y) > clamp.y:
            y = clamp.y * cmp(self.y, 0)
        return Vector2D(x, y)


    ## Convert to gridspace from realspace
    cpdef public Vector2D toGridspace(Vector2D self):
        return Vector2D(int(self.x / constants.blockSize), 
                        int(self.y / constants.blockSize))


    ## Convert to realspace from gridspace
    cpdef public Vector2D toRealspace(Vector2D self):
        x = self.x * constants.blockSize
        y = self.y * constants.blockSize
        return Vector2D(self.x * constants.blockSize, 
                        self.y * constants.blockSize)


    ## Convert to a tuple
    cpdef public tuple tuple(Vector2D self):
        return (self.x, self.y)


    ## Determine if any of the given points are close to us
    cpdef public bint fuzzyMatchList(Vector2D self, list alts):
        for alt in alts:
            if self.distance(alt) < constants.DELTA:
                return True
        return False


    ## Provide iteration over all 8 adjacent locations.
    cpdef public list perimeter(Vector2D self):
        cdef list result = []
        for offset in perimeterOrder:
            result.append(self.add(offset))
        return result


    ## Provide iteration over the 4 immediately adjacent locations
    cpdef public list NEWSPerimeter(Vector2D self):
        cdef list result = []
        for offset in NEWSPerimeterOrder:
            result.append(self.add(offset))
        return result


    ## Allow access through array indexing.
    def __getitem__(self, i):
        if i == 0:
            return self.x
        return self.y


    ## Hashing. Two Vector2Ds may hash to the same value without being 
    # the same object.
    # Shifting X up by 20 gives us a range of about a million to play in before
    # collisions start becoming a problem.
    def __hash__(self):
        return hash(int(self.x) << 20) ^ hash(int(self.y))
    

    ## Comparison test. Does not order vectors; just tests for equality.
    def __richcmp__(self, alt, int op):
        if type(self) != type(alt):
            isEqual = False
        else:
            isEqual = (abs(self.x - alt.x) < constants.EPSILON) and (abs(self.y - alt.y) < constants.EPSILON)
        if (isEqual and op == 2) or (not isEqual and op == 3):
            return True
        return False


    ## Convert to string (serialize)
    def __repr__(self):
        return "<Vector2D (" + str(self.x) + ", " + str(self.y) + ")>"


    ## Convert to string (pretty-print)
    def __str__(self):
        return "<" + str(self.x) + ", " + str(self.y) + ">"


## List of offsets in North, East, West, South directions. Used for iterating 
# over spaces adjacent to a given space in the map.
NEWSPerimeterOrder = [Vector2D(0, -1), Vector2D(1, 0),
                      Vector2D(-1, 0), Vector2D(0, 1)]
## List of offsets in all 8 directions. Used for iterating over spaces adjacent
# to a given space in the map.
perimeterOrder = [Vector2D(0, -1), Vector2D(1, -1), Vector2D(1, 0),
                  Vector2D(1, 1), Vector2D(0, 1), Vector2D(-1, 1),
                  Vector2D(-1, 0), Vector2D(-1, -1)]

