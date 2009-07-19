from vector2d import Vector2D

import math
import pygame
from pygame.locals import *

## @package constants This package contains a bunch of "constants" 
# (read: global variables that shouldn't be modified during execution) that 
# are used to configure the program in various ways.

## Name of the game, displayed as the title of the game window.
gameName = 'Jetblade RL'

## For debugging purposes, any class that needs to have a unique ID should use
# this object and increment it when they're done. So this is one that 
# actually *isn't* constant.
globalId = 0

## Screen width
sw = 900
## Screen height
sh = 650

## The size of a single block of terrain in the map
blockSize = 50


## "Small number" used largely for checking equality of floating point numbers.
EPSILON = .0001
## Slightly less-small number than EPSILON, used for checking Line coincidence
# in Map and Line modules.
DELTA = .1
## Large number to initialize minimum values to.
BIGNUM = 999988887777666655554444333322221111

## Path to the custom map generation modules
mapPath = 'data/mapgen'
## Path to image files and their configuration
imagePath = 'data/images'
## Path to soundeffects
soundPath = 'data/sound'
## Path to fonts
fontPath = 'data/fonts'
## Name of the module used to configure animation data
spriteFilename = 'spriteConfig'
## Name of the module used to configure fonts
fontFilename = 'fontConfig'

## Location to display the FPS string onscreen.
fpsDisplayLoc = Vector2D(sw - 20, sh - 20)

ACTION_QUIT = 'quit'

## In-game UI context, for UI elements and event handling.
CONTEXT_GAME = 1
## Main menu UI context, for UI elements and event handling.
CONTEXT_MENU = 2
