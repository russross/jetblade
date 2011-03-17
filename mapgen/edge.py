import game
import constants
import generator
import seed
import util
import logger
from vector2d import Vector2D
from range1d import Range1D

import math
import random
import pygame
import os


## How often to try placing platforms.
platformInterval = 7

# Wallwalker parameters
## How many steps in the wallwalker algorithm to aggregate to determine the 
# local slope of the tunnel wall.
slopeAveragingBracketSize = 5
## If a wallwalker takes longer than this, give up. 
maxWallwalkerSteps = 2500

## Distance from straight vertical to consider a tunnel to be vertical for
# accessibility tests
verticalTunnelAngleFuzz = math.pi / 20.0
## Tunnels shorter than this are ignored.
minVerticalTunnelLength = 6 * constants.blockSize
## Different ways of placing platforms down in vertical tunnels.
# -1 = left, 0 = middle, 1 = right
verticalTunnelPlatformPatterns = [[-1, 0, 1], [1, 0, -1], [1, 0, -1, 0]]
## Vertical distance between platforms when fixing vertical tunnel accessibility
verticalTunnelPlatformGap = 4


## See http://en.wikipedia.org/w/index.php?title=Marching_squares&oldid=354746853
# Values of each subsquare (for determining index into this list) are:
# 8 1
# 4 2
marchingSquares = [Vector2D(1, 0), Vector2D(1, 0), Vector2D(0, 1), 
                   Vector2D(0, 1), Vector2D(-1, 0), Vector2D(-1, 0), 
                   Vector2D(-1, 0), Vector2D(-1, 0), Vector2D(0, -1), 
                   Vector2D(1, 0), Vector2D(0, -1), Vector2D(0, 1), 
                   Vector2D(0, -1), Vector2D(1, 0), Vector2D(0, -1), 
                   None]

slopePlatformRequirement = math.pi / 8.0
## Surface normal ranges that indicate walls.
wallAngles = [Range1D(-slopePlatformRequirement,
                      slopePlatformRequirement),
              Range1D(math.pi - slopePlatformRequirement,
                      math.pi + slopePlatformRequirement)]


## MapEdges are connections between two GraphNodes. They act as the primary
# interface between the symbolic graph-based map and the 2D array of blocks
# that the player actually sees.
class MapEdge:
    ## Create a new MapEdge instance. Determine the local zone and region
    # information, pick a tunnel feature type, and determine our tunnel width.
    # The two input parameters are the two GraphNode instances that this edge
    # connects. They may be the same, in which case this edge is considered
    # to be a "junction" edge (i.e. placed at the intersection of two normal
    # edges). This allows us to unify the map-mutating code that creates
    # junctions with that which creates tunnels.
    def __init__(self, start, end):
        self.id = constants.globalId
        constants.globalId += 1

        ## Start of the edge.
        self.start = start
        ## End of the edge.
        self.end = end

        ## Individual open (non-wall) spaces in the map that belong to this 
        # edge.
        self.spaces = set()

        ## Information about the terrain we are in.
        # Map our location to the region map to get our terrain info.
        self.terrain = game.map.getTerrainInfoAtGridLoc(
                self.start.toGridspace()
        )

        # Select tunnel type and load the relevant module.
        ## The tunnel feature type, e.g. straight, bumpy, staircase.
        self.tunnelType = util.pickWeightedOption(
                game.map.getRegionInfo(self.terrain, 'tunnelTypes')
        )

        ## The module that contains the information needed to create our tunnel
        # feature type.
        self.featureModule = game.featureManager.loadFeature(
                self.tunnelType, self
        )

        ## This color is used for debugging output only.
        self.color = [random.randint(64,255) for i in xrange(3)]
    

    ## Return true if this edge represents a junction in the graph
    def isJunction(self):
        return self.start is self.end


    ## Passthrough to self.featureModule.carveTunnel.
    def carveTunnel(self):
        if not self.isJunction():
            self.featureModule.carveTunnel()


    ## Add any features we require now that tunnels and rooms have been 
    # carved out.
    def createFeatures(self):
        self.featureModule.createFeature()

        environment = util.pickWeightedOption(
                game.map.getRegionInfo(self.terrain, 'environments')
        )
        if environment is not None:
            effect = game.envEffectManager.loadEnvEffect(environment)
            effect.createRegion(game.map, self)


    ## Calculate the bounds of the open space occupied by our sector. This is
    # useful for some tunnel features to constrain the area they try to mutate.
    def getSectorBounds(self):
        minX = constants.BIGNUM
        minY = constants.BIGNUM
        maxX = -constants.BIGNUM
        maxY = -constants.BIGNUM
        for loc in self.spaces:
            minX = min(minX, loc.x)
            minY = min(minY, loc.y)
            maxX = max(maxX, loc.x)
            maxY = max(maxY, loc.y)
        return (minX, minY, maxX, maxY)


    ## Get the points closest to our start and end that are still in our
    # sector. This is useful for some tunnel features (e.g. the maze feature).
    def getStartAndEndLoc(self):
        startLoc = self.start.toGridspace()
        endLoc = self.end.toGridspace()
        delta = endLoc.sub(startLoc).normalize()
        while not self.getIsOurSpace(startLoc):
            startLoc = startLoc.add(delta)
            if startLoc.distance(endLoc) < 1:
                return (None, None)
        while not self.getIsOurSpace(endLoc):
            endLoc = endLoc.sub(delta)
            if startLoc.distance(endLoc) < 1:
                return (None, None)

        startLoc = startLoc.toInt()
        endLoc = endLoc.toInt()
        return (startLoc, endLoc)


    ## Measure the distance, in gridspace, from the given loc to either a wall
    # or the end of our space.
    def getDistToCeiling(self, loc):
        curLoc = Vector2D(loc.x, loc.y - 1)
        dist = 1
        while self.getIsOurSpace(curLoc):
            curLoc = curLoc.addY(-1)
            dist += 1
        return dist


    def getTunnelWidth(self):
        return constants.blockSize * random.choice(
                game.map.getRegionInfo(self.terrain, 'tunnelWidths')
        )


    def getTunnelLength(self):
        return constants.blockSize * random.choice(
                game.map.getRegionInfo(self.terrain, 'tunnelLengths')
        )


    ## Get the radius of an open space to carve out to connect two tunnel
    # segments.
    def getJunctionRadius(self):
        widths = game.map.getRegionInfo(self.terrain, 'tunnelWidths')
        return widths[0] * constants.blockSize


    ## Carve an open space out around our center, only if we're a junction
    # in the graph. The spacefilling automaton that we use to create open
    # tunnels walls everything off wherever two edges in the map meet; thus, 
    # we need to manually open up any walls that are within a certain radius
    # of a junction.
    def createJunction(self):
        if not self.isJunction():
            return

        # We're going to lay claim to some points during this process. Update
        # their ownership when we're done so we don't let ones we've already
        # claimed convince us that it's okay to take more.
        claimedPoints = set()

        center = self.start.toGridspace()
        radius = int(self.getJunctionRadius() / constants.blockSize)

        # Iterate over points in the accepted area, claiming them if they belong
        # to edges that we're related to.
        for x in xrange(max(center.ix - radius, 1),
                        min(center.ix + radius, game.map.numCols - 1)):
            for y in xrange(max(center.iy - radius, 1),
                            min(center.iy + radius, game.map.numRows - 1)):
                point = Vector2D(x, y)
                if point in game.map.deadSeeds:
                    if self.start.isEdgeRelated(game.map.deadSeeds[point].owner):
                        claimedPoints.add(point)

        # Convert each claimed point into open space. Then check its neighbors,
        # and fill them with walls if they aren't related to us.
        for point in claimedPoints:
            game.map.blocks[point.ix][point.iy] = generator.BLOCK_EMPTY
            game.map.assignSpace(point, self)

            # Patch walls around the deleted space
            for nearPoint in point.perimeter():
                if not game.map.getIsInBounds(nearPoint):
                    continue
                # If we hit a space that's not a wall or open space, or
                # if we hit a space that's owned by a node of the graph
                # that we aren't connected to, put a wall in.
                altEdge = None
                if nearPoint in game.map.deadSeeds:
                    altEdge = game.map.deadSeeds[nearPoint].owner
                if (game.map.blocks[nearPoint.ix][nearPoint.iy] == generator.BLOCK_UNALLOCATED or
                        (altEdge is not None and
                         not self.start.isEdgeRelated(altEdge))
                   ):
                    game.map.blocks[nearPoint.ix][nearPoint.iy] = generator.BLOCK_WALL
                    game.map.deadSeeds[nearPoint] = seed.Seed(self, 0, constants.BIGNUM)


    ## Walk the walls of our space, trying to add Furniture instances where
    # appropriate.
    def placeFurniture(self):
        if self.featureModule.shouldCheckAccessibility():
            furnitureFrequency = game.map.getRegionInfo(self.terrain, 'furnitureFrequency')
            for (space, angle) in self.walkWalls(3, furnitureFrequency, True):
                normal = Vector2D(math.cos(angle), math.sin(angle))
                furniture = game.furnitureManager.pickFurniture(self.terrain, space, normal)
                if furniture is not None:
                    game.map.addFurniture(furniture)


    ## Place platforms in our space to help make the map accessible to the
    # player.
    def fixAccessibility(self):
        if self.isJunction():
            self.fixAccessibilityWallwalk()
        elif self.featureModule.shouldCheckAccessibility():
            # Determine which accessibility-fixing algorithm to use.
            if self.start.distance(self.end) > minVerticalTunnelLength:
                angle = self.getAngle()
                if (abs(angle - math.pi / 2.0) < verticalTunnelAngleFuzz or
                        abs(angle - 3*math.pi / 2.0) < verticalTunnelAngleFuzz):
                    self.fixAccessibilityVertical()
                else:
                    self.fixAccessibilityWallwalk()
            else:
                self.fixAccessibilityWallwalk()


    ## Ensure that vertical shaft tunnels are accessible by making a 
    # "staircase" out of floating platforms, using one of a few placement
    # patterns.
    def fixAccessibilityVertical(self):
        # Make certain there's a platform at the bottom to get into the tunnel.
        bottomLoc = self.start.copy()
        topLoc = self.end.copy()
        if self.start.y < self.end.y:
            (bottomLoc, topLoc) = (topLoc, bottomLoc)
        # Back out of the junction a bit.
        bottomLoc = bottomLoc.addY(-self.getJunctionRadius() / 2.0)
        bottomLoc = bottomLoc.toGridspace()
        topLoc = topLoc.toGridspace()
        platformWidth = random.choice(generator.platformWidths)
        game.map.addPlatform(bottomLoc, platformWidth)

        # Now place platforms along the tunnel according to the pattern.
        platformPattern = random.choice(verticalTunnelPlatformPatterns)
        index = random.randint(0, len(platformPattern)-1)

        curLoc = bottomLoc
        while curLoc.y > topLoc.y:
            curLoc = curLoc.addY(-verticalTunnelPlatformGap)
            direction = platformPattern[index]
            platformLoc = curLoc.copy()
            if direction != 0:
                while self.getIsOurSpace(platformLoc):
                    platformLoc = platformLoc.addX(direction)
                platformLoc = platformLoc.addX(-direction)
            if self.getIsOurSpace(platformLoc):
                game.map.addPlatform(platformLoc, platformWidth)
            index = (index + 1) % len(platformPattern)


    ## Fix accessibility for generic tunnels by walking along walls and 
    # placing platforms wherever the walls are too steep or the ceiling is 
    # too far away. 
    def fixAccessibilityWallwalk(self):
        spacesSinceLastPlatform = platformInterval
        for (currentSpace, angle) in self.walkWalls(slopeAveragingBracketSize):
            spacesSinceLastPlatform += 1
            if spacesSinceLastPlatform < platformInterval:
                # Still too recent since the last platform
                continue
            # If the slope is too extreme, then create a platform nearby.
            isWallOrCeiling = False
            for bracket in wallAngles:
                if bracket.contains(angle):
                    isWallOrCeiling = True
                    break
            # Default to checking for platforms above the floor
            lineDelta = Vector2D(0, -1)
            buildDistance = generator.minDistForFloorPlatform
            if isWallOrCeiling:
                # Draw the line perpendicular to the local surface instead.
                lineDelta = Vector2D(math.cos(angle), math.sin(angle))
                buildDistance = generator.minDistForPlatform
            distance = game.map.getDistanceToWall(currentSpace, lineDelta, self)
            if distance > buildDistance:
                game.map.markPlatform(currentSpace, lineDelta, distance)
                spacesSinceLastPlatform = 0
            

    ## Yield a series of spaces, and the local surface normal angle at those
    # spaces, along the perimeter of our territory.
    # \param slopeAveragingDistance The number of blocks to use when calculating
    # local slope.
    # \param skipRate How often to yield a block (1 => always; 2 => every other
    # block, etc.).
    # \param shouldUseOnlyRealWalls By default, this algorithm walks the 
    # boundary of this node's region, regardless of the presence of nearby 
    # blocks. If this parameter is True, then only spaces that are adjacent to 
    # walls will be returned.
    def walkWalls(self, slopeAveragingDistance, skipRate = 1, 
                  shouldUseOnlyRealWalls = False):
        # Find a point in the grid that's part of our sector, by walking
        # our line in gridspace.
        # This breaks down at junctions, where start and end
        # points are the same), but we know they own their endpoints.
        originalSpace = self.start.toGridspace()
        if not self.isJunction():
            endSpace = self.end.toGridspace()
            delta = endSpace.sub(originalSpace).normalize()
            while (not self.getIsOurSpace(originalSpace) and 
                    originalSpace.distance(endSpace) > 2):
                originalSpace = originalSpace.add(delta)
                
        # Find a wall from that point by dropping straight down.
        while (self.getIsOurSpace(originalSpace)):
            originalSpace = originalSpace.addY(1)
        # And back out.
        originalSpace = originalSpace.addY(-1).toInt()
        
        # If we can't find our sector, then probably all of it
        # got absorbed by other sectors or pushed into walls, so don't 
        # do the wallwalker. Otherwise, carry on.
        if not self.getIsOurSpace(originalSpace):
            return
        
        first = True
        numSteps = 0
        currentSpace = originalSpace.copy()
        recentSpaces = []
        while first or currentSpace.distanceSquared(originalSpace) > constants.EPSILON:
            first = False
            recentSpaces.append(currentSpace)
            startSpace = None
            if len(recentSpaces) >= slopeAveragingDistance:
                startSpace = recentSpaces.pop(0)
            if startSpace is not None:
                shouldReturnSpace = (numSteps % skipRate) == 0
                if shouldReturnSpace and shouldUseOnlyRealWalls:
                    # Check neighboring spaces for walls
                    shouldReturnSpace = False
                    for space in currentSpace.perimeter():
                        if game.map.getBlockAtGridLoc(space) != generator.BLOCK_EMPTY:
                            shouldReturnSpace = True
                            break
                if shouldReturnSpace:
                    delta = currentSpace.sub(startSpace)
                    # We know the wallwalker travels clockwise; thus, the 
                    # surface normal is always to our right.
                    angle = delta.angle() - math.pi / 2.0
                    yield (currentSpace, angle)
            numSteps += 1
            if numSteps > maxWallwalkerSteps:
                # This should never happen, and indicates something went 
                # wrong in map generation.
                marks = [self.start.average(self.end).toGridspace()]
                game.map.markLoc = currentSpace
                game.map.drawStatus(deadSeeds = game.map.deadSeeds, marks = marks)
                logger.fatal("Hit maximum steps for node",self.id)
            # Get the space adjacent to our own that continues the walk, 
            # by using the Marching Squares algorithm
            # (http://en.wikipedia.org/wiki/Marching_squares)
            x = currentSpace.x
            y = currentSpace.y
            marchIndex = 0
            if not self.getIsOurSpace(Vector2D(x, y)):
                marchIndex += 1
            if not self.getIsOurSpace(Vector2D(x, y+1)):
                marchIndex += 2
            if not self.getIsOurSpace(Vector2D(x-1, y+1)):
                marchIndex += 4
            if not self.getIsOurSpace(Vector2D(x-1, y)):
                marchIndex += 8
            currentSpace = currentSpace.add(marchingSquares[marchIndex])


    ## Mark the given gridspace location as being part of our sector.
    def assignSpace(self, loc):
        self.spaces.add(loc)


    ## Remove a space from our sector.
    def unassignSpace(self, loc):
        self.spaces.discard(loc)


    ## Return true if the passed-in location is one of the open spaces owned
    # by this node.
    def getIsOurSpace(self, loc):
        return loc.toInt() in self.spaces


    ## Return our terrain info.
    def getTerrainInfo(self):
        return self.terrain


    ## Get the angle from start to end, in radians.
    def getAngle(self):
        return util.clampDirection(self.start.sub(self.end).angle())


    ## Get the slope from our end to our start.
    def getSlope(self):
        return self.start.sub(self.end).slope()


    ## Draw the edge. This is strictly for debugging purposes, and thus uses
    # SDL drawing instead of OpenGL drawing.
    def draw(self, screen, scale):
        p1 = self.start.multiply(scale)
        p2 = self.end.multiply(scale)
        pygame.draw.line(screen, self.color, p1.tuple(), p2.tuple(), 4)

        font = pygame.font.Font(
                os.path.join(constants.fontPath, 'MODENINE.TTF'), 16
        )
        if self.isJunction():
            text = font.render(str(self.start.toGridspace()), False, (0, 127, 255))
            rect = text.get_rect()
            rect.left = p1.x - 50
            rect.top = p1.y
            screen.blit(text, rect)
        else:
            drawLoc = p1.average(p2)
            for i, line in enumerate([str(self.id), self.tunnelType]):
                text = font.render(line, False, (0, 127, 255))
                rect = text.get_rect()
                rect.left = drawLoc.x - 50
                rect.top = drawLoc.y + 18 * i
                screen.blit(text, rect)
                

    
    ## Convert to string.
    def __str__(self):
        locationStr = " at " + str(self.start)
        if not self.isJunction():
            locationStr = " from " + str(self.start) + " to " + str(self.end)
        return ("[MapEdge " + str(self.id) + locationStr + " of type " +
                str(self.tunnelType) + "]")
