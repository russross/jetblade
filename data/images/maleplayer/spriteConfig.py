import math

def runUpdateFunc(obj):
    speed = obj.vel.magnitude()
    if speed < .25 * obj.maxVel.x:
        return 2/3.0
    elif speed < .5 * obj.maxVel.x:
        return 2/2.25
    elif speed < .75 * obj.maxVel.x:
        return 2/1.5
    else:
        return 2

def crawlUpdateFunc(obj):
    if obj.runDirection:
        return .5
    return 0

def crawlTurnUpdateFunc(obj):
    if obj.runDirection != obj.facing:
        return 1
    elif obj.runDirection:
        return -1
    return 0

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
        'drawOffset' : (-75, -75),
        'moveOffset' : (-50, -131),
    },
    'climb-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
        'drawOffset' : (-75, -75),
        'moveOffset' : (50, -131),
    },
    'run-l' : {
        'polygon' : standingPolygon,
        'updateFunc' : runUpdateFunc,
    },
    'run-r' : {
        'polygon' : standingPolygon,
        'updateFunc' : runUpdateFunc, 
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
        'updateFunc' : crawlUpdateFunc,
    },
    'crawl-r' : {
        'polygon' : crawlingPolygon,
        'updateFunc' : crawlUpdateFunc,
    },
    'crawlturn-l' : {
        'polygon' : crawlingPolygon,
        'loop' : False,
        'updateFunc' : crawlTurnUpdateFunc,
    },
    'crawlturn-r' : {
        'polygon' : crawlingPolygon,
        'loop' : False,
        'updateFunc' : crawlTurnUpdateFunc,
    },
    'kick1-l' : {
        'polygon' : standingPolygon,
        'loop' : False,
    },
    'kick1-r' : {
        'polygon' : standingPolygon,
        'loop' : False,
    },
}
