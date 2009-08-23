import constants

import os

## TerrainInfo is a container class that describes the local terrain, which 
# determines the graphics used for terrain blocks, the available background 
# props, the selection of tunnel types, and so on. A given location is part of 
# a large zone and a smaller region which is a part of that zone. For example, 
# the "cooled lava" region would be a part of the "hot" zone.
class TerrainInfo:

    ## Instantiate an instance of the class.
    def __init__(self, zone, region):
        self.zone = zone
        self.region = region


    ## Return true if there is a directory for this terrain.
    def getIsValid(self):
        path = os.path.join(constants.spritePath, 'terrain', self.zone, self.region)
        return os.path.exists(path)


    ## Equality check
    def __eq__(self, alt):
        return self.zone == alt.zone and self.region == alt.region


    ## Inequality check
    def __ne__(self, alt):
        return not self.__eq__(alt)


    ## Convert to string
    def __str__(self):
        return "[Terrain: zone " + self.zone + ", region " + self.region + "]"

