import jetblade
import constants

## Props are background objects that have no influence on gameplay aside from
# simply looking pretty. 
class Prop:
    def __init__(self, loc, terrain, flavor, group, item):
        self.id = constants.globalId
        constants.globalId += 1
        ## Location of the prop in realspace.
        self.loc = loc
        ## Terrain group for the prop, e.g. "jungle" or "hotzone"
        self.terrain = terrain
        ## Sub-group for the prop, e.g. "grass" or "lava"
        self.flavor = flavor
        ## Group of props, e.g. "trees"
        self.group = group
        ## Specific item in the group of props.
        self.item = item
        imagePath = 'terrain/' + self.terrain + '/' + self.flavor + '/props/' + self.group + '/' + self.item
        ## Image of the prop. 
        # \todo: convert these to sprites so that props can be animated.
        self.surface = jetblade.imageManager.loadSurface(imagePath)

    ## Draw the prop. This is called by the game's Map instance before any 
    # other objects are drawn. 
    def draw(self, screen, camera, scale = 1):
        drawLoc = (self.loc[0] * scale, self.loc[1] * scale)
        jetblade.imageManager.drawGameObjectAt(screen, self.surface, drawLoc, camera, scale)

    ## Return the bounding box for the prop. Required for props to be insertable
    # into QuadTree instances.
    def getBounds(self):
        rect = self.surface.get_rect()
        rect.topleft = self.loc
        return rect

