import jetblade

import pygame
import sys

## @package logger This package contains logging logic (including the Logger
# class), and related constants.

## Different log levels.
(LOG_FATAL, LOG_ERROR, LOG_WARN, LOG_INFORM, LOG_DEBUG) = range(1, 6)
## Descriptor strings for the log levels
logStrings = {
    LOG_DEBUG : 'DEBUG',
    LOG_INFORM : 'INFO',
    LOG_WARN : 'WARNING',
    LOG_ERROR : 'ERROR',
    LOG_FATAL : 'FATAL',
}

defaultLogLevel = LOG_INFORM

## Time in milliseconds to wait after displaying a fatal error, 
# before exiting the program.
errorMessageDelayTime = 10000


## This class simply performs logging and tracks the current log level.
# Instead of calling its log function directly, use one of the module-level
# functions (debug, inform, warn, error, fatal). 
class Logger:
    def __init__(self):
        self.logLevel = defaultLogLevel

    ## Log the provided text at the given log level
    def log(self, level, *entries):
        if self.logLevel >= level:
            string = ''
            for entry in entries:
                string += str(entry) + ' '
            print logStrings[level] + ':',string
            return string
        return None

logger = Logger()


## Set the current log level
def setLogLevel(level):
    logger.logLevel = level


## Get the current log level
def getLogLevel():
    return logger.logLevel

## Log output at the debug level
def debug(*entries):
    return logger.log(LOG_DEBUG, *entries)


## Log output at the inform level
def inform(*entries):
    return logger.log(LOG_INFORM, *entries)


## Log output at the warning level
def warn(*entries):
    return logger.log(LOG_WARN, *entries)


## Log output at the error level
def error(*entries):
    return logger.log(LOG_ERROR, *entries)


## Print an error to the screen, wait a bit, then exit the program. Call this
# function when unrecoverable errors have occurred. 
def fatal(*entries):
    message = log(LOG_FATAL, *entries)
    errorString = "Sorry, an error occurred: " + message
    errorString2 = "The program will now shut down."
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
