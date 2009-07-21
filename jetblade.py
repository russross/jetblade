#!/usr/local/bin/python2.5

import jetblade
import imagemanager
import configmanager
import dynamicclassmanager
import gameobjectmanager
import featuremanager
import enveffectmanager
import propmanager
import eventmanager
import animationmanager
import fontmanager
import soundmanager
import font
import map
import player
import camera
import constants
import util
import logger

import sys
import random
import os
import pygame
import cProfile
import time
import optparse
from pygame.locals import *

## \mainpage Jetblade
# This is the documentation for the Jetblade project. Jetblade is a 
# 2D platforming game in the style of the Metroid and Castlevania series, 
# with procedurally-generated maps. At the moment it is still deep in 
# development, and is thus not remotely playable. Jetblade is an open-source
# project, and your contributions are welcome!
#
# Jetblade is written in Python with PyGame. 
# 
# Broadly, the project
# can be broken down into the following categories:
# - Large-scale procedural map generation, the creation of a selection of 
# tunnels and their interconnections, the selection of different types of 
# regions, the ensuring of general accessibility, and the creation of specific
# roadblocks to add meaning to exploration. Important classes for this 
# category are the Map and TreeNode. 
# - Small-scale procedural map generation, the definition of what a region of 
# the map is like, and the creation of interesting features
# at the scale of an individual tunnel or %room. The TreeNode class is important
# for this, as are the various dynamically-loaded modules in the data/mapgen
# directory.
# - Platforming gameplay, the implementation of 2D physics in a run&jump 
# context, the addition of abilities to the player, and the creation of 
# new creatures for the player to encounter and possibly battle. Important
# classes for this category are the PhysicsObject, TerrestrialObject, 
# and Player class, at the moment. You may also want to examine the Blender
# model files.
#
# Additionally, for general information on running the program, see the 
# jetblade package documentation.

## @package jetblade This package contains the logic for setting up and running
# the program. It initializes PyGame, instantiates necessary global singletons,
# and runs the main game loop.
# By default, when started, Jetblade will generate a map, save the map 
# definition file to disk (using the map seed as the filename), and then 
# switch to gameplay mode. 
# Notable commandline options:
# - -debug: turn on debugging output (warning: verbose!)
# - -num X: generate X maps, and exit
# - -saveimage: save an image of the entire map after generating, then exit
# - -justmapgen: only generate a map; don't begin gameplay afterwards
# - -seed X: use X as a seed for map generation
# - -mapfile X: try to load X as a map definition file, and start gameplay mode
# - -record: record every rendered frame to disk. Note: this can be toggled
#    during gameplay as well.

## Number of physics updates to try to make each second. Tweaking this directly
# determines the speed of gameplay, to the limits of the computer's hardware.
physicsUpdatesPerSecond = 30
## Number of physics updates to try to make each second when we're recording
# images of the game to file.
slowPhysicsUpdatesPerSecond = 4

## Wrapper around the introductory logic; this is where we set our cProfile 
# hooks.
def run():
    init()
    while 1:
        startGame()
        gameLoop()


## Process commandline flags and set up singletons.
def init():
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
    parser.add_option('-l', '--loglevel', default = logger.LOG_INFORM,  
                      type = 'int',
                      dest = 'logLevel',
                      help = "Set the log level to LEVEL (5: debug; 1: fatal)")
    (options, args) = parser.parse_args(sys.argv)
    jetblade.seed = options.seed
    jetblade.mapFilename = options.mapFilename
    jetblade.shouldSaveImage = options.shouldSaveImage
    jetblade.numMaps = options.numMaps
    jetblade.shouldExitAfterMapgen = options.shouldExitAfterMapgen
    jetblade.isRecording = options.isRecording
    logger.setLogLevel(options.logLevel)

    if jetblade.numMaps > 1 and jetblade.mapFilename is not None:
        logger.error("Cannot use multiple-map generation with a sourced map file.")
        sys.exit()
    elif jetblade.numMaps > 1 and jetblade.seed is not None:
        logger.error("Cannot use multiple-map generation with a fixed random seed.")
        sys.exit()
    elif jetblade.seed is None:
        jetblade.seed = int(time.time())
    
    if jetblade.shouldExitAfterMapgen and jetblade.mapFilename is not None:
        logger.error("-justmapgen and -mapfile are incompatible")
        sys.exit()


    pygame.init()
    jetblade.shouldDisplayFPS = 1
    jetblade.configManager = configmanager.ConfigManager()
    jetblade.dynamicClassManager = dynamicclassmanager.DynamicClassManager()
    jetblade.featureManager = featuremanager.FeatureManager()
    jetblade.envEffectManager = enveffectmanager.EnvEffectManager()
    jetblade.propManager = propmanager.PropManager()
    jetblade.imageManager = imagemanager.ImageManager()
    jetblade.eventManager = eventmanager.EventManager()
    jetblade.animationManager = animationmanager.AnimationManager()
    jetblade.fontManager = fontmanager.FontManager()
    jetblade.soundManager = soundmanager.SoundManager()
    pygame.display.set_caption('Jetblade')
    jetblade.screen = util.setupScreen()



## Create the map(s) and player. If we've been told to make multiple maps
# or to save the map, then exit once we're done.
def startGame():
    jetblade.map = None
    if jetblade.mapFilename:
        jetblade.map = map.Map(jetblade.mapFilename)
        jetblade.map.init()
        if jetblade.shouldSaveImage:
            jetblade.map.drawAll('%d.png' % jetblade.seed)
        if jetblade.shouldExitAfterMapgen:
            sys.exit()
    else:
        for i in range(0, jetblade.numMaps):
            jetblade.envEffectManager.reset()
            jetblade.propManager.reset()
            logger.inform("Making map %d of %d" % (i + 1, jetblade.numMaps))
            if jetblade.numMaps == 1:
                logger.inform("Using seed",jetblade.seed)
                random.seed(str(jetblade.seed))
            else:
                jetblade.seed = int(time.time())
                logger.inform("Using seed",jetblade.seed)
                random.seed(str(jetblade.seed))
            jetblade.map = map.Map()
            jetblade.map.init()
            if jetblade.shouldSaveImage:
                jetblade.map.drawAll(str(jetblade.seed) + '.png')
        if jetblade.shouldExitAfterMapgen:
            sys.exit()
    jetblade.player = player.Player()
    jetblade.gameObjectManager = gameobjectmanager.GameObjectManager()
    jetblade.gameObjectManager.addObject(jetblade.player)


## The main game loop. Performs a target of physicsUpdatesPerSecond
# updates to the physics/game logic per second, and otherwise draws as many
# frames as possible between update cycles.
# For debugging purposes, you can turn on and off debugging output, and save
# the displayed frames to files.
def gameLoop():

    curTs = pygame.time.get_ticks()
    timeAccum = 0
    physicsUpdateRate = 1000.0 / physicsUpdatesPerSecond
    curSec = int(curTs / 1000)
    jetblade.frameNum = 0
    physicsNum = 0
    framesSincePrevSec = 0
    jetblade.curFPS = 0

    cam = camera.Camera()
    zoomLevel = 1

    while 1:
        logger.debug("Frame %d Physics %d" % (jetblade.frameNum, physicsNum))
        events = jetblade.eventManager.processEvents([], constants.CONTEXT_GAME)
        # Check for a couple of events.
        for event in events:
            if event.type in (KEYDOWN, KEYUP):
                if event.action == 'startRecording' and event.type == KEYUP:
                    jetblade.isRecording = not jetblade.isRecording
                    if jetblade.isRecording:
                        # Recording images to disk takes so long that it 
                        # causes massive frameskip; tweak the target 
                        # physics update rate to compensate.
                        physicsUpdateRate = 1000.0 / slowPhysicsUpdatesPerSecond
                    else:
                        physicsUpdateRate = 1000.0 / physicsUpdatesPerSecond
                elif event.action == 'toggleDebug' and event.type == KEYUP:
                    if logger.getLogLevel != logger.LOG_DEBUG:
                        logger.setLogLevel(logger.LOG_DEBUG)
                    else:
                        logger.setLogLevel(logger.LOG_INFORM)

        newTs = pygame.time.get_ticks()
        dt = newTs - curTs
        curTs = newTs
        timeAccum += dt

        count = 0
        while timeAccum >= physicsUpdateRate:
            count += 1
            physicsNum += 1
            jetblade.gameObjectManager.update()
            cam.update()
            timeAccum -= physicsUpdateRate

        logger.debug("Did",count,"physics updates, have",timeAccum,"in the accumulator towards next physics update (step",physicsUpdateRate,")")

        jetblade.draw(zoomLevel, cam, timeAccum / physicsUpdateRate)
 
        jetblade.frameNum += 1
        framesSincePrevSec += 1
        
        if int(curTs / 1000) != curSec:
            jetblade.curFPS = framesSincePrevSec
            logger.debug("FPS: ",framesSincePrevSec)
            curSec = int(curTs / 1000)
            framesSincePrevSec = 0


## Draw the game. 
def draw(zoomLevel, cam, progress):
    drawLoc = cam.getDrawLoc(progress)

    if zoomLevel != 1:
        drawSurface = pygame.Surface((constants.sw / zoomLevel, constants.sh / zoomLevel))
        jetblade.map.draw(drawSurface, drawLoc, progress)
        drawSurface = pygame.transform.rotozoom(drawSurface, 0, zoomLevel)
        jetblade.screen.blit(drawSurface, (0, 0))
    else:
        jetblade.screen.fill((0, 0, 0))
        jetblade.map.drawBackground(jetblade.screen, drawLoc, progress)
        jetblade.gameObjectManager.draw(jetblade.screen, drawLoc, progress)
        jetblade.map.drawMidground(jetblade.screen, drawLoc, progress)
    if jetblade.shouldDisplayFPS:
        jetblade.fontManager.drawText('MODENINE', jetblade.screen, 
            ["FPS: " + str(jetblade.curFPS)], constants.fpsDisplayLoc, 24, 
            font.TEXT_ALIGN_RIGHT)
    pygame.display.update()

    if jetblade.isRecording:
        pygame.image.save(jetblade.screen, 'screenshot-%04d' % (jetblade.frameNum) + '.png')

if __name__ == '__main__':
#    run()
    cProfile.run('run()', 'profiling.txt')
