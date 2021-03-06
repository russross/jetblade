import constants
import splashscreen

import pygame
import sys
import traceback

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
## Length of lines when displaying fatal errors
fatalMessageLineLength = 140

## This class simply performs logging and tracks the current log level.
# Instead of calling its log function directly, use one of the module-level
# functions (debug, inform, warn, error, fatal). 
class Logger:
    def __init__(self):
        self.logLevel = defaultLogLevel
        self.prevLogLevel = self.logLevel

    ## Log the provided text at the given log level
    def log(self, level, *entries):
        if self.logLevel >= level:
            string = ''
            for entry in entries:
                string += str(entry) + ' '
            print logStrings[level] + ':',string
            if level < LOG_DEBUG and not splashscreen.getIsDoneLoading():
                splashscreen.updateMessage(string)
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
# \todo Update this to work with OpenGL instead of PyGame rendering.
def fatal(*entries):
    message = logger.log(LOG_FATAL, *entries)
    try:
        traceback.print_exc()
    except Exception, e:
        # No traceback to print
        pass
    errorStrings = ["Sorry, an error occurred: "]
    for i in xrange(0, len(message), fatalMessageLineLength):
        errorStrings.append(message[i*fatalMessageLineLength:(i+1)*fatalMessageLineLength])
    errorStrings.append("The program will now shut down.")
    # Draw the strings to the screen...
    sys.exit()


## Switch between the current log level and debug mode
def toggleDebug():
    if logger.logLevel == LOG_DEBUG:
        logger.logLevel = logger.prevLogLevel
        if logger.logLevel == LOG_DEBUG:
            # Previous log level was already debug; default to inform.
            logger.logLevel = LOG_INFORM
    else:
        logger.prevLogLevel = logger.logLevel
        logger.logLevel = LOG_DEBUG
