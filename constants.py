import os
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
## Default scaling factor
DEFAULT_ZOOM = 1

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
mapPath = os.path.join('data', 'mapgen')
## Path to custom game object modules
objectsPath = os.path.join('data', 'objects')
## Path to image files and their configuration
spritePath = os.path.join('data', 'sprites')
## Path to soundeffects
soundPath = os.path.join('data', 'sound')
## Path to fonts
fontPath = os.path.join('data', 'fonts')
## Path to miscellaneous resources
otherPath = os.path.join('data', 'other')
## Name of the module used to configure animation data
spriteFilename = 'spriteConfig'
## Name of the module used to configure fonts
fontFilename = 'fontConfig'

ACTION_QUIT = 'quit'

## In-game UI context, for UI elements and event handling.
CONTEXT_GAME = 1
## Main menu UI context, for UI elements and event handling.
CONTEXT_MENU = 2
