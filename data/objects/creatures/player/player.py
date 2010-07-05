from ...base import terrestrialobject
import game
import logger
import font
import constants
from vector2d import Vector2D

from ...base.terrestrialstates import groundedattackstate
from ...base.terrestrialstates import flinchstate

def getClassName():
    return 'Player'

energyDisplayLoc = Vector2D(20, 20)
energyDisplayColor = (250, 250, 100, 150)

## The Player class handles the player's avatar in the game. 
class Player(terrestrialobject.TerrestrialObject):
    ## Instantiate a Player object
    # \todo (Long-term) Add support for the female version
    def __init__(self):
        terrestrialobject.TerrestrialObject.__init__(self, game.map.getStartLoc().toRealspace(), 'maleplayer')
        self.canHang = True
        self.faction = 'player'
        ## Amount of health remaining before dying
        self.health = 100
        ## Invincibility time after getting hit
        self.invincibilityTimer = 0
        ## Velocity to impart when hit (when facing right)
        self.flinchVel = Vector2D(-40, -10)
        ## Number of frames of invincibility to get after getting hit
        self.mercyInvincibilityFrames = 45
        ## Number of frames to flinch.
        self.flinchFrames = 5

        self.runAcceleration = .8
        self.runDeceleration = 2.4
        self.airAcceleration = 4.8
        self.airDeceleration = 4.8
        self.crawlSpeed = 11.1
        self.jumpSpeed = -15.2
        self.maxJumpRiseFrames = 10
        self.maxGroundVel = Vector2D(17.2, 20)
        self.maxAirVel = Vector2D(8.6, 30.4)


    ## Set appropriate flags according to the current input.
    def AIUpdate(self):
        if self.state.name == 'flinch':
            # No updates to state when flinching.
            self.invincibilityTimer -= 1
            return
        shouldCrawl = False 
        shouldJump = False 
        runDirection = 0
        shouldClimb = False
        isAttacking = False
        for event in game.eventManager.getCurrentActions():
            if event.action == 'left':
                runDirection = -1
            elif event.action == 'right': 
                runDirection = 1
            elif event.action == 'jump':
                shouldJump = True
            elif event.action == 'climb':
                shouldClimb = True
            elif event.action == 'crouch':
                shouldCrawl = True
            elif event.action == 'attack':
                isAttacking = True

        if self.state.name == 'grounded' and isAttacking:
            self.setState(groundedattackstate.GroundedAttackState(self, 'kick1'))

        if shouldCrawl and self.state.name == 'grounded':
            logger.debug("Input: crawling")
            self.shouldCrawl = True
        elif not shouldCrawl:
            self.shouldCrawl = False
        # Pressed down while hanging, so let go
        if shouldCrawl and self.state.name == 'hang':
            logger.debug("Input: Releasing hang")
            self.shouldReleaseHang = True

        if shouldClimb and self.state.name == 'hang':
            self.shouldClimb = True

        if shouldJump:
            # Start a jump
            logger.debug("Input: Jumping")
            self.shouldJump = True

        self.runDirection = runDirection

        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= 1


    ## Make the player flicker if they're invincible. Display the player's
    # vital statistics.
    def draw(self, screen, *args):
        if self.invincibilityTimer == 0 or game.frameNum % 2 == 1:
            terrestrialobject.TerrestrialObject.draw(self, screen, *args)
        # \todo This draws on the same layer the player does (so e.g. behind
        # terrain). 
        game.fontManager.drawText(
                    'MODENINE', 18, 
                    ["Energy: %d" % self.health], 
                    loc = energyDisplayLoc, 
                    color = energyDisplayColor)


    ## Process a collision. Take damage from enemies if we're vulnerable
    def processCollision(self, collision):
        terrestrialobject.TerrestrialObject.processCollision(self, collision)
        if collision.type == 'enemy' and self.invincibilityTimer == 0:
            self.setState(flinchstate.FlinchState(self, collision.altObject))

