import constants

## A Range1D is simply a one-dimensional range, used when projecting Polygon 
# instances onto vectors. 
cdef class Range1D:
    cdef public double min
    cdef public double max
    cpdef public bool contains(Range1D self, double value)
    cpdef public double clamp(Range1D self, double value)
    cpdef public Range1D addScalar(Range1D self, double value)
    cpdef public Range1D extend(Range1D self, double value)
    cpdef public double getOverlap(Range1D self, Range1D range)


