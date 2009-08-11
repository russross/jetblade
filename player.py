import terrestrialobject
import game
import logger
import font
import constants
from vector2d import Vector2D

## Number of frames of invincibility to get after getting hit
mercyInvincibilityFrames = 45
## Default starting health
defaultHealth = 100
## Velocity to impart when hit (when facing right)
flinchVel = Vector2D(-40, -10)

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
        self.health = defaultHealth
        ## Invincibility time after getting hit
        self.invincibilityTimer = 0


    ## Set appropriate flags according to the current input.
    def AIUpdate(self):
        if self.sprite.getCurrentAnimation() == 'flinch':
            # No updates to state when flinching.
            self.invincibilityTimer -= 1
            return
        shouldCrawl = False 
        isJumping = False 
        runDirection = 0
        isClimbing = False
        isAttacking = False
        for event in game.eventManager.getCurrentActions():
            if event.action == 'left':
                runDirection = -1
            elif event.action == 'right': 
                runDirection = 1
            elif event.action == 'jump':
                isJumping = True
            elif event.action == 'climb':
                isClimbing = True
            elif event.action == 'crouch':
                shouldCrawl = True
            elif event.action == 'attack':
                isAttacking = True

        if self.isGrounded and isAttacking:
            self.sprite.setAnimation('kick1')
            self.vel = Vector2D(0, 0)

        if shouldCrawl and self.isGrounded:
            logger.debug("Input: crawling")
            self.shouldCrawl = True
        elif not shouldCrawl:
            self.shouldCrawl = False
        # Pressed down while hanging, so let go
        if shouldCrawl and self.isHanging:
            logger.debug("Input: Releasing hang")
            self.justStoppedHanging = True

        if isClimbing and self.isHanging:
            self.justStartedClimbing = True

        if isJumping:
            # Start a jump
            logger.debug("Input: Jumping")
            self.justJumped = True

        if isClimbing and self.isHanging:
            logger.debug("Input: Climbing")
            self.isClimbing = True

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
                    'MODENINE', screen, 
                    ["Energy: %d" % self.health], 
                    energyDisplayLoc, 18, font.TEXT_ALIGN_LEFT,
                    energyDisplayColor)


    ## Process a collision. Take damage from enemies if we're vulnerable
    def processCollision(self, collision):
        terrestrialobject.TerrestrialObject.processCollision(self, collision)
        if collision.type == 'enemy' and self.invincibilityTimer == 0:
            self.invincibilityTimer = mercyInvincibilityFrames
            self.health -= collision.altObject.touchDamage
            self.sprite.setAnimation('flinch')
            self.vel = Vector2D(flinchVel.x * cmp(collision.altObject.loc.x, self.loc.x), flinchVel.y)
            self.isGrounded = False
            self.isGravityOn = False
            self.shouldApplyVelocityCap = False


    def completeAnimation(self, animation):
        action = animation.name[:-2]
        if action == 'flinch':
            # Restore control after finishing the flinch.
            self.isGravityOn = True
            self.shouldApplyVelocityCap = True
        return terrestrialobject.TerrestrialObject.completeAnimation(self, animation)
