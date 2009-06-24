#!/usr/local/bin/python2.5
import math
import pygame
from pygame.locals import *

## @package constants This package contains a bunch of "constants" 
# (read: global variables) that are used to configure the program in various
# ways.

## Name of the game, displayed as the title of the game window.
gameName = 'Jetblade RL'

## For debugging purposes, any class that needs to have a unique ID should use
# this object. 
globalId = 0

## Screen width
sw = 900
## Screen height
sh = 650

## The size of a single block of terrain in the map
blockSize = 50
## Minimum width of the game world
minUniverseWidth = sw * 16
## Minimum height of the game world
minUniverseHeight = sh * 16
## Degree to which the game world dimensions are allowed to vary. The range thus
# defined is e.g. 
# [minUniverseWidth, minUniverseWidth + universeDimensionVariance] for width.
universeDimensionVariance = 0
## Amount to scale the map by when calling Map.drawStatus()
drawStatusScaleFactor = .2
## Amount to scale the map by when calling Map.DrawAll()
# Note that PyGame can't create surfaces bigger than about 16k pixels to a side
drawAllScaleFactor = .2

## Used by the 'room' tunnel type; minimum size of a room in blocks.
# This is the attempted size, not necessarily the actually achieved size. 
minRoomSize = blockSize * 20
## Degree to which the attempted size may vary 
# (between [minRoomSize, minRoomSize + roomSizeVariance])
roomSizeVariance = blockSize * 20
## Amount to thicken walls by in Map.expandWalls
wallThickness = 2

## Minimum physical distance between branches of the tree that describes the 
# general shape of the map.
treePruneDistance = 15 * blockSize

## Maximum distance from the root of the tree to a leaf node.
maxTreeDepth = 50
## Above this depth in the tree, we try harder to make as many children as 
# possible.
mustRetryDepth = 3
## Number of times to retry making children above mustRetryDepth
numRetriesNearRoot = 50
## Number of times to retry making children below mustRetryDepth
numRetriesFarFromRoot = 5

## Minimum size of a tree sector. Sectors smaller than this are absorbed into
# neighboring sectors.
minimumSectorSize = 10
## Minimum size of a section of connected walls. smaller islands are 
# converted to open space.
minimumIslandSize = 20

# Platform placement parameters
## Distance from the wall/ceiling to build platforms.
minDistForPlatform = 4
## As minDistForPlatform, but only when building from a floor.
minDistForFloorPlatform = 4
## Minimum horizontal distance between platforms.
minHorizDistToOtherPlatforms = 6
## Minimum vertical distance between platforms.
minVertDistToOtherPlatforms = 4
## Platforms have widths randomly selected from this list.
platformWidths = [1, 2, 2, 3]
## Platforms are randomly pushed to the left/right by choosing from this list.
platformHorizontalOffsets = [-1, 0, 1]

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
## Number of physics updates to try to make each second. Tweaking this directly
# determines the speed of gameplay, to the limits of the computer's hardware.
physicsUpdatesPerSecond = 60

## "Small number" used largely for checking equality of floating point numbers.
EPSILON = .0001
## Slightly less-small number than EPSILON, used for checking Line coincidence
# in Map and Line modules.
DELTA = .1
## Large number to initialize minimum values to.
BIGNUM = 999988887777666655554444333322221111

## Time in milliseconds to wait after displaying a fatal error, 
# before exiting the program.
errorMessageDelayTime = 10000

## Default player controls if no configuration file is found.
defaultPlayerKeys = {
    'left': K_LEFT,
    'right': K_RIGHT,
    'climb': K_UP,
    'jump': K_SPACE,
    'crouch': K_DOWN,
    'zoomin': K_PERIOD,
    'zoomout': K_COMMA,
    'startRecording': K_a,
    'toggleDebug': K_o,
    'quit': K_ESCAPE,
}

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
