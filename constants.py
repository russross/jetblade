#!/usr/local/bin/python2.5
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

## List of offsets in North, East, West, South directions. Used for iterating 
# over spaces adjacent to a given space in the map.
NEWSPerimeterOrder = [(0, -1), (1, 0), (-1, 0), (0, 1)]
## List of offsets in all 8 directions. Used for iterating over spaces adjacent
# to a given space in the map.
perimeterOrder = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

## Log level for debugging output
LOG_DEBUG = 5
## Log level for inform output
LOG_INFORM = 4
## Log level for warning output
LOG_WARN = 3
## Log level for error output
LOG_ERROR = 2
## Log level for fatal output
LOG_FATAL = 1
## Descriptor strings for the log levels
logStrings = {
    LOG_DEBUG : 'DEBUG',
    LOG_INFORM : 'INFO',
    LOG_WARN : 'WARNING',
    LOG_ERROR : 'ERROR',
    LOG_FATAL : 'FATAL',
}


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
sfxPath = 'data/sfx'
## Path to fonts
fontPath = 'data/fonts'
## Name of the module used to configure animation data
spriteFilename = 'spriteConfig.py'
## Fonts to load. 
# \todo Make this more modular (move it out to a font config module)
fontNames = ['MODENINE.TTF', 'ETHNOCEN.TTF']
## Distance between lines, as a multiplier on the size of the font.
textLineVerticalOffsetMultiplier = .85

## Set of font sizes to load. Only these sizes will be available in-game.
fontSizes = [6, 12, 18, 36, 54, 128]
miniFontSize = 6
tinyFontSize = 12
smallFontSize = 18
mediumFontSize = 36
largeFontSize = 54
hugeFontSize = 128
## Align text to the left, in ImageManager.drawText
TEXT_ALIGN_LEFT = 1
## Align text to the middle, in ImageManager.drawText
TEXT_ALIGN_CENTER = 2
## Align text to the right, in ImageManager.drawText
TEXT_ALIGN_RIGHT = 3

## Location to display the FPS string onscreen.
fpsDisplayLoc = [sw - 20, sh - 20]

ACTION_QUIT = 'quit'

## In-game UI context, for UI elements and event handling.
CONTEXT_GAME = 1
## Main menu UI context, for UI elements and event handling.
CONTEXT_MENU = 2
