import math

def runUpdateFunc(obj):
    speed = math.sqrt(obj.vel[0]**2 + obj.vel[1]**2)
    if speed < .25 * obj.maxVel[0]:
        return 2/3.0
    elif speed < .5 * obj.maxVel[0]:
        return 2/2.25
    elif speed < .75 * obj.maxVel[0]:
        return 2/1.5
    else:
        return 2

def crawlUpdateFunc(obj):
    if obj.runDirection:
        return .75
    return 0

def crawlTurnUpdateFunc(obj):
    if obj.runDirection != obj.facing:
        return 1
    elif obj.runDirection:
        return -1
    return 0

sprites = {
    'idle-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateRate' : .25,
    },
    'idle-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateRate' : .25,
    },
    'jump-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : .5,
    },
    'jump-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : .5,
    },
    'fall-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'fall-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'standjump-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : .5,
    },
    'standjump-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : .5,
    },
    'standfall-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'standfall-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'updateRate' : 1/3.0,
    },
    'hang-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'drawOffset' : (0, 6),
        'updateRate' : .2,
    },
    'hang-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'drawOffset' : (0, 6),
        'updateRate' : .2,
    },
    'climb-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'drawOffset' : (-75, -75),
        'moveOffset' : (-50, -131),
    },
    'climb-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'loop' : False,
        'drawOffset' : (-75, -75),
        'moveOffset' : (50, -131),
    },
    'run-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateFunc' : runUpdateFunc,
    },
    'run-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateFunc' : runUpdateFunc, 
    },
    'runstop-l' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateRate' : 1,
    },
    'runstop-r' : {
        'polygon' : [(55,10), (95,10), (95,145), (55,145)],
        'updateRate' : 1,
    },
    'crouch-l' : {
        'polygon' : [(55,65), (95,65), (95,145), (55,145)],
        'updateRate' : .25,
    },
    'crouch-r' : {
        'polygon' : [(55,65), (95,65), (95,145), (55,145)],
        'updateRate' : .25,
    },
    'crawl-l' : {
        'polygon' : [(35,95), (115,95), (115,145), (35,145)],
        'updateFunc' : crawlUpdateFunc,
    },
    'crawl-r' : {
        'polygon' : [(35,95), (115,95), (115,145), (35,145)],
        'updateFunc' : crawlUpdateFunc,
    },
    'crawlturn-l' : {
        'polygon' : [(35,95), (115,95), (115,145), (35,145)],
        'loop' : False,
        'updateFunc' : crawlTurnUpdateFunc,
    },
    'crawlturn-r' : {
        'polygon' : [(35,95), (115,95), (115,145), (35,145)],
        'loop' : False,
        'updateFunc' : crawlTurnUpdateFunc,
    },
}
