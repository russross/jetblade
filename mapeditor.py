import block
import constants
import game
import logger
import terraininfo
import scenery
import uielement
from vector2d import Vector2D

import pygame
import os

## Amount to adjust screen coordinates by to get to the block grid, since each
# terrain tile is offset from (0, 0) by a fixed amount (to allow terrain
# tiles to extend outside their physical bounding box).
# \todo Not certain how to fix this, but it's a hardcoded number that we
# shouldn't need.
blockOffset = -25

## Number of items to show per row in the display of tiles, scenery, etc. 
numItemsPerRow = 10

## This class allows you to edit the currently-loaded map.
class MapEditor:
    def __init__(self):
        ## Current terrain mode.
        self.terrain = terraininfo.TerrainInfo('jungle', 'grass')
        ## Current status message
        self.messageString = ''
        ## UIElements associated with the editor.
        self.UIElements = []
        ## A string describing the current edit mode. See setEditMode.
        self.editMode = 'blocks'
        ## List of objects for placement (instances of Blocks or 
        # Scenerys, as appropriate). 
        self.objects = []
        ## Index into self.objects of current object to place
        self.currentObjectIndex = 0
        ## Current block variant to display (see Block.subType)
        self.blockSubtype = 0
        ## Whether or not to enable map editing
        self.isActive = False
        ## Whether or not the editor controls are displayed when the editor is
        # active.
        self.areControlsDisplayed = True
        ## Whether or not the map grid is displayed when the editor is active.
        self.isMapGridDisplayed = True
        ## Any UIElements that we need to draw.
        self.drawnUIElements = []
        ## These UI elements don't change over time, so we can precalculate them
        self.fixedUIElements = None

    def init(self):
        self.fixedUIElements = [
            uielement.ButtonUIElement(
                    Vector2D((tileSize + 10) * 12 + 30, 30),
                    lambda: self.incrementSubtype(-1),
                    os.path.join('mapeditor', 'arrows'), 'up'),
            uielement.ButtonUIElement(
                    Vector2D((tileSize + 10) * 12 + 30, 110),
                    lambda: self.incrementSubtype(1), 
                    os.path.join('mapeditor', 'arrows'), 'down'),
            # Mouse wheel scrolls up
            uielement.SimpleUIElement('mouseDown', 
                    lambda loc, button: button == 4,
                    lambda: self.incrementSubtype(-1)),
            # Mouse wheel scrolls down
            uielement.SimpleUIElement('mouseDown', 
                    lambda loc, button: button == 5,
                    lambda: self.incrementSubtype(-1)),
        ]
        self.getBlockTypes()


    ## Given a list of objects, create the UI elements needed to make a grid
    # of those objects to choose from.
    def createChooserGrid(self):
        self.UIElements = []
        offset = Vector2D(20, 20)
        delta = tileSize + 20
        lowerRight = Vector2D(20, 20)
        count = 0
        for object in self.objects:
            self.UIElements.append(
                    EditorChooserUIElement(self, object, count, offset)
            )
            offset = offset.add(Vector2D(delta, 0))
            lowerRight = lowerRight.setX(max(lowerRight.x, offset.x))
            count += 1
            if count % numItemsPerRow == 0:
                offset = Vector2D(20, offset.y + delta)
        bottomY = 20 + min(3, count / 20 + 2) * delta
        # Extend the rect out to include the up/down arrows.
        self.chooserRect = pygame.rect.Rect(20, 20, 
                20 + (numItemsPerRow + 1) * delta, bottomY)
        self.UIElements.append(MapPickerUIElement(self, self.chooserRect))
        self.UIElements.extend(self.fixedUIElements)
        

    ## Retrieve the available block types for the current terrain type.
    def getBlockTypes(self):
        path = os.path.join(constants.spritePath, 'terrain',self.terrain.zone, 
                            self.terrain.region, 'blocks')
        blockNames = os.listdir(path)
        self.objects = []
        for blockName in blockNames:
            self.objects.append(block.Block(Vector2D(0, 0), self.terrain, 
                                            blockName, self.blockSubtype)) 
        self.createChooserGrid()
        self.currentObjectIndex = 0
        self.message("Loaded blocks for " + str(self.terrain))


    ## Retrieve the available scenery items for the current terrain.
    def getSceneryTypes(self):
        path = os.path.join(constants.spritePath, 'terrain',self.terrain.zone, 
                            self.terrain.region, 'scenery', 'sceneryConfig')
        module = game.dynamicClassManager.loadModuleItems(path, 'scenery')
        sceneryConfig = module.scenery
        self.objects = []
        for nameInfo, data in sceneryConfig.iteritems():
            if nameInfo[0] is None or nameInfo[1] is None:
                continue
            self.objects.append(scenery.Scenery(Vector2D(0, 0), self.terrain, 
                                                nameInfo[0], nameInfo[1])
            )
        self.createChooserGrid()
        self.currentObjectIndex = 0
        self.message("Loaded scenery for " + str(self.terrain))


    ## Change the current mode (i.e. what we're editing). 
    # @param mode String describing the new edit mode. Possible values:
    #  - 'blocks': Modify map terrain tiles
    #  - 'scenery': Modify background scenery objects
    def setEditMode(self, mode):
        if mode == 'blocks':
            self.getBlockTypes()
        elif mode == 'scenery': 
            self.getSceneryTypes()
        self.editMode = mode


    ## Check for inputs from the user.
    def update(self):
        if not self.isActive:
            return
        game.eventManager.processCurrentEvents(self.UIElements, constants.CONTEXT_GAME)


    ## Draw the available block set, the map grid, and our current message
    def draw(self, screen, cameraLoc, *args):
        if not self.isActive:
            return
        if self.isMapGridDisplayed:
            # Display a grid of lines every blockSize pixels across the map.
            xOffset = constants.blockSize - (cameraLoc.x % constants.blockSize) + blockOffset
            for i in xrange(0, constants.sw, constants.blockSize):
                pygame.draw.line(
                        screen, (255, 255, 255),
                        (i + xOffset, 0), (i + xOffset, constants.sh))
            yOffset = constants.blockSize - (cameraLoc.y % constants.blockSize)
            for j in xrange(0, constants.sh, constants.blockSize):
                pygame.draw.line(
                        screen, (255, 255, 255),
                        (0, j + yOffset), (constants.sw, j + yOffset))
                    
        if self.areControlsDisplayed:
            pygame.draw.rect(screen, (0, 0, 0), self.chooserRect)
            pygame.draw.rect(screen, (255, 255, 255), self.chooserRect, 3)
            fakeCameraLoc = Vector2D(constants.sw / 2.0, constants.sh / 2.0)
            for element in self.UIElements:
                element.draw(screen)
            game.fontManager.drawText('MODENINE', game.screen, 
                                      [self.messageString], 
                                      Vector2D(20, constants.sh - 20), 18)


    ## Set a new object type for placement
    def setObjectType(self, objectIndex):
        self.currentObjectIndex = objectIndex
        self.message("Set object type to %d: %s" % 
                     (objectIndex, self.objects[objectIndex]))
        

    ## Turn the editor on and off.
    def toggleActive(self):
        self.isActive = not self.isActive
        if self.isActive:
            # Display help.
            return """
Click on the map to place blocks. Right-click to delete blocks instead.
Click on the blocks at the top of the screen to switch which block you are
placing. Or use the number keys in conjunction with the left-side modifier keys:
second row: shift, third row: control, fourth row: alt/option, 
fifth row: shift + control, sixth row: shift + alt/option, 
seventh row: control + alt.
Click the arrows (or use the mouse wheel) to change the block subtypes.
Use the console command setTerrain to change terrain types: specify
the terrain group (e.g. jungle, hotzone) and the region (e.g. grass, lava).
Use the console command editorControls to hide/show the block picker."""


    ## Toggle display of the map grid
    def toggleGridDisplay(self):
        self.isMapGridDisplayed = not self.isMapGridDisplayed


    ## Toggle display of the editor controls
    def toggleControlDisplay(self):
        self.areControlsDisplayed = not self.areControlsDisplayed


    ## Set the current terrain type
    def setTerrain(self, zone, region):
        newTerrain = terraininfo.TerrainInfo(zone, region)
        if newTerrain.getIsValid():
            self.terrain = newTerrain
            if self.editMode == 'blocks':
                self.getBlockTypes()
            elif self.editMode == 'scenery':
                self.getSceneryTypes()
        else:
            return "Invalid terrain type " + zone + ", " + region


    ## Change the current block subtype if we're in block mode.
    def incrementSubtype(self, amount):
        if self.editMode == 'blocks':
            self.blockSubtype += amount
            curIndex = self.currentObjectIndex
            self.getBlockTypes()
            self.currentObjectIndex = curIndex
            self.message("Changed block subtype")


    ## Handle a click on the map: create or delete a map object, as appropriate.
    def clickedMapTile(self, gridLoc, shouldCreate):
        newObject = self.objects[self.currentObjectIndex].copy(gridLoc)
        if self.editMode == 'blocks':
            if shouldCreate:
                game.map.addBlock(newObject)
                self.message("Added a new block at " + str(gridLoc))
            elif game.map.deleteBlock(gridLoc):
                self.message("Deleted a block at " + str(gridLoc))
        elif self.editMode == 'scenery':
            if shouldCreate:
                game.map.addBackgroundObject(newObject)
                self.message("Added some scenery at " + str(gridLoc))
            elif game.map.removeBackgroundObject(gridLoc):
                self.message("Deleted scenery at " + str(gridLoc))


    ## Change our message.
    def message(self, text):
        self.messageString = text
        logger.debug(text)

## Size of an item in the picker, in pixels
tileSize = 50
## List of modifiers
modKeys = [pygame.K_LSHIFT, pygame.K_LCTRL, pygame.K_LALT]
## Different modifiers that can be used to trigger UI elements in
# combination with number keys.
modKeyCombos = [[pygame.K_LSHIFT], [pygame.K_LCTRL], [pygame.K_LALT],
           [pygame.K_LSHIFT, pygame.K_LCTRL], 
           [pygame.K_LSHIFT, pygame.K_LALT],
           [pygame.K_LCTRL, pygame.K_LALT]]
## This is a simple UI element for handling clicking on the selectables in
# the map editor.
class EditorChooserUIElement(uielement.UIElement):
    def __init__(self, editor, parentObject, index, position):
        ## Link to the map editor.
        self.editor = editor
        ## Object type that we select.
        self.parentObject = parentObject
        ## Position for drawing our stuff, except for parentObject
        self.position = position
        ## Bounding rect for mouse picking
        self.rect = pygame.Rect(
                position.x + tileSize / 2, position.y + tileSize / 2, 
                tileSize, tileSize)
        bounds = self.parentObject.getBounds()
        ## Scale for fitting our object into the rect.
        self.scale = float(tileSize) / bounds.w
        if bounds.h > bounds.w:
            self.scale = float(tileSize) / bounds.h
        # HACK: because scale factors also change the draw position, 
        # pre-emptively reverse-adjust it.
        # \todo Add support for scaling factors that don't change the draw
        # position (both ways are useful, mind; we need the current behavior
        # for scaling the entire world map down to size, for example).
        if abs(self.scale - 1) > constants.EPSILON:
            self.parentObject.moveTo(
                    position.add(
                            Vector2D(tileSize / 2, tileSize / 2)
                    ).divide(self.scale)
            )
        else:
            self.parentObject.moveTo(position)
        ## Number key that triggers us.
        self.keyTrigger = ord(str((index + 1) % 10))
        ## List of modifier keys that must be pressed to trigger us.
        self.modTriggers = []
        ## Place in the list of block UI elements
        self.index = index
        if self.index > 9:
            # We need a mod key to trigger this one.
            self.modTriggers = modKeyCombos[int((self.index - 1) / 10 - 1)]


    def draw(self, screen):
        fakeCameraLoc = Vector2D(constants.sw / 2.0, constants.sh / 2.0)
        self.parentObject.draw(screen, fakeCameraLoc, 
                progress = 0, scale = self.scale)
        game.fontManager.drawText('MODENINE', screen, 
                [str((self.index + 1) % 10)], 
                self.position.add(Vector2D(tileSize / 2.0 + 3, tileSize / 2.0 + 10)), 18)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)


    def mouseMove(self, mouseLoc):
        pass


    def mouseUp(self, mouseLoc, button):
        if self.rect.collidepoint(mouseLoc.tuple()):
            self.doAction()


    def processEvents(self, events):
        pressedKeys = pygame.key.get_pressed()
        for mod in self.modTriggers:
            if not pressedKeys[mod]:
                return
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == self.keyTrigger:
                    self.doAction()
    

    def doAction(self):
        self.editor.setObjectType(self.index)


## This UI element handles clicks on the map proper
class MapPickerUIElement(uielement.UIElement):
    def __init__(self, editor, rect):
        ## Any clicks within this box are ignored.
        self.rect = rect
        ## Link to the map editor instance
        self.editor = editor


    ## Passthrough to mouseMotion
    def mouseDown(self, mouseLoc, button):
        self.mouseMotion(mouseLoc)


    ## Track the mouse's position, and tell the editor what block was clicked
    # on.
    def mouseMotion(self, mouseLoc):
        pressedButtons = pygame.mouse.get_pressed()
        if (not self.rect.collidepoint(mouseLoc.tuple()) and 
                (pressedButtons[0] or pressedButtons[2])):
            # Clicked on the map; figure out where and set a block.
            topLeftCorner = game.camera.getLoc().add(
                    Vector2D(-constants.sw / 2.0, 
                             -constants.sh / 2.0))
            blockGridLoc = mouseLoc.add(topLeftCorner).addScalar(blockOffset).toGridspace()
            self.editor.clickedMapTile(blockGridLoc, 
                    shouldCreate = pressedButtons[0])


