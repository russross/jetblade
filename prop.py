import sprite
import logger

import os

## Props are background objects that have no influence on gameplay aside from
# simply looking pretty. 
class Prop:
    def __init__(self, loc, terrain, group, item):
        ## Location of the prop in realspace.
        self.loc = loc
        ## TerrainInfo instance describing the local terrain
        self.terrain = terrain
        ## Group of props, e.g. "trees"
        self.group = group
        ## Specific item in the group of props.
        self.item = item
        imagePath = os.path.join('terrain', self.terrain.zone, 
                self.terrain.region, 'props', self.group)
        self.sprite = sprite.Sprite(imagePath, self, self.loc)
        self.sprite.setAnimation(self.item, False)


    ## Draw the prop. This is called by the game's Map instance before any 
    # other objects are drawn. 
    def draw(self, screen, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, None, scale)


    ## Return the bounding box for the prop. Required for props to be insertable
    # into QuadTree instances.
    def getBounds(self):
        return self.sprite.getBounds(self.loc)

