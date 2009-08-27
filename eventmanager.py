import constants
from vector2d import Vector2D

import game
import pygame
from pygame import *

## This class handles user input and other events.
class EventManager:
    def __init__(self):
        self.events = []

    ## Return a list of current input actions (generally, keys that are 
    # pressed).
    def getCurrentActions(self):
        result = []
        for action in game.configManager.getCurrentActions():
            result.append(Event(action, KEYDOWN))
        return result


    ## Get all actions from the event queue.
    def processNewEvents(self, UIElements, context):
        self.events = pygame.event.get()
        self.processEvents(self.events, UIElements, context)


    ## As getNewEvents, but works with the cached set of events so we don't
    # trample the event queue.
    def processCurrentEvents(self, UIElements, context):
        self.processEvents(self.events, UIElements, context)

    
    ## Consume input, and hand it off to UIElement instances.
    def processEvents(self, events, UIElements, context):
        for event in events:
            if event.type == KEYDOWN:
                for element in UIElements:
                    element.keyDown(event.key)
            elif event.type == KEYUP:
                for element in UIElements:
                    element.keyUp(event.key)
            elif event.type == MOUSEMOTION:
                mouseLoc = Vector2D(pygame.mouse.get_pos())
                for element in UIElements:
                    element.mouseMotion(mouseLoc)
            elif event.type == MOUSEBUTTONDOWN:
                mouseLoc = Vector2D(pygame.mouse.get_pos())
                for element in UIElements:
                    element.mouseDown(mouseLoc, event.button)
            elif event.type == MOUSEBUTTONUP:
                mouseLoc = Vector2D(pygame.mouse.get_pos())
                for element in UIElements:
                    element.mouseUp(mouseLoc, event.button)
        for element in UIElements:
            element.processEvents(events)


    ## Get our current events since the last time we checked the queue
    def getEvents(self):
        return self.events


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

