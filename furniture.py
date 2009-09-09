import sprite
import block
import logger

import os

## Furniture is a placed item on the map that the player can interact with
# (like terrain) but that is not placed on the block grid, generally because
# it's too big to fit into a single square. However, they are otherwise very
# similar; the major difference is that furniture doesn't have subtypes 
# encoded into the sprite animations.
class Furniture(block.Block):
    ## Instantiate a Furniture instance
    def __init__(self, loc, terrain, group, subGroup):
        ## Location in realspace
        self.loc = loc
        ## Approximate location in gridspace. 
        # \todo This is needed for some routines in TerrestrialObject because 
        # it assumes that all 'solid' collision types are with terrain blocks.
        self.gridLoc = self.loc.toRealspace()
        ## Terrain group that holds this Furniture instance's config and 
        # image files.
        self.terrain = terrain
        ## Group of furniture this belongs to within that terrain
        self.group = group
        ## Subtype of furniture this belongs to within the group
        self.subGroup = subGroup
        imagePath = os.path.join('terrain', self.terrain.zone, 
                self.terrain.region, 'furniture', self.group)
        ## Sprite for drawing and collision detection.
        self.sprite = sprite.Sprite(imagePath, self, self.loc)
        self.sprite.setAnimation(self.subGroup, False)
        ## Bounding rectangle.
        self.rect = self.sprite.getBounds(self.loc)


    ## Draw the furniture. Just a passthrough to Sprite.draw.
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, self.loc, scale)


    ## Convert to a string
    def __str__(self):
        return ("[Furniture at " + str(self.loc) + " terrain " + 
                str(self.terrain) + " group " + str(self.group) + 
                " subgroup " + str(self.subGroup) + "]")
