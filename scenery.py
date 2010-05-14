import game
import sprite
import logger

import os

## Scenery are background objects that have no influence on gameplay aside from
# simply looking pretty. Each one is attached to a specific block in the map.
class Scenery:
    def __init__(self, gridLoc, terrain, group, item):
        ## Tile we are attached to
        self.gridLoc = gridLoc    
        ## Offset from our top-left corner to the tile we're attached to.
        self.anchor = game.sceneryManager.getAnchorForScenery(terrain, group, item)
        ## Location in realspace.
        self.loc = self.gridLoc.toRealspace().add(self.anchor)
        ## TerrainInfo instance describing the local terrain
        self.terrain = terrain
        ## Group of items, e.g. "trees"
        self.group = group
        ## Specific item in the group of items.
        self.item = item
        imagePath = os.path.join('terrain', self.terrain.zone, 
                self.terrain.region, 'scenery', self.group)
        self.sprite = sprite.Sprite(imagePath, self, self.loc)
        self.sprite.setAnimation(self.item, False)


    ## Make an identical instance of us.
    def copy(self, gridLoc = None):
        if gridLoc is None:
            gridLoc = self.gridLoc
        return Scenery(gridLoc, self.terrain, self.group, self.item)


    ## Update our positional information. Generally only used by the map 
    # editor, which needs to show objects that aren't actually attached to 
    # terrain.
    def moveTo(self, newRealspaceLoc):
        self.loc = newRealspaceLoc


    ## Draw the piece of scenery. This is called by the game's Map instance 
    # before any other objects are drawn. 
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, self.loc, scale)


    ## Return the bounding box for the item. Required for items to be insertable
    # into QuadTree instances.
    def getBounds(self):
        return self.sprite.getBounds(self.loc)


    ## Convert to string
    def __str__(self):
        return "[Scenery (%s, %s) for terrain %s at %s]" % (
                self.group, self.item, str(self.terrain), str(self.loc))

