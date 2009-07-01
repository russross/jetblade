import util
import constants

import pygame

## A simple container class for platforms that we plan to add to the map during
# mapgen.
class Platform:
    ## Instantiate a Platform. 
    # The loc and width parameters are in gridspace units; convert them into
    # realspace units because the QuadTree class works better on larger units.
    # \param loc The location, in gridspace, of the platform
    # \param width The width, in blocks, of the platform.
    def __init__(self, loc, width):
        self.loc = loc
        self.width = width

    ## Return a bounding box for the platform.
    def getBounds(self):
        loc = util.gridspaceToRealspace(self.loc)
        rect = pygame.Rect(loc[0], loc[1], self.width * constants.blockSize, constants.blockSize)
        return rect

