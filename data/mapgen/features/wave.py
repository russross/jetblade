import straight
import constants
import util
import math
import random


## Number of waves to make in the tunnel.
waveTunnelNumCycles = 3
## Magnitude, in absolute distance, of each wave.
waveTunnelMagnitude = 3 * constants.blockSize

def getClassName():
    return 'WaveTunnel'

## Carve a sinusoidal wave tunnel from the self.sector's 
# parent to its endpoint.
class WaveTunnel(straight.StraightTunnel):
    def carveTunnel(self):
        start = self.sector.parent.loc
        end = self.sector.loc
        width = self.sector.getTunnelWidth()
        dist = util.pointPointDistance(start, end)
        # Get the multiplier needed to obtain the desired number of cycles.
        # E.g. y = sin(.2pi*x) == 1 cycle per 10 traveled
        rateMultiplier = 2 * waveTunnelNumCycles * math.pi / dist
        if random.random() < .5:
            rateMultiplier *= -1

        lineAngle = math.atan2(end[1] - start[1], end[0] - start[0])

        for baseX in range(0, int(dist), constants.blockSize):
            baseY = math.sin(baseX * rateMultiplier) * waveTunnelMagnitude
            # Rotate baseX, baseY to be aligned with start->end
            r = math.sqrt(baseX**2 + baseY**2)
            theta = math.atan2(baseY, baseX)
            theta += lineAngle
            x = r * math.cos(theta) + start[0]
            y = r * math.sin(theta) + start[1]
            self.map.plantSeed((x, y), self.sector, width)


    def shouldCheckAccessibility(self):
        return straight.StraightTunnel.shouldCheckAccessibility(self, 1)

