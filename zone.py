import constants
import logger
import range1d
from vector2d import Vector2D

import sys
import os
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
        path = os.path.join(constants.mapPath, 'zones')
        path = path.replace(os.sep, '.')
        zoneConfigModule = __import__(path, globals(), locals(), ['zones'])
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
        logger.fatal("Failed to load zone data:",e)


## Place a starting point for each zone in the area [[0, 1], [0, 1]] such
# that each zone's point is in that zone's elevation range and all of the
# zones are as far away from each other as possible.
# This is used for laying out the region map in the Map instance.
def placeZones(zoneConfigData):
    zonePoints = dict()
    for zoneName, zoneData in zoneConfigData.iteritems():
        elevationRange = zoneData['elevationRange']
        zonePoints[zoneName] = Vector2D(random.random(),
                random.uniform(elevationRange[0], elevationRange[1]))
    
    for i in xrange(0, zonePlacementIterations):
        newPoints = dict()
        for zoneName, zoneLoc in zonePoints.iteritems():
            vector = Vector2D(0, 0)
            for altName, altLoc in zonePoints.iteritems():
                if zoneName == altName:
                    continue
                distance = zoneLoc.distance(altLoc)
                direction = altLoc.sub(zoneLoc).normalize()
                vector = vector.add(direction.multiply(zoneGravityMultiplier / distance))

            xRange = range1d.Range1D(0, 1)
            yRange = range1d.Range1D(zoneConfigData[zoneName]['elevationRange'][0],
                    zoneConfigData[zoneName]['elevationRange'][1])
            newLoc = vector.add(zoneLoc)
            newLoc = Vector2D(xRange.clamp(newLoc.x), yRange.clamp(newLoc.y))
            newPoints[zoneName] = newLoc
        zonePoints = newPoints

    return zonePoints

