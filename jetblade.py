#!/usr/local/bin/python2.5

import constants

import sys
import time
import pygame
import cProfile
import optparse

## @package jetblade This package contains the logic for setting up and running
# the program. It initializes PyGame, instantiates necessary global singletons,
# and starts the main game loop.
# By default, when started, Jetblade will generate a map, save the map 
# definition file to disk (using the map seed as the filename), and then 
# switch to gameplay mode. Run `jetblade.py -h` or `jetblade.py --help` to
# get a list of commandline options.

## Wrapper around the introductory logic; this is where we set our cProfile 
# hooks.
def run():
    options = getOptions()

    # Display a splash screen while we wait
    pygame.init()
    splashSurface = pygame.image.load(constants.otherPath + '/splashscreen.png')
    screen = pygame.display.set_mode((constants.sw, constants.sh))
    splashRect = splashSurface.get_rect()
    splashRect.topleft = (0, 0)
    screen.blit(splashSurface, splashRect)
    pygame.display.update()

    # Compile any Cython modules
    import pyximport; pyximport.install()
    import vector2d
    import polygon
    import range1d

    # Prepare game singletons
    import game
    game.screen = screen
    init(game, options)

    # Start gameplay
    import mainloop
    mainloop.startGame()
    mainloop.gameLoop()


## Obtain and validate commandline options.
# Do this prior to initializing pygame because that takes a noticeable amount
# of time, which is wasted if there is an error in the commandline arguments.
def getOptions():
    parser = optparse.OptionParser()
    parser.add_option('-s', '--seed', dest = 'seed', 
                      default = None,
                      help = "use SEED as PRNG seed for map generation",
                      metavar = 'SEED')
    parser.add_option('-f', '--mapfile', dest = 'mapFilename',
                      default = None,
                      help = "load FILE to play in", metavar = 'FILE')
    parser.add_option('-i', '--saveimage', action = 'store_true',
                      default = False,
                      dest = 'shouldSaveImage',
                      help = "save a PNG of the map after generating")
    parser.add_option('-j', '--justmapgen', action = 'store_true', 
                      default = False,
                      dest = 'shouldExitAfterMapgen',
                      help = "exit after generating maps (do not play the game)")
    parser.add_option('-n', '--num', default = 1, dest = 'numMaps',
                      type = 'int',
                      help = "Generate NUM maps", 
                      metavar = 'NUM')
    parser.add_option('-r', '--record', default = False, action = 'store_true',
                      dest = 'isRecording',
                      help = "Record every frame of gameplay to a PNG file")
    parser.add_option('-l', '--loglevel', default = None,
                      type = 'int',
                      dest = 'logLevel',
                      help = "Set the log level to LEVEL (5: debug; 1: fatal)")
    (options, args) = parser.parse_args(sys.argv)

    if options.numMaps > 1 and options.mapFilename is not None:
        print "Cannot use multiple-map generation with a sourced map file."
        sys.exit()
    elif options.numMaps > 1 and options.seed is not None:
        print "Cannot use multiple-map generation with a fixed random seed."
        sys.exit()
    elif options.seed is None:
        options.seed = int(time.time())
    
    if options.shouldExitAfterMapgen and options.mapFilename is not None:
        print "-justmapgen and -mapfile are incompatible"
        sys.exit()
    return options

## Set up the game according to the passed-in options
def init(game, options):
    game.seed = options.seed
    game.mapFilename = options.mapFilename
    game.shouldSaveImage = options.shouldSaveImage
    game.numMaps = options.numMaps
    game.shouldExitAfterMapgen = options.shouldExitAfterMapgen
    game.isRecording = options.isRecording
    if options.logLevel is not None:
        import logger
        logger.setLogLevel(options.logLevel)

    game.shouldDisplayFPS = 1
    pygame.display.set_caption('Jetblade')

if __name__ == '__main__':
#    run()
    cProfile.run('run()', 'profiling.txt')
