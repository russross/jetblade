import constants
import line
import treenode
import zone
import block
import enveffect
import prop
import jetblade
import util
import quadtree
import seed

import sys
import math
import copy
import random
import pygame

## Minimum width of the game world
minUniverseWidth = constants.sw * 24
## Minimum height of the game world
minUniverseHeight = constants.sh * 24
## Degree to which the game world dimensions are allowed to vary. The range thus
# defined is e.g. 
# [minUniverseWidth, minUniverseWidth + universeDimensionVariance] for width.
universeDimensionVariance = 0

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

## Amount to scale the map by when calling Map.drawStatus()
drawStatusScaleFactor = .2
## Amount to scale the map by when calling Map.DrawAll()
# Note that PyGame can't create surfaces bigger than about 16k pixels to a side
drawAllScaleFactor = .2

## Minimum physical distance between branches of the tree that describes the 
# general shape of the map.
treePruneDistance = 15 * constants.blockSize

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
platformWidths = [1, 2, 2, 3]
## Platforms are randomly pushed to the left/right by choosing from this list.
platformHorizontalOffsets = [-1, 0, 1]

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

## The Map class handles creating, updating, and displaying the game map. This
# includes the following structures:
# - The root TreeNode for the tree that describes the high-level structure of 
#   the map tunnels.
# - A grid of terrain tiles.
# - Another grid for environmental effects.
# - A quadtree containing all background props.
class Map:

    ## Prepare a blank map and a bunch of values we'll need while
    # constructing it. Most of this is unneeded if we're loading the map.
    def __init__(self, mapName = None):
        ## Number of the most recent file output by drawStatus()
        self.statusIter = 0
        self.mapName = mapName
         
        ## 2D array of blocks, None, or 0.
        # - Block: standard filled space
        # - None: Nominally solid space but not drawn
        # - 0 Empty space
        # 
        # During construction, the values are different:
        # - 0: Empty space
        # - 1: Uninitialized space
        # - 2: Wall
        # \todo These should be enumerated somewhere and the enums used instead
        # of bare integers.
        self.blocks = None
        
        ## Marks spaces as belonging to different environments. Built to same
        # scale as blocks.
        self.envGrid = None

        ## Holds background props.
        self.backgroundQuadTree = None

        ## Marks high-level structure of the map.
        self.tree = None

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

        ## A list of locations that we will want to add platforms to.
        self.platforms = []

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
            self.loadMap()
        else:
            self.createMap()


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
        self.backgroundQuadTree = quadtree.QuadTree(pygame.rect.Rect((0, 0), (self.width, self.height)))

        ## This quadtree holds lines; we use it to make certain that limbs of
        # the tree do not come too close to each other (or intersect). 
        self.treeLines = quadtree.QuadTree(pygame.rect.Rect((0, 0), (self.width, self.height)))
        self.treeLines.addObjects([line.Line((0, 0), (self.width, 0)),
                line.Line((self.width, 0), (self.width, self.height)),
                line.Line((self.width, self.height), (0, self.height)),
                line.Line((0, self.height), (0, 0))])

        self.numCols = self.width / constants.blockSize
        self.numRows = self.height / constants.blockSize
        
        util.debug("Making a",self.numCols,"x",self.numRows,"map")
        util.debug("Started making map at",pygame.time.get_ticks())

        # First we need to figure out which parts of the map belong to which
        # regions. Make a low-rez overlay for the map that marks out regions.
        self.regions = self.makeRegions()
        util.debug("Done marking regions at",pygame.time.get_ticks())

        # Create the array for the actual blocks.
        self.blocks = []
        self.envGrid = []
        for i in range(0, self.numCols):
            self.blocks.append([])
            self.envGrid.append([])
            for j in range(0, self.numRows):
                self.blocks[i].append(1)
                self.envGrid[i].append([])
        util.debug("Grid laid out at",pygame.time.get_ticks())
        
        # Generate the tree that will be used to mark out tunnels.
        self.tree = treenode.TreeNode([self.width / 2.0, self.height / 2.0], None, 0)
        depth = 0
        while self.tree.createTree():
            depth += 1
            util.debug("Created tree at depth",depth,"at",pygame.time.get_ticks())
#            self.drawStatus()
        util.debug("Done constructing tree at",pygame.time.get_ticks())
         
        # Lay the seeds for those tunnels.
        self.tree.createTunnels()
        util.debug("Seeds planted at",pygame.time.get_ticks())
#        self.drawStatus()

        # Expand the seeds and carve out those tunnels. 
        (self.blocks, self.deadSeeds) = self.expandSeeds(self.seeds, self.blocks)
        util.debug("Done expanding seeds at",pygame.time.get_ticks())
#        self.drawStatus()

        # Clean up the points where tunnels meet.
        self.createJunctions()
        util.debug("Done creating junctions at",pygame.time.get_ticks())
#        self.drawStatus()

        # Remove isolated chunks of land.
        self.removeIslands()
        util.debug("Done removing islands at",pygame.time.get_ticks())

        # Make the walls a bit thicker.
        self.expandWalls()
        util.debug("Done expanding walls at",pygame.time.get_ticks())
#        self.drawStatus()

        # Tell the tree nodes which spaces belong to them.
        self.assignSquares()
        util.debug("Done assigning squares at",pygame.time.get_ticks())

        # Fill in tunnels with interesting terrain.
        self.tree.createFeatures()
        util.debug("Done creating tunnel features at",pygame.time.get_ticks())

        # Reassign any seeds that got isolated in the last step to prevent
        # loops in the next step.
        (self.blocks, self.deadSeeds) = self.fixSeedOwnership(self.blocks, self.deadSeeds)
        util.debug("Done fixing seed ownership at",pygame.time.get_ticks())

        # Walk the walls of sectors of the tree and add platforms where needed.
        self.fixAccessibility()
        util.debug("Done fixing accessibility at",pygame.time.get_ticks())

        # Mark those platforms on the map.
        self.buildPlatforms()

        # Set the block types for each cell in self.blocks.
        self.setBlocks()
        util.debug("Done setting block types at",pygame.time.get_ticks())

        # Turn those block types into instances of the Block class.
        self.instantiateBlocks()
        util.debug("Done instantiating blocks at",pygame.time.get_ticks())

        self.markLoc = None
        self.drawStatus(self.blocks, None, self.deadSeeds)

        # \todo Pick a better starting point for the player.
        self.startLoc = [int(self.numCols / 2), int(self.numRows / 2)]
        while self.blocks[self.startLoc[0]][self.startLoc[1]] != 0:
            self.startLoc[1] -= 1

        self.writeMap(str(jetblade.seed))

        util.debug("Done making map at",pygame.time.get_ticks())
        numUsedSpaces = 0
        for x in range(0, self.numCols):
            for y in range(0, self.numRows):
                if self.blocks[x][y] is not None:
                    numUsedSpaces += 1
        totalSpaces = self.numCols * self.numRows
        percent = numUsedSpaces / float(totalSpaces)
        util.debug(numUsedSpaces,"of",totalSpaces,"spaces are occupied for a %.2f%% occupancy rate" % percent)


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
        for i in range(0, cols):
            blocks.append([])
            for j in range(0, rows):
                blocks[i].append(1)
                # Map (i, j) to the ranges ([0, 1], [0, 1]) and find the zone
                # point that is closest to that location. Mark (i, j) as 
                # belonging to that zone.
                loc = (i / float(cols), j / float(rows))
                closestZone = None
                closestDist = constants.BIGNUM
                for zoneName, zoneLoc in zonePoints.iteritems():
                    dist = util.pointPointDistance(loc, zoneLoc)
                    if dist < closestDist:
                        closestZone = zoneName
                        closestDist = dist
                
                if closestZone not in zoneToBlocksMap:
                    zoneToBlocksMap[closestZone] = []
                zoneToBlocksMap[closestZone].append((i, j))
                blockToZoneMap[(i, j)] = closestZone

        # Create a set of seeds for the different zones. Place them randomly
        # within each zone, and give them life proportionate to their desired
        # size.
        seeds = dict()
        for zoneName, zoneInfo in self.zoneData.iteritems():
            totalWeight = 0
            zoneLocs = zoneToBlocksMap[zoneName]
            for region, weight in zoneInfo['regionWeights'].iteritems():
                totalWeight += weight
            zoneSize = math.sqrt(len(zoneLocs))
            for regionName, weight in zoneInfo['regionWeights'].iteritems():
                loc = random.choice(zoneLocs)
                numTries = 0
                while loc in seeds and numTries < regionOverlayNumSeedingRetries:
                    numTries += 1
                    loc = random.choice(zoneLocs)
                life = int(zoneSize * math.sqrt(weight / float(totalWeight)))
                seeds[loc] = seed.Seed((zoneName, regionName), life, 0)

        # Prep the overlay for the seed expansion step
        for i in range(0, cols):
            for j in range(0, rows):
                blocks[i][j] = 1

        # And expand those seeds into regions
        (blocks, seeds) = self.expandSeeds(seeds, blocks)
        
        # There's no guarantee that we reached every space in blocks, so 
        # convert the ones that weren't touched into a default for that region,
        # while we turn everything into "open space" for fixSeedOwnership, which
        # will eliminate islands for us.
        for i in range(0, cols):
            for j in range(0, rows):
                if blocks[i][j] == 1:
                    zoneName = blockToZoneMap[(i, j)]
                    seeds[(i, j)] = seed.Seed((zoneName, self.zoneData[zoneName]['biggestRegion']), 0, constants.BIGNUM)
                blocks[i][j] = 0

        
        (blocks, seeds) = self.fixSeedOwnership(blocks, seeds, 0)
        result = dict()
        for loc, resultSeed in seeds.iteritems():
            result[loc] = resultSeed.node
        return result


    ## Create open junctions wherever two corridors meet.
    def createJunctions(self):
        self.tree.createJunctions()


    ## Widen every wall by adding walls on either side.
    def expandWalls(self):
        # If we only go in one direction, we get walls from one sector
        # adjacent to open spaces owned by a different sector, which creates
        # terrain mismatches.
        amount = wallThickness / 2
        newBlocks = copy.deepcopy(self.blocks)
        for i in range(amount, self.numCols - amount):
            for j in range(amount, self.numRows - amount):
                if self.blocks[i][j] == 2:
                    for ii in range(-amount, amount + 1):
                        for jj in range(-amount, amount + 1):
                            newBlocks[i-ii][j-jj] = 2
        self.blocks = newBlocks


    ## Replace the values in self.blocks with block type info. At this point
    # self.blocks consists of the following:
    # - 0: empty space
    # - 1: filled space surrounded by other filled space
    # - 2: filled space next to empty space
    # - Tuple of block typestring (e.g. 'upleft') and adjacency signature
    def setBlocks(self):
        for i in range(0, self.numCols):
            for j in range(0, self.numRows):
                if self.blocks[i][j] == 1:
                    self.blocks[i][j] = None
                elif self.blocks[i][j] not in (0, None):
                    (type, signature) = self.getBlockType(i, j)
                    self.blocks[i][j] = (type, signature)


    ## Return the type of block that should be drawn at the given grid loc.
    # Determine this by the locations of neighbors of the block -- its 
    # "adjacency signature". 
    def getBlockType(self, x, y):
        # Get the set of adjacencies for this block. 
        # 0 = empty.
        # 1 = occupied.
        adjacencies = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        numOpen = 0

        for i in range(x-1,x+2):
            for j in range(y-1,y+2):
                if self.getBlockAtGridLoc((i, j)) == 0:
                    adjacencies[j-(y-1)][i-(x-1)] = 0
                    numOpen += 1

        # We should always get 1 result back because all values in the 
        # adjacencies array are 0 or 1 (see that function for more information).
        signature = util.adjacencyArrayToSignatures(adjacencies)[0]

        if signature in self.adjacenciesMap:
            return (self.adjacenciesMap[signature], signature)
        return ('center', signature)


    ## Do a connectivity check on the map. Remove all areas whose size is 
    # less than minimumIslandSize. This is very similar to the 
    # logic in fixSeedOwnership(), but operates on walls instead of seeds and 
    # removes islands intirely instead of merging them with neighbors.
    def removeIslands(self):
        chunks = []
        seenSpaces = dict()
        
        for i in range(0, self.numCols):
            for j in range(0, self.numRows):
                key = (i, j)
                if (self.blocks[i][j] != 0 and 
                        not seenSpaces.has_key(key)):
                    newChunk = []
                    fillStack = [key]
                    seenSpaces[key] = 1
                    while fillStack:
                        loc = fillStack.pop(0)
                        newChunk.append(loc)
                        for offset in constants.NEWSPerimeterOrder:
                            x = loc[0] + offset[0]
                            y = loc[1] + offset[1]
                            if (self.getIsInBounds((x, y)) and 
                                    self.blocks[x][y] != 0 and
                                    not seenSpaces.has_key((x, y))):
                                fillStack.append((x, y))
                                seenSpaces[(x, y)] = type
                    chunks.append(newChunk)

        for chunk in chunks:
            if len(chunk) < minimumIslandSize:
                for loc in chunk:
                    self.blocks[loc[0]][loc[1]] = 0


    ## For each block in self.blocks that is not 0 (empty space) or
    # None (filled, undrawn space), create a Block instance.
    # At this time, also instantiate any props that are attached to the blocks.
    def instantiateBlocks(self):
        for i in range(0, self.numCols):
            for j in range(0, self.numRows):
                if isinstance(self.blocks[i][j], tuple):
                    (type, signature) = self.blocks[i][j]
                    terrain = None
                    flavor = None
                    if (i, j) in self.deadSeeds:
                        (terrain, flavor) = self.deadSeeds[(i, j)].node.getTerrainInfo()
                        blockLoc = (i * constants.blockSize, j * constants.blockSize)
                        self.blocks[i][j] = block.Block(blockLoc, type, signature, terrain, flavor)
                        # Choose a prop to attach to the block.
                        newProp = jetblade.propManager.selectProp(terrain, flavor, signature)
                        if newProp is not None:
                            newProp.loc = util.addVectors(blockLoc, newProp.loc)
                            self.addBackgroundObject(newProp)
                    else:
                        # This space was probably originally uninitialized, and
                        # became a wall as part of expandWalls(). For now, just
                        # leave it blank.
                        # \todo: make a wall by picking up region info 
                        # from adjacent blocks.
                        self.blocks[i][j] = 0
#                        self.markLoc = (i, j)
#                        self.drawStatus()
#                        util.fatal("Unable to find terrain information for block at " + str((i,j)))


    ## Plant a seed for hollowing out part of the map at the desired
    # location.
    def plantSeed(self, loc, node, size):
        x = int(loc[0] / constants.blockSize)
        y = int(loc[1] / constants.blockSize)
        if self.getIsInBounds((x, y)):
            self.seeds[(x, y)] = seed.Seed(node, int(size / constants.blockSize / 2.0), 0)


    ## Run a spacefilling automaton to divide a grid up into different sectors.
    # \param seeds A mapping of locations to Seed instances
    # \param blocks A grid of blocks, which may be:
    # - 0: open
    # - 1: uninitialized
    # - 2: Closed
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
        while len(seeds):
            # Uncomment this if you want to see images be drawn at each step,
            # but don't want images for the creation of regions (before the 
            # tunnel tree is made).
#            if self.blocks is not None:
#                self.drawStatus(blocks, seeds, deadSeeds)
            newSeeds = dict()
            for loc, curSeed in seeds.iteritems():
                # If the counter expires while the seed is not in open space,
                # or the seed is on the border, replace
                # it with a wall.
                if ((loc[0] <= 0 or loc[0] >= numCols - 1 or
                        loc[1] <= 0 or loc[1] >= numRows - 1) or
                        (curSeed.life <= 0 and blocks[loc[0]][loc[1]] != 0)):
                    deadSeeds[loc] = curSeed
                    blocks[loc[0]][loc[1]] = 2
                    continue

                if (blocks[loc[0]][loc[1]] == 2):
                    # A wall sprung up under us. Check if there's a dead
                    # seed there; if so, try to merge with it.
                    if loc in deadSeeds:
                        newSeed = self.tryMergeDeadSeed(curSeed, loc, seeds, deadSeeds, numCols, numRows)
                        if newSeed is not None:
                            newSeeds[loc] = newSeed
                            del deadSeeds[loc]
                            blocks[loc[0]][loc[1]] = 1
                    else:
                        # No seeds on walls.
                        continue
                    
                if blocks[loc[0]][loc[1]] == 0: # No seeds on empty space
                    deadSeeds[loc] = curSeed
                    continue

                for offset in constants.perimeterOrder:
                    # Check adjacent blocks for seeds. If none, expand into the
                    # space. If there is a seed, make a wall, unless it's our
                    # own seed in which case we merge with it.
                    x = loc[0] + offset[0]
                    y = loc[1] + offset[1]
                    if not self.getIsInBounds((x, y), numCols, numRows):
                        continue
                    if (x, y) in seeds and (x, y) not in newSeeds:
                        # Two adjacent seeds; either merge or make wall.
                        altSeed = seeds[(x, y)]
                        if altSeed.node == curSeed.node:
                            # Merge the seeds
                            newSeeds[(x, y)] = seed.Seed(curSeed.node, 
                                    max(curSeed.life, altSeed.life) - 1,
                                    max(curSeed.age, altSeed.age) + 1)
                        else:
                            # Conflict; make a wall.
                            altSeed.life = 0
                            altSeed.age = constants.BIGNUM
                            curSeed.life = 0
                            curSeed.age = constants.BIGNUM
                            blocks[x][y] = 2
                            blocks[loc[0]][loc[1]] = 2
                    elif blocks[x][y] == 1:
                        # No seed there; plant one.
                        newSeeds[(x, y)] = seed.Seed(curSeed.node, curSeed.life - 1, curSeed.age + 1)
                    elif blocks[x][y] != 0 and deadSeeds.has_key((x, y)):
                        # Hit a wall containing a dead seed; try to merge
                        # with it.
                        newSeed = self.tryMergeDeadSeed(curSeed, (x, y), seeds, deadSeeds, numCols, numRows)
                        if newSeed is not None:
                            newSeeds[(x, y)] = newSeed
                            del deadSeeds[(x, y)]
                            blocks[x][y] = 1
   
                # Done expanding; zero our location if we didn't wall it 
                # earlier.
                if blocks[loc[0]][loc[1]] != 2:
                    blocks[loc[0]][loc[1]] = 0
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
        if altSeed.node != curSeed.node:
            return None
        for offset in constants.perimeterOrder:
            x = loc[0] + offset[0]
            y = loc[1] + offset[1]
            if not self.getIsInBounds((x, y), numCols, numRows):
                continue
            if (x, y) in seeds and seeds[(x, y)].node != curSeed.node:
                return None
            if (x, y) in deadSeeds and deadSeeds[(x, y)].node != curSeed.node:
                return None

        newSeed = seed.Seed(curSeed.node, curSeed.life - 1, curSeed.age + 1)
        return newSeed


    ## Assign all open spaces to the sectors that own them.
    def assignSquares(self):
        for loc, seed in self.deadSeeds.iteritems():
            if self.blocks[loc[0]][loc[1]] == 0:
                seed.node.assignSpace(loc)


    ## Finds islands of dead seeds and reassigns their ownership.
    # It is possible to get islands of dead seeds that are in the "wrong"
    # sector (i.e. they are entirely surrounded by walls, or seeds from a 
    # different sector). This breaks our wallwalking algorithm in 
    # treenode.fixAccessibility(), so find these islands and fix them.
    # "Islands" are regions of seeds that are below a minimum cutoff size.
    def fixSeedOwnership(self, blocks, seeds, shouldReassignSpaces = 1):
        chunks = []
        seenSpaces = dict()

        numCols = len(blocks)
        numRows = len(blocks[0])
        
        for i in range(0, numCols):
            for j in range(0, numRows):
                key = (i, j)
                if (blocks[i][j] == 0 and 
                        key not in seenSpaces and 
                        key in seeds):
                    type = seeds[key].node # Local sector type.
                    newChunk = []
                    fillStack = [key]
                    seenSpaces[key] = newChunk
                    while fillStack:
                        loc = fillStack.pop(0)
                        newChunk.append(loc)
                        for offset in constants.NEWSPerimeterOrder:
                            x = loc[0] + offset[0]
                            y = loc[1] + offset[1]
                            if (x < 0 or x >= numCols or 
                                    y < 0 or y >= numRows or
                                    blocks[x][y] != 0):
                                continue
                            if ((x, y) not in seenSpaces and 
                                    (x, y) in seeds and 
                                    seeds[(x, y)].node == type):
                                fillStack.append((x, y))
                                seenSpaces[(x, y)] = newChunk
                    chunks.append(newChunk)

        chunkStack = []
        chunkStack.extend(chunks)
        while chunkStack:
            chunk = chunkStack.pop(0)
            if len(chunk) < minimumSectorSize:
                altChunk = None
                for loc in chunk:
                    if altChunk is not None:
                        break
                    for offset in constants.NEWSPerimeterOrder:
                        x = loc[0] + offset[0]
                        y = loc[1] + offset[1]
                        if not self.getIsInBounds((x, y), numCols, numRows):
                            continue
                        if ((x, y) in seenSpaces and 
                                seenSpaces[(x, y)] != chunk):
                            altChunk = seenSpaces[(x, y)]
                if altChunk is not None:
                    newType = seeds[altChunk[0]].node
                    for loc in chunk:
                        key = (loc[0], loc[1])
                        seed = seeds[key]
                        if shouldReassignSpaces:
                            seed.node.unassignSpace(key)
                            newType.assignSpace(key)
                        seeds[key].node = newType
                        seenSpaces[key] = altChunk
                    altChunk.extend(chunk)
                    chunkStack.append(altChunk)
                else:
                    # Couldn't find a valid neighbor for this seed; it must be
                    # isolated by walls. Turn it into one.
                    for loc in chunk:
                        blocks[loc[0]][loc[1]] = 2
                        
        return (blocks, seeds)


    ## Call treenode.fixAccessibility() to create platforms to ensure map 
    # accessibility.
    def fixAccessibility(self):
        self.tree.fixAccessibility()


    ## Find the nearest wall to the given starting block along the 
    # normalized vector <dx, dy>.
    def getDistanceToWall(self, start, dx, dy):
        currentSpace = copy.deepcopy(start)
        distance = 0
        while (self.getIsInBounds(currentSpace) and
                (self.blocks[int(currentSpace[0])][int(currentSpace[1])] == 0 or
                 distance < 2)):
            currentSpace[0] += dx
            currentSpace[1] += dy
            distance = util.pointPointDistance(start, currentSpace)
        return util.pointPointDistance(start, currentSpace) * constants.blockSize


    ## Build platforms out from start along <dx, dy> until we get distance
    # away from start.
    def markPlatform(self, start, dx, dy, distance):
        totalDistance = 0
        while totalDistance < distance:
            buildDistance = minDistForPlatform + totalDistance
            buildX = int(start[0] + dx * buildDistance) + random.choice(platformHorizontalOffsets)
            buildY = int(start[1] + dy * buildDistance)
            buildLoc = [buildX, buildY]
            shouldBuild = 1
            for (loc, count) in self.platforms:
                # Check for platforms too close by.
                if (abs(loc[0] - buildLoc[0]) < minHorizDistToOtherPlatforms and 
                        abs(loc[1] - buildLoc[1]) < minVertDistToOtherPlatforms):
                    shouldBuild = 0
                    break
            if shouldBuild:
                self.addPlatform(buildLoc, random.choice(platformWidths))
            totalDistance += buildDistance


    ## Create a set of blocks for each location in self.platforms.
    def buildPlatforms(self):
        for (loc, width) in self.platforms:
            first = int(loc[0] - width / 2.0)
            last = int(loc[0] + width / 2.0) - 1
            for x in range(first, last + 1):
                if x < 0 or x >= self.numCols or self.blocks[x][loc[1]] == 1:
                    continue
                type = 'updown'
                if x == first:
                    type = 'leftend'
                elif x == last:
                    type = 'rightend'
                self.blocks[x][loc[1]] = type


    ## Draw an intermediary status image and saves it to disk. These are often 
    # very helpful for debugging purposes.
    # \param blocks The current blocks for the grid. Uses self.blocks if None.
    # \param seeds Active seeds used during map.expandSeeds().
    # \param deadSeeds Inactive seeds, used to mark sectors on the map.
    # \param marks List of other locations that should be specially marked.
    # In addition to the above, if map.markLoc is defined, then the map will
    # be focused on that location.
    def drawStatus(self, blocks = None, seeds = None, deadSeeds = None, marks = None):
        if blocks is None:
            blocks = self.blocks
        self.statusIter += 1
        util.debug("Drawing status number",self.statusIter,"with mark",self.markLoc)
#        if self.statusIter < 25:
#            return
        # Draw things a bit smaller...
        scale = drawStatusScaleFactor
        screen = pygame.Surface((self.width * scale, self.height * scale))
        size = constants.blockSize * scale

        if blocks is not None:
            numCols = len(blocks)
            numRows = len(blocks[0])
            for i in range(0, numCols):
                for j in range(0, numRows):
                    rect = pygame.rect.Rect((i * size, j * size), (size, size))
                    if blocks[i][j] in (1, None):
                        pygame.draw.rect(screen, (64, 64, 64), rect)
                    elif blocks[i][j] != 0:
                        pygame.draw.rect(screen, (255, 255, 255), rect)
#                        jetblade.imageManager.drawText(screen,
#                                ['%d, %d' % (i, j)], 
#                                (i * size, j * size + size / 2.0),
#                                0, constants.tinyFontSize,
#                                constants.TEXT_ALIGN_LEFT, (0, 0, 0, 255))

#        if self.regions is not None:
#            regionBlock = size / regionOverlayResolutionMultiplier
#            for (i, j), (zoneName, regionName) in self.regions.iteritems():
#                overlayRect = pygame.rect.Rect((i * regionBlock,
#                                                j * regionBlock),
#                                               (regionBlock-1, regionBlock-1))
#                color = self.zoneData[zoneName]['regions'][regionName]['color']
#                color = (color[0], color[1], color[2], 255)
#                pygame.draw.rect(screen, color, overlayRect)
        
        add = int(constants.blockSize / 2.0 * scale)
        if (deadSeeds is not None and len(deadSeeds) and 
                hasattr(deadSeeds[deadSeeds.keys()[0]].node, 'color')):
            for loc, seed in deadSeeds.iteritems():
                drawLoc = (loc[0]*size + add, loc[1]*size + add)
                pygame.draw.circle(screen, seed.node.color, drawLoc, add)

        if seeds is not None:
            for loc, seed in seeds.iteritems():
                drawLoc = (loc[0]*size + add, loc[1]*size + add)
                diff = 255 if seed.life <= 0 else int(255 / seed.life)
                pygame.draw.circle(screen, (0, diff, 255-diff), drawLoc, add)

        if marks is not None:
            for loc in marks:
                drawLoc = (loc[0]*size + add, loc[1]*size + add)
                pygame.draw.circle(screen, (255, 0, 0), drawLoc, add)

        if self.markLoc is not None:
            drawLoc = (self.markLoc[0]*size + add, self.markLoc[1]*size + add)
            pygame.draw.circle(screen, (0, 255, 255), drawLoc, add+4, 4)

            subRect = pygame.Rect((self.markLoc[0] * size - 400, 
                                   self.markLoc[1] * size - 400),
                                   (800, 800))
            subSurface = pygame.Surface((800, 800))
            subSurface.blit(screen, (0, 0), subRect)
            screen = subSurface

        if self.markLoc is None and self.tree is not None:
            self.tree.draw(screen, scale)

        pygame.image.save(screen, 'premap-%03d' % self.statusIter + '.png')
        jetblade.screen.fill((0, 0, 0))
        if self.markLoc is None:
            # Non-zoomed view, so scale it so it all fits.
            screen = pygame.transform.rotozoom(screen, 0, constants.sw / float(self.width * scale))
        jetblade.screen.blit(screen, (0, 0))
        pygame.display.update()
        util.debug("Status drawn")


    ## Draw a complete view of the map for purposes of looking pretty. Saves 
    # the result to disk under the provided filename.
    def drawAll(self, filename):
        scale = drawAllScaleFactor
        center = (self.width / 2.0 * scale, self.height / 2.0 * scale)
        size = constants.blockSize * scale
        
        screen = pygame.Surface((int(self.width * scale), int(self.height * scale)))
        
        self.backgroundQuadTree.draw(screen, center, 0, scale)
                
        for x in range(0, self.numCols):
            for y in range(0, self.numRows):
                for effect in self.envGrid[x][y]:
                    effect.draw(screen, util.gridspaceToRealspace((x, y)), center, 0, scale)

        for y in range(self.numRows - 1, 0, -1):
            # Draw from bottom to top because blocks may "hang" down a bit.
            for x in range(0, self.numCols):
                block = self.blocks[x][y]
                if block:
                    block.draw(screen, center, 0, scale)
                elif block is None:
                    rect = pygame.rect.Rect((x * size, y * size), (size, size))
                    pygame.draw.rect(screen, (64, 64, 64), rect)
        
        pygame.image.save(screen, filename)


    ## Draw the background props and any environmental effects at the given
    # location.
    def drawBackground(self, screen, cameraLoc, progress):
        self.backgroundQuadTree.draw(screen, cameraLoc, progress)
        if self.envGrid is not None:
            rect = screen.get_rect()
            rect.center = cameraLoc
            width = rect.width
            height = rect.height
            # \todo Remove the duplication between this and drawMidground
            minX = int((cameraLoc[0] - width / 2.0) / constants.blockSize) - 1
            minY = int((cameraLoc[1] - width / 2.0) / constants.blockSize) - 1
            maxX = int((cameraLoc[0] + height / 2.0) / constants.blockSize) + 3
            maxY = int((cameraLoc[1] + height / 2.0) / constants.blockSize) + 3
            for x in range(minX, maxX):
                if x < 0 or x > self.numCols:
                    continue
                for y in range(minY, maxY):
                    if y < 0 or y > self.numRows:
                        continue
                    for effect in self.envGrid[x][y]:
                        effect.draw(screen, util.gridspaceToRealspace((x, y)), 
                                    cameraLoc, progress)


    ## Draw the terrain tiles.
    def drawMidground(self, screen, cameraLoc, progress):
        rect = screen.get_rect()
        rect.center = cameraLoc
        width = rect.width
        height = rect.height
        minX = int((cameraLoc[0] - width / 2.0) / constants.blockSize) - 1
        minY = int((cameraLoc[1] - width / 2.0) / constants.blockSize) - 1
        maxX = int((cameraLoc[0] + height / 2.0) / constants.blockSize) + 3
        maxY = int((cameraLoc[1] + height / 2.0) / constants.blockSize) + 3
        for x in range(minX, maxX+1):
            if x < 0 or x > self.numCols:
                continue
            for y in range(minY, maxY+1):
                if y < 0 or y > self.numRows or not self.blocks[x][y]:
                    continue
                self.blocks[x][y].draw(screen, cameraLoc, progress)


    ## Determine if the given line is allowed to be added to our set. Invalid
    # lines come too close to other lines. This code ensures that we don't have
    # accidental crossings in the map.
    # \param safePoints List of points that are already known to connect to 
    # other lines in the tree. newLine is allowed to touch points in safePoints,
    # but otherwise is not allowed to come close to other lines.
    def getIsValidLine(self, newLine, safePoints):
        rect = newLine.getBounds()
        center = copy.deepcopy(rect.center)
        rect.width += 2 * treePruneDistance
        rect.height += 2 * treePruneDistance
        rect.center = center
        for altLine in self.treeLines.getObjectsIntersectingRect(rect):
            collisionResult = altLine.lineLineIntersect(newLine)
            # We only allow lines with shared endpoints if only one endpoint
            # is shared, and the lines are not coincident. Or, they may be 
            # coincident if
            # the point that isn't shared is far from the other line
            # (because this means the new line is a continuation of the old 
            # one)
            for p1 in [altLine.start, altLine.end]:
                for p2 in [newLine.start, newLine.end]:
                    if util.pointPointDistance(p1, p2) < constants.DELTA:
                        # altLine and newLine share a point. Check if it's
                        # a safe one.
                        isSafePoint = False
                        for p3 in safePoints:
                            if p1 == p3 or p2 == p3:
                                isSafePoint = True
                                break
                        if not isSafePoint:
                            return False
            if collisionResult in [line.LINE_INTERSECT, line.LINE_COINCIDENT]:
                # No crossing lines
                return False
            if (not util.fuzzyVectorMatch(newLine.end, safePoints) and 
                    util.pointLineDistance(newLine.end, altLine) < treePruneDistance):
                # Endpoint of new line can't be too close to other lines
                return False
            if (not util.fuzzyVectorMatch(altLine.end, safePoints) and 
                    util.pointLineDistance(altLine.end, newLine) < treePruneDistance): 
                # Endpoints of existing lines can't be too close to new line
                return False
        return True


    ## Add the given line to our set.
    def addLine(self, line):
        self.treeLines.addObject(line)


    ## See if the given circle hits any of our blocks or platforms. If it
    # does, return the (realspace) point of collision.
    def collideCircle(self, center, radius):
        centerx = int(center[0] / constants.blockSize)
        centery = int(center[1] / constants.blockSize)
        radiusSquared = (radius/float(constants.blockSize))**2
        for x in range(centerx - radius, centerx + radius):
            if x < 0 or x >= self.numCols:
                continue
            for y in range(centery - radius, centery + radius):
                if y < 0 or y >= self.numRows:
                    continue
                dist = (centerx - x)**2 + (centery - y)**2
                if dist < radiusSquared and self.blocks[x][y]:
                    return (x * constants.blockSize, y * constants.blockSize)
        for (platform, count) in self.platforms:
            if util.pointPointDistance(platform, center) < radius:
                return (platform[0] * constants.blockSize, platform[1] * constants.blockSize)
        return None


    ## Assign the given space to the given node, and unassign it from whoever
    # owned it before.
    def assignSpace(self, space, node):
        if space in self.deadSeeds:
            self.deadSeeds[space].node.unassignSpace(space)
        node.assignSpace(space)
        self.deadSeeds[space] = seed.Seed(node, 0, constants.BIGNUM)


    ## Mark a space as containing a platform. Don't do tile assignation until
    # later, as it might interfere with TreeNode.fixAccessibility() if done
    # now.
    def addPlatform(self, loc, size):
        loc = [int(loc[0]), int(loc[1])]
        util.debug("Adding a platform at",loc,"with size",size)
        if self.getIsInBounds(loc):
            self.platforms.append((loc, size))


    ## Add a background object (a prop) to the map.
    def addBackgroundObject(self, obj):
        self.backgroundQuadTree.addObject(obj)


    ## Mark the given tile as containing the selected environmental effect.
    def addEnvEffect(self, loc, effect):
        if loc[0] >= 0 and loc[0] < self.numCols and loc[1] >= 0 and loc[1] < self.numRows:
            self.envGrid[loc[0]][loc[1]].append(effect)


    def getStartLoc(self):
        return self.startLoc


    ## Collide the provided polygon against terrain tiles. Return the tile with
    # the largest ejection vector (as that is the tile that the polygon probably
    # hit first).
    def collidePolygon(self, poly, loc):
        upperLeft = util.realspaceToGridspace((poly.upperLeft[0] + loc[0], poly.upperLeft[1] + loc[1]))
        lowerRight = util.realspaceToGridspace((poly.lowerRight[0] + loc[0], poly.lowerRight[1] + loc[1]))
        longestOverlap = -constants.BIGNUM
        resultVector = None
        resultBlock = None
        upperLeft[0] -= 1
        upperLeft[1] -= 1
        lowerRight[0] += 2
        lowerRight[1] += 2
        for x in range(upperLeft[0], lowerRight[0]):
            if x < 0 or x >= self.numCols:
                continue
            for y in range(upperLeft[1], lowerRight[1]):
                if y < 0 or y >= self.numRows:
                    continue
                if self.blocks[x][y] not in (None, 0):
                    (overlap, vector) = self.blocks[x][y].collidePolygon(poly, loc)
                    if vector is not None:
                        if overlap > longestOverlap:
                            longestOverlap = overlap
                            resultVector = vector
                            resultBlock = self.blocks[x][y]
        if resultVector is not None:
            util.debug("Collision result is",(longestOverlap, resultVector, resultBlock.orientation),"against block at",resultBlock.gridLoc)
            util.debug("Polygon",poly,"at",loc,"hit polygon",resultBlock.sprite.getPolygon(),"at",resultBlock.loc)
            checkLoc = util.addVectors(resultBlock.gridLoc, resultVector)
            checkBlock = self.getBlockAtGridLoc(checkLoc)
            if checkBlock and checkBlock != resultBlock:
                util.debug("Ejection vector points into another block")
                # Objects that get sufficiently embedded in the walls can get 
                # inaccurate ejection vectors because the shortest path for one 
                # tile of the wall is right into another tile. Manually correct
                # the ejection vector if this happens.
                # \todo It'd be nice if we didn't have to do this.
                for offset in constants.NEWSPerimeterOrder:
                    checkLoc = util.addVectors(resultBlock.gridLoc, offset)
                    if not self.getBlockAtGridLoc(checkLoc):
                        util.debug("Converting ejection vector from",resultVector,"to",offset)
                        resultVector = offset
                        break
        return (longestOverlap, resultVector, resultBlock)


    ## Load map information from disk. The filename is equal to the name of the
    # map.
    # \todo This parser is very brittle, and while the map file format is not
    # meant to be directly user-editable, there's no reason we couldn't be 
    # more flexible here.
    def loadMap(self):
        fh = open(self.mapName, 'r')
        lineNum = 0
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
                self.blocks = []
                self.envGrid = []
                for i in range(0, self.numCols):
                    self.blocks.append([])
                    self.envGrid.append([])
                    for j in range(0, self.numRows):
                        self.blocks[i].append(0)
                        self.envGrid[i].append([])

                self.backgroundQuadTree = quadtree.QuadTree(pygame.rect.Rect((0, 0), (self.width, self.height)))
                
                mode = 'start'
            elif mode == 'start':
                if line == 'blocks:':
                    mode = 'blocks'
                    continue
                # Read starting location
                (x, y) = line.split(',')
                self.startLoc = [int(x), int(y)]
            elif mode == 'blocks':
                if line == 'enveffects:':
                    mode = 'enveffects'
                    continue
                (x, y, orientation, terrain, flavor) = line.split(',')
                x = int(x)
                y = int(y)
                flavor = flavor.rstrip()
                self.blocks[x][y] = orientation + ':' + terrain + ':' + flavor
            elif mode == 'enveffects':
                if line == 'bgprops:':
                    mode = 'bgprops'
                    continue
                (location, effects) = line.split(':')
                (x, y) = location.split(',')
                x = int(x)
                y = int(y)
                effects = effects.split(',')
                self.envGrid[x][y].extend([enveffect.EnvEffect(name) for name in effects])
            elif mode == 'bgprops':
                (x, y, terrain, flavor, group, item) = line.split(',')
                x = int(x)
                y = int(y)
                self.backgroundQuadTree.addObject(prop.Prop((x, y), terrain, flavor, group, item))
        for x in range(0, self.numCols):
            for y in range(0, self.numRows):
                if self.blocks[x][y]:
                    (orientation, terrain, flavor) = self.blocks[x][y].split(':')
                    self.blocks[x][y] = block.Block((x * constants.blockSize, 
                                                     y * constants.blockSize),
                                                orientation, None, 
                                                terrain, flavor)


    ## Write our map to disk so it can be read by loadMap().
    # \todo: Add support for enviroments to the map file.
    def writeMap(self, name):
        fh = open(name + '.map', 'w')
        fh.write("%d,%d\n" % (self.numCols, self.numRows))
        fh.write("%d,%d\n" % (self.startLoc[0], self.startLoc[1]))
        fh.write("blocks:\n")
        for x in range(0, self.numCols):
            for y in range(0, self.numRows):
                if self.blocks[x][y] not in (None, 0):
                    block = self.blocks[x][y]
                    fh.write("%d,%d,%s,%s,%s\n" % (x, y, block.orientation, block.terrain, block.flavor))
        fh.write("enveffects:\n")
        for x in range(0, self.numCols):
            for y in range(0, self.numRows):
                if self.envGrid[x][y]:
                    string = ",".join(effect.name for effect in self.envGrid[x][y])
                    fh.write("%d,%d:%s\n" % (x, y, string))
        
        fh.write("bgprops:\n")
        for prop in self.backgroundQuadTree.getObjects():
            fh.write("%d,%d,%s,%s,%s,%s\n" % 
                     (prop.loc[0], prop.loc[1], prop.terrain, 
                      prop.flavor, prop.group, prop.item))


    ## Simple boundary check for the blocks grid.
    def getIsInBounds(self, loc, numCols = -1, numRows = -1):
        if numCols == -1:
            numCols = self.numCols
        if numRows == -1:
            numRows = self.numRows
        return (loc[0] >= 0 and loc[0] < numCols and
                loc[1] >= 0 and loc[1] < numRows)


    ## Returns the region information at the given location. See makeRegions()
    # for more information on regions.
    def getTerrainInfoAtGridLoc(self, loc):
        regionLoc = (int(loc[0] * regionOverlayResolutionMultiplier), 
                     int(loc[1] * regionOverlayResolutionMultiplier))
        if regionLoc in self.regions:
            return self.regions[regionLoc]
        return (None, None)


    def getBlockAtGridLoc(self, loc):
        if not self.getIsInBounds(loc):
            return None
        return self.blocks[int(loc[0])][int(loc[1])]


    # Retrieve information from self.zoneData.
    def getRegionInfo(self, zone, region, field):
        if (zone in self.zoneData and 
                region in self.zoneData[zone]['regions'] and
                field in self.zoneData[zone]['regions'][region]):
            return self.zoneData[zone]['regions'][region][field]
        return None

