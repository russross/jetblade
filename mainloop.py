#!/usr/local/bin/python2.5

import game
import font
import map
import player
import camera
import constants
import logger
from vector2d import Vector2D

import sys
import random
import pygame
import cProfile
import time
import optparse
from pygame.locals import *

## Location to display the FPS string onscreen.
fpsDisplayLoc = Vector2D(constants.sw - 20, constants.sh - 40)

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

## Number of physics updates to try to make each second. Tweaking this directly
# determines the speed of gameplay, to the limits of the computer's hardware.
physicsUpdatesPerSecond = 30


## Create the map(s) and player. If we've been told to make multiple maps
# or to save the map, then exit once we're done.
def startGame():
    game.map = None
    if game.mapFilename:
        game.map = map.Map(game.mapFilename)
        game.map.init()
        if game.shouldSaveImage:
            game.map.drawAll('%d.png' % game.seed)
        if game.shouldExitAfterMapgen:
            sys.exit()
    else:
        for i in xrange(0, game.numMaps):
            game.envEffectManager.reset()
            game.propManager.reset()
            logger.inform("Making map %d of %d" % (i + 1, game.numMaps))
            if game.numMaps == 1:
                logger.inform("Using seed",game.seed)
                random.seed(str(game.seed))
            else:
                game.seed = int(time.time())
                logger.inform("Using seed",game.seed)
                random.seed(str(game.seed))
            game.map = map.Map()
            game.map.init()
            if game.shouldSaveImage:
                game.map.drawAll(str(game.seed) + '.png')
        if game.shouldExitAfterMapgen:
            sys.exit()
    game.gameObjectManager.setup()
    game.player = player.Player()
    game.gameObjectManager.addObject(game.player)
    game.gameObjectManager.addNewObject('creatures/darkclone',
            game.player.loc.add(Vector2D(300, 0)))


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
    game.frameNum = 0
    physicsNum = 0
    framesSincePrevSec = 0
    game.curFPS = 0

    cam = camera.Camera()
    zoomLevel = 1

    while 1:
#        if pygame.time.get_ticks() > 10000:
#            logger.inform("Finished",game.frameNum, 
#                          "frames for an average framerate of",
#                          game.frameNum*1000/pygame.time.get_ticks())
#            sys.exit()
        logger.debug("Frame %d Physics %d Time %d" % (game.frameNum, physicsNum, pygame.time.get_ticks()))
        events = game.eventManager.processEvents([], constants.CONTEXT_GAME)
        # Check for a couple of events.
        for event in events:
            if event.type in (KEYDOWN, KEYUP):
                if event.action == 'startRecording' and event.type == KEYUP:
                    game.isRecording = not game.isRecording
                elif event.action == 'toggleDebug' and event.type == KEYUP:
                    if logger.getLogLevel() != logger.LOG_DEBUG:
                        logger.setLogLevel(logger.LOG_DEBUG)
                    else:
                        logger.setLogLevel(logger.LOG_INFORM)

        newTs = pygame.time.get_ticks()
        dt = newTs - curTs
        curTs = newTs
        timeAccum += dt

        count = 0
        if timeAccum > physicsUpdateRate:
            # Only do at most one physics update between drawings, even if more
            # time has passed.
            count += 1
            physicsNum += 1
            game.gameObjectManager.update()
            cam.update()
            timeAccum -= int(timeAccum / physicsUpdateRate) * physicsUpdateRate

        logger.debug("Did",count,"physics updates, have",timeAccum,"in the accumulator towards next physics update (step",physicsUpdateRate,")")

        draw(zoomLevel, cam, timeAccum / physicsUpdateRate)
 
        game.frameNum += 1
        framesSincePrevSec += 1
        
        if int(curTs / 1000) != curSec:
            game.curFPS = framesSincePrevSec
            logger.debug("FPS: ",framesSincePrevSec)
            curSec = int(curTs / 1000)
            framesSincePrevSec = 0


## Draw the game. 
def draw(zoomLevel, cam, progress):
    drawLoc = cam.getDrawLoc(progress)

    if zoomLevel != 1:
        drawSurface = pygame.Surface((constants.sw / zoomLevel, constants.sh / zoomLevel))
        game.map.draw(drawSurface, drawLoc, progress)
        drawSurface = pygame.transform.rotozoom(drawSurface, 0, zoomLevel)
        game.screen.blit(drawSurface, (0, 0))
    else:
        game.screen.fill((0, 0, 0))
        game.map.drawBackground(game.screen, drawLoc, progress)
        game.gameObjectManager.draw(game.screen, drawLoc, progress)
        game.map.drawMidground(game.screen, drawLoc, progress)
    if game.shouldDisplayFPS:
        game.fontManager.drawText('MODENINE', game.screen, 
            ["FPS: " + str(game.curFPS),
             'Frame: ' + str(game.frameNum)], fpsDisplayLoc, 18, 
            font.TEXT_ALIGN_RIGHT)
    pygame.display.update()

    if game.isRecording:
        pygame.image.save(game.screen, 'screenshot-%04d' % (game.frameNum) + '.png')