import constants

## A Range1D is simply a one-dimensional range, used when projecting Polygon 
# instances onto vectors. 
class Range1D:
    def __init__(self, min = constants.BIGNUM, max = -constants.BIGNUM):
        self.min = min
        self.max = max


    ## Return true if the provided scalar is in our range
    def contains(self, value):
        return value > self.min and value < self.max

    ## Return the amount of overlap between ourself and the given range.
    def getOverlap(self, range):
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

