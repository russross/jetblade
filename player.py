import terrestrialobject
import jetblade
import logger
from vector2d import Vector2D

## The Player class handles the player's avatar in the game. 
class Player(terrestrialobject.TerrestrialObject):
    ## Instantiate a Player object
    # \todo (Long-term) Add support for the female version
    def __init__(self):
        terrestrialobject.TerrestrialObject.__init__(self, jetblade.map.getStartLoc().toRealspace(), 'maleplayer')
        self.canHang = True


    ## Set appropriate flags according to the current input.
    def AIUpdate(self):
        shouldCrawl = False 
        isJumping = False 
        runDirection = 0
        isClimbing = False
        isAttacking = False
        for event in jetblade.eventManager.getCurrentActions():
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
            self.isAnimationLocked = True
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

