import constants

## A Range1D is simply a one-dimensional range, used when projecting Polygon 
# instances onto vectors. 
cdef class Range1D:
    def __new__(self, min = constants.BIGNUM, max = -constants.BIGNUM):
        self.min = min
        self.max = max


    ## Return true if the provided scalar is in our range
    cpdef public bool contains(Range1D self, double value):
        return value >= self.min and value <= self.max

    
    ## Clamp the given value so it is contained by us.
    cpdef public double clamp(Range1D self, double value):
        return min(self.max, max(self.min, value))


    ## Add an offset to min and max
    cpdef public Range1D addScalar(Range1D self, double value):
        return Range1D(self.min + value, self.max + value)


    ## Extend us so that we contain the given value.
    cpdef public Range1D extend(Range1D self, double value):
        return Range1D(min(self.min, value), max(self.max, value))


    ## Return the amount of overlap between ourself and the given range.
    cpdef public double getOverlap(Range1D self, Range1D range):
        result = -1
        if (self.max >= range.min and self.max <= range.max and
            self.min <= range.min):
            # us:   <----->
            # them:    <----->
            result = self.max - range.min
        elif (range.max >= self.min and range.max <= self.max and
              range.min <= self.min):
            # us:      <----->
            # them: <----->
            result = range.max - self.min
        elif (self.max >= range.min and self.max <= range.max and
              self.min >= range.min and self.min <= range.max):
            # us:     <-->
            # them: <------>
            result = min(range.max - self.min, self.max - range.min)
        elif (range.max >= self.min and range.max <= self.max and
              range.min >= self.min and range.min <= self.max):
            # us:   <------>
            # them:   <-->
            result = min(self.max - range.min, range.max - self.min)
        elif (abs(self.max - range.max) <= constants.EPSILON and
              abs(self.min - range.min) <= constants.EPSILON):
            result = self.max - self.min
        return result


    def __str__(self):
        return "range [%f, %f]" % (self.min, self.max)

