import terrestrialobject
import jetblade
import util

## The Player class handles the player's avatar in the game. 
class Player(terrestrialobject.TerrestrialObject):
    ## Instantiate a Player object
    # \todo (Long-term) Add support for the female version
    def __init__(self):
        terrestrialobject.TerrestrialObject.__init__(self, util.gridspaceToRealspace(jetblade.map.getStartLoc()), 'maleplayer')
        self.canHang = True


    ## Set appropriate flags according to the current input.
    def AIUpdate(self):
        shouldCrawl = False 
        isJumping = False 
        runDirection = 0
        isClimbing = False
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

        if shouldCrawl and self.isGrounded:
            print "Input: crawling"
            self.shouldCrawl = True
        elif not shouldCrawl:
            self.shouldCrawl = False
        # Pressed down while hanging, so let go
        if shouldCrawl and self.isHanging:
            print "Input: Releasing hang"
            self.justStoppedHanging = True

        if isClimbing and self.isHanging:
            self.justStartedClimbing = True

        if isJumping:
            # Start a jump
            print "Input: Jumping"
            self.justJumped = True

        if isClimbing and self.isHanging:
            print "Input: Climbing"
            self.isClimbing = True

        self.runDirection = runDirection

