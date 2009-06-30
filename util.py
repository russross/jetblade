import jetblade
import constants
import line

import math
import os
import pygame
from pygame.locals import *
import sys
import random

## @package util
# The functions in util are general utility functions that are not tied to any
# specific class.

## Time in milliseconds to wait after displaying a fatal error, 
# before exiting the program.
errorMessageDelayTime = 10000

## Log the provided text at the given log level
def log(level, *entries):
    if jetblade.logLevel >= level:
        string = ''
        for entry in entries:
            string += str(entry) + ' '
        print constants.logStrings[level] + ':',string
        return string
    return None


def debug(*entries):
    return log(constants.LOG_DEBUG, *entries)


def inform(*entries):
    return log(constants.LOG_INFORM, *entries)


def warn(*entries):
    return log(constants.LOG_WARN, *entries)


def error(*entries):
    return log(constants.LOG_ERROR, *entries)


## Print an error to the screen, wait a bit, then exit the program. Call this
# function when unrecoverable errors have occurred. 
def fatal(*entries):
    message = log(constants.LOG_FATAL, *entries)
    errorString = "Sorry, an error occurred: " + message
    errorString2 = "The program will now shut down."
    debug(errorString)
    debug(errorString2)
    errorFont = pygame.font.Font(None, 24)
    textSurface = errorFont.render(errorString, True, (255, 255, 255))
    textSurface2 = errorFont.render(errorString2, True, (255, 255, 255))
    rect = textSurface.get_rect()
    rect.centerx = constants.sw / 2.0
    rect.centery = constants.sh / 2.0
    rect2 = textSurface.get_rect()
    rect2.centerx = constants.sw / 2.0
    rect2.centery = constants.sh / 2.0 + 30
    jetblade.screen.fill((0, 0, 0))
    jetblade.screen.blit(textSurface, rect)
    jetblade.screen.blit(textSurface2, rect2)
    pygame.display.update()
    pygame.time.delay(errorMessageDelayTime)
    sys.exit()


## Retrieves the location of the user's home directory, depending on OS.
def getHomePath():
    if sys.platform in ['win32', 'cygwin']:
        return os.environ.get('APPDATA')
    else: # Assume OSX/Linux; both should work
        return os.environ.get('HOME')


## Retrieve the text from the clipboard, using different methods depending on
# OS.
def getClipboardText():
    if sys.platform in ['win32', 'cygwin']:
        import win32clipboard
        win32clipboard.OpenClipboard()
        text = ''
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
            text = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return text
    else:
        import subprocess
        p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
        retcode = p.wait()
        data = p.stdout.read()
        return data


## Create the display surface. 
def setupScreen():
    mode = 0
    if jetblade.configManager.getConfigValue('fullscreen'):
        mode = pygame.FULLSCREEN
    screen = pygame.display.set_mode((constants.sw, constants.sh), mode)
    if screen is None:
        # Give up on fullscreen mode
        screen = pygame.display.set_mode((constants.sw, constants.sh))
    return screen


def addVectors(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]


def subtractFromVector(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1]]

## Adjust the passed-in location so that it is relative to the upper-left
# corner of the passed-in rect.
def adjustLocForRect(loc, rect):
    result = (loc[0] - rect.topleft[0], loc[1] - rect.topleft[1])
    return result


## As adjustLocForRect, but move the rect so it is centered at the given
# location first.
def adjustLocForCenter(loc, center, rect):
    rect.centerx = center[0]
    rect.centery = center[1]
    return adjustLocForRect(loc, rect)


## Get an image from the list based on the provided index.
def getDrawFrame(index, surfaces):
    return surfaces[int(index) % len(surfaces)]


## Limit angles to the range [0, 2pi].
def clampDirection(dir):
    result = dir % (math.pi * 2)
    return result


## Clamp the provided value so its magnitude is not over the limit
def clampValue(value, limit):
    if abs(value) > limit:
        return cmp(value, 0) * limit
    return value


## Like clampValue, but with a list of values and a list of clamps
def clampVector(vector, clamps):
    result = []
    for index in range(0, len(vector)):
        result.append(clampValue(vector[index], clamps[index]))
    return result


## Determine if vector is close to any of the vectors in vectorList
def fuzzyVectorMatch(vector, vectorList):
    for alt in vectorList:
        if pointPointDistance(vector, alt) < constants.DELTA:
            return True
    return False

## Return true if the point is somewhat close to the line, based on a 
# bounding box check.
def pointCloseToLine(point, line, maxDist):
    p1 = line.start
    p2 = line.end
    rect = pygame.Rect(min(p1[0], p2[0]) - maxDist, min(p1[1], p2[1]) - maxDist, 
                       abs(p1[0] - p2[0]) + maxDist*2, abs(p1[1] - p2[1]) + maxDist*2)
    return rect.collidepoint(point)


## Return the distance from the point to the line. Logic taken from
# http://www.codeguru.com/forum/printthread.php?t=194400
def pointLineDistance(point, line):
    cx = point[0]
    cy = point[1]
    ax = line.start[0]
    ay = line.start[1]
    bx = line.end[0]
    by = line.end[1]
    # In short: project our endpoint onto the line, then determine how
    # far along that projection we are, then deal with endpoints.

    rNumerator = (cx-ax)*(bx-ax) + (cy-ay)*(by-ay)
    rDenominator = (bx-ax)*(bx-ax) + (by-ay)*(by-ay)
    r = rNumerator / rDenominator

    px = ax + r * (bx - ax) # Projecting onto line
    py = ay + r * (by - ay) # Ditto

    # This is the distance if the line were infinite instead of a 
    # segment
    s = ((ay-cy)*(bx-ax)-(ax-cx)*(by-ay) ) / rDenominator
    distance = abs(s) * math.sqrt(rDenominator)

    # x, y is the point on the line closest to (cx, cy)
    x = px
    y = py
    if r < 0 or r > 1:
        # The projection is not on the line, so look at endpoint
        # distances.
        dist1 = (cx-ax)*(cx-ax) + (cy-ay)*(cy-ay)
        dist2 = (cx-bx)*(cx-bx) + (cy-by)*(cy-by)
        if dist1 < dist2:
            x = ax
            y = ay
            distance = math.sqrt(dist1)
        else:
            x = bx
            y = by
            distance = math.sqrt(dist2)

    return distance


def vectorMagnitude(v):
    return math.sqrt(v[0]**2 + v[1]**2)


def pointPointDistance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def pointPointDistanceSquare(p1, p2):
    return min(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))


## This is frequently used for drawing objects between physics updates.
def interpolatePoints(start, end, percent):
    delta = (end[0] - start[0], end[1] - start[1])
    return [start[0] + delta[0] * percent, start[1] + delta[1] * percent]


def realspaceToGridspace(loc):
    return [int(loc[0] / constants.blockSize), int(loc[1] / constants.blockSize)]


def gridspaceToRealspace(loc):
    return [loc[0] * constants.blockSize, loc[1] * constants.blockSize]


def roundVector(vector):
    return (int(vector[0] + .5), int(vector[1] + .5))


## Select one of a group of options that are provided as a dict, mapping option
# to the weight for that option. For example, if all weights are 1, then every
# option has an equal chance of being chosen. If one weight were 5, then the
# corresponding object would be 5 times more likely to be chosen than its 
# neighbors. 
def pickWeightedOption(options):
    if options is None:
        return None
    totalWeights = 0
    for type, weight in options.iteritems():
        totalWeights += weight
    index = random.randint(0, totalWeights)
    for type, weight in options.iteritems():
        index -= weight
        if index <= 0:
            return type
    print "Failed to select an option from",options
    return None


## Convert a 3x3 array of 0s, 1s, and 2s into a list of scalar values:
# - 0: add zero to result
# - 1: add 2^index to result
# - 2: represents "either 0 or 1", so duplicate the results and add 2^index
# to half the elements.
# This is used to quickly represent which spaces that are adjacent to a given
# block are occupied.
def adjacencyArrayToSignatures(kernel):
    # First, convert the 2D array into a 1D array
    array = []
    for row in kernel:
        array.extend(row)

    result = [0]
    for i in range(0, len(array)):
        temp = []
        if array[i] == 2:
            temp.extend(result)
        if array[i] in [1, 2]:
            result = [x + 2**i for x in result]
        result.extend(temp)
    # Uniquify list on our way out.
    return dict().fromkeys(result).keys()


## Normalize a vector so its magnitude is 1.
def getNormalizedVector(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    mag = math.sqrt(dx**2 + dy**2)
    if mag > constants.EPSILON:
        dx /= mag
        dy /= mag
    return (dx, dy)


## Drop a perpendicular from the point onto the vector and find the
# intersection point.
def projectPointOntoVector(point, vector):
    if abs(vector[0]) < constants.EPSILON:
        # Vertical line
        return (0, point[1])
    m = vector[1] / vector[0]
    x = (m * point[1] + point[0]) / (m**2 + 1)
    y = (m**2 * point[1] + m * point[0]) / (m**2 + 1)
    return (x, y)


## Load a class from the named module. Assumes that the module includes a
# function getClassName() that indicates the name of the class to load.
def loadDynamicClass(path):
    try:
        debug("Loading environment effect",path)
        # In order to allow arbitrary naming of these classes, we first 
        # import a function that tells us the name of the class, then we 
        # import the class itself.
        # \todo: seems like this could be done better somehow.
        nameFuncModule = __import__(path, globals(), locals(), ['getClassName'])
        className = nameFuncModule.getClassName()
        classModule = __import__(path, globals(), locals(), [className])
        initFunc = getattr(classModule, className)
        return initFunc
    except Exception, e:
        fatal("Failed to load module",path,":",e)

