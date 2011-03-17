import constants

import pygame

## A simple container class for platforms that we plan to add to the map during
# mapgen.
class FloatingPlatform:
    ## Instantiate a FloatingPlatform. 
    # The loc and width parameters are in gridspace units.
    # \param loc The location, in gridspace, of the platform
    # \param width The width, in blocks, of the platform.
    def __init__(self, loc, width):
        self.loc = loc
        self.width = width

    ## Return a bounding box for the platform. We use realspace units here 
    # because the quadtree we're storing these objects in works better with
    # larger numbers (it has a fixed minimum grid size).
    def getBounds(self):
        loc = self.loc.toRealspace()
        rect = pygame.Rect(loc.x, loc.y, self.width * constants.blockSize, constants.blockSize)
        return rect


    ## Convert to string
    def __str__(self):
        return "[FloatingPlatform at " + str(self.loc) + " with width " + str(self.width) + "]"

