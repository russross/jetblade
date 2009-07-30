import terrestrialobject
import game

def getClassName():
    return 'DarkClone'


## Standard "evil clone" of the player.
class DarkClone(terrestrialobject.TerrestrialObject):
    def __init__(self, loc):
        terrestrialobject.TerrestrialObject.__init__(self, loc, game.player.name)
        self.canHang = True
        self.prevVel = self.vel


    def AIUpdate(self):
        self.runDirection = cmp(0, self.loc.sub(game.player.loc).x)
        if self.isHanging:
            self.justStartedClimbing = True
        elif (not self.isGrounded or 
                (not self.isCrawling and self.prevVel.x == 0 and 
                 self.vel.x == 0)
             ):
            self.justJumped = True
        self.prevVel = self.vel

