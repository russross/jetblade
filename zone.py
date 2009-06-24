import constants
import util
import sys
import random

zonePlacementIterations = 100
zoneGravityMultiplier = -.005


## A Zone is a large-scale grouping of similar Region instances. Zones try to 
# place themselves at specific elevation ranges. 
class Zone:
    def __init__(self, name, spaces, regions):
        self.name = name
        self.elevationRange = elevationRange
        self.regions = regions


## A Region is a specific portion of terrain within a given Zone. 
# Each sector of the map is part of a single Region. 
class Region:
    def __init__(self, name, spaces):
        ## The name of the Region, for lookup in the data files.
        self.name = name
        ## How likely this Region is to occur within the Zone, and thus, 
        # how much of the Zone will be composed of this Region relative to 
        # other Regions. 
        self.frequency = frequency


## Load all Zone and Region data from the zones.py file. 
def loadZoneData():
    try:
        zoneConfigModule = __import__('zones', globals(), locals(), ['zones'])
        zoneConfigData = zoneConfigModule.zones
        # Pull out the frequency information to a separate dict
        for zoneName, zoneData in zoneConfigData.iteritems():
            regions = zoneData['regions']
            weights = dict()
            maxWeight = 0
            biggestRegion = None
            for regionName, regionData in regions.iteritems():
                weight = regionData['frequency']
                weights[regionName] = weight
                if maxWeight < weight:
                    maxWeight = weight
                    biggestRegion = regionName
                if 'aligned' not in regionData:
                    # Default setting: don't align tunnels
                    regionData['aligned'] = 0
            zoneData['biggestRegion'] = biggestRegion
            zoneData['regionWeights'] = weights
        return zoneConfigData
    except Exception, e:
        print "Failed to load zone data:",e
        sys.exit()


## Place a starting point for each zone in the area [[0, 1], [0, 1]] such
# that each zone's point is in that zone's elevation range and all of the
# zones are as far away from each other as possible.
# This is used for laying out the region map in the Map instance.
def placeZones(zoneConfigData):
    zonePoints = dict()
    for zoneName, zoneData in zoneConfigData.iteritems():
        elevationRange = zoneData['elevationRange']
        zonePoints[zoneName] = [random.random(), random.uniform(elevationRange[0], elevationRange[1])]
    
    for i in range(0, zonePlacementIterations):
        newPoints = dict()
        for zoneName, zoneLoc in zonePoints.iteritems():
            vector = [0, 0]
            for altName, altLoc in zonePoints.iteritems():
                if zoneName == altName:
                    continue
                distance = util.pointPointDistance(zoneLoc, altLoc)
                direction = util.getNormalizedVector(zoneLoc, altLoc)
                vector[0] += direction[0] / distance * zoneGravityMultiplier
                vector[1] += direction[1] / distance * zoneGravityMultiplier
            newLoc = list(util.addVectors(zoneLoc, vector))
            newLoc[0] = max(newLoc[0], 0)
            newLoc[0] = min(newLoc[0], 1)
            newLoc[1] = max(newLoc[1], zoneConfigData[zoneName]['elevationRange'][0])
            newLoc[1] = min(newLoc[1], zoneConfigData[zoneName]['elevationRange'][1])
            newPoints[zoneName] = newLoc
        zonePoints = newPoints

    return zonePoints

