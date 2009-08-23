
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
    # \todo Handle different mouse buttons. For now, use 
    # pygame.mouses.get_pressed().
    def mouseDown(self, mouseLoc):
        pass


    ## React to a mouse button being released.
    def mouseUp(self, mouseLoc):
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


    def mouseMove(self, mouseLoc):
        if self.eventType == 'mouseMove':
            self.act(mouseLoc)


    def mouseDown(self, mouseLoc):
        if self.eventType == 'mouseDown':
            self.act(mouseLoc)


    def mouseUp(self, mouseLoc):
        if self.eventType == 'mouseUp':
            self.act(mouseLoc)


    def processEvents(self, events):
        if self.eventType == 'processEvents':
            self.act(events)


    def act(self, *args):
        if self.eventCondition(*args):
            self.eventAction()
