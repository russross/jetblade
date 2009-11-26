import sprite

import os
import sys

## Environmental effects are localized changes in physics or display. For
# example, areas that are underwater, having falling rain, wind, etc. 
# Specific environmental effects are subclasses of the base class and should
# implement the following functions:
# - createRegion: Determines which parts of the map should have this 
#   effect running. 
# - enter, traverse, and exit: Are triggered when any game object enters, 
#   moves through, or exits the area of the effect. 
# - draw: Draw a single tile's worth of the effect. You can choose not to 
#   override this function, in which case a default behavior will be provided.
class EnvEffect:
    ## Instantiate a base environmental effect. You should never have cause to 
    # make one of these, but all subclasses need to remember to call this 
    # after setting themselves up.
    def __init__(self, name):
        self.sprite = sprite.Sprite(os.path.join('effects', 'environments', name), self)

        ## All spaces that have the effect.
        self.spaces = set()
        ## Name of the effect, which is the same as the module name for the 
        # effect's code (and not necessarily the same as the class in that 
        # module!). 
        self.name = name
        ## Dict of game objects currently in the effect.
        self.residentObjects = dict()
        ## Dict of game objects that we handled this frame.
        self.handledObjects = dict()


    ## Add a single grid location to our set of spaces, and add it to the map.
    def addSpace(self, loc, map):
        self.spaces.add(loc)
        map.addEnvEffect(loc, self)


    ## Determine which spaces are part of the environment, starting from the
    # provided sector of the map.
    def createRegion(self, map, sector):
        pass


    ## Draw a single space in the grid. This is the default draw behavior that
    # just does the effect's image; if you have anything else you want to draw
    # (e.g. particle effects) you should override this function. 
    def draw(self, screen, loc, camera, progress, scale = 1):
        self.sprite.draw(screen, camera, progress, loc, scale)


    ## Handle general updates. Specifically, find objects that have left our
    # region (by being in self.residentObjects but not in self.handledObjects).
    def update(self):
        self.sprite.update()
        remainingObjects = dict().update(self.residentObjects.keys())
        for object in self.handledObjects.keys():
            del remainingObjects[object]
        for object in remainingObjects.keys():
            self.exit(object.loc, object)
            del self.residentObjects[object]

    ## The Map instance will call this function to handle objects that are 
    # intersecting with environmental effects. We then call enter(), exit(), 
    # or traverse() as appropriate from here.
    def handleObject(self, obj):
        if obj not in self.handledObjects:
            if obj in self.residentObjects:
                self.traverse(obj)
            else:
                self.enter(obj)
            self.handledObjects.append(obj)


    ## Called when an object enters the environment's area of effect.
    def enter(self, obj):
        pass


    ## Called when an object is already in the environment's area of effect.
    def traverse(self, obj):
        pass


    ## Called when an object exits the environment's area of effect.
    def exit(self, obj):
        pass

