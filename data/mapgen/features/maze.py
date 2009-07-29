import straight
import constants
import logger
import map
import vector2d
from vector2d import Vector2D

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
            logger.debug("Unable to make maze for",self.sector.id,"from",self.sector.loc,"to",self.sector.parent.loc)
            return

        (minX, minY, maxX, maxY) = self.sector.getSectorBounds()

        # Get the root of the tree we're building
        delta = startLoc.sub(endLoc).normalize()
        firstCell = startLoc.int()
        if firstCell.x % 2:
            firstCell = firstCell.addX(cmp(delta.x, 0) or 1)
        if firstCell.y % 2:
            firstCell = firstCell.addY(cmp(delta.y, 0) or 1)

        # Turn our region into rooms of size 1, so we can carve walls 
        # to make the maze. Cells where both x and y are even are open; the rest
        # are closed.
        changedBlocks = set()
        for loc in self.sector.spaces:
            if loc.x % 2 or loc.y % 2:
                self.map.blocks[loc.ix][loc.iy] = map.BLOCK_WALL
                changedBlocks.add(loc)

        # Run the growing tree algorithm
        cellStack = [firstCell]
        seenCells = set()
        while cellStack:
            index = random.randint(0, len(cellStack)-1)
            cell = cellStack[index]

            # Check verticial clearance
            verticalClearance = 0
            for i in range(1, mazeMaximumColumnHeight):
                offY = cell.iy + i
                # This is a bit of a hack -- stop checking once we run
                # outside the self.sector. Assume that platforms will fix 
                # accessibility once we're out.
                # If we don't do this, then we can prematurely empty cellStack 
                # and end up with blocked-off corridors.
                # \todo Find a better way to handle this.
                if (offY >= self.map.numRows or 
                        self.map.blocks[cell.ix][offY] != map.BLOCK_EMPTY or
                        Vector2D(cell.x, offY) not in self.sector.spaces):
                    break
                verticalClearance += 1
            for i in range(1, mazeMaximumColumnHeight):
                offY = cell.iy - i
                if (offY < 0 or 
                        self.map.blocks[cell.ix][offY] != map.BLOCK_EMPTY or
                        Vector2D(cell.x, offY) not in self.sector.spaces):
                    break
                verticalClearance += 1

            availableNeighbors = []
            for offset in vector2d.NEWSPerimeterOrder:
                adjacentBlock = cell.add(offset.multiply(2))
                # Check to see if adjacent cells are already marked
                if adjacentBlock in self.sector.spaces and adjacentBlock not in seenCells:
                    # Neighbors above/below must pass a maximum vertical
                    # tunnel height check.
                    if offset.y == 0 or verticalClearance + 2 < mazeMaximumColumnHeight:
                        availableNeighbors.append(adjacentBlock)

            if not availableNeighbors:
                # Can't add more openings to this cell.
                cellStack.pop(index)
                continue

            # Pick a direction and carve a wall.
            neighbor = random.choice(availableNeighbors)
            seenCells.add(neighbor)
            cellStack.append(neighbor)
            # Get the offset to reach the wall.
            delta = neighbor.sub(cell).divide(2).int()
            self.map.blocks[delta.ix][delta.iy] = map.BLOCK_EMPTY

        # Step five: because of our limit on vertical expansion, it's possible 
        # to get incomplete mazes. Check for blocks that aren't in seenCells 
        # that should be; if we find any, revert the maze rather than have 
        # bits of it be blocked off.
        shouldRevert = False
        for loc in self.sector.spaces:
            if loc not in seenCells:
                shouldRevert = True
                break

        if shouldRevert:
            for block in changedBlocks:
                self.map.blocks[block.ix][block.iy] = map.BLOCK_EMPTY
        else:
            # Step six: clear some space at the beginning and end of the maze.
            for loc in [startLoc, endLoc]:
                for x in range(int(loc.x - mazeEndpointOpenSpace),
                               int(loc.x + mazeEndpointOpenSpace)):
                    if x < 0 or x >= self.map.numCols:
                        continue
                    for y in range(int(loc.y - mazeEndpointOpenSpace),
                                   int(loc.y + mazeEndpointOpenSpace)):
                        if y < 0 or y >= self.map.numRows:
                            continue
                        if Vector2D(x, y) in self.sector.spaces:
                            self.map.blocks[x][y] = map.BLOCK_EMPTY
                self.map.addPlatform(loc, mazeEndpointOpenSpace)
            self.madeMaze = True
        
    ## Only if we failed to make the maze, in which case this is a standard
    # straight tunnel.
    def shouldCheckAccessibility(self):
        return (not self.madeMaze and straight.StraightTunnel.shouldCheckAccessibility(self))

