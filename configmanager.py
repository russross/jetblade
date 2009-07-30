import util
import logger
import constants

import os
import sys
import pygame


## Default player controls if no configuration file is found.
defaultPlayerKeys = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'climb': pygame.K_UP,
    'jump': pygame.K_SPACE,
    'crouch': pygame.K_DOWN,
    'attack': pygame.K_LSHIFT,
    'zoomin': pygame.K_PERIOD,
    'zoomout': pygame.K_COMMA,
    'startRecording': pygame.K_a,
    'toggleDebug': pygame.K_o,
    'quit': pygame.K_ESCAPE,
}

## This class loads general game configuration information (e.g. controls, 
# display resolution, fullscreen modee, etc.). 
class ConfigManager:

    ## Load configuration information from file, or use the defaualts if no
    # file exists.
    def __init__(self):
        ## Maps config keys to their values.
        self.config = {
            'sound': 1,
            'fullscreen': 0,
        }
        ## Maps action names (e.g. 'jump', 'left') to PyGame key identifiers.
        self.controls = defaultPlayerKeys
        filename = self.getConfigPath()
        self.isFirstTimePlaying = False
        if not os.path.exists(filename):
            self.isFirstTimePlaying = True
            self.writeConfig()
        else:
            logger.debug("Reading a file to get config")
            fh = open(filename, 'r')
            for line in fh:
                (action, key) = line.split(':', 1)
                key = key.rstrip()
                if action in defaultPlayerKeys:
                    self.controls[action] = int(key)
                else:
                    self.config[action] = int(key)
            fh.close()

            for action, key in defaultPlayerKeys.items():
                if not action in self.controls:
                    logger.fatal('Controls do not have an entry for action [' + action + ']')
        logger.debug("Controls are",str(self.controls))
            
    def writeConfig(self):
        # Write default controls
        filename = self.getConfigPath()
        fh = open(filename, 'w')
        for action, key in self.controls.iteritems():
            fh.write(action + ':' + str(key) + "\n")
        for action, key in self.config.items():
            fh.write(action + ':' + str(key) + "\n")
        fh.close()

    def setControl(self, action, key):
        self.controls[action] = int(key)
        self.writeConfig()

    def getConfigValue(self, key):
        if key in self.config:
            return self.config[key]
        logger.warn("Don't have a config entry for " + key)
        return None

    def toggleConfigValue(self, key):
        if key in self.config:
            self.config[key] = 1 if not self.config[key] else 0
        self.writeConfig()
        
    def getActionForKey(self, key, context):
        key = int(key)
        if context == constants.CONTEXT_GAME:
            for action, myKey in self.controls.iteritems():
                if key == myKey:
                    return action
        elif context == constants.CONTEXT_MENU:
            if key == K_ESCAPE:
                return constants.ACTION_QUIT
        return None

    def getCurrentActions(self):
        keyStates = pygame.key.get_pressed()
        result = []
        for action, key in self.controls.iteritems():
            if keyStates[key]:
                result.append(action)
        return result

    def getConfigPath(self):
        return self.getHomePath() + '/.jetbladeconfig.txt'

    ## Retrieves the location of the user's home directory, depending on OS.
    def getHomePath(self):
        if sys.platform in ['win32', 'cygwin']:
            return os.environ.get('APPDATA')
        else: # Assume OSX/Linux; both should work
            return os.environ.get('HOME')



       
    def getControls(self):
        return self.controls

    def getIsFirstTimePlaying(self):
        return self.isFirstTimePlaying

