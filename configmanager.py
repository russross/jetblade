import util
import constants

import os
import pygame


## Default player controls if no configuration file is found.
defaultPlayerKeys = {
    'left': K_LEFT,
    'right': K_RIGHT,
    'climb': K_UP,
    'jump': K_SPACE,
    'crouch': K_DOWN,
    'zoomin': K_PERIOD,
    'zoomout': K_COMMA,
    'startRecording': K_a,
    'toggleDebug': K_o,
    'quit': K_ESCAPE,
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
            util.debug("Reading a file to get config")
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
                    util.fatal('Controls do not have an entry for action [' + action + ']')
        util.debug("Controls are",str(self.controls))
            
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
        util.warn("Don't have a config entry for " + key)
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
        return util.getHomePath() + '/.jetbladeconfig.txt'
       
    def getControls(self):
        return self.controls

    def getIsFirstTimePlaying(self):
        return self.isFirstTimePlaying
