#!/usr/local/bin/python2.5

import game
import font
import map
import camera
import constants
import logger
import uielement
from vector2d import Vector2D

import pyconsole

import os
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
# \todo Introduce a cap on display updates per second. Normally Pygame will
# block display updates until vsync, but apparently this doesn't always work
# properly.
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
            game.sceneryManager.reset()
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
    game.player = game.gameObjectManager.addNewObject(
            os.path.join('creatures', 'player', 'player')
    )
#    game.gameObjectManager.addNewObject('creatures/darkclone/darkclone',
#            game.player.loc.add(Vector2D(300, 0)))
    game.mapEditor.init()
    consoleFunctions = {
        'saveMap' : game.map.writeMap,
        'edit' : game.mapEditor.toggleActive,
        'editCon' : game.mapEditor.toggleControlDisplay,
        'editGrid' : game.mapEditor.toggleGridDisplay,
        'editType' : game.mapEditor.setEditMode,
        'setTerrain' : game.mapEditor.setTerrain,
        'setLogLevel' : logger.setLogLevel,
    }
    game.console = pyconsole.Console(game.screen, 
            pygame.rect.Rect(0, 0, constants.sw, constants.sh),
            consoleFunctions)
    game.console.set_active(False)


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

    game.camera = camera.Camera()
    zoomLevel = 1

    def toggleIsRecording():
        game.isRecording = not game.isRecording
    toggleRecordAction = uielement.SimpleUIElement('keyUp',
            lambda key : game.configManager.getActionForKey(key, constants.CONTEXT_GAME) == 'startRecording',
            toggleIsRecording)
    toggleDebugAction = uielement.SimpleUIElement('keyUp',
            lambda key : game.configManager.getActionForKey(key, constants.CONTEXT_GAME) == 'toggleDebug',
            logger.toggleDebug)
    quitAction = uielement.SimpleUIElement('keyUp',
            lambda key : game.configManager.getActionForKey(key, constants.CONTEXT_GAME) == 'quit',
            lambda: sys.exit())
    UIElements = [toggleRecordAction, toggleDebugAction, quitAction]

    while 1:
#        if pygame.time.get_ticks() > 10000:
#            logger.inform("Finished",game.frameNum, 
#                          "frames for an average framerate of",
#                          game.frameNum*1000/pygame.time.get_ticks())
#            sys.exit()
        logger.debug("Frame %d Physics %d Time %d" % (game.frameNum, physicsNum, pygame.time.get_ticks()))
        # Don't pass UI elements along if the console is intercepting input.
        UIElementsToUse = []
        if not game.console.active:
            UIElementsToUse = UIElements
        game.eventManager.processNewEvents(UIElementsToUse, constants.CONTEXT_GAME)
        game.console.process_input(game.eventManager.getEvents())

        if not game.console.active:
            game.mapEditor.update()

            newTs = pygame.time.get_ticks()
            dt = newTs - curTs
            curTs = newTs
            timeAccum += dt

            if timeAccum > physicsUpdateRate:
                # Only do at most one physics update between drawings, even if more
                # time has passed.
                physicsNum += 1
                game.gameObjectManager.update()
                game.camera.update()
                timeAccum -= int(timeAccum / physicsUpdateRate) * physicsUpdateRate

        draw(zoomLevel, timeAccum / physicsUpdateRate)
 
        game.frameNum += 1
        framesSincePrevSec += 1
        
        if int(curTs / 1000) != curSec:
            game.curFPS = framesSincePrevSec
            logger.debug("FPS: ",framesSincePrevSec)
            curSec = int(curTs / 1000)
            framesSincePrevSec = 0


## Draw the game. 
def draw(zoomLevel, progress):
    drawLoc = game.camera.getDrawLoc(progress)

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
    game.mapEditor.draw(game.screen, drawLoc, progress)
    game.console.draw()
    pygame.display.update()

    if game.isRecording:
        pygame.image.save(game.screen, 'screenshot-%04d' % (game.frameNum) + '.png')
