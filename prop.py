import jetblade
import constants

## Props are background objects that have no influence on gameplay aside from
# simply looking pretty. 
class Prop:
    def __init__(self, loc, terrain, group, item):
        self.id = constants.globalId
        constants.globalId += 1
        ## Location of the prop in realspace.
        self.loc = loc
        ## TerrainInfo instance describing the local terrain
        self.terrain = terrain
        ## Group of props, e.g. "trees"
        self.group = group
        ## Specific item in the group of props.
        self.item = item
        imagePath = 'terrain/' + self.terrain.zone + '/' + self.terrain.region + '/props/' + self.group + '/' + self.item
        ## Image of the prop. 
        # \todo: convert these to sprites so that props can be animated.
        self.surface = jetblade.imageManager.loadSurface(imagePath)

    ## Draw the prop. This is called by the game's Map instance before any 
    # other objects are drawn. 
    def draw(self, screen, camera, scale = 1):
        drawLoc = self.loc.multiply(scale)
        jetblade.imageManager.drawGameObjectAt(screen, self.surface, drawLoc, camera, scale)

    ## Return the bounding box for the prop. Required for props to be insertable
    # into QuadTree instances.
    def getBounds(self):
        rect = self.surface.get_rect()
        rect.topleft = self.loc.tuple()
        return rect

