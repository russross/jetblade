from vector2d import Vector2D

import math

## Run animation cycle rate depends on velocity.
def runUpdate(obj):
    speed = obj.vel.magnitude()
    if speed < .25 * obj.maxVel.x:
        return 2/3.0
    elif speed < .5 * obj.maxVel.x:
        return 2/2.25
    elif speed < .75 * obj.maxVel.x:
        return 2/1.5
    else:
        return 2


## Crawling either is on or off.
def crawlUpdate(obj):
    if obj.runDirection:
        return .5
    return 0


## Turn around
def crawlTurnUpdate(obj):
    if obj.runDirection != obj.facing:
        return 1
    elif obj.runDirection:
        return -1
    return 0


## Create an attack on the left
def kickLeft(obj, game):
    game.gameObjectManager.addNewObject('attacks/baseattack', 
                         [(55,30), (95,30), (95,145), (55,145)],
                          Vector2D(-40, 0), obj, 4, 10)


## Create an attack on the right
def kickRight(obj, game):
    game.gameObjectManager.addNewObject('attacks/baseattack', 
                         [(55,30), (95,30), (95,145), (55,145)],
                          Vector2D(40, 0), obj, 4, 10)
    

standingPolygon = [(55,10), (95,10), (95,145), (55,145)]
crawlingPolygon = [(35,95), (115,95), (115,145), (35,145)]

sprites = {
    'idle-l' : {
        'polygon' : standingPolygon,
        'updateRate' : .25,
    },
    'idle-r' : {
        'polygon' : standingPolygon,
        'updateRate' : .25,
    },
    'jump-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : .5,
    },
    'jump-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : .5,
    },
    'fall-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'fall-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'standjump-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : .5,
    },
    'standjump-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : .5,
    },
    'standfall-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'standfall-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'hang-l' : {
        'polygon' : standingPolygon,
        'drawOffset' : (0, 6),
        'updateRate' : .2,
    },
    'hang-r' : {
        'polygon' : standingPolygon,
        'drawOffset' : (0, 6),
        'updateRate' : .2,
    },
    'climb-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'drawOffset' : (-75, -65),
        'moveOffset' : (-50, -131),
    },
    'climb-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'drawOffset' : (-75, -65),
        'moveOffset' : (50, -131),
    },
    'run-l' : {
        'polygon' : standingPolygon,
        'updateFunc' : runUpdate
    },
    'run-r' : {
        'polygon' : standingPolygon,
        'updateFunc' : runUpdate 
    },
    'runstop-l' : {
        'polygon' : standingPolygon,
        'updateRate' : 1,
    },
    'runstop-r' : {
        'polygon' : standingPolygon,
        'updateRate' : 1,
    },
    'crawl-l' : {
        'polygon' : crawlingPolygon,
        'updateFunc' : crawlUpdate
    },
    'crawl-r' : {
        'polygon' : crawlingPolygon,
        'updateFunc' : crawlUpdate
    },
    'crawlturn-l' : {
        'polygon' : crawlingPolygon,
        'loop' : False,
        'updateFunc' : crawlTurnUpdate,
        'interruptible' : False,
    },
    'crawlturn-r' : {
        'polygon' : crawlingPolygon,
        'loop' : False,
        'updateFunc' : crawlTurnUpdate,
        'interruptible' : False,
    },
    'flinch-l' : {
        'polygon' : standingPolygon,
        'updateRate' : .1,
    },
    'flinch-r' : {
        'polygon' : standingPolygon,
        'updateRate' : .1,
    },
    'kick1-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'frameActions' : {
            10 : kickLeft,
        },
        'updateRate' : 1.5,
    },
    'kick1-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'frameActions' : {
            10 : kickRight,
        },
        'updateRate' : 1.5,
    },
}
