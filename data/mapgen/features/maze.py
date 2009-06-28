import straight
import constants
import util
import random

## In mazes, vertical segments can be at most this many blocks tall.
mazeMaximumColumnHeight = 6 
## Amount of open space to make at endpoints
mazeEndpointOpenSpace = 2 

def getClassName():
    return 'Maze'

class Maze(straight.StraightTunnel):

    def __init__(self, map, sector):
        self.madeMaze = False
        straight.StraightTunnel.__init__(self, map, sector)

    ## Use a growing tree algorithm:
    # http://www.astrolog.org/labyrnth/algrithm.htm
    # to create the maze.
    def createFeature(self):
        # Fill our area with a maze, putting an opening at either end.
        (startLoc, endLoc) = self.sector.getStartAndEndLoc()
        if startLoc is None or endLoc is None:
            print "Unable to make maze for",self.sector.id,"from",self.sector.loc,"to",self.sector.parent.loc
            return

        (minX, minY, maxX, maxY) = self.sector.getSectorBounds()

        # Get the root of the tree we're building
        (dx, dy) = util.getNormalizedVector(startLoc, endLoc)
        firstCell = [int(startLoc[0]), int(startLoc[1])]
        if firstCell[0] % 2:
            firstCell[0] += cmp(dx, 0) or 1
        if firstCell[1] % 2:
            firstCell[1] += cmp(dy, 0) or 1

        # Turn our region into rooms of size 1, so we can carve walls 
        # to make the maze. Cells where both x and y are even are open; the rest
        # are closed.
        changedBlocks = dict()
        for (x, y) in self.sector.spaces.keys():
            if x % 2 or y % 2:
                self.map.blocks[x][y] = 2
                changedBlocks[(x, y)] = 1

        # Run the growing tree algorithm
        cellStack = [firstCell]
        seenCells = dict()
        while cellStack:
            index = random.randint(0, len(cellStack)-1)
            cell = cellStack[index]

            # Check verticial clearance
            verticalClearance = 0
            for i in range(1, mazeMaximumColumnHeight):
                offY = cell[1] + i
                # This is a bit of a hack -- stop checking once we run
                # outside the self.sector. Assume that platforms will fix things once
                # we're out.
                # If we don't do this, then we can prematurely empty cellStack and
                # end up with blocked-off corridors.
                # \todo Find a better way to handle this.
                if (offY >= self.map.numRows or 
                        self.map.blocks[cell[0]][offY] != 0 or
                        (cell[0], offY) not in self.sector.spaces):
                    break
                verticalClearance += 1
            for i in range(1, mazeMaximumColumnHeight):
                offY = cell[1] - i
                if (offY < 0 or 
                        self.map.blocks[cell[0]][offY] != 0 or
                        (cell[0], offY) not in self.sector.spaces):
                    break
                verticalClearance += 1

            availableNeighbors = []
            for offset in constants.NEWSPerimeterOrder:
                # Check to see if adjacent cells are already marked
                x = cell[0] + offset[0] * 2
                y = cell[1] + offset[1] * 2
                if (x, y) in self.sector.spaces and (x, y) not in seenCells:
                    # Neighbors above/below must pass a maximum vertical
                    # tunnel height check.
                    if offset[1] == 0 or verticalClearance + 2 < mazeMaximumColumnHeight:
                        availableNeighbors.append((x, y))

            if not availableNeighbors:
                # Can't add more openings to this cell.
                cellStack.pop(index)
                continue

            # Pick a direction and carve a wall.
            neighbor = random.choice(availableNeighbors)
            seenCells[neighbor] = 1
            cellStack.append(neighbor)
            # Get the offset to reach the wall.
            dx = (neighbor[0] - cell[0]) / 2
            dy = (neighbor[1] - cell[1]) / 2
            self.map.blocks[cell[0] + dx][cell[1] + dy] = 0

        # Step five: because of our limit on vertical expansion, it's possible to 
        # get incomplete mazes. Check for blocks that aren't in seenCells that
        # should be; if we find any, revert the maze.
        shouldRevert = 0
        for loc in self.sector.spaces:
            if loc not in seenCells:
                shouldRevert = 1
                break
        if shouldRevert:
            for block in changedBlocks:
                self.map.blocks[block[0]][block[1]] = 0

        else:
            # Step six: clear some space at the beginning and end of the maze.
            for loc in [startLoc, endLoc]:
                for x in range(int(loc[0] - mazeEndpointOpenSpace),
                               int(loc[0] + mazeEndpointOpenSpace)):
                    if x < 0 or x >= self.map.numCols:
                        continue
                    for y in range(int(loc[1] - mazeEndpointOpenSpace),
                                   int(loc[1] + mazeEndpointOpenSpace)):
                        if y < 0 or y >= self.map.numRows:
                            continue
                        if (x, y) in self.sector.spaces:
                            self.map.blocks[x][y] = 0
                self.map.addPlatform(loc, mazeEndpointOpenSpace)
            self.madeMaze = True
        
    ## Only if we failed to make the maze, in which case this is a standard
    # straight tunnel.
    def shouldCheckAccessibility(self):
        return not self.madeMaze

