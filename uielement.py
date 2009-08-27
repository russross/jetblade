import sprite
from vector2d import Vector2D
import constants

## This class handles user interface objects that can interact with the
# EventManager that processes the event queue.
class UIElement:
    ## Instantiate
    def __init__(self):
        pass


    ## React to a key being pressed
    def keyDown(self, key):
        pass


    ## React to a key being released.
    def keyUp(self, key):
        pass


    ## React to the mouse moving
    def mouseMotion(self, mouseLoc):
        pass


    ## React to a mouse button being pressed.
    def mouseDown(self, mouseLoc, mouseButton):
        pass


    ## React to a mouse button being released.
    def mouseUp(self, mouseLoc, mouseButton):
        pass


    ## Examine the event queue and do what you need.
    def processEvents(self, events):
        pass


## This class is a simple UIElement that can be configured at instantiation to
# respond to a specific input event and take some action.
class SimpleUIElement(UIElement):
    def __init__(self, eventType, eventCondition, eventAction):
        ## String, indicating what type of action to react to: 
        # keyDown, keyUp, mouseMove, mouseDown, mouseUp, processEvents.
        self.eventType = eventType
        ## Function to execute to determine if action should be taken. Accepts
        # as input the appropriate argument for the event type reacted to, 
        # returns a boolean.
        self.eventCondition = eventCondition
        ## Function to execute as the action. Accepts no arguments.
        self.eventAction = eventAction


    def keyDown(self, key):
        if self.eventType == 'keyDown':
            self.act(key)


    def keyUp(self, key):
        if self.eventType == 'keyUp':
            self.act(key)


    def mouseMotion(self, mouseLoc):
        if self.eventType == 'mouseMove':
            self.act(mouseLoc, mouseButton)


    def mouseDown(self, mouseLoc, mouseButton):
        if self.eventType == 'mouseDown':
            self.act(mouseLoc, mouseButton)


    def mouseUp(self, mouseLoc, mouseButton):
        if self.eventType == 'mouseUp':
            self.act(mouseLoc, mouseButton)


    def processEvents(self, events):
        if self.eventType == 'processEvents':
            self.act(events)


    def act(self, *args):
        if self.eventCondition(*args):
            self.eventAction()


## This class represents an object that can be clicked on. It includes support
# for loading a sprite and drawing it onscreen.
class ButtonUIElement(UIElement):
    def __init__(self, spriteName, animationName, loc, action):
        ## Draw location on the screen
        self.loc = loc
        ## Action to perfom if clicked
        self.action = action
        ## Required to use sprites
        self.facing = 1
        ## Sprite for drawing and mouse picking.
        self.sprite = sprite.Sprite(spriteName, self)
        self.sprite.setAnimation(animationName, False)


    ## Draw the UI element, at a fixed location onscreen.
    def draw(self, screen):
        fakeCameraLoc = Vector2D(constants.sw / 2.0, constants.sh / 2.0)
        self.sprite.draw(screen, fakeCameraLoc, 0, self.loc)


    def mouseUp(self, mouseLoc, mouseButton):
        poly = self.sprite.getPolygon()
        if poly.containsPoint(self.loc, mouseLoc):
            self.action()
