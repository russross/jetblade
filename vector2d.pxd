
cdef class Vector2D:
    cdef public double x
    cdef public double y
    cpdef public Vector2D add(Vector2D self, Vector2D alt)
    cpdef public Vector2D addScalar(Vector2D self, double addend)
    cpdef public Vector2D addX(Vector2D self, double addend)
    cpdef public Vector2D addY(Vector2D self, double addend)
    cpdef public Vector2D sub(Vector2D self, Vector2D alt)
    cpdef public Vector2D multiply(Vector2D self, double multiplicand)
    cpdef public Vector2D divide(Vector2D self, double divisor)
    cpdef public Vector2D setX(Vector2D self, double xVal)
    cpdef public Vector2D setY(Vector2D self, double yVal)
    cpdef public Vector2D average(Vector2D self, Vector2D alt)
    cpdef public Vector2D round(Vector2D self)
    cpdef public Vector2D toInt(Vector2D self)
    cpdef public double distance(Vector2D self, Vector2D alt)
    cpdef public double distanceSquared(Vector2D self, Vector2D alt)
    cpdef public double gridDistance(Vector2D self, Vector2D alt)
    cpdef public double magnitude(Vector2D self)
    cpdef public double magnitudeSquared(Vector2D self)
    cpdef public Vector2D normalize(Vector2D self)
    cpdef public Vector2D invert(Vector2D self)
    cpdef public double slope(Vector2D self)
    cpdef public double angle(Vector2D self)
    cpdef public Vector2D projectOnto(Vector2D self, Vector2D alt)
    cpdef public double getComponentOn(Vector2D self, Vector2D vector)
    cpdef public Vector2D interpolate(Vector2D self, Vector2D alt, double altWeight)
    cpdef public Vector2D clamp(Vector2D self, Vector2D clamp)
    cpdef public Vector2D toGridspace(Vector2D self)
    cpdef public Vector2D toRealspace(Vector2D self)
    cpdef public tuple tuple(Vector2D self)
    cpdef public bint fuzzyMatchList(Vector2D self, list alts)
    cpdef public list perimeter(Vector2D self)
    cpdef public list NEWSPerimeter(Vector2D self)
