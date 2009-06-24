import jetblade

import pygame
from pygame import *

## This class handles user input and other events.
class EventManager:
    def __init__(self):
        pass

    ## Return a list of current input actions (generally, keys that are 
    # pressed).
    def getCurrentActions(self):
        result = []
        for action in jetblade.configManager.getCurrentActions():
            result.append(Event(action, KEYDOWN))
        return result

    
    ## Consume input, and return a list of Event instances.
    def processEvents(self, UIElements, context):
        actions = []
        for event in pygame.event.get():
            if event.type == QUIT:
                actions.append(Event(constants.ACTION_QUIT))
            elif event.type in (KEYDOWN, KEYUP):
                action = jetblade.configManager.getActionForKey(event.key, context)
                if action is not None:
                    actions.append(Event(action, event.type))
            elif event.type == MOUSEMOTION:
                mouseLoc = pygame.mouse.get_pos()
                for element in UIElements:
                    element.mouseMove(mouseLoc)
            elif event.type == MOUSEBUTTONUP:
                mouseLoc = pygame.mouse.get_pos()
                for element in UIElements:
                    if element.mouseUp(mouseLoc):
                        actions.append(element.getAction())
        return actions


## This class represents a single input event.
class Event:
    def __init__(self, action, type = None):
        ## The name of the action
        self.action = action
        ## The type of the action, e.g. pygame.MOUSEMOTION or pygame.KEYUP.
        self.type = type

    def getAction(self):
        return self.action

    def getType(self):
        return self.type

