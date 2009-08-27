import Blender
from Blender.Scene import Render

import os
import math

if not os.path.exists('/tmp/output'):
    os.mkdir('/tmp/output')

objects = Blender.Object.Get()
camera = Blender.Object.Get('Camera')
renderScene = Blender.Scene.GetCurrent()
renderScene.setCurrentCamera(camera)

renderScene.setLayers(camera.layers)
context = renderScene.getRenderingContext()

context.displayMode = 0

locationToNameMap = {
    (0, 0) : 'center',
    (-7, 7) : 'upleft',
    (0, 7) : 'up',
    (7, 7) : 'upright',
    (7, 0) : 'right',
    (7, -7) : 'downright',
    (0, -7) : 'down',
    (-7, -7) : 'downleft',
    (-7, 0) : 'left',
    (-14, 0) : 'leftright',
    (-14, 14) : 'upleftsquare',
    (0, 14) : 'updown',
    (14, 14) : 'uprightsquare',
    (14, 0) : 'allway',
    (14, -14) : 'downrightsquare',
    (-14, -14) : 'downleftsquare',
    (-21, 0) : 'leftend',
    (0, 21) : 'upend',
    (21, 0) : 'rightend',
    (0, -21) : 'downend'
}

for object in objects:
    shouldRender = True
    for layer in object.layers:
        if layer in camera.layers:
            shouldRender = False
            break
    if not shouldRender:
        continue
    prevLayer = object.Layer
    prevLoc = object.getLocation()
    object.Layer = camera.Layer
    objName = 'unknown'
    yzLoc = (prevLoc[1], prevLoc[2])
    minDist = 10000
    for loc, name in locationToNameMap.iteritems():
        dist = math.sqrt((loc[0] - yzLoc[0])**2 + (loc[1] - yzLoc[1])**2)
        if dist < minDist:
            objName = name
            minDist = dist
    object.setLocation([0, 0, 0])
    Blender.Redraw(-1)

    if not os.path.exists('/tmp/output/' + objName):
        os.mkdir('/tmp/output/' + objName)
    context.setRenderPath('/tmp/output/' + objName)
    context.render()
    object.Layer = prevLayer
    object.setLocation(prevLoc)
    context.saveRenderedImage('/' + str(object.layers[0]) + '.png')

