import terraininfo
import game
import constants
import block
import logger
import uielement
from vector2d import Vector2D

import pygame
import os

## This class allows you to edit the currently-loaded map.
class MapEditor:
    def __init__(self):
        ## Current terrain mode for new blocks.
        self.terrain = terraininfo.TerrainInfo('jungle', 'grass')
        ## Current status message
        self.message = ''
        ## UIElements associated with the editor.
        self.UIElements = []
        ## Current block type for placement
        self.blockType = ''
        ## Current block subtype
        self.blockSubtype = 0
        ## Whether or not to enable map editing
        self.isActive = False
        ## Whether or not the editor controls are displayed when the editor is
        # active.
        self.isDisplayed = True
        ## Any UIElements that we need to draw.
        self.drawnUIElements = []
        ## These UI elements don't change over time, so we can precalculate them
        self.fixedUIElements = None

    def init(self):
        self.fixedUIElements = [
            uielement.ButtonUIElement(
                    Vector2D((constants.blockSize + 10) * 12 + 30, 30),
                    lambda: self.incrementSubtype(-1),
                    os.path.join('mapeditor', 'arrows'), 'up'),
            uielement.ButtonUIElement(
                    Vector2D((constants.blockSize + 10) * 12 + 30, 110),
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


    ## Retrieve the available block types for the current terrain type.
    def getBlockTypes(self):
        path = os.path.join(constants.spritePath, 'terrain',self.terrain.zone, 
                            self.terrain.region, 'blocks')
        blockNames = os.listdir(path)
        self.UIElements = []
        offset = Vector2D(20, 20)
        lowerRight = Vector2D(20, 20)
        count = 0
        for blockName in blockNames:
            count += 1
            self.UIElements.append(BlockUIElement(self, 
                    block.Block(offset, self.terrain, blockName, 
                    self.blockSubtype),
                    count)
            )
            offset = offset.add(Vector2D(constants.blockSize + 20, 0))
            lowerRight = lowerRight.setX(max(lowerRight.x, offset.x))
            if count % 10 == 0:
                offset = Vector2D(20, offset.y + constants.blockSize + 20)
        lowerRight = lowerRight.setY(offset.y)
        self.blocksRect = pygame.rect.Rect(20, 20, 
                lowerRight.x, lowerRight.y)
        self.UIElements.append(MapUIElement(self, lowerRight.y))
        self.UIElements.extend(self.fixedUIElements)
        self.blockType = blockNames[0]
        self.message = "Loaded blocks for " + str(self.terrain)


    ## Check for inputs from the user.
    def update(self):
        if not self.isActive:
            return
        game.eventManager.processCurrentEvents(self.UIElements, constants.CONTEXT_GAME)


    ## Draw the available block set, and our current message
    def draw(self, screen, cameraLoc, *args):
        if not self.isActive or not self.isDisplayed:
            return
        pygame.draw.rect(screen, (0, 0, 0), self.blocksRect)
        pygame.draw.rect(screen, (255, 255, 255), self.blocksRect, 3)
        fakeCameraLoc = Vector2D(constants.sw / 2.0, constants.sh / 2.0)
        for element in self.UIElements:
            element.draw(screen)
        game.fontManager.drawText('MODENINE', game.screen, [self.message], 
                                  Vector2D(20, constants.sh - 20), 18)


    ## Set a new block type for placement
    def setBlockType(self, type):
        self.blockType = type
        self.message = "Set block type to " + type


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


    ## Toggle display of the editor controls
    def toggleDisplay(self):
        self.isDisplayed = not self.isDisplayed


    ## Set the current terrain type
    def setTerrain(self, zone, region):
        newTerrain = terraininfo.TerrainInfo(zone, region)
        if newTerrain.getIsValid():
            self.terrain = newTerrain
            self.getBlockTypes()
        else:
            return "Invalid terrain type " + zone + ", " + region


    ## Change the current block subtype
    def incrementSubtype(self, amount):
        self.blockSubtype += amount
        curType = self.blockType
        self.getBlockTypes()
        self.blockType = curType
        self.message = "Changed block subtype"

       
## List of modifiers
modKeys = [pygame.K_LSHIFT, pygame.K_LCTRL, pygame.K_LALT]
## Different modifiers that can be used to trigger UI elements in
# combination with number keys.
modKeyCombos = [[pygame.K_LSHIFT], [pygame.K_LCTRL], [pygame.K_LALT],
           [pygame.K_LSHIFT, pygame.K_LCTRL], 
           [pygame.K_LSHIFT, pygame.K_LALT],
           [pygame.K_LCTRL, pygame.K_LALT]]
## This is a simple UI element for handling clicking on the blocks in the map
# editor.
class BlockUIElement(uielement.UIElement):
    def __init__(self, editor, parentBlock, index):
        ## Link to the map editor.
        self.editor = editor
        ## Block type that we select.
        self.parentBlock = parentBlock
        ## Bounding rect for mouse picking
        self.rect = parentBlock.getBounds()
        ## Number key that triggers us.
        self.keyTrigger = ord(str(index % 10))
        ## List of modifier keys that must be pressed to trigger us.
        self.modTriggers = []
        ## Place in the list of block UI elements
        self.index = index
        if self.index > 10:
            # We need a mod key to trigger this one.
            self.modTriggers = modKeyCombos[int((self.index - 1) / 10 - 1)]


    def draw(self, screen):
        fakeCameraLoc = Vector2D(constants.sw / 2.0, constants.sh / 2.0)
        self.parentBlock.draw(screen, fakeCameraLoc, 0)
        game.fontManager.drawText('MODENINE', screen, 
                [str(self.index % 10)], 
                self.parentBlock.loc.addScalar(constants.blockSize / 2.0), 18)


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
        self.editor.setBlockType(self.parentBlock.orientation)

## Amount to adjust screen coordinates by to get to the block grid, since each
# terrain tile is offset from (0, 0) by a fixed amount.
# \todo Not certain how to fix this, but it's a hardcoded number that we
# shouldn't need.
blockOffset = -25
## This UI element handles creating and destroying blocks.
class MapUIElement(uielement.UIElement):
    def __init__(self, editor, topY):
        ## Bounding box for mouse picking
        self.rect = pygame.rect.Rect(0, topY, constants.sw, constants.sh - topY)
        ## Link to the map editor instance
        self.editor = editor


    ## Passthrough to mouseMotion
    def mouseDown(self, mouseLoc, button):
        self.mouseMotion(mouseLoc)


    ## Track the mouse's position, and either create or remove blocks from the
    # map.
    def mouseMotion(self, mouseLoc):
        pressedButtons = pygame.mouse.get_pressed()
        if (self.rect.collidepoint(mouseLoc.tuple()) and 
                (pressedButtons[0] or pressedButtons[2])):
            # Clicked on the map; figure out where and set a block.
            topLeftCorner = game.camera.getLoc().add(
                    Vector2D(-constants.sw / 2.0, 
                             -constants.sh / 2.0))
            blockGridLoc = mouseLoc.add(topLeftCorner).addScalar(blockOffset).toGridspace()
            if pressedButtons[0]:
                newBlock = block.Block(blockGridLoc.toRealspace(), 
                        self.editor.terrain, self.editor.blockType, 
                        self.editor.blockSubtype)
                game.map.addBlock(newBlock)
                self.editor.message = "Added a new block at " + str(newBlock.gridLoc)
            else:
                game.map.deleteBlock(blockGridLoc)
                self.editor.message = "Deleted a block at " + str(blockGridLoc)

