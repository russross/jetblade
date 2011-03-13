import constants
import line
import mapgraph
import zone
import block
import furniture
import enveffect
import scenery
import game
import util
import logger
import quadtree
import seed
import floatingplatform
import terraininfo
import collisiondata
from vector2d import Vector2D

import sys
import math
import copy
import random
import pygame

## Minimum width of the game world
minUniverseWidth = constants.blockSize * 200
## Minimum height of the game world
minUniverseHeight = constants.blockSize * 200
## Degree to which the game world dimensions are allowed to vary. The range thus
# defined is e.g. 
# [minUniverseWidth, minUniverseWidth + universeDimensionVariance] for width.
universeDimensionVariance = constants.blockSize * 00

## Amount to thicken walls by in Map.expandWalls
wallThickness = 2

## Minimum size of a tree sector. Sectors smaller than this are absorbed into
# neighboring sectors.
minimumSectorSize = 10
## Minimum size of a section of connected walls. smaller islands are 
# converted to open space.
minimumIslandSize = 20

## How finely-grained the region grid is (lower numbers mean lower resolution
# and thus faster map generation).
regionOverlayResolutionMultiplier = .1
## How many times to retry seeding a region.
regionOverlayNumSeedingRetries = 10

## Amount to scale the map by when calling Map.drawStatus()
drawStatusScaleFactor = .4
## Amount to scale the map by when calling Map.DrawAll()
# Note that PyGame can't create surfaces bigger than about 16k pixels to a side
drawAllScaleFactor = .2

# Platform placement parameters
## Distance from the wall/ceiling to build platforms.
minDistForPlatform = 4
## As minDistForPlatform, but only when building from a floor.
minDistForFloorPlatform = 4
## Minimum horizontal distance between platforms.
minHorizDistToOtherPlatforms = 6
## Minimum vertical distance between platforms.
minVertDistToOtherPlatforms = 4
## Platforms have widths randomly selected from this list.
platformWidths = [2, 2, 3]

## This maps different block configurations to block types, for setting terrain
# in getBlockType(). We'll convert each array into a set of scalar signatures
# using util.adjacencyArrayToSignature().
# - 0: must be open
# - 1: must be filled
# - 2: do not care
adjacencyKernelToBlockTypeMap = {
    ((2, 0, 2), 
     (1, 1, 1),
     (2, 1, 2)) : 'up',
    ((2, 1, 2),
     (1, 1, 0),
     (2, 1, 2)) : 'right',
    ((2, 1, 2),
     (1, 1, 1),
     (2, 0, 2)) : 'down',
    ((2, 1, 2), 
     (0, 1, 1),
     (2, 1, 2)) : 'left',
    ((0, 0, 2), 
     (0, 1, 1), 
     (1, 1, 1)) : 'upleft',
    ((2, 0, 0),
     (1, 1, 0),
     (1, 1, 1)) : 'upright',
    ((1, 1, 2),
     (1, 1, 0),
     (2, 0, 0)) : 'downright',
    ((2, 1, 1),
     (0, 1, 1),
     (0, 0, 2)) : 'downleft',
    ((2, 0, 2),
     (1, 1, 1),
     (2, 0, 2)) : 'updown',
    ((2, 1, 2),
     (0, 1, 0),
     (2, 1, 2)) : 'leftright',
    ((2, 1, 2),
     (1, 1, 0),
     (2, 0, 2)) : 'downrightsquare',
    ((2, 1, 2),
     (0, 1, 1),
     (2, 0, 2)) : 'downleftsquare',
    ((2, 0, 2),
     (0, 1, 1),
     (0, 1, 2)) : 'upleftsquare',
    ((2, 0, 2),
     (1, 1, 0),
     (2, 1, 0)) : 'uprightsquare',
    ((2, 0, 2),
     (1, 1, 0),
     (2, 0, 2)) : 'rightend',
    ((2, 1, 2),
     (0, 1, 0),
     (2, 0, 2)) : 'downend',
    ((2, 0, 2),
     (0, 1, 1),
     (2, 0, 2)) : 'leftend',
    ((2, 0, 2),
     (0, 1, 0),
     (2, 1, 2)) : 'upend',
    ((0, 0, 0),
     (0, 1, 0),
     (0, 0, 0)) : 'allway'
}

## Block type enums: empty space, unallocated space, and wall.
(BLOCK_EMPTY, BLOCK_UNALLOCATED, BLOCK_WALL) = range(3)

## Maximum attempts to disentangle an object from a wall before we give up 
# and start zipping it.
maxCollisionRetries = 15
## Distance to zip if we fail to pull an object out of the terrain.
zipAmount = Vector2D(0, -constants.blockSize)

## The Map class handles creating, updating, and displaying the game map. This
# includes the following structures:
# - The root TreeNode for the tree that describes the high-level structure of 
#   the map tunnels.
# - A grid of terrain tiles.
# - Another grid for environmental effects.
# - A quadtree containing all background scenery.
# \todo Several dicts in this class don't match the style guideline.
class Map:

    ## Prepare a blank map and a bunch of values we'll need while
    # constructing it. Most of this is unneeded if we're loading the map.
    def __init__(self, mapName = None):
        ## Number of the most recent file output by drawStatus()
        self.statusIter = 0
        self.mapName = mapName
         
        ## 2D array of blocks (or None to indicate empty space)
        # During map construction, we use BLOCK_* values instead
        self.blocks = None
       
        ## Holds Furniture instances
        self.furnitureQuadTree = None
       
        ## Marks spaces as belonging to different environments. Built to same
        # scale as blocks.
        self.envGrid = None

        ## Holds background scenery.
        self.backgroundQuadTree = None

        ## MapEdge instances that mark the tunnels of the map.
        self.tunnelEdges = []

        ## Holds configuration information for the different zones
        self.zoneData = None

        ## This will be a dict that maps locations to zones.
        self.regions = None

        ## Maps locations to objects (either TreeNode instances or regions)
        self.seeds = dict()

        ## Seeds that are no longer expanding. We use these to mark ownership
        # of areas.
        self.deadSeeds = dict()

        ## If this is not None, then drawStatus() will focus on this area.
        self.markLoc = None

        ## Maps block adjacency signatures (see adjacencyKernelToBlockTypeMap)
        # to block orientations.
        self.adjacenciesMap = dict()

        for kernel, type in adjacencyKernelToBlockTypeMap.iteritems():
            keys = util.adjacencyArrayToSignatures(kernel)
            for key in keys:
                self.adjacenciesMap[key] = type
        

    ## Either create or load a map.
    def init(self):
        if self.mapName is not None:
            try:
                image = pygame.image.load(self.mapName)
                self.loadImageAsMap(image)
            except Exception, e: # File is text, not an image
                self.loadMap()
        else:
            self.createMap()
        # \todo This is slow for big maps. Either chunk it up into multiple
        # smaller display lists and only draw relevant ones, or only draw
        # tiles if they're in view (which is slow when we zoom out, but would
        # allow for tiles to cycle display frames more readily).
        frameLocs = []
        for i in xrange(0, self.numCols):
            for j in xrange(0, self.numRows):
                if self.blocks[i][j]:
                    frameLocs.append((self.blocks[i][j].getFrame(), 
                                      self.blocks[i][j].loc)) 

        self.blockDisplayList = game.imageManager.createDisplayList(frameLocs)


    ## Create a map, by the following steps:
    # - Divide the universe up into regions
    # - Generate a tree to mark the locations of tunnels.
    # - Place seeds for the spacefilling automaton (expandSeeds()) along the 
    #   limbs of the tree.
    # - Run expandSeeds() to carve out tunnels starting from those seeds.
    # - Clean up the tunnel intersections.
    # - Remove any small islands in the map.
    # - Thicken the walls.
    # - Clean up TreeNode ownership of tiles by removing islands.
    # - Construct special map features.
    # - Run a wallwalking algorithm to fix map accessibility by placing 
    #   platforms.
    # - Choose the type of block for each space in the grid, based on the region
    #   the space is in and the space's neighbors, then instantiate the Block 
    #   objects.
    # - Find the starting point for the player.
    def createMap(self):
        self.width = int(minUniverseWidth + random.uniform(0, universeDimensionVariance))
        self.height = int(minUniverseHeight + random.uniform(0, universeDimensionVariance))
        self.furnitureQuadTree = quadtree.QuadTree(self.getBounds())
        self.backgroundQuadTree = quadtree.QuadTree(self.getBounds())

        ## A quadtree of Platform instances created during fixAccessibility, 
        # that will be converted into actual blocks near the end of mapgen.
        self.platformsQuadTree = quadtree.QuadTree(self.getBounds())
        
        self.numCols = self.width / constants.blockSize
        self.numRows = self.height / constants.blockSize
        
        logger.inform("Making a",self.numCols,"x",self.numRows,"map","; that's",
                      self.numCols * constants.blockSize,"x",
                      self.numRows * constants.blockSize,"pixels")
        logger.inform("Started making map at",pygame.time.get_ticks())

        # First we need to figure out which parts of the map belong to which
        # regions. Make a low-rez overlay for the map that marks out regions.
        logger.inform("Marking regions at",pygame.time.get_ticks())
        self.regions = self.makeRegions()

        # Create the array for the actual blocks.
        logger.inform("Laying out grid at",pygame.time.get_ticks())
        self.blocks = []
        self.envGrid = []
        for i in xrange(0, self.numCols):
            self.blocks.append([])
            self.envGrid.append([])
            for j in xrange(0, self.numRows):
                self.blocks[i].append(BLOCK_UNALLOCATED)
                self.envGrid[i].append([])

        # Generate the tree that will be used to mark out tunnels.
        logger.inform("Generating graph of map at",pygame.time.get_ticks())
        self.tunnelEdges = mapgraph.makeGraph([])
         
        # Lay the seeds for those tunnels.
        logger.inform("Planting seeds at",pygame.time.get_ticks())
        [edge.carveTunnel() for edge in self.tunnelEdges]

        # Expand the seeds and carve out those tunnels. 
        logger.inform("Expanding seeds at",pygame.time.get_ticks())
        (self.blocks, self.deadSeeds) = self.expandSeeds(self.seeds, self.blocks)

        # Clean up the points where tunnels meet.
        logger.inform("Creating junctions at",pygame.time.get_ticks())
        [edge.createJunction() for edge in self.tunnelEdges]

        # Remove isolated chunks of land.
        logger.inform("Removing islands at",pygame.time.get_ticks())
        self.removeIslands()

        # Make the walls a bit thicker.
        logger.inform("Expanding walls at",pygame.time.get_ticks())
        self.expandWalls()

        # Tell the tree nodes which spaces belong to them.
        logger.inform("Assigning squares at",pygame.time.get_ticks())
        self.assignSquares()

        # Fill in tunnels with interesting terrain.
        logger.inform("Creating tunnel features at",pygame.time.get_ticks())
        [edge.createFeatures() for edge in self.tunnelEdges]

        # Reassign any seeds that got isolated in the last step to prevent
        # loops in the next step.
        logger.inform("Fixing seed ownership at",pygame.time.get_ticks())
        (self.blocks, self.deadSeeds) = self.fixSeedOwnership(self.blocks, self.deadSeeds)
#        self.drawStatus()

        # Walk the walls and put down furniture objects
        logger.inform("Placing furniture at",pygame.time.get_ticks())
        [edge.placeFurniture() for edge in self.tunnelEdges]

        # Place platforms down to make inaccessible areas accessible.
        logger.inform("Fixing accessibility at",pygame.time.get_ticks())
        [edge.fixAccessibility() for edge in self.tunnelEdges]
#        self.drawStatus()

        # Mark those platforms on the map.
        logger.inform("Building platforms at",pygame.time.get_ticks())
        self.buildPlatforms()

        # Turn those block types into instances of the Block class.
        logger.inform("Instantiating blocks at",pygame.time.get_ticks())
        self.instantiateBlocks()

        logger.inform("Drawing status at",pygame.time.get_ticks())
        self.markLoc = None
        self.drawStatus(self.blocks, None, None)

        # \todo Pick a better starting point for the player.
        self.startLoc = self.tunnelEdges[0].start.loc.toGridspace()
        while self.blocks[self.startLoc.ix][self.startLoc.iy] != BLOCK_EMPTY:
            self.startLoc = self.startLoc.addY(-1)

        logger.inform("Saving map file at",pygame.time.get_ticks())
        self.writeMap(str(game.seed))

        logger.inform("Done making map at",pygame.time.get_ticks())
        numUsedSpaces = 0
        for x in xrange(0, self.numCols):
            for y in xrange(0, self.numRows):
                if not self.blocks[x][y]:
                    numUsedSpaces += 1
        totalSpaces = self.numCols * self.numRows
        percent = numUsedSpaces / float(totalSpaces) * 100
        logger.inform(numUsedSpaces,"of",totalSpaces,"spaces are occupied for a %.2f%% occupancy rate" % percent)


    ## Create a low-rez overlay of the map that determines where different
    # regions are. Each region is a subset of some overarching zone (for
    # example, a "furnace" region in the "magma caverns" zone). Regions
    # are important for varying map generation, particularly in the availability
    # of different map features and the selection of terrain tiles.
    # We use the same spacefilling automaton we use to carve tunnels, to
    # make the region map.
    def makeRegions(self):
        # First step: place zones down and map each space in our low-rez map
        # to a zone. Each zone has certain preferences for size and elevation.
        self.zoneData = zone.loadZoneData()
        zonePoints = zone.placeZones(self.zoneData)
        cols = int(self.numCols * regionOverlayResolutionMultiplier) + 1
        rows = int(self.numRows * regionOverlayResolutionMultiplier) + 1
        
        # Make three things: a fake set of "blocks" for expandSeeds to play in,
        # a mapping of zones to lists of "blocks" in the zones, and a reverse
        # mapping of "blocks" to the zones that own them.
        blocks = []
        zoneToBlocksMap = dict()
        blockToZoneMap = dict()
        for i in xrange(0, cols):
            blocks.append([])
            for j in xrange(0, rows):
                blocks[i].append(BLOCK_UNALLOCATED)
                # Map (i, j) to the ranges ([0, 1], [0, 1]) and find the zone
                # point that is closest to that location. Mark (i, j) as 
                # belonging to that zone.
                loc = Vector2D(i / float(cols), j / float(rows))
                closestZone = None
                closestDist = constants.BIGNUM
                for zoneName, zoneLoc in zonePoints.iteritems():
                    dist = loc.distance(zoneLoc)
                    if dist < closestDist:
                        closestZone = zoneName
                        closestDist = dist
                
                if closestZone not in zoneToBlocksMap:
                    zoneToBlocksMap[closestZone] = []
                space = Vector2D(i, j)
                zoneToBlocksMap[closestZone].append(space)
                blockToZoneMap[space] = closestZone

        # Create a set of seeds for the different zones. Place them randomly
        # within each zone, and give them life proportionate to their desired
        # size.
        seeds = dict()
        terrainInfoCache = dict()
        for zoneName, zoneInfo in self.zoneData.iteritems():
            totalWeight = 0
            zoneLocs = zoneToBlocksMap[zoneName]
            for region, weight in zoneInfo['regionWeights'].iteritems():
                totalWeight += weight
            zoneSize = math.sqrt(len(zoneLocs))
            for regionName, weight in zoneInfo['regionWeights'].iteritems():
                terrain = terraininfo.TerrainInfo(zoneName, regionName)
                terrainInfoCache[(zoneName, regionName)] = terrain
                loc = random.choice(zoneLocs)
                numTries = 0
                while loc in seeds and numTries < regionOverlayNumSeedingRetries:
                    numTries += 1
                    loc = random.choice(zoneLocs)
                life = int(zoneSize * math.sqrt(weight / float(totalWeight)))
                seeds[loc] = seed.Seed(terrain, life, 0)

        # And expand those seeds into regions
        (blocks, seeds) = self.expandSeeds(seeds, blocks)
        
        # There's no guarantee that we reached every space, so 
        # convert the ones that weren't touched into a default for that region,
        # while we turn everything into "open space" for fixSeedOwnership, which
        # will eliminate islands (very small regions) for us.
        for i in xrange(0, cols):
            for j in xrange(0, rows):
                space = Vector2D(i, j)
                if space not in seeds:
                    zoneName = blockToZoneMap[space]
                    regionName = self.zoneData[zoneName]['biggestRegion']
                    if (zoneName, regionName) not in terrainInfoCache:
                        terrainInfoCache[zoneName][regionName] = terraininfo.TerrainInfo(zoneName, regionName)
                    seeds[space] = seed.Seed(terrainInfoCache[(zoneName, regionName)], 
                                             0, constants.BIGNUM)
                blocks[i][j] = BLOCK_EMPTY

        (blocks, seeds) = self.fixSeedOwnership(blocks, seeds, 0)

        result = dict()
        for loc, resultSeed in seeds.iteritems():
            result[loc] = resultSeed.owner

        return result


    ## Widen every wall by adding walls on either side.
    def expandWalls(self):
        # If we only go in one direction, we get walls from one sector
        # adjacent to open spaces owned by a different sector, which creates
        # terrain mismatches.
        amount = wallThickness / 2
        newBlocks = copy.deepcopy(self.blocks)
        for i in xrange(amount, self.numCols - amount):
            for j in xrange(amount, self.numRows - amount):
                if self.blocks[i][j] == BLOCK_WALL:
                    for ii in xrange(-amount, amount + 1):
                        for jj in xrange(-amount, amount + 1):
                            newBlocks[i-ii][j-jj] = BLOCK_WALL
        self.blocks = newBlocks


    ## Replace the values in self.blocks with block type info. At this point
    # self.blocks consists of the following:
    # - 0: empty space
    # - 1: filled space surrounded by other filled space
    # - 2: filled space next to empty space
    # - Tuple of block typestring (e.g. 'upleft') and adjacency signature
    def instantiateBlocks(self):
        for i in xrange(0, self.numCols):
            for j in xrange(0, self.numRows):
                gridLoc = Vector2D(i, j)
                terrain = self.getTerrainInfoAtGridLoc(gridLoc)
                sector = self.getSectorAtGridLoc(gridLoc)
                if sector is not None:
                    terrain = sector.getTerrainInfo()
                if self.blocks[i][j] == BLOCK_UNALLOCATED:
                    self.blocks[i][j] = block.Block(gridLoc, terrain, 'center')
                elif self.blocks[i][j] == BLOCK_WALL:
                    (type, signature) = self.getBlockType(i, j)
                    self.blocks[i][j] = block.Block(gridLoc, terrain, type)
                    # Choose a scenery item to attach to the block.
                    newItem = game.sceneryManager.selectScenery(gridLoc, terrain, signature)
                    if newItem is not None:
                        self.addBackgroundObject(newItem)
                # else self.blocks[i][j] == BLOCK_EMPTY, do nothing


    ## Return the type of block that should be drawn at the given grid loc.
    # Determine this by the locations of neighbors of the block -- its 
    # "adjacency signature". 
    def getBlockType(self, x, y):
        # Get the set of adjacencies for this block. 
        # 0 = empty.
        # 1 = occupied.
        adjacencies = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

        for i in xrange(x-1,x+2):
            for j in xrange(y-1,y+2):
                if self.getBlockAtGridLoc(Vector2D(i, j)) == BLOCK_EMPTY:
                    adjacencies[j-(y-1)][i-(x-1)] = 0

        # We should always get 1 result back because all values in the 
        # adjacencies array are 0 or 1 (see that function for more information).
        signature = util.adjacencyArrayToSignatures(adjacencies)[0]

        if signature in self.adjacenciesMap:
            return (self.adjacenciesMap[signature], signature)
        return ('center', signature)


    ## Do a connectivity check on the map. Remove all areas whose size is 
    # less than minimumIslandSize. This is very similar to the 
    # logic in fixSeedOwnership(), but operates on walls (and unallocated
    # space) instead of seeds and 
    # removes islands entirely instead of merging them with neighbors.
    def removeIslands(self):
        chunks = []
        seenSpaces = set()
        
        for i in xrange(0, self.numCols):
            for j in xrange(0, self.numRows):
                startLoc = Vector2D(i, j)
                if (self.blocks[i][j] == BLOCK_WALL and 
                        startLoc not in seenSpaces):
                    # Start a new chunk of contiguous land. Floodfill out from
                    # this point, grabbing all adjacent occupied spaces and
                    # adding them to the chunk.
                    newChunk = []
                    fillStack = [startLoc]
                    seenSpaces.add(startLoc)
                    while fillStack:
                        loc = fillStack.pop(0)
                        newChunk.append(loc)
                        for neighbor in loc.NEWSPerimeter():
                            if (self.getIsInBounds(neighbor) and 
                                    self.blocks[neighbor.ix][neighbor.iy] != BLOCK_EMPTY and
                                    neighbor not in seenSpaces):
                                fillStack.append(neighbor)
                                seenSpaces.add(neighbor)
                    chunks.append(newChunk)

        for chunk in chunks:
            if len(chunk) < minimumIslandSize:
                for loc in chunk:
                    self.blocks[loc.ix][loc.iy] = BLOCK_EMPTY


    ## Plant a seed for hollowing out part of the map at the desired
    # location.
    def plantSeed(self, loc, node, size):
        target = loc.toGridspace()
        if self.getIsInBounds(target):
            self.seeds[target] = seed.Seed(node, int(size / constants.blockSize / 2.0), 0)


    ## Run a spacefilling automaton to divide a grid up into different sectors.
    # \param seeds A mapping of locations to Seed instances
    # \param blocks A grid of blocks
    # Each seed ordinarily replaces all neighbor spaces with copies of itself
    # that have 1 less turn to live. When a seed dies (has 0 life), its location
    # is marked as open in the blocks grid. Dead seeds are retained so we can
    # map spaces to the sectors that own those spaces.
    # When two expanding seeds collide, they merge if they are for the same
    # sector (as determined by their 'node' property), or form a wall between
    # them if they are not. 
    def expandSeeds(self, seeds, blocks):
        deadSeeds = dict()
        numCols = len(blocks)
        numRows = len(blocks[0])
        logger.debug("Expanding seeds for a",numCols,"by",numRows,"grid")
        while len(seeds):
            # Uncomment this if you want to see images be drawn at each step,
            # but don't want images for the creation of regions (before the 
            # tunnel tree is made). self.blocks is not defined until after
            # regions are done being created.
#            if self.blocks is not None:
#                self.drawStatus(blocks, seeds, deadSeeds)
            newSeeds = dict()
            for loc, curSeed in seeds.iteritems():
                # If the counter expires while the seed is not in open space,
                # replace it with a wall.
                if (not self.getIsInBounds(loc, numCols, numRows) or 
                        (curSeed.life <= 0 and blocks[loc.ix][loc.iy] != BLOCK_EMPTY)):
                    deadSeeds[loc] = curSeed
                    blocks[loc.ix][loc.iy] = BLOCK_WALL
                    continue

                if (blocks[loc.ix][loc.iy] == BLOCK_WALL):
                    # A wall sprung up under us. Check if there's a dead
                    # seed there; if so, try to merge with it.
                    if loc in deadSeeds:
                        newSeed = self.tryMergeDeadSeed(curSeed, loc, seeds, deadSeeds, numCols, numRows)
                        if newSeed is not None:
                            newSeeds[loc] = newSeed
                            del deadSeeds[loc]
                            blocks[loc.ix][loc.iy] = BLOCK_UNALLOCATED
                    else:
                        # No seeds on walls.
                        continue
                    
                if blocks[loc.ix][loc.iy] == BLOCK_EMPTY:
                    # No seeds on empty space
                    deadSeeds[loc] = curSeed
                    continue

                for adjLoc in loc.perimeter():
                    # Check adjacent blocks for seeds. If none, expand into the
                    # space. If there is a seed, make a wall, unless it's our
                    # own seed in which case we merge with it.
                    if not self.getIsInBounds(adjLoc, numCols, numRows):
                        continue
                    if adjLoc in seeds or adjLoc in newSeeds:
                        # Two adjacent seeds; either merge or make wall.
                        altSeed = None
                        if adjLoc in seeds:
                            altSeed = seeds[adjLoc]
                        else:
                            altSeed = newSeeds[adjLoc]
                        if altSeed.owner == curSeed.owner:
                            # Merge the seeds
                            newSeeds[adjLoc] = seed.Seed(curSeed.owner, 
                                    max(curSeed.life, altSeed.life) - 1,
                                    max(curSeed.age, altSeed.age) + 1)
                        else:
                            # Conflict; make a wall.
                            altSeed.life = 0
                            altSeed.age = constants.BIGNUM
                            curSeed.life = 0
                            curSeed.age = constants.BIGNUM
                            blocks[loc.ix][loc.iy] = BLOCK_WALL
                            blocks[adjLoc.ix][adjLoc.iy] = BLOCK_WALL
                    elif blocks[loc.ix][loc.iy] == BLOCK_UNALLOCATED:
                        # No seed there; plant one.
                        newSeeds[adjLoc] = seed.Seed(curSeed.owner, curSeed.life - 1, curSeed.age + 1)
                    elif (blocks[adjLoc.ix][adjLoc.iy] != BLOCK_EMPTY and
                            deadSeeds.has_key(adjLoc)):
                        # Hit a wall containing a dead seed; try to merge
                        # with it.
                        newSeed = self.tryMergeDeadSeed(curSeed, adjLoc, seeds, deadSeeds, numCols, numRows)
                        if newSeed is not None:
                            newSeeds[adjLoc] = newSeed
                            del deadSeeds[adjLoc]
                            blocks[adjLoc.ix][adjLoc.iy] = BLOCK_UNALLOCATED
   
                # Done expanding; zero our location if we didn't wall it 
                # earlier.
                if blocks[loc.ix][loc.iy] != BLOCK_WALL:
                    blocks[loc.ix][loc.iy] = BLOCK_EMPTY
                deadSeeds[loc] = curSeed
            seeds = newSeeds
        return (blocks, deadSeeds)


    ## Try to merge the given seed with the dead seed at loc. We can merge
    # if they have the same source on the tree, and there are no seeds 
    # adjacent to that seed, dead or alive, that have a different source.
    # \param seed The seed that wants to expand into loc
    # \param loc The location that seed is expanding into
    def tryMergeDeadSeed(self, curSeed, loc, seeds, deadSeeds, numCols, numRows):
        altSeed = deadSeeds[loc]
        if altSeed.owner != curSeed.owner:
            return None
        for neighbor in loc.perimeter():
            if not self.getIsInBounds(neighbor, numCols, numRows):
                continue
            if neighbor in seeds and seeds[neighbor].owner != curSeed.owner:
                return None
            if neighbor in deadSeeds and deadSeeds[neighbor].owner != curSeed.owner:
                return None

        newSeed = seed.Seed(curSeed.owner, curSeed.life - 1, curSeed.age + 1)
        return newSeed


    ## Assign all open spaces to the sectors that own them.
    def assignSquares(self):
        for loc, seed in self.deadSeeds.iteritems():
            if self.blocks[loc.ix][loc.iy] == BLOCK_EMPTY:
                seed.owner.assignSpace(loc)


    ## Finds islands of dead seeds and reassigns their ownership.
    # It is possible to get islands of dead seeds that are in the "wrong"
    # sector (i.e. they are entirely surrounded by walls, or seeds from a 
    # different sector). This breaks our wallwalking algorithm in 
    # treenode.fixAccessibility(), so find these islands and fix them.
    # "Islands" are regions of seeds that are below a minimum cutoff size.
    def fixSeedOwnership(self, blocks, seeds, shouldReassignSpaces = 1):
        chunks = []
        spaceToChunkMap = dict()

        numCols = len(blocks)
        numRows = len(blocks[0])
        
        for i in xrange(0, numCols):
            for j in xrange(0, numRows):
                key = Vector2D(i, j)
                if (blocks[i][j] == BLOCK_EMPTY and 
                        key not in spaceToChunkMap and 
                        key in seeds):
                    type = seeds[key].owner # Local sector type.
                    newChunk = []
                    fillStack = [key]
                    spaceToChunkMap[key] = newChunk
                    while fillStack:
                        loc = fillStack.pop(0)
                        newChunk.append(loc)
                        for neighbor in loc.NEWSPerimeter():
                            if (not self.getIsInBounds(neighbor, numCols, numRows) or
                                    blocks[neighbor.ix][neighbor.iy] != BLOCK_EMPTY):
                                continue
                            if (neighbor not in spaceToChunkMap and 
                                    neighbor in seeds and 
                                    seeds[neighbor].owner == type):
                                fillStack.append(neighbor)
                                spaceToChunkMap[neighbor] = newChunk
                    chunks.append(newChunk)

        chunkStack = []
        chunkStack.extend(chunks)
        while chunkStack:
            chunk = chunkStack.pop(0)
            if len(chunk) < minimumSectorSize:
                # Find an adjacent chunk to merge with
                altChunk = None
                for loc in chunk:
                    if altChunk is not None:
                        break
                    for neighbor in loc.NEWSPerimeter():
                        if not self.getIsInBounds(neighbor, numCols, numRows):
                            continue
                        if (neighbor in spaceToChunkMap and 
                                spaceToChunkMap[neighbor] != chunk):
                            # Found a different chunk to try merging with.
                            altChunk = spaceToChunkMap[neighbor]
                            break
                if altChunk is not None:
                    newType = seeds[altChunk[0]].owner
                    for loc in chunk:
                        seed = seeds[loc]
                        if shouldReassignSpaces:
                            seed.owner.unassignSpace(loc)
                            newType.assignSpace(loc)
                        seeds[loc].owner = newType
                        spaceToChunkMap[loc] = altChunk
                    altChunk.extend(chunk)
                    chunkStack.append(altChunk)
                else:
                    # Couldn't find a valid neighbor for this seed; it must be
                    # isolated by walls. Turn it into one.
                    for loc in chunk:
                        blocks[loc.ix][loc.iy] = BLOCK_WALL
                        
        return (blocks, seeds)


    ## Find the nearest wall to the given starting block along the 
    # normalized vector direction. Return the realspace distance to that wall.
    # \param edge MapEdge in the tree that we are to contain our search to. If 
    # None, then do not constrain the search. Otherwise, treat regions outside
    # that node's area as walls.
    def getDistanceToWall(self, start, direction, edge = None):
        currentSpace = start.copy()
        intCurrent = currentSpace.toInt()
        distance = 0
        # While currentSpace is valid, it's empty space (or filled space close
        # to the start), and we're in the specified sector or we don't care 
        # about the sector, move currentSpace out along direction and
        # recalculate distance.
        while (self.getIsInBounds(currentSpace) and
                (self.blocks[intCurrent.ix][intCurrent.iy] == BLOCK_EMPTY or
                     distance < 2) and
                (edge is None or intCurrent in self.deadSeeds and
                    self.deadSeeds[intCurrent].owner == edge)):
            currentSpace = currentSpace.add(direction)
            intCurrent = currentSpace.toInt()
            distance = currentSpace.distance(start)
        return distance


    ## Build platforms out from start along direction until we get distance
    # away from start.
    def markPlatform(self, start, direction, distance):
        totalDistance = 0
        while totalDistance < distance:
            buildDistance = minDistForPlatform + totalDistance
            buildLoc = start.add(direction.multiply(buildDistance)).toInt()
            shouldBuild = 1
            realLoc = buildLoc.toRealspace()
            width = minHorizDistToOtherPlatforms * constants.blockSize
            height = minVertDistToOtherPlatforms * constants.blockSize
            rect = pygame.Rect(realLoc.x - width, 
                               realLoc.y - height,
                               width * 2,
                               height * 2)
            if not self.platformsQuadTree.getObjectsIntersectingRect(rect):
                self.addPlatform(buildLoc, random.choice(platformWidths))
            totalDistance += buildDistance


    ## Create a set of blocks for each location in self.platforms.
    def buildPlatforms(self):
        for platform in self.platformsQuadTree.getObjects():
            loc = platform.loc
            width = platform.width
            first = int(loc.x - width / 2.0)
            last = int(loc.x + width / 2.0)
            for x in xrange(first, last):
                if (x < 0 or x >= self.numCols or 
                        self.blocks[x][loc.iy] == BLOCK_UNALLOCATED):
                    continue
                self.blocks[x][loc.iy] = BLOCK_WALL


    ## Draw an intermediary status image and saves it to disk. These are often 
    # very helpful for debugging purposes.
    # \param blocks The current blocks for the grid. Uses self.blocks if None.
    # \param seeds Active seeds used during map.expandSeeds().
    # \param deadSeeds Inactive seeds, used to mark sectors on the map.
    # \param marks List of other locations that should be specially marked.
    # \param shouldZoom If true and self.markLoc is set, zoom in on that
    # location.
    # In addition to the above, if map.markLoc is defined, then the map will
    # be focused on that location.
    def drawStatus(self, blocks = None, seeds = None, deadSeeds = None, 
                   marks = None, shouldZoom = True):
        if blocks is None:
            blocks = self.blocks
        self.statusIter += 1
        logger.debug("Drawing status number",self.statusIter,"with mark",self.markLoc)
#        if self.statusIter < 25:
#            return
        # Draw things a bit smaller...
        scale = drawStatusScaleFactor
        screen = pygame.Surface((self.width * scale, self.height * scale))
        size = constants.blockSize * scale

        if blocks is not None:
            numCols = len(blocks)
            numRows = len(blocks[0])
            for i in xrange(0, numCols):
                for j in xrange(0, numRows):
                    rect = pygame.rect.Rect((i * size, j * size), (size, size))
                    if blocks[i][j] in (BLOCK_UNALLOCATED, None):
                        pygame.draw.rect(screen, (64, 64, 64), rect)
                    elif blocks[i][j] != BLOCK_EMPTY:
                        pygame.draw.rect(screen, (255, 255, 255), rect)

#        if self.regions is not None:
#            regionBlock = size / regionOverlayResolutionMultiplier
#            for (i, j), (zoneName, regionName) in self.regions.iteritems():
#                overlayRect = pygame.rect.Rect((i * regionBlock,
#                                                j * regionBlock),
#                                               (regionBlock-1, regionBlock-1))
#                color = self.zoneData[zoneName]['regions'][regionName]['color']
#                color = (color[0], color[1], color[2], 255)
#                pygame.draw.rect(screen, color, overlayRect)
        
        seedRadius = int(constants.blockSize / 2.0 * scale)
        if (deadSeeds is not None and len(deadSeeds) and 
                hasattr(deadSeeds[deadSeeds.keys()[0]].owner, 'color')):
            for loc, seed in deadSeeds.iteritems():
                drawLoc = loc.multiply(size).addScalar(seedRadius).toInt()
                pygame.draw.circle(screen, seed.owner.color, 
                                   drawLoc.tuple(), seedRadius)

        if seeds is not None:
            for loc, seed in seeds.iteritems():
                drawLoc = loc.multiply(size).addScalar(seedRadius).toInt()
                diff = 255 if seed.life <= 0 else int(255 / seed.life)
                pygame.draw.circle(screen, (0, diff, 255 - diff), 
                        drawLoc.tuple(), seedRadius)

        if marks is not None:
            for loc in marks:
                drawLoc = loc.multiply(size).addScalar(seedRadius)
                pygame.draw.circle(screen, (255, 0, 0), drawLoc.tuple(), seedRadius)

        if self.markLoc is not None:
            drawLoc = self.markLoc.multiply(size).addScalar(seedRadius)
            pygame.draw.circle(screen, (0, 255, 255), drawLoc.tuple(), seedRadius+4, 4)

            if shouldZoom:
                subRect = pygame.Rect((self.markLoc.x * size - 400, 
                                       self.markLoc.y * size - 400),
                                       (800, 800))
                subSurface = pygame.Surface((800, 800))
                subSurface.blit(screen, (0, 0), subRect)
                screen = subSurface

        if self.markLoc is None:
            [edge.draw(screen, scale) for edge in self.tunnelEdges]

        pygame.image.save(screen, 'premap-%03d' % self.statusIter + '.png')
        game.imageManager.drawBackground()
        if self.markLoc is None:
            # Non-zoomed view, so scale it so it all fits.
            screen = pygame.transform.rotozoom(screen, 0, constants.sw / float(self.width * scale))


    ## Draw a complete view of the map for purposes of looking pretty. Saves 
    # the result to disk under the provided filename.
    # \todo This was broken by the OpenGL transition -- we no longer use Surface
    # objects to draw to, instead drawing directly to the screen.
    def drawAll(self, filename):
        scale = drawAllScaleFactor
        center = Vector2D(self.width, self.height).multiply(scale / 2.0)
        size = constants.blockSize * scale
        
        screen = pygame.Surface((int(self.width * scale), int(self.height * scale)))
        self.backgroundQuadTree.draw(screen, center, 0, scale)
        self.furnitureQuadTree.draw(screen, center, 0, scale)

        for x in xrange(0, self.numCols):
            for y in xrange(0, self.numRows):
                for effect in self.envGrid[x][y]:
                    effect.draw(screen, Vector2D(x, y).toRealspace(), center, 0, scale)

        for y in xrange(self.numRows - 1, 0, -1):
            # Draw from bottom to top because blocks may "hang" down a bit.
            for x in xrange(0, self.numCols):
                block = self.blocks[x][y]
                if block:
                    block.draw(screen, center, 0, scale)
                elif block is None:
                    rect = pygame.rect.Rect((x * size, y * size), 
                                            (size, size))
                    pygame.draw.rect(screen, (64, 64, 64), rect)
        
        pygame.image.save(screen, filename)


    ## Draw the background scenery and any environmental effects at the given
    # location.
    def drawBackground(self, progress):
        self.backgroundQuadTree.draw(progress)
        # \todo This culls which environmental effects to draw based on the 
        # camera position, but doesn't take into account zoom, so when we 
        # zoom out, effects will not be drawn when they should be. 
        rect = pygame.rect.Rect(0, 0, constants.sw, constants.sh)
        rect.center = game.camera.getDrawLoc().tuple()
        min = Vector2D(rect.topleft).toGridspace().sub(Vector2D(1, 1))
        max = Vector2D(rect.bottomright).toGridspace().add(Vector2D(2, 2))
        for x in xrange(min.ix, max.ix):
            if x < 0 or x >= self.numCols:
                continue
            for y in xrange(min.iy, max.iy):
                if y < 0 or y >= self.numRows:
                    continue
                for effect in self.envGrid[x][y]:
                    effect.draw(Vector2D(x, y).toRealspace(), progress)


    ## Draw the furniture and terrain tiles.
    def drawMidground(self, progress):
        self.furnitureQuadTree.draw(progress)
        game.imageManager.drawList(self.blockDisplayList)


    ## Assign the given space to the given node, and unassign it from whoever
    # owned it before.
    def assignSpace(self, space, node):
        if space in self.deadSeeds:
            self.deadSeeds[space].owner.unassignSpace(space)
        node.assignSpace(space)
        self.deadSeeds[space] = seed.Seed(node, 0, constants.BIGNUM)


    ## Mark a space as containing a platform. Don't do tile assignation until
    # later, as it might interfere with TreeNode.fixAccessibility() if done
    # now.
    def addPlatform(self, loc, size):
        loc = loc.toInt()
        if self.getIsInBounds(loc):
            newPlatform = floatingplatform.FloatingPlatform(loc, size)
            self.platformsQuadTree.addObject(newPlatform)


    ## Add a background object (a Scenery instance) to the map.
    def addBackgroundObject(self, obj):
        self.backgroundQuadTree.addObject(obj)


    ## Remove all background objects found that are attached to the 
    # specified grid location.
    def removeBackgroundObject(self, gridLoc):
        didDelete =  False
        for object in self.backgroundQuadTree.getObjects():
            if object.gridLoc == gridLoc:
                self.backgroundQuadTree.removeObject(object)
                didDelete = True
        return didDelete


    ## Mark the given tile as containing the selected environmental effect.
    def addEnvEffect(self, loc, effect):
        loc = loc.toInt()
        if self.getIsInBounds(loc):
            self.envGrid[loc.ix][loc.iy].append(effect)


    def getStartLoc(self):
        return self.startLoc


    ## Collide the given object against our terrain, and keep doing it until
    # the object is not intersecting any blocks, or we hit our maximum number
    # of attempts (in which case the object gets zipped). 
    def collideObject(self, object):
        numAttempts = 0
        while numAttempts < maxCollisionRetries:
            numAttempts += 1

            collision = self.collidePolygon(object.getPolygon(), object.loc)
            logger.debug("Received collision information",collision)
            if collision is not None:
                object.processCollision(collision)
            else:
                # No collision, so we're done here.
                break
        if numAttempts == maxCollisionRetries:
            logger.debug("Forced to zip object",object.name,"at",object.loc)
            # Terrain collision detection failed; zip.
            object.loc = object.loc.add(zipAmount)


    ## Collide a polygon against our terrain, and return a CollisionData object.
    def collidePolygon(self, poly, loc):
        result = collisiondata.CollisionData(None, -constants.BIGNUM, 'solid', None)
        polyRect = poly.getBounds(loc)
        logger.debug("Trying",poly.printAdjusted(loc))
        # First, check for furniture hits. 
        # \todo We don't correct ejection vectiors for furniture, even though
        # we could still get improper ejection directions
        for item in self.furnitureQuadTree.getObjectsIntersectingRect(polyRect):
            (overlap, vector) = item.collidePolygon(poly, loc)
            if vector is not None and overlap > result.distance:
                result.distance = overlap
                result.vector = vector
                result.altObject = item
                return result
        excludedColumns = dict()
        excludedRows = dict()
        upperLeft = poly.upperLeft.add(loc).toGridspace().add(Vector2D(-1, -1))
        lowerRight = poly.lowerRight.add(loc).toGridspace().add(Vector2D(2, 2))

        for x in xrange(max(0, upperLeft.ix), min(self.numCols, lowerRight.ix)):
            if x in excludedColumns:
                continue
            for y in xrange(max(0, upperLeft.iy), min(self.numRows, lowerRight.iy)):
                if y in excludedRows:
                    continue
                if (self.blocks[x][y] != BLOCK_EMPTY and
                        self.blocks[x][y].getBounds().colliderect(polyRect)):
                    (overlap, vector) = self.blocks[x][y].collidePolygon(poly, loc)
                    if vector is not None:
                        if overlap > result.distance:
                            result.distance = overlap
                            result.vector = vector
                            result.altObject = self.blocks[x][y]
                        # Prune out some blocks that we needn't care about. If
                        # a creature runs horizontally into one block, then
                        # all blocks immediately above/below that block are
                        # uninteresting, for example.
                        if abs(vector.y) < constants.EPSILON:
                            excludedColumns[x] = True
                        elif abs(vector.x) < constants.EPSILON:
                            excludedRows[y] = True
        if result.vector is not None:
            result.vector = self.fixEjectionVector(result.vector, result.altObject)
            return result
        return None


    ## Determine if there is a block adjacent to the given block along the
    # provided vector. If there is, find an alternate direction that isn't
    # obstructed and return it.
    def fixEjectionVector(self, vector, centerBlock):
        checkLoc = centerBlock.gridLoc.add(vector)
        checkBlock = self.getBlockAtGridLoc(checkLoc)
        if checkBlock and checkBlock != centerBlock:
            logger.debug("Ejection vector points into another block")
            # Objects that get sufficiently embedded in the walls can get 
            # inaccurate ejection vectors because the shortest path for one 
            # tile of the wall is into another tile. Manually correct
            # the ejection vector if this happens.
            # \todo It'd be nice if we didn't have to do this.
            for checkLoc in centerBlock.gridLoc.NEWSPerimeter():
                if not self.getBlockAtGridLoc(checkLoc):
                    delta = checkLoc.sub(centerBlock.gridLoc)
                    logger.debug("Converting ejection vector from",vector,"to",delta)
                    vector = delta
                    break
        return vector


    ## Load map information from disk. The filename is equal to the name of the
    # map.
    # \todo This parser is very brittle, and while the map file format is not
    # meant to be directly user-editable, there's no reason we couldn't be 
    # more flexible here.
    def loadMap(self):
        fh = open(self.mapName, 'r')
        lineNum = 0
        terrainInfoCache = dict()
        envEffectCache = dict()
        mode = 'dimensions'
        for line in fh:
            line = line.rstrip()
            lineNum += 1
            if mode == 'dimensions':
                # Read map dimensions
                (cols, rows) = line.split(',')
                self.numCols = int(cols)
                self.width = self.numCols * constants.blockSize
                self.numRows = int(rows)
                self.height = self.numRows * constants.blockSize
                logger.inform("Loading a",self.numCols,"by",self.numRows,"map")
                self.blocks = []
                self.envGrid = []
                for i in xrange(0, self.numCols):
                    self.blocks.append([])
                    self.envGrid.append([])
                    for j in xrange(0, self.numRows):
                        self.blocks[i].append(BLOCK_EMPTY)
                        self.envGrid[i].append([])

                self.furnitureQuadTree = quadtree.QuadTree(self.getBounds())
                self.backgroundQuadTree = quadtree.QuadTree(self.getBounds())
                
                mode = 'start'
            elif mode == 'start':
                if line == 'blocks:':
                    logger.inform("Loading block information at",pygame.time.get_ticks())
                    mode = 'blocks'
                    continue
                # Read starting location
                (x, y) = line.split(',')
                self.startLoc = Vector2D(int(x), int(y))
            elif mode == 'blocks':
                if line == 'furniture:':
                    logger.inform("Loading furniture at",pygame.time.get_ticks())
                    mode = 'furniture'
                    continue
                (x, y, zone, region, orientation, subType) = line.split(',')
                x = int(x)
                y = int(y)
                subType = int(subType)
                region = region.rstrip()
                if (zone, region) not in terrainInfoCache:
                    terrainInfoCache[(zone, region)] = terraininfo.TerrainInfo(zone, region)
                self.blocks[x][y] = block.Block(Vector2D(x, y),
                                            terrainInfoCache[(zone, region)], 
                                            orientation, subType)
            elif mode == 'furniture':
                if line == 'enveffects:':
                    logger.inform("Loading environmental effects at",pygame.time.get_ticks())
                    mode = 'enveffects'
                    continue
                (x, y, zone, region, group, subGroup) = line.split(',')
                x = int(x)
                y = int(y)
                if (zone, region) not in terrainInfoCache:
                    terrainInfoCache[(zone, region)] = terraininfo.TerrainInfo(zone, region)
                newFurniture = furniture.Furniture(Vector2D(x, y), 
                        terrainInfoCache[(zone, region)], group, subGroup)
                self.furnitureQuadTree.addObject(newFurniture)
            elif mode == 'enveffects':
                if line == 'scenery:':
                    logger.inform("Loading scenery at",pygame.time.get_ticks())
                    mode = 'scenery'
                    continue
                (location, effects) = line.split(':')
                (x, y) = location.split(',')
                x = int(x)
                y = int(y)
                effects = effects.split(',')
                for name in effects:
                    if name not in envEffectCache:
                        envEffectCache[name] = enveffect.EnvEffect(name)
                    envEffectCache[name].addSpace(Vector2D(x, y), self)

            elif mode == 'scenery':
                (x, y, zone, region, group, item) = line.split(',')
                x = int(x)
                y = int(y)
                if (zone, region) not in terrainInfoCache:
                    terrainInfoCache[(zone, region)] = terraininfo.TerrainInfo(zone, region)
                self.addBackgroundObject(
                        scenery.Scenery(Vector2D(x, y), 
                                  terrainInfoCache[(zone, region)], 
                                  group, item))
        logger.inform("Done loading map at",pygame.time.get_ticks())

    
    ## Load an image file as if it were a map. Each pixel is one tile; 
    # black pixels are filled, others are not.
    # Uses a dummy start location of (0, 0), since this isn't meant to be 
    # used for actual gameplay; just for converting images to normal maps.
    # \todo Base the terrain used on the color of the pixel.
    def loadImageAsMap(self, image):
        self.startLoc = Vector2D(0, 0)
        (self.numCols, self.numRows) = image.get_size()
        self.width = self.numCols * constants.blockSize
        self.height = self.numRows * constants.blockSize
        logger.inform("Loading a",self.numCols,"by",self.numRows,"map from an image")
        self.blocks = []
        self.envGrid = []
        for i in xrange(0, self.numCols):
            self.blocks.append([])
            self.envGrid.append([])
            for j in xrange(0, self.numRows):
                self.blocks[i].append(BLOCK_EMPTY)
                self.envGrid[i].append([])

        self.furnitureQuadTree = quadtree.QuadTree(self.getBounds())
        self.backgroundQuadTree = quadtree.QuadTree(self.getBounds())
                
        self.zoneData = zone.loadZoneData()
        colorToTerrainMap = {}

        for i in xrange(self.numCols):
            if i % 10 == 0:
                logger.inform("Creating column", i)
            for j in xrange(self.numRows):
                color = image.get_at((i, j))
                (r, g, b, a) = color
                if a != 0: # Nonzero opacity
                    self.blocks[i][j] = BLOCK_WALL
                else:
                    self.blocks[i][j] = BLOCK_EMPTY
                if color not in colorToTerrainMap:
                    # Find the color of an existing terrain that best-matches
                    # the color in the image, and use that terrain.
                    bestDistance = None
                    bestZone = None
                    bestRegion = None
                    for zoneName, zoneInfo in self.zoneData.iteritems():
                        for regionName, regionData in zoneInfo['regions'].iteritems():
                            (ra, rg, rb) = regionData['color']
                            distance = math.sqrt((r - ra) ** 2 + 
                                                 (g - rg) ** 2 + 
                                                 (b - rb) ** 2)
                            if bestDistance is None or distance < bestDistance:
                                bestDistance = distance
                                bestZone = zoneName
                                bestRegion = regionName
                    colorToTerrainMap[color] = terraininfo.TerrainInfo(
                            bestZone, bestRegion
                    )

        # We could do this in the original pass if we modified getBlockType,
        # but this way keeps the image manipulation work to one place and 
        # shouldn't have too bad a hit to our performance.
        logger.inform("Instantiating blocks")
        for i in xrange(self.numCols):
            for j in xrange(self.numRows):
                if self.blocks[i][j] == BLOCK_WALL:
                    blockLoc = Vector2D(i, j)
                    terrain = colorToTerrainMap[image.get_at((i, j))]
                    (type, signature) = self.getBlockType(i, j)
                    self.blocks[i][j] = block.Block(blockLoc, terrain, type)
                # else self.blocks[i][j] == BLOCK_EMPTY, do nothing

        logger.inform("Map load complete")


    ## Add a block to the map.
    # \todo Handle expanding the map to place blocks outside of its current
    # boundaries.
    def addBlock(self, newBlock):
        if self.getIsInBounds(newBlock.gridLoc):
            self.blocks[newBlock.gridLoc.ix][newBlock.gridLoc.iy] = newBlock
        else:
            logger.warn("Block location", newBlock.gridLoc, "is out of bounds")


    ## Remove a block from the map
    def deleteBlock(self, blockLoc):
        if self.getIsInBounds(blockLoc):
            self.blocks[blockLoc.ix][blockLoc.iy] = BLOCK_EMPTY
        else:
            logger.warn("Tried to delete block at", blockLoc, 
                        "which is out of bounds")


    ## Add furniture at the given location. 
    def addFurniture(self, furniture):
        rect = furniture.getBounds()
        topLeft = Vector2D(rect.topleft).toGridspace()
        bottomRight = Vector2D(rect.bottomright).toGridspace()
        logger.debug("Placing furniture",furniture,"with bounds from",topLeft,"to",bottomRight)
        for x in xrange(max(0, topLeft.ix), min(self.numCols, bottomRight.ix)):
            for y in xrange(max(0, topLeft.iy), min(self.numRows, bottomRight.iy)):
                if self.blocks[x][y] != BLOCK_EMPTY:
                    logger.debug("Removed block at",(x,y))
                self.blocks[x][y] = BLOCK_EMPTY
        self.furnitureQuadTree.addObject(furniture)


    ## Write our map to disk so it can be read by loadMap().
    # \todo Make saveable objects handle their own read/write logic. This is
    # getting pretty ugly.
    def writeMap(self, name = None):
        if name is None:
            name = self.mapName.replace('.map', '') + '-tmp'
        fh = open(name + '.map', 'w')
        fh.write("%d,%d\n" % (self.numCols, self.numRows))
        fh.write("%d,%d\n" % (self.startLoc.x, self.startLoc.y))
        fh.write("blocks:\n")
        for x in xrange(0, self.numCols):
            for y in xrange(0, self.numRows):
                if self.blocks[x][y] not in (BLOCK_EMPTY, None):
                    block = self.blocks[x][y]
                    fh.write("%d,%d,%s,%s,%s,%d\n" % (x, y, 
                        block.terrain.zone, block.terrain.region,
                        block.orientation, block.subType))
        fh.write("furniture:\n")
        for item in self.furnitureQuadTree.getObjects():
            fh.write("%d,%d,%s,%s,%s,%s\n" % (item.loc.x, item.loc.y,
                                            item.terrain.zone, 
                                            item.terrain.region,
                                            item.group, item.subGroup))
        fh.write("enveffects:\n")
        for x in xrange(0, self.numCols):
            for y in xrange(0, self.numRows):
                if self.envGrid[x][y]:
                    string = ",".join(effect.name for effect in self.envGrid[x][y])
                    fh.write("%d,%d:%s\n" % (x, y, string))
        
        fh.write("scenery:\n")
        for item in self.backgroundQuadTree.getObjects():
            fh.write("%d,%d,%s,%s,%s,%s\n" % 
                     (item.loc.x, item.loc.y, item.terrain.zone, 
                      item.terrain.region, item.group, item.item))


    ## Simple boundary check for the blocks grid.
    def getIsInBounds(self, loc, numCols = None, numRows = None):
        if numCols is None:
            numCols = self.numCols
        if numRows is None:
            numRows = self.numRows
        return (loc.x >= 0 and loc.x < numCols and
                loc.y >= 0 and loc.y < numRows)


    ## Returns the region information at the given location. See makeRegions()
    # for more information on regions.
    def getTerrainInfoAtGridLoc(self, loc):
        regionLoc = loc.multiply(regionOverlayResolutionMultiplier).toInt()
        if regionLoc in self.regions:
            return self.regions[regionLoc]
        return None


    def getBlockAtGridLoc(self, loc):
        if not self.getIsInBounds(loc):
            return None
        loc = loc.toInt()
        return self.blocks[loc.ix][loc.iy]


    ## Get the TreeNode that owns the given space, if any.
    def getSectorAtGridLoc(self, loc):
        if loc not in self.deadSeeds:
            return None
        return self.deadSeeds[loc].owner


    ## Return the data in the specified field for the given terrain type.
    def getRegionInfo(self, info, field):
        if (info.zone in self.zoneData and 
                info.region in self.zoneData[info.zone]['regions'] and
                field in self.zoneData[info.zone]['regions'][info.region]):
            return self.zoneData[info.zone]['regions'][info.region][field]
        return None


    ## Return the size of the game map as a PyGame Rect.
    def getBounds(self):
        return pygame.rect.Rect((0, 0), (self.width, self.height))

