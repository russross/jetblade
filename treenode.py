import jetblade
import constants
import map
import seed
import line
import util

import math
import copy
import random
import pygame


## Minimum branching angle.
minTreeAngleDistance = math.pi / 20.0

## Maximum depth for the tree (not counting loops).
maxTreeDepth = 50
## Leaf nodes at this depth or less are required to retry generating children.
mustRetryDepth = 3
## Number of retry attempts for leaf nodes at depth under mustRetryDepth.
numRetriesNearRoot = 50
## Number of retry attempts for leaf nodes at depth greater than mustRetryDepth.
numRetriesFarFromRoot = 5

## Used by the 'room' tunnel type; minimum size of a room in blocks.
# This is the attempted size, not necessarily the actually achieved size. 
minRoomSize = constants.blockSize * 20
## Degree to which the attempted size may vary 
# (between [minRoomSize, minRoomSize + roomSizeVariance])
roomSizeVariance = constants.blockSize * 20

# Wallwalker parameters
## How many steps in the wallwalker algorithm to aggregate to determine the 
# local slope of the tunnel wall.
slopeAveragingBracketSize = 5
## How often to try placing platforms.
platformInterval = 7
## If a wallwalker takes longer than this, give up. 
maxWallwalkerSteps = 500

## Minimum depth of tree from the last time we changed region types, to prevent
# frequent region switches.
minRegionTransitionDistance = 3

## Maximum distance from the root of the tree to a leaf node.
maxTreeDepth = 50
## Children under this depth are not allowed to create loops.
minDepthForLoops = 3
## How far apart two nodes must be to make a loop
minTreeDistanceForLoops = 4
## How far apart two loops can be
minTreeDistanceToLoops = 0
## Minimum distance between two nodes for a loop to be allowed.
minDistForLoops = 15 * constants.blockSize
## Maximum distance between two nodes for a loop to be allowed.
maxDistForLoops = 45 * constants.blockSize
## Minimum angle distance between the prospective connection and adjacent 
# tunnels.
minAngleDistanceForLoops = math.pi / 3.0

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


## See http://en.wikipedia.org/wiki/Marching_squares
# Values of each subsquare (for determining index into this list) are:
# 8 1
# 4 2
marchingSquares = [(1, 0), (1, 0), (0, 1), (0, 1), (-1, 0), (-1, 0), (-1, 0),                   (-1, 0), (0, -1), (1, 0), (0, -1), (0, 1), (0, -1), (1, 0),                   (0, -1), (None, None)]

slopePlatformRequirement = math.pi / 8.0
## Threshholds for considering a given segment of terrain to be a wall.
wallAngles = [(-math.pi/2.0 -slopePlatformRequirement,
               -math.pi/2.0 + slopePlatformRequirement),
              (math.pi/2.0 - slopePlatformRequirement,
               math.pi/2.0 + slopePlatformRequirement)]

## TreeNodes are branches of a planar tree graph that are used to describe the 
# high-level structure of the game map. Generally speaking, each node describes
# an edge in the graph that lies along a tunnel in the game. TreeNode instances
# handle the following tasks:
# - Expansion of the tree
# - Determination of tilesets and allowed map features
# - Loading map feature creation code
# - Fixing accessibility by placing platforms and carving junctions
class TreeNode:
    ## Create a new TreeNode instance. Determine the local zone and region
    # information, pick a tunnel feature type, and determine our tunnel width.
    def __init__(self, loc, parent, recurseDepth, loopNode = None, isJunctionNode = False):
        self.id = constants.globalId
        constants.globalId += 1

        ## Endpoint of this edge in the tree
        self.loc = loc
        ## Parent node
        self.parent = parent
        ## Depth in the tree
        self.depth = recurseDepth
        ## Distance to the closest loop in the tree
        self.connectionDistance = constants.BIGNUM

        ## Distance since the last time this limb of the tree changed region
        # types.
        self.regionTransitionDistance = 0
        ## Determines if we should retry making children when generating the
        # map.
        self.haveMadeChildren = False
        ## Individual spaces in the map that belong to this TreeNode
        self.spaces = dict()
        ## Child nodes
        self.children = []
        ## If this node is part of a loop, then junctionChild points to the 
        # other end of the loop.
        self.junctionChild = None
        ## Whether or not this node is itself forming a loop.
        self.isJunctionNode = isJunctionNode
        ## A list of all nodes that are connected to us that aren't our 
        # children or our parent.
        self.connections = []
        ## If this node is part of a loop, this is the node that forms the loop.
        self.loopNode = loopNode
        if self.loopNode is not None:
            self.connections.append(loopNode)
            loopNode.addConnection(self)
            for child in loopNode.children:
                self.connections.append(child)

        ## Our zone and region, based on the region map in Map.
        (self.zoneType, self.regionType) = (None, None)
        # Map our location to the region map to get our zone and region.
        if self.parent is None:
            (self.zoneType, self.regionType) = jetblade.map.getTerrainInfoAtGridLoc(util.realspaceToGridspace(self.loc))
        elif self.parent.getRegionTransitionDistance() < minRegionTransitionDistance:
            (self.zoneType, self.regionType) = self.parent.getTerrainInfo()
            self.regionTransitionDistance = self.parent.getRegionTransitionDistance() + 1
        else:
            (self.zoneType, self.regionType) = jetblade.map.getTerrainInfoAtGridLoc(util.realspaceToGridspace(self.parent.loc))
            if self.zoneType != self.parent.zoneType or self.regionType != self.parent.regionType:
                self.regionTransitionDistance = 0
            else:
                self.regionTransitionDistance = self.parent.getRegionTransitionDistance() + 1

        # Select tunnel type and load the relevant module.
        ## The tunnel feature type, e.g. straight, bumpy, staircase.
        self.tunnelType = util.pickWeightedOption(jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'tunnelTypes'))

        ## The module that contains the information needed to create our tunnel
        # feature type.
        self.featureModule = jetblade.featureManager.loadFeature(self.tunnelType, self)

        ## This color is used for debugging output only.
        self.color = (random.randint(64,255), random.randint(64,255), random.randint(64,255))
        

    ## Make children. We do this in a function call instead of in the 
    # constructor so we can build the tree breadth-first instead of depth-first.
    # This prevents us from making a tree that has a very low branching 
    # factor near the root because available space was blocked up early. 
    def createTree(self):
        didCreateOrRecurse = 0
        if (self.depth < maxTreeDepth and 
                not len(self.children) and
                not self.haveMadeChildren):
            self.haveMadeChildren = True
            # Create children, but don't call createTree on them yet.
            # Default to going in four directions if we have no parent
            direction = random.uniform(0, math.pi)
            directions = (direction, 
                          direction + math.pi / 2.0, 
                          direction + math.pi,
                          direction + 3 * math.pi / 2.0)
            if jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'aligned'):
                # Must align to the grid.
                directions = (0, math.pi / 2.0, math.pi, 3 * math.pi / 2.0)

            numAttempts = 0
            isFirst = 1

            # Determine how many times we try to make children based on our
            # distance from the root.
            maxRetries = numRetriesFarFromRoot
            if self.depth < mustRetryDepth:
                maxRetries = numRetriesNearRoot
            while numAttempts < maxRetries and len(self.children) < 2:
                numAttempts += 1
                self.children = []
                rootDirection = 0
                if self.parent is not None:
                    # Split the current path into two at 60-degree angles
                    parentLoc = self.parent.loc
                    rootDirection = self.getAngle()
                    direction = rootDirection + random.uniform(-math.pi/2.0,math.pi/2.0)
                    directions = (direction - math.pi/6.0, direction + math.pi/6.0)
                    # Check for alignment with the grid.
                    if jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'aligned'):
                        # Round rootDirection to a cardinal direction.
                        newBaseDirection = math.floor((rootDirection + math.pi / 4.0) / (math.pi / 2.0)) * math.pi / 2.0
                        directions = [newBaseDirection, 
                                      newBaseDirection + math.pi / 2.0,
                                      newBaseDirection - math.pi / 2.0]

                for direction in directions:
                    if (self.parent is not None and 
                            abs(util.clampDirection(direction) - util.clampDirection(rootDirection)) < minTreeAngleDistance):
                        continue
                    length = self.getTunnelLength()
                    childX = self.loc[0] + math.cos(direction) * length
                    childY = self.loc[1] + math.sin(direction) * length
                    childLoc = (childX, childY)
                    childLine = line.Line(self.loc, childLoc)
                    if (childX > 0 and childX < jetblade.map.width and
                        childY > 0 and childY < jetblade.map.height and
                        jetblade.map.getIsValidLine(childLine, [self.loc])):
                        self.children.append(TreeNode(childLoc, self, self.depth + 1))
                        didCreateOrRecurse = 1
                        
            for child in self.children:
                # Now that we're done trying to add children, add these lines
                # to the map. Adding them earlier would result in spurious 
                # lines being created because of the retry logic.
                jetblade.map.addLine(line.Line(self.loc, child.loc))
        else:
            # Call createTree on any children
            for child in self.children:
                if child.createTree():
                    didCreateOrRecurse = 1

        if not didCreateOrRecurse:
            # We're done making children, so it's time for the children to 
            # try making loops.
            if self.parent is None:
                for child in self.children:
                    child.createConnections()
        return didCreateOrRecurse


    ## Try to create loops in the map, by finding nodes that are 
    # a large number of steps from us in the graph but are a short physical
    # distance away.
    def createConnections(self):
        # Only try making connections if we're far from the center, not at the
        # maximum depth, and not already part of a connection.
        if (self.depth > minDepthForLoops and
                self.depth < maxTreeDepth and 
                self.loopNode is None and
                not self.connections):
            # Try making a loop to a nearby branch on a different part of 
            # the tree.
            nearbyNodes = self.parent.getNearbyNodes(self.loc, self, 0)
            for node in nearbyNodes:
                # Don't make connections if they form too tight an angle with
                # any of our children or our parent.
                if (not self.canAddConnection(node.loc) or 
                        not node.canAddConnection(self.loc)):
                    continue
                    
                dist = util.pointPointDistance(self.loc, node.loc)
                nodeLine = line.Line(self.loc, node.loc)
                if (jetblade.map.getIsValidLine(nodeLine, [self.loc, node.loc]) and 
                        not node.getConnections()):

                    self.children.append(TreeNode(node.loc, self, self.depth + 1, node))
                    self.parent.setConnectionDistance(self, 1)
                    node.setConnectionDistance(self, 1)
                    jetblade.map.addLine(nodeLine)
                    break

        for child in self.children:
            child.createConnections()


    ## Return true iff the line from us to loc is not too close to any 
    # of our existing lines and doesn't form any overly-sharp angles.
    def canAddConnection(self, loc):
        nodeAngle = util.clampDirection(math.atan2(self.loc[1] - loc[1], self.loc[0] - loc[0]))
        neighbors = []
        neighbors.extend(self.children)
        if self.parent is not None:
            neighbors.append(self.parent)
        for neighbor in neighbors:
            neighborAngle = util.clampDirection(math.atan2(self.loc[1] - neighbor.loc[1], self.loc[0] - neighbor.loc[0]))
            angleDist = abs(neighborAngle - nodeAngle)
            if angleDist < minAngleDistanceForLoops:
                return False
        return True


    ## Prepare the map for map.expandSeeds by laying down seeds according to 
    # our tunnel feature logic. 
    def createTunnels(self):
        if self.parent is not None:
            self.featureModule.carveTunnel()
        # Recurse
        for child in self.children:
            child.createTunnels()



    ## Add any features we require now that tunnels and rooms have been 
    # carved out.
    def createFeatures(self):
        if self.parent is not None:
            self.featureModule.createFeature()

            environment = util.pickWeightedOption(jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'environments'))
            if environment is not None:
                effect = jetblade.envEffectManager.loadEnvEffect(environment)
                effect.createRegion(jetblade.map, self)

        for child in self.children:
            child.createFeatures()
        
    ## Calculate the bounds of the open space occupied by our sector.
    def getSectorBounds(self):
        minX = constants.BIGNUM
        minY = constants.BIGNUM
        maxX = -constants.BIGNUM
        maxY = -constants.BIGNUM
        for loc in self.spaces.keys():
            minX = min(minX, loc[0])
            minY = min(minY, loc[1])
            maxX = max(maxX, loc[0])
            maxY = max(maxY, loc[1])
        return (minX, minY, maxX, maxY)


    ## Get the points closest to our start and end that are still in our
    # sector. This is useful for some tunnel features (e.g. the maze feature).
    def getStartAndEndLoc(self):
        startLoc = util.realspaceToGridspace([self.loc[0], self.loc[1]])
        endLoc = util.realspaceToGridspace([self.parent.loc[0], self.parent.loc[1]])
        (dx, dy) = util.getNormalizedVector(startLoc, endLoc)
        while not self.getIsOurSpace(startLoc):
            startLoc[0] += dx
            startLoc[1] += dy
            if util.pointPointDistance(startLoc, endLoc) < 1:
                return (None, None)
        while not self.getIsOurSpace(endLoc):
            endLoc[0] -= dx
            endLoc[1] -= dy
            if util.pointPointDistance(startLoc, endLoc) < 1:
                return (None, None)

        return (startLoc, endLoc)


    ## Measure the distance, in gridspace, from the given loc to either a wall
    # or the end of our space.
    def getDistToCeiling(self, loc):
        x = loc[0]
        curY = loc[1] - 1 # Start in open space
        dist = 1
        while self.getIsOurSpace((x, curY)):
            curY -= 1
            dist += 1
        return dist


    def getTunnelWidth(self):
        return random.choice(jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'tunnelWidths')) * constants.blockSize


    def getTunnelLength(self):
        return random.choice(jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'tunnelLengths')) * constants.blockSize


    def getJunctionRadius(self):
        widths = jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'tunnelWidths')
        return widths[0] * constants.blockSize


    def getRoomSize(self):
        return random.uniform(minRoomSize, minRoomSize + roomSizeVariance)


    ## Carve a junction out of the map grid at our endpoint, if we have 
    # children or loops. We have two types of junctions, circular and square,
    # which may be set in the configuration for the region.
    def createJunctions(self):
        if not self.children and not self.connections:
            return
        center = util.realspaceToGridspace(self.loc)
        radius = int(self.getJunctionRadius() / constants.blockSize)
        distFunc = util.pointPointDistance
        if jetblade.map.getRegionInfo(self.zoneType, self.regionType, 'aligned'):
            # Use a square junction instead of a circular one.
            distFunc = util.pointPointDistanceSquare

        # Iterate over points in the accepted area, converting them to 
        # open space surrounded by walls if they are related to us.
        for x in range(center[0] - int(radius), 
                       center[0] + int(radius)):
            if x <= 0 or x >= jetblade.map.numCols - 1:
                continue
            for y in range(center[1] - int(radius), 
                           center[1] + int(radius)):
                if y <= 0 or y >= jetblade.map.numRows - 1:
                    continue
                dist = distFunc((x, y), center)
                if (dist <= radius and 
                        (x, y) in jetblade.map.deadSeeds and 
                        self.getRelationType(jetblade.map.deadSeeds[(x, y)].node) != 'none'):
                    jetblade.map.blocks[x][y] = 0
                    # Reassign the space to a dummy child
                    if self.junctionChild is None:
                        self.junctionChild = TreeNode(self.loc, self, constants.BIGNUM, None, 1)
                        self.junctionChild.color = (0, 0, 0)
                    jetblade.map.assignSpace((x, y), self.junctionChild)
                    
                    # Patch walls around the deleted space
                    for offset in constants.perimeterOrder:
                        ax = x + offset[0]
                        ay = y + offset[1]
                        if not jetblade.map.getIsInBounds((ax, ay)):
                            continue
                        # If we hit a space that's not a wall or open space, or
                        # if we hit a space that's owned by a non-junction node
                        # of the tree that we aren't connected to, put a wall 
                        # in.
                        altNode = None
                        if (ax, ay) in jetblade.map.deadSeeds:
                            altNode = jetblade.map.deadSeeds[(ax, ay)].node
                        if (jetblade.map.blocks[ax][ay] == 1 or 
                                (altNode is not None and
                                 self.getRelationType(altNode) == 'none' and
                                 not altNode.getIsJunctionNode()
                                )):
                            jetblade.map.blocks[ax][ay] = 2
                            jetblade.map.deadSeeds[(ax, ay)] = seed.Seed(self.junctionChild, 0, constants.BIGNUM)

        for child in self.children:
            child.createJunctions()


    ## Return a string describing the relation of the given node to ourself.
    def getRelationType(self, node):
        if self.isJunctionNode:
            if node.isJunctionNode:
                return self.parent.getRelationType(node.parent)
            return self.parent.getRelationType(node)
        elif node.isJunctionNode:
            return self.getRelationType(node.parent)
        if node.id == self.id:
            return 'self'
        if self.parent is not None:
            if self.parent.id == node.id:
                return 'parent'
            siblings = self.parent.children
            for sibling in siblings:
                if sibling.id == node.id:
                    return 'sibling'
        for child in self.children:
            if child.id == node.id:
                return 'child'
        if self.junctionChild is not None and self.junctionChild.id == node.id:
            return 'child'
        for connection in self.connections:
            if connection.id == node.id:
                return 'connection'
        if self.loopNode is not None and node.id == self.loopNode.id:
            return 'connection'
        return 'none'


    ## Return any nodes in the tree that are near the given location, but
    # at least minTreeDistanceForLoops away by connections.
    def getNearbyNodes(self, loc, originator, treeDistance):
        result = []
        if (treeDistance >= minTreeDistanceForLoops and 
                self.connectionDistance >= minTreeDistanceToLoops):
            dist = util.pointPointDistance(self.loc, loc)
            if dist > minDistForLoops and dist < maxDistForLoops:
                result.append(self)

        # Recurse down the tree.
        for child in self.children:
            if child != originator:
                result.extend(child.getNearbyNodes(loc, self, treeDistance + 1))
        # Recurse up the tree.
        if self.parent is not None and self.parent != originator:
            result.extend(self.parent.getNearbyNodes(loc, self, treeDistance + 1))
        return result


    ## Update our node distance to the nearest connection
    def setConnectionDistance(self, originator, distance):
        if self.connectionDistance > distance:
            self.connectionDistance = distance
            for child in self.children:
                if child != originator:
                    child.setConnectionDistance(self, distance + 1)
        if self.parent is not None and self.parent != originator:
            self.parent.setConnectionDistance(self, distance + 1)
        
    def getConnections(self):
        return self.connections

    ## Break the tree concept by creating a connection to a node in a 
    # different part of the tree.
    def addConnection(self, node, shouldRecurse = 1):
        self.connections.append(node)
        if shouldRecurse:
            for child in self.children:
                child.addConnection(node, 0)


    ## Place platforms in our space to help make the map accessible to the
    # player.
    def fixAccessibility(self):
        if (self.parent is not None and 
                (self.isJunctionNode or self.featureModule.shouldCheckAccessibility())):
            util.debug("Checking accessibility for node",self.id)
            # Determine which accessibility-fixing algorithm to use.
            if util.pointPointDistance(self.loc, self.parent.loc) > minVerticalTunnelLength:
                angle = self.getAngle()
                if (abs(angle - math.pi / 2.0) < verticalTunnelAngleFuzz or
                        abs(angle - 3*math.pi / 2.0) < verticalTunnelAngleFuzz):
                    self.fixAccessibilityVertical()
                else:
                    self.fixAccessibilityWallwalk()
            else:
                self.fixAccessibilityWallwalk()

        for child in self.children:
            child.fixAccessibility()
        if self.junctionChild is not None:
            self.junctionChild.fixAccessibility()


    ## Ensure that vertical shaft tunnels are accessible by making a "spiral
    # staircase" out of floating platforms.
    def fixAccessibilityVertical(self):
        # Make certain there's a platform at the bottom to get into the tunnel.
        bottomLoc = self.loc
        topLoc = self.parent.loc
        if self.loc[1] < self.parent.loc[1]:
            bottomLoc = self.parent.loc
            topLoc = self.loc
        bottomLoc = (bottomLoc[0], bottomLoc[1] - self.getJunctionRadius() / 2.0)
        bottomLoc = util.realspaceToGridspace(bottomLoc)
        topLoc = util.realspaceToGridspace(topLoc)
        platformWidth = random.choice(map.platformWidths)
        jetblade.map.addPlatform(bottomLoc, platformWidth)

        # Now place platforms along the tunnel on alternating sides.
        platformPattern = random.choice(verticalTunnelPlatformPatterns)
        index = random.randint(0, len(platformPattern)-1)

        curLoc = [bottomLoc[0], bottomLoc[1] - verticalTunnelPlatformGap]
        while curLoc[1] > topLoc[1]:
            curLoc = [curLoc[0], curLoc[1] - verticalTunnelPlatformGap]
            direction = platformPattern[index]
            platformLoc = copy.copy(curLoc)
            if direction != 0:
                while self.getIsOurSpace(platformLoc):
                    platformLoc[0] += direction
                platformLoc[0] -= direction
            if self.getIsOurSpace(platformLoc):
                jetblade.map.addPlatform(platformLoc, platformWidth)
                jetblade.map.markLoc = platformLoc
            index = (index + 1) % len(platformPattern)


    ## Fix accessibility for generic tunnels by walking along walls and 
    # placing platforms wherever the walls are too steep or the ceiling is 
    # too far away. 
    def fixAccessibilityWallwalk(self):
        # Find a point in the grid that's part of our sector, by walking
        # our line in gridspace.
        # This breaks down for the junction nodes (whose start and end
        # points are the same), but we know they own their endpoints.
        originalSpace = self.getLocOnGrid()
        if not self.isJunctionNode:
            parentSpace = self.parent.getLocOnGrid()
            (dx, dy) = util.getNormalizedVector(originalSpace, parentSpace)
            while (not self.getIsOurSpace(originalSpace) and 
                    util.pointPointDistance(originalSpace, parentSpace) > 2):
                originalSpace[0] += dx
                originalSpace[1] += dy
        # Find a wall from that point
        while (self.getIsOurSpace(originalSpace)):
            originalSpace[1] += 1
        originalSpace[1] -= 1
        originalSpace = [int(originalSpace[0]), int(originalSpace[1])]
        if self.getIsOurSpace(originalSpace):
#                print "Starting from",originalSpace
            # If we can't find our sector, then probably all of it
            # got absorbed by other sectors or pushed into walls, so don't 
            # do the wallwalker.
            localSlope = 0
            first = 1
            currentSpace = originalSpace
            recentSpaces = []
            spacesSinceLastPlatform = 0
            numSteps = 0
            while first or currentSpace != originalSpace:
                numSteps += 1
                if numSteps > maxWallwalkerSteps:
                    util.debug("Hit maximum steps for node",self.id)
                    break
                first = 0
                # Walk around the perimeter of the region, finding the average 
                # slope over every slopeAveragingBracketSize blocks. If the 
                # slope is too extreme, then create a platform nearby.
                startSpace = None
                if len(recentSpaces) >= slopeAveragingBracketSize:
                    startSpace = recentSpaces.pop(0)
                if startSpace is not None and spacesSinceLastPlatform > platformInterval:
                    dx = currentSpace[0] - startSpace[0]
                    dy = currentSpace[1] - startSpace[1]
                    angle = math.atan2(dy, dx)
                    angleBrackets = []
                    
                    isWallOrCeiling = 0
                    for bracket in wallAngles:
                        if angle > bracket[0] and angle < bracket[1]:
                            isWallOrCeiling = 1
                            break
                    # Default to checking for platforms above the floor
                    lineDx = 0
                    lineDy = -1
                    buildDistance = map.minDistForFloorPlatform
                    if isWallOrCeiling:
                        # Draw the line perpendicular to the local surface instead.
                        lineDx = -dy
                        lineDy = dx
                        magnitude = math.sqrt(lineDx**2+lineDy**2)
                        lineDx /= magnitude
                        lineDy /= magnitude
                        buildDistance = map.minDistForPlatform
                    distance = jetblade.map.getDistanceToWall(currentSpace, lineDx, lineDy)
                    if distance > buildDistance:
                        jetblade.map.markPlatform(currentSpace, lineDx, lineDy, distance)
                        spacesSinceLastPlatform = 0
                recentSpaces.append(currentSpace)
                spacesSinceLastPlatform += 1

                # Get the space adjacent to our own that continues the walk, 
                # by using the Marching Squares algorithm
                # (http://en.wikipedia.org/wiki/Marching_squares)
                x = currentSpace[0]
                y = currentSpace[1]
                marchIndex = 0
                if not self.getIsOurSpace((x, y)):
                    marchIndex += 1
                if not self.getIsOurSpace((x, y+1)):
                    marchIndex += 2
                if not self.getIsOurSpace((x-1, y+1)):
                    marchIndex += 4
                if not self.getIsOurSpace((x-1, y)):
                    marchIndex += 8
                currentSpace = [x + marchingSquares[marchIndex][0],
                                y + marchingSquares[marchIndex][1]]
        else: # Couldn't find a good space to start from
            pass
#                print "Unable to find a good starting place for",self.id
#            jetblade.map.drawStatus() 


    ## Mark the given gridspace location as being part of our sector.
    def assignSpace(self, loc):
        self.spaces[loc] = 1


    ## Remove a space from our sector.
    def unassignSpace(self, loc):
        if loc in self.spaces:
            del self.spaces[loc]


    ## Return true if the passed-in location is one of the open spaces owned
    # by this node.
    def getIsOurSpace(self, loc):
        return (int(loc[0]), int(loc[1])) in self.spaces


    ## Return true if this node is one of the "blank" leaf nodes placed at 
    # a junction of normal nodes.
    def getIsJunctionNode(self):
        return self.isJunctionNode


    ## Return a tuple of terrain information.
    def getTerrainInfo(self):
        return (self.zoneType, self.regionType)


    ## Map our location to the map grid.
    def getLocOnGrid(self):
        return util.realspaceToGridspace(self.loc)


    ## Get the angle from our parent to ourselves, in radians.
    def getAngle(self):
        if self.parent is not None:
            return util.clampDirection(math.atan2(self.loc[1] - self.parent.loc[1], self.loc[0] - self.parent.loc[0]))
        return 0


    ## Get the slope from our parent to ourselves.
    def getSlope(self):
        if self.parent is not None:
            dy = self.loc[1] - self.parent.loc[1]
            dx = self.loc[0] - self.parent.loc[0]
            if abs(dx) < constants.EPSILON:
                # Vertical.
                return constants.BIGNUM * cmp(dy, 0)
            return dy / dx
        return 0

    def getRegionTransitionDistance(self):
        return self.regionTransitionDistance

    def printTree(self):
        ids = []
        for child in self.children:
            ids.append(child.id)
        util.debug("Node",self.id,"has child IDs",ids)
        for child in self.children:
            child.printTree()


    ## This is strictly for debugging purposes only. 
    def draw(self, screen, scale):
        p1 = [self.loc[0] * scale, self.loc[1] * scale]
        if self.parent is not None:
            p2 = [self.parent.loc[0] * scale, self.parent.loc[1] * scale]
            pygame.draw.line(screen, self.color, p1, p2, 4)
        for child in self.children:
            # Note this does not include junction nodes
            child.draw(screen, scale)

        parentId = -1
        if self.parent is not None:
            parentId = self.parent.id
        drawLoc = p1
        if self.loopNode is not None:
            drawLoc = util.addVectors(p1, (0, 40))
        jetblade.imageManager.drawText(screen, 
                ['%d %d' % (self.loc[0], self.loc[1]),
                 '%d %d' % (self.id, parentId), 
                 '%s' % self.tunnelType],
                drawLoc, 0, constants.tinyFontSize, 
                constants.TEXT_ALIGN_CENTER, (255, 0, 0, 255))


    ## Generate a textual representation
    def __str__(self):
        locationStr = " at " + str(self.loc)
        if self.parent is not None:
            locationStr = " from " + str(self.parent.loc) + " to " + str(self.loc)
        return "TreeNode " + str(self.id) + locationStr + " of type " + str(self.tunnelType)
